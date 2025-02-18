# monitor_and_upload.py
from __future__ import print_function
import sys

import requests

from MeasurementUI import start_ui, MeasurementUI

# 添加zygo模組路徑
zygo_path = 'C:\\projects\\zygo2_erp_connector'  # 調整為實際路徑
if zygo_path not in sys.path:
    sys.path.append(zygo_path)

# 然後再導入zygo
from zygo import ui, mx, connectionmanager
from zygo.ui import show_dialog, DialogMode
from zygo.units import Units
import time
from settings_manager import SettingsManager
import threading
from erp_util import ERPAPIUtil
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class MeasurementMonitor:
    def __init__(self):
        self.is_running = True
        self.measurement_lock = threading.Lock()
        self.db_lock = threading.Lock()
        self.last_data = None
        self.current_position = 0
        self.settings_manager = SettingsManager()  # 增加这行
        self.new_data_available = False
        self.upload_error = False
        self.last_upload_error = False

    def _get_next_position(self):
        """获取下一个点位编号"""
        self.current_position += 1
        return str(self.current_position)

    def _get_settings(self):
        with self.db_lock:
            try:
                settings = self.settings_manager.load_current_settings()
                if settings is None:
                    settings = {}

                # 获取点位，但不重置
                position_name = settings.get('position_name', '1')
                try:
                    self.current_position = int(position_name)
                except ValueError:
                    settings['position_name'] = '1'
                    self.current_position = 1

                return settings
            except Exception as e:
                logging.error("Error getting settings: %s", str(e))
                return None

    def _check_settings(self, settings):
        """Validate settings"""
        if not settings:
            logging.warning("No settings found")
            return False
            
        required = ["sample_name", "group_name", "position_name", "operator"]
        if not all(settings.get(key) for key in required):
            missing = [key for key in required if not settings.get(key)]
            logging.warning("Missing required settings: %s", missing)
            return False
            
        return True

    def check_network(self):
        try:
            response = requests.get("https://erp.topgiga.com.tw/", timeout=5)
            return True
        except:
            return False
    def connect_to_zygo(self):
        try:
            self.uid = connectionmanager.connect(host='localhost', port=8733)
            logging.info("Connected to Zygo successfully")
            return True
        except Exception as e:
            logging.error("Failed to connect to Zygo: %s", str(e))
            return False

    def get_measurement_data(self, settings):
        """收集所有测量字段的数据"""

        base_data = {
            'sample_name': settings.get('sample_name', ''),
            'group_name': settings.get('group_name', ''),
            'position_name': settings.get('position_name', ''),
            'operator': settings.get('operator', 'Unknown'),
            'slide_id': settings.get('slide_id', ''),
            'sample_number': settings.get('sample_number', ''),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }


        # 收集 SOP 参数作为 attributes
        sop_params = {}
        excluded_fields = [
            'sample_name', 'group_name', 'position_name',
            'operator', 'measurement_fields', 'timestamp',
            'slide_id', 'sample_number'
        ]
        for key, value in settings.items():
            if key not in excluded_fields:
                sop_params[key] = value


        # 收集测量数据
        measurement_results = []
        has_changes = False

        # 检查 measurement_fields 是否存在
        if 'measurement_fields' not in settings:
            logging.error("No measurement fields found in settings")
            return None

        for field in settings.get('measurement_fields', []):
            try:
                field_name = field['name']
                cleaned_path = [
                    segment.strip().strip('"').strip("'")
                    for segment in field['path'].split(',')
                ]
                path = tuple(cleaned_path)
                value = mx.get_result_number(path, Units.MicroMeters)

                if value is not None:
                    # 创建测量数据记录
                    measurement_data = {
                        'field_name': field_name,
                        'value': value,
                        'attributes': sop_params.copy(),  # 每个测量数据都有相同的 SOP 参数作为属性
                        'operator': base_data['operator']
                    }

                    if (self.last_data is None or
                            field_name not in self.last_data or
                            abs(self.last_data.get(field_name, 0) - value) > 1e-6):
                        has_changes = True

                    measurement_results.append(measurement_data)

            except Exception as e:
                logging.error("Error getting field %s: %s", field_name, str(e))

        if has_changes and measurement_results:
            self.last_data = {result['field_name']: result['value']
                              for result in measurement_results}
            self.new_data_available = True  # 设置新数据标志

            return base_data, measurement_results

        logging.warning("No measurement data available")
        return None

    def monitoring_thread(self):
        while self.is_running:
            try:
                if not hasattr(self, 'uid'):
                    if not self.connect_to_zygo():
                        time.sleep(5)
                        continue

                settings = self._get_settings()
                if not self._check_settings(settings):
                    time.sleep(5)
                    continue

                with self.measurement_lock:
                    data = self.get_measurement_data(settings)
                    if data:
                        # 先更新点位
                        next_pos = self._get_next_position()
                        settings['position_name'] = next_pos
                        # 尝试上传数据
                        success, error = self.upload_to_erp(data, settings)
                        self.last_upload_error = not success
                        logging.info(next_pos)
                        # 无论上传是否成功，都保存新的点位设置
                        self.settings_manager.save_settings(
                            settings["sample_name"],
                            next_pos,  # 使用新点位
                            settings["group_name"],
                            settings["operator"],
                            settings.get("appx_filename", "Unknown.appx"),
                            settings.get("slide_id", "Unknown.appx"),
                            settings.get("sample_number", "Unknown.appx"),
                            settings
                        )
                        logging.info(self.settings_manager.load_current_settings())
                        self.new_data_available = True
                    else:
                        # 當 get_measurement_data 返回 None 時
                        # 重置點位為1
                        # 試片編號初始化為1
                        self.current_position = 0
                        settings['sample_number'] = "1"
                        settings['position_name'] = "1"




                        # 保存更新的設置
                        self.settings_manager.save_settings(
                            settings["sample_name"],
                            settings["position_name"],
                            settings["group_name"],
                            settings["operator"],
                            settings.get("appx_filename", "Unknown.appx"),
                            settings.get("slide_id", "Unknown.appx"),
                            settings.get("sample_number", "Unknown.appx"),
                            settings
                        )

                time.sleep(5)

            except Exception as e:
                logging.error("Error in monitoring thread: %s", str(e))
                time.sleep(5)

    def upload_to_erp(self, data, settings):
        if not self.check_network():
            self.upload_error = True
            self.new_data_available = True
            return False, "Network connection failed"
        """上傳所有測量點的數據"""
        base_data, measurements = data


        # 組合完整的測量數據
        measurement_data_list = []
        for measurement in measurements:
            measurement_data_list.append(measurement)

        # 记录发送的数据用于调试
        logging.info("Uploading measurement data: %s", str(measurement_data_list))

        # 上傳所有測量點
        success, error = ERPAPIUtil.upload_measurement(
            base_data["sample_name"],
            base_data["position_name"],
            base_data["group_name"],
            base_data["operator"],
            settings.get("appx_filename", "Unknown.appx"),
            base_data["slide_id"],
            base_data["sample_number"],
            measurement_data_list
        )

        if success:
            logging.info("Successfully uploaded all measurements")
        else:
            logging.error("Failed to upload measurements: %s", error)
        return success, error

    def start(self):
        # 在启动时重置点位
        self.current_position = 0
        self.monitor_thread = threading.Thread(target=self.monitoring_thread)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logging.info("Monitoring started")

    def stop(self):
        self.is_running = False
        if hasattr(self, 'uid'):
            connectionmanager.terminate()
        logging.info("Monitoring stopped")


def main():
    monitor = MeasurementMonitor()
    try:
        monitor.start()
        while True:
            try:
                # 启动UI
                start_ui(monitor)
            except Exception as e:
                logging.error("UI Error: {0}".format(str(e)))
            # UI关闭后等待一段时间再重新启动
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt")
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
# monitor_and_upload.py
from __future__ import print_function
import sys

if sys.version_info[0] >= 3:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode
else:
    from urllib2 import Request, urlopen, HTTPError, URLError
    from urllib import urlencode

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
            response = urlopen("https://erp.topgiga.com.tw/", timeout=5)
            return True
        except (HTTPError, URLError):
            return False
        except Exception as e:
            logging.error("Network check error: %s" % str(e))
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
        logging.debug("Settings received: %s", str(settings))

        # 基本数据保持不变
        base_data = {
            'sample_name': settings.get('sample_name', ''),
            'group_name': settings.get('group_name', ''),
            'position_name': settings.get('position_name', ''),
            'operator': settings.get('operator', 'Unknown'),
            'slide_id': settings.get('slide_id', ''),
            'sample_number': settings.get('sample_number', ''),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # SOP 参数收集保持不变
        sop_params = {}
        excluded_fields = [
            'sample_name', 'group_name', 'position_name',
            'operator', 'measurement_fields', 'timestamp',
            'slide_id', 'sample_number'
        ]
        for key, value in settings.items():
            if key not in excluded_fields:
                sop_params[key] = value

        # 检查 measurement_fields 是否存在
        if 'measurement_fields' not in settings:
            logging.error("No measurement fields found in settings")
            return None

        # 获取所有需要的字段名
        required_fields = set(field['name'] for field in settings.get('measurement_fields', []))
        logging.debug(f"Required fields: {required_fields}")

        # 收集测量数据
        measurement_results = []
        collected_fields = set()
        has_changes = False

        for field in settings.get('measurement_fields', []):
            try:
                field_name = field['name']
                cleaned_path = [
                    segment.strip().strip('"').strip("'")
                    for segment in field['path'].split(',')
                ]
                path = tuple(cleaned_path)

                # 获取测量值
                value = mx.get_result_number(path, Units.MicroMeters)
                logging.debug(f"Field {field_name} at path {path}: {value}")

                if value is not None:
                    # 创建测量数据记录
                    measurement_data = {
                        'field_name': field_name,
                        'value': value,
                        'attributes': sop_params.copy(),
                        'operator': base_data['operator']
                    }

                    # 检查数据变化
                    if (self.last_data is None or
                            field_name not in self.last_data or
                            abs(self.last_data.get(field_name, 0) - value) > 1e-6):
                        has_changes = True

                    measurement_results.append(measurement_data)
                    collected_fields.add(field_name)

            except Exception as e:
                logging.error(f"Error getting field {field_name}: {str(e)}")

        # 检查是否收集到所有字段
        if collected_fields != required_fields:
            missing = required_fields - collected_fields
            logging.warning(f"Missing data for fields: {missing}")
            logging.warning(f"Collected fields: {collected_fields}")
            return None

        # 只有在有变化且数据完整时才返回
        if has_changes and len(measurement_results) == len(required_fields):
            self.last_data = {result['field_name']: result['value']
                              for result in measurement_results}
            self.new_data_available = True

            logging.info(f"Returning {len(measurement_results)} measurements")
            return base_data, measurement_results

        logging.debug("No changes or incomplete data")
        return None

    def monitoring_thread(self):
        last_settings = None
        important_fields = ["sample_name", "group_name", "slide_id", "sample_number"]

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

                # 检查重要设置是否变化
                important_settings_changed = False
                if last_settings is not None:
                    for field in important_fields:
                        if settings.get(field) != last_settings.get(field):
                            important_settings_changed = True
                            break

                with self.measurement_lock:
                    data = self.get_measurement_data(settings)
                    if data is not None:
                        # 处理有新数据的情况
                        next_pos = self._get_next_position()
                        settings['position_name'] = next_pos
                        success, error = self.upload_to_erp(data, settings)
                        self.last_upload_error = not success

                        # 保存设置
                        self.settings_manager.save_settings(
                            settings["sample_name"],
                            next_pos,
                            settings["group_name"],
                            settings["operator"],
                            settings.get("appx_filename", "Unknown.appx"),
                            settings.get("slide_id", "Unknown.appx"),
                            settings.get("sample_number", "Unknown.appx"),
                            settings
                        )
                    elif important_settings_changed:
                        # 只在重要设置改变时重置
                        self.current_position = 0
                        settings['position_name'] = "1"
                        settings['sample_number'] = "1"

                        # 保存重置后的设置
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

                # 更新上一次的设置
                last_settings = dict(settings)
                time.sleep(5)

            except Exception as e:
                logging.error("Error in monitoring thread: %s" % str(e))
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
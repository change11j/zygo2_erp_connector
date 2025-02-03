# monitor_and_upload.py
from __future__ import print_function
import sys
from zygo import ui, mx, connectionmanager
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

    def _get_settings(self):
        """Thread-safe settings retrieval"""
        with self.db_lock:
            settings_manager = SettingsManager()
            try:
                settings = settings_manager.load_current_settings()
                return settings
            finally:
                settings_manager.close()

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

    def connect_to_zygo(self):
        try:
            self.uid = connectionmanager.connect(host='localhost', port=8733)
            logging.info("Connected to Zygo successfully")
            return True
        except Exception as e:
            logging.error("Failed to connect to Zygo: %s", str(e))
            return False

    def get_measurement_data(self, settings):
        """收集所有測量欄位的數據"""
        base_data = {
            'operator': settings.get('operator', 'Unknown'),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # 加入 SOP 參數（這些將成為 attributes）
        attributes = {}
        for key, value in settings.items():
            if key not in ['sample_name', 'group_name', 'position_name', 'operator', 'measurement_fields', 'timestamp']:
                attributes[key] = value

        # 收集所有測量點的數據
        measurement_results = []
        has_changes = False

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
                    # 為每個測量點創建數據集
                    field_data = {
                        'field_name': field_name,
                        'value': value
                    }
                    # 為每個測量點添加屬性
                    for attr_name, attr_value in attributes.items():
                        field_data[attr_name] = attr_value

                    # 檢查是否有變化
                    if (self.last_data is None or
                            field_name not in self.last_data or
                            abs(self.last_data.get(field_name, 0) - value) > 1e-6):
                        has_changes = True

                    measurement_results.append(field_data)

            except Exception as e:
                logging.error("Error getting field %s: %s", field['name'], str(e))

        if has_changes and measurement_results:
            # 更新最後的數據
            self.last_data = {result['field_name']: result['value']
                              for result in measurement_results}
            return base_data, measurement_results

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
                        base_data, measurement_results = data

                        # 打印基本信息
                        logging.info("New measurement data at: %s", base_data['timestamp'])

                        # 打印每個測量點
                        for measurement in measurement_results:
                            if 'value' in measurement:
                                logging.info("%s: %.6f um", measurement['field_name'], measurement['value'])

                        # 打印屬性
                        for key, value in base_data.items():
                            if key not in ['timestamp', 'operator']:
                                logging.info("%s: %s", key, value)

                        logging.info("-" * 50)

                        # 上傳數據
                        self.upload_to_erp(data, settings)

                time.sleep(5)

            except Exception as e:
                logging.error("Error in monitoring thread: %s", str(e))
                time.sleep(5)

    def upload_to_erp(self, data, settings):
        """上傳所有測量點的數據"""
        base_data, measurements = data

        for measurement in measurements:
            try:
                # 組合完整的數據
                full_data = base_data.copy()
                full_data.update(measurement)

                success, error = ERPAPIUtil.upload_measurement(
                    settings["sample_name"],
                    settings["group_name"],
                    settings["position_name"],
                    full_data
                )

                if success:
                    logging.info("Successfully uploaded measurement: %s = %.6f um",
                                 measurement['field_name'], measurement['value'])
                else:
                    logging.error("Failed to upload measurement %s: %s",
                                  measurement['field_name'], error)

            except Exception as e:
                logging.error("Error uploading measurement %s: %s",
                              measurement['field_name'], str(e))
    def start(self):
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
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt")
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
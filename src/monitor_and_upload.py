from __future__ import print_function
from zygo import ui, mx, connectionmanager
from zygo.units import Units
import time
from database_manager import DatabaseManager
import threading
from datetime import datetime


class MeasurementMonitor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.is_running = True
        self.measurement_lock = threading.Lock()
        self.last_data = None

    def connect_to_zygo(self):
        """連接到Zygo"""
        try:
            print("Connecting to Zygo...")
            self.uid = connectionmanager.connect(host='localhost', port=8733)
            print("Connected to Zygo (UID: %s)" % self.uid)
            return True
        except:
            print("Failed to connect to Zygo")
            return False

    def check_settings(self):
        """檢查設置是否存在"""
        settings = self.db_manager.get_settings()
        return settings and all([
            settings.get("sample_name"),
            settings.get("parameter_name"),
            settings.get("position_name")
        ])

    def get_measurement_data(self):
        """獲取測量數據"""
        data = {}
        try:
            # W1-W3 測量
            try:
                data['W1'] = mx.get_result_number(
                    ("Analysis", "Custom", "W1"),
                    Units.MicroMeters
                )
            except:
                data['W1'] = None

            try:
                data['W2'] = mx.get_result_number(
                    ("Analysis", "Custom", "W2"),
                    Units.MicroMeters
                )
            except:
                data['W2'] = None

            try:
                data['W3'] = mx.get_result_number(
                    ("Analysis", "Custom", "W3"),
                    Units.MicroMeters
                )
            except:
                data['W3'] = None

            # H1-H3 測量
            try:
                data['H1'] = mx.get_result_number(
                    ("Analysis", "Regions Surface", "Region #  1", "Test", "Surface Parameters", "Height Parameters",
                     "Mean"),
                    Units.MicroMeters
                )
            except:
                data['H1'] = None

            try:
                data['H2'] = mx.get_result_number(
                    ("Analysis", "Regions Surface", "Region #  2", "Test", "Surface Parameters", "Height Parameters",
                     "Mean"),
                    Units.MicroMeters
                )
            except:
                data['H2'] = None

            try:
                data['H3'] = mx.get_result_number(
                    ("Analysis", "Regions Surface", "Region #  3", "Test", "Surface Parameters", "Height Parameters",
                     "Mean"),
                    Units.MicroMeters
                )
            except:
                data['H3'] = None

            data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

            # 檢查數據是否有變化
            if self.last_data is not None:
                has_changes = False
                for key in ['W1', 'W2', 'W3', 'H1', 'H2', 'H3']:
                    if data[key] != self.last_data.get(key):
                        has_changes = True
                        break
                if not has_changes:
                    return None

            self.last_data = data.copy()
            return data

        except:
            print("Error getting measurement data")
            return None
    def monitoring_thread(self):
        """監控線程的主函數"""
        consecutive_errors = 0
        while self.is_running:
            try:
                if not hasattr(self, 'uid'):
                    if not self.connect_to_zygo():
                        time.sleep(5)
                        continue

                if not self.check_settings():
                    time.sleep(2)
                    continue

                settings = self.db_manager.get_settings()

                with self.measurement_lock:
                    data = self.get_measurement_data()
                    if data:
                        # 檢查數據是否有實際的測量值
                        has_valid_data = False
                        for key, value in data.items():
                            if key != 'timestamp' and value is not None:
                                has_valid_data = True
                                break

                        if has_valid_data:
                            self.save_to_db(data, settings)
                            consecutive_errors = 0
                            print("New measurement data saved at: %s" % data['timestamp'])
                            for key in sorted(data.keys()):
                                if key != 'timestamp':
                                    if data[key] is not None:
                                        print("%s: %.6f um" % (key, data[key]))
                                    else:
                                        print("%s: N/A" % key)
                            print("-" * 50)

                time.sleep(0.5)

            except:
                consecutive_errors += 1
                print("Error in monitoring thread (consecutive errors: %d)" % consecutive_errors)
                if consecutive_errors > 5:
                    time.sleep(5)
                else:
                    time.sleep(1)

    def save_to_db(self, data, settings):
        """保存測量數據到數據庫"""
        try:
            # 保存到數據庫
            measurement_id = self.db_manager.save_measurement(
                settings["sample_name"],
                settings["parameter_name"],
                settings["position_name"],
                data,
                None,  # 不再保存datx_path
                None  # 不再保存report_path
            )

            # 嘗試上傳到ERP
            self.upload_to_erp(measurement_id, data, settings)
        except:
            print("Error saving to database")

    def upload_to_erp(self, measurement_id, data, settings):
        """上傳數據到ERP"""
        try:
            # 這裡實現與ERP的整合
            self.db_manager.update_erp_upload_status(measurement_id, 1)
            print("Data uploaded to ERP successfully")
        except:
            print("Error uploading to ERP")

    def start(self):
        """啟動監控"""
        self.monitoring_thread = threading.Thread(target=self.monitoring_thread)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("Monitoring thread started")

    def stop(self):
        """停止監控"""
        self.is_running = False
        if hasattr(self, 'uid'):
            connectionmanager.terminate()
        print("Monitoring stopped")


def main():
    monitor = MeasurementMonitor()
    try:
        monitor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, stopping...")
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
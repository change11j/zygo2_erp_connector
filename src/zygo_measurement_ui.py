from __future__ import print_function  # Python 3.4.3 compatibility
import os
from datetime import datetime
from zygo import ui, mx, connectionmanager
from zygo.units import Units
import time
import json

class MeasurementController(object):  # 明確繼承自 object 以支持舊版本
    def __init__(self):
        self.settings = []
        self.current_sample = None
        self.current_parameter = None
        self.current_position = None
        
    def get_measurement_data(self):
        """獲取當前測量數據並打印詳細資訊"""
        data = {}
        print("\nReading measurements...")
        print("-" * 50)


        # 獲取各項測量結果
        try:
            data['W1'] = mx.get_result_number(
                ("Analysis", "Custom", "W1"),
                Units.MicroMeters)
            print("W1: {0:.6f} um".format(data['W1']))
        except Exception as e:
            print("Error reading W1: {0}".format(str(e)))
            data['W1'] = None
            
        try:
            data['W2'] = mx.get_result_number(
                ("Analysis", "Custom", "W2"),
                Units.MicroMeters)
            print("W2: {0:.6f} um".format(data['W2']))
        except Exception as e:
            print("Error reading W2: {0}".format(str(e)))
            data['W2'] = None
            
        try:
            data['W3'] = mx.get_result_number(
                ("Analysis", "Custom", "W3"),
                Units.MicroMeters)
            print("W3: {0:.6f} um".format(data['W3']))
        except Exception as e:
            print("Error reading W3: {0}".format(str(e)))
            data['W3'] = None

        try:
            data['H1'] = mx.get_result_number(
                ("Analysis", "Regions Surface", "Region #  1", "Test", "Surface Parameters", "Height Parameters", "Mean"),
                Units.MicroMeters)
            print("H1: {0:.6f} um".format(data['H1']))
        except Exception as e:
            print("Error reading H1: {0}".format(str(e)))
            data['H1'] = None
            
        try:
            data['H2'] = mx.get_result_number(
                ("Analysis", "Regions Surface", "Region #  2", "Test", "Surface Parameters", "Height Parameters", "Mean"),
                Units.MicroMeters)
            print("H2: {0:.6f} um".format(data['H2']))
        except Exception as e:
            print("Error reading H2: {0}".format(str(e)))
            data['H2'] = None
            
        try:
            data['H3'] = mx.get_result_number(
                ("Analysis", "Regions Surface", "Region #  3", "Test", "Surface Parameters", "Height Parameters", "Mean"),
                Units.MicroMeters)
            print("H3: {0:.6f} um".format(data['H3']))
        except Exception as e:
            print("Error reading H3: {0}".format(str(e)))
            data['H3'] = None

        # 添加時間戳
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        print("Timestamp: {0}".format(data['timestamp']))
        
        print("-" * 50)
        print("All available data keys: {0}".format(list(data.keys())))
        print("\nRaw data dictionary:")
        print(json.dumps(data, indent=2))
        
        return data

    def save_measurement_with_data(self, base_dir):
        """儲存測量數據和額外資訊"""
        if not all([self.current_sample, self.current_parameter, self.current_position]):
            raise ValueError("未設置完整的量測參數")
            
        # 獲取測量數據
        print("\nGetting measurement data...")
        data = self.get_measurement_data()
        if not data:
            raise ValueError("無法獲取測量數據")
            
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = "{0}_{1}_{2}_{3}".format(
            self.current_sample,
            self.current_parameter,
            self.current_position,
            timestamp
        )
        
        # 確保目錄存在
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            print("Created directory: {0}".format(base_dir))
            
        # 儲存原始數據
        datx_path = os.path.join(base_dir, "{0}.datx".format(filename_base))
        mx.save_data(datx_path)
        print("Saved DATX file: {0}".format(datx_path))
        
        # 儲存測量結果
        result_text = []
        result_text.append("Sample: {0}".format(self.current_sample))
        result_text.append("Parameter: {0}".format(self.current_parameter))
        result_text.append("Position: {0}".format(self.current_position))
        result_text.append("Timestamp: {0}".format(data['timestamp']))
        result_text.append("\nMeasurement Results:")
        result_text.append("-" * 50)
        
        for key in ['W1', 'W2', 'W3', 'H1', 'H2', 'H3']:
            if data[key] is not None:
                result_text.append("{0}: {1:.6f} um".format(key, data[key]))
            else:
                result_text.append("{0}: N/A".format(key))
                
        txt_path = os.path.join(base_dir, "{0}_results.txt".format(filename_base))
        with open(txt_path, 'w') as f:
            f.write('\n'.join(result_text))
        print("Saved results file: {0}".format(txt_path))
            
        return datx_path, txt_path

def main():
    try:
        # 連接到Zygo
        print("Connecting to Zygo...")
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo (UID: {0})".format(uid))
        ui.show_dialog("已連接到Zygo (UID: {0})".format(uid), ui.DialogMode.message_ok)

        controller = MeasurementController()
        base_dir = r"D:\Measurements"  # 根據實際需求修改路徑

        while True:
            choice = ui.show_dropdown_dialog(
                "測量控制",
                ["設定測量參數", "執行測量", "查看當前數據", "退出"],
                ui.DialogMode.message_ok_cancel
            )

            if choice == 0:  # 設定參數
                print("\nSetting measurement parameters...")
                sample_name = ui.show_input_dialog(
                    "請輸入Sample名稱：",
                    "",
                    ui.DialogMode.message_ok_cancel,
                    50
                )
                if not sample_name:
                    continue

                parameter_name = ui.show_input_dialog(
                    "請輸入參數名稱：",
                    "",
                    ui.DialogMode.message_ok_cancel,
                    50
                )
                if not parameter_name:
                    continue

                position_name = ui.show_input_dialog(
                    "請輸入量測點位：",
                    "",
                    ui.DialogMode.message_ok_cancel,
                    50
                )
                if not position_name:
                    continue

                controller.current_sample = sample_name
                controller.current_parameter = parameter_name
                controller.current_position = position_name
                
                print("Parameters set:")
                print("Sample: {0}".format(sample_name))
                print("Parameter: {0}".format(parameter_name))
                print("Position: {0}".format(position_name))
                
                ui.show_dialog("測量參數已設定", ui.DialogMode.message_ok)

            elif choice == 1:  # 執行測量
                if not all([controller.current_sample, controller.current_parameter, controller.current_position]):
                    ui.show_dialog("請先設定測量參數", ui.DialogMode.warning_ok)
                    continue

                print("\nExecuting measurement...")
                try:
                    datx_path, txt_path = controller.save_measurement_with_data(base_dir)
                    result_msg = "測量完成！\n\n數據文件：\n{0}\n\n結果文件：\n{1}".format(datx_path, txt_path)
                    print("\nMeasurement completed successfully!")
                    ui.show_dialog(result_msg, ui.DialogMode.message_ok)
                except Exception as e:
                    error_msg = "測量失敗：{0}".format(str(e))
                    print("\nError: {0}".format(error_msg))
                    ui.show_dialog(error_msg, ui.DialogMode.error_ok)

            elif choice == 2:  # 查看當前數據
                print("\nReading current data...")
                try:
                    data = controller.get_measurement_data()
                    if data:
                        msg_parts = []
                        msg_parts.append("時間：{0}".format(data['timestamp']))
                        msg_parts.append("")
                        for key in ['W1', 'W2', 'W3', 'H1', 'H2', 'H3']:
                            if data[key] is not None:
                                msg_parts.append("{0}: {1:.6f} um".format(key, data[key]))
                            else:
                                msg_parts.append("{0}: N/A".format(key))
                        ui.show_dialog("\n".join(msg_parts), ui.DialogMode.message_ok)
                    else:
                        ui.show_dialog("無法獲取測量數據", ui.DialogMode.warning_ok)
                except Exception as e:
                    error_msg = "讀取數據失敗：{0}".format(str(e))
                    print("\nError: {0}".format(error_msg))
                    ui.show_dialog(error_msg, ui.DialogMode.error_ok)

            else:  # 退出
                print("\nExiting program...")
                break

    except Exception as e:
        error_msg = "程式錯誤：{0}".format(str(e))
        print("\nFatal error: {0}".format(error_msg))
        ui.show_dialog(error_msg, ui.DialogMode.error_ok)
    finally:
        connectionmanager.terminate()
        print("\nDisconnected from Zygo")
        ui.show_dialog("已斷開與Zygo的連接", ui.DialogMode.message_ok)

if __name__ == "__main__":
    main()

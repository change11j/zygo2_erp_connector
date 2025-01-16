# history_viewer.py
from __future__ import print_function

import traceback

from zygo import ui
from database_manager import DatabaseManager
import json


class HistoryViewer(object):
    def __init__(self):
        self.db_manager = DatabaseManager()

    def show_history(self):
        """顯示歷史記錄"""
        try:
            while True:
                choice = ui.show_dropdown_dialog(
                    "測量數據查看",
                    ["查看最新數據", "按Sample查詢", "按參數查詢",
                     "按點位查詢", "查看未上傳數據", "退出"],
                    ui.DialogMode.message_ok_cancel
                )

                if choice == 0:  # 查看最新數據
                    records = self.db_manager.get_measurements(limit=10)
                    self.display_records(records)

                elif choice == 1:  # 按Sample查詢
                    sample_name = ui.show_input_dialog(
                        "請輸入Sample名稱：",
                        "",
                        ui.DialogMode.message_ok_cancel,
                        50
                    )
                    if sample_name:
                        records = self.db_manager.get_measurements(sample_name=sample_name)
                        self.display_records(records)

                elif choice == 2:  # 按參數查詢
                    parameter_name = ui.show_input_dialog(
                        "請輸入參數名稱：",
                        "",
                        ui.DialogMode.message_ok_cancel,
                        50
                    )
                    if parameter_name:
                        records = self.db_manager.get_measurements(parameter_name=parameter_name)
                        self.display_records(records)

                elif choice == 3:  # 按點位查詢
                    position_name = ui.show_input_dialog(
                        "請輸入點位名稱：",
                        "",
                        ui.DialogMode.message_ok_cancel,
                        50
                    )
                    # history_viewer.py (續)
                    if position_name:
                        records = self.db_manager.get_measurements(position_name=position_name)
                        self.display_records(records)

                elif choice == 4:  # 查看未上傳數據
                    records = self.db_manager.get_unuploaded_measurements()
                    if records:
                        self.display_records(records, show_upload_status=True)
                    else:
                        ui.show_dialog("目前沒有未上傳的數據", ui.DialogMode.message_ok)

                else:  # 退出
                    break

        except:
            print(traceback.format_exc())

    def display_records(self, records, show_upload_status=False):
        """顯示查詢結果"""
        if not records:
            ui.show_dialog("未找到符合條件的記錄", ui.DialogMode.message_ok)
            return

        # 構建顯示文本
        display_text = []

        for record in records:
            display_text.append("-" * 50)
            display_text.append("ID: {0}".format(record[0]))
            display_text.append("Sample: {0}".format(record[1]))
            display_text.append("Parameter: {0}".format(record[2]))
            display_text.append("Position: {0}".format(record[3]))
            display_text.append("Time: {0}".format(record[6]))  # timestamp

            if show_upload_status:
                status = "已上傳" if record[5] else "未上傳"  # erp_upload_status
                display_text.append("ERP Upload Status: {0}".format(status))

            # 解析測量數據
            try:
                measurement_data = json.loads(record[4])  # measurement_data
                display_text.append("\nMeasurement Data:")
                for key in ['W1', 'W2', 'W3', 'H1', 'H2', 'H3']:
                    if key in measurement_data:
                        if measurement_data[key] is not None:
                            display_text.append("{0}: {1:.6f} um".format(
                                key, measurement_data[key]))
                        else:
                            display_text.append("{0}: N/A".format(key))
            except:
                display_text.append("Error parsing measurement data")

            # 顯示文件路徑
            if record[7]:  # datx_path
                display_text.append("\nDATX file: {0}".format(record[7]))
            if record[8]:  # report_path
                display_text.append("Report file: {0}".format(record[8]))

            # 添加額外的空行，使記錄更易讀
            display_text.append("")

        # 一次性顯示所有記錄
        ui.show_dialog("\n".join(display_text), ui.DialogMode.message_ok)


def main():
    viewer = HistoryViewer()
    viewer.show_history()


if __name__ == "__main__":
    main()
# settings_manager.py
from __future__ import print_function
from zygo import ui
from database_manager import DatabaseManager


def show_settings_dialog():
    """顯示設置對話框"""
    db_manager = DatabaseManager()
    current_settings = db_manager.get_settings() or {}

    # 獲取sample名稱
    sample_name = ui.show_input_dialog(
        "請輸入Sample名稱：",
        current_settings.get("sample_name", ""),
        ui.DialogMode.message_ok_cancel,
        50
    )
    if not sample_name:
        return False

    # 獲取參數名稱
    parameter_name = ui.show_input_dialog(
        "請輸入參數名稱：",
        current_settings.get("parameter_name", ""),
        ui.DialogMode.message_ok_cancel,
        50
    )
    if not parameter_name:
        return False

    # 獲取量測點位
    position_name = ui.show_input_dialog(
        "請輸入量測點位：",
        current_settings.get("position_name", ""),
        ui.DialogMode.message_ok_cancel,
        50
    )
    if not position_name:
        return False

    # 保存設置
    db_manager.save_settings(sample_name, parameter_name, position_name)
    ui.show_dialog("設置保存成功！", ui.DialogMode.message_ok)
    return True


def main():
    show_settings_dialog()


if __name__ == "__main__":
    main()
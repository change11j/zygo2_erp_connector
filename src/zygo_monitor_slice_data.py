from __future__ import print_function
import os
import json
from datetime import datetime
from zygo import mx, ui
from zygo.connectionmanager import connect, terminate
from zygo.units import Units


def connect_to_mx():
    """Connect to Mx"""
    try:
        print("Attempting to connect to Mx...")
        uid = connect(host='localhost', port=8733)
        print("Successfully connected to Mx. UID: {0}".format(uid))
        return True
    except Exception as e:
        print("Failed to connect to Mx: {0}".format(str(e)))
        return False


def save_to_json(data, filename):
    """Save data to JSON file"""
    try:
        save_dir = os.path.join(os.getcwd(), 'surface_data')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        full_path = os.path.join(save_dir, filename)
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("Data saved to: {0}".format(full_path))
        return full_path
    except Exception as e:
        print("Error saving JSON file: {0}".format(str(e)))
        return None


def get_surface_data():
    """Get surface data from specified control path"""
    try:
        # 使用正確的路徑獲取控制項
        control = ui.get_control(("ANALYZE", "Surface", "Surface", "3D Surface Data", "sliceControl1"))

        if not control:
            raise Exception("Could not find the specified control")

        # 收集資料
        data = {
            "timestamp": datetime.now().isoformat(),
            "surface_data": {}
        }

        # 保存控制項資料
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        control_filename = "surface_data_{0}.dat".format(timestamp_str)
        save_dir = os.path.join(os.getcwd(), 'surface_data')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        dat_path = os.path.join(save_dir, control_filename)
        control.save_data(dat_path)

        # 獲取資料矩陣資訊
        data["surface_data"]["dimensions"] = {
            "size_x": mx.get_data_size_x(control, Units.MicroMeters),
            "size_y": mx.get_data_size_y(control, Units.MicroMeters),
            "center_x": mx.get_data_center_x(control, Units.MicroMeters),
            "center_y": mx.get_data_center_y(control, Units.MicroMeters),
            "origin_x": mx.get_data_origin_x(control, Units.MicroMeters),
            "origin_y": mx.get_data_origin_y(control, Units.MicroMeters)
        }

        # 保存 DAT 文件路徑
        data["surface_data"]["dat_file"] = control_filename

        # 儲存為 JSON
        json_filename = "surface_metadata_{0}.json".format(timestamp_str)
        saved_path = save_to_json(data, json_filename)

        return data, saved_path

    except Exception as e:
        print("Error getting surface data: {0}".format(str(e)))
        return None, None


def main():
    try:
        # Connect to Mx
        if not connect_to_mx():
            raise Exception("Failed to connect to Mx")

        # Check if application is open
        if not mx.is_application_open():
            raise Exception("Zygo application is not open")

        print("\nGetting surface data...")
        data, saved_path = get_surface_data()

        if data and saved_path:
            print("\nSuccessfully collected and saved surface data!")
            print("Data saved to: {0}".format(saved_path))
        else:
            print("\nFailed to collect surface data.")

    except Exception as e:
        print("Program error: {0}".format(str(e)))
    finally:
        try:
            terminate()
            print("Connection terminated")
        except:
            pass


if __name__ == "__main__":
    main()
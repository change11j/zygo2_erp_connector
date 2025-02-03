from __future__ import print_function
from zygo import mx, connectionmanager


def connect_to_zygo():
    """連接到Zygo"""
    try:
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected successfully. UID: {0}".format(uid))
        return True
    except Exception as e:
        print("Connection failed: {0}".format(str(e)))
        return False


def get_path_name():
    """獲取路徑名稱"""
    if not connect_to_zygo():
        print("Failed to connect to Zygo")
        return

    try:
        path_name = mx.get_attribute_string(("Analysis", "Custom", "W1"))
        print("Path name: {0}".format(path_name))
    except Exception as e:
        print("Error getting path name: {0}".format(str(e)))
    finally:
        try:
            connectionmanager.terminate()
            print("Connection terminated")
        except Exception as e:
            print("Error terminating connection: {0}".format(str(e)))


def main():
    get_path_name()


if __name__ == "__main__":
    main()
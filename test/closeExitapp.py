from zygo import mx
from zygo.connectionmanager import connect, terminate
from zygo.ui import show_dialog, DialogMode
import time


def check_and_close_mx():
    """
    Check if MX application is running and close it if needed
    Returns:
        bool: True if operation was successful, False otherwise
    """
    try:
        # First establish connection
        connect(host='localhost', port=8733)

        # Check if MX application is open
        is_open = mx.is_application_open()

        if is_open:
            # Get current application path
            current_app = mx.get_application_path()
            print("Found running MX instance at: {0}".format(current_app))

            # Close the application
            print("Closing MX application...")
            mx.close_application()

            # Verify it's closed
            time.sleep(1)  # Give it a moment to close
            if not mx.is_application_open():
                print("MX application closed successfully")
                result = True
            else:
                print("Failed to close MX application")
                result = False
        else:
            print("No running MX instance found")
            result = True

    except Exception as e:
        print("Error occurred: {0}".format(str(e)))
        result = False

    finally:
        # Always terminate the connection
        terminate()

    return result


if __name__ == "__main__":
    check_and_close_mx()
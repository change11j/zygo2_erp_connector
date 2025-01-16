from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx, ui
from zygo.units import Units
import time

def get_current_data():
    """Get current measurement data without measuring"""
    try:
        data = {}
        # Get numeric results with error handling for each
        try:
            data['PV'] = mx.get_result_number(
                ("Analysis", "Surface", "Surface Parameters", "Height Parameters", "PV"),
                Units.MicroMeters)
        except:
            data['PV'] = None

        try:
            data['Mean'] = mx.get_result_number(
                ("Analysis", "Regions Surface", "Region #  1", "Test", "Surface Parameters", "Height Parameters", "Mean"),
                Units.MicroMeters)
        except:
            data['Mean'] = None

        try:
            # 使用 Process Statistics (2) 的路徑
            process_stats_path = ("Analysis", "Intensity Data Processing", "VisionPro Tool Group (1)", "LineWidth")
            data['LineWidth'] = mx.get_result_number(
                process_stats_path,
                Units.MicroMeters)
        except:
            data['LineWidth'] = None

        # Get current time as reference
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

        return data
    except Exception as e:
        print("Error getting data: {0}".format(str(e)))
        return None

def monitor_current_data():
    """Continuously monitor current data"""
    try:
        print("Starting Zygo Data Monitoring...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)

        # Connect to Zygo
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        print("\nMonitoring process statistics...")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)

        last_data = None

        while True:
            try:
                # Get current data
                current_data = get_current_data()

                # Print data values if they've changed
                if current_data:
                    if not last_data or any(current_data.get(k) != last_data.get(k) 
                            for k in current_data if k != 'timestamp'):
                        print("\nNew data detected at: {0}".format(current_data['timestamp']))
                        if current_data['PV'] is not None:
                            print("PV Value: {0:.3f} um".format(current_data['PV']))
                        if current_data['Mean'] is not None:
                            print("Mean Value: {0:.3f} um".format(current_data['Mean']))
                        if current_data.get('LineWidth') is not None:
                            print("LineWidth: {0:.3f} um".format(current_data['LineWidth']))
                        print("-" * 50)
                        last_data = current_data

                time.sleep(2)

            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print("Error in monitoring loop: {0}".format(str(e)))
                time.sleep(5)

    except Exception as e:
        print("Error occurred: {0}".format(str(e)))
    finally:
        connectionmanager.terminate()
        print("Disconnected from Zygo")
        print("Process completed!")

if __name__ == "__main__":
    monitor_current_data()

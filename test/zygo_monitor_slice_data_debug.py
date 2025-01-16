from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx, ui
from zygo.units import Units
import time

def inspect_control(control):
    """Inspect a control object and print its details"""
    print("\nInspecting Control:")
    print("Name: {0}".format(control.name))
    print("ID: {0}".format(control._id))
    print("Path: {0}".format(control.path))
    
    # Try to get direct data using print_data
    try:
        print("\nTrying print_data method:")
        control.print_data()
    except Exception as e:
        print("print_data error: {0}".format(str(e)))

    # # Try to save image to inspect data
    # try:
    #     print("\nTrying save_image method:")
    #     temp_file = "slice_data_temp.png"
    #     control.save_image(temp_file)
    #     print("Saved control image to: {0}".format(temp_file))
    # except Exception as e:
    #     print("save_image error: {0}".format(str(e)))

    # Try to get current data
    try:
        print("\nTrying to get data directly:")
        if hasattr(control, 'data'):
            print("Control data: {0}".format(control.data))
    except Exception as e:
        print("get data error: {0}".format(str(e)))

def get_current_data():
    """Get current measurement data without measuring"""
    try:
        data = {}
        try:
            data['PV'] = mx.get_result_number(
                ("Analysis", "Surface", "Surface Parameters", "Height Parameters", "PV"),
                Units.MicroMeters)
        except:
            data['PV'] = None

        try:
            data['RMS'] = mx.get_result_number(
                ("Analysis", "Surface", "Surface Parameters", "Height Parameters", "RMS"),
                Units.MicroMeters)
        except:
            data['RMS'] = None

        try:
            # Get the slice control and inspect it
            slice_control_path = ("ANALYZE", "Surface", "Surface", "3D Surface Data", "sliceControl1")
            slice_control = ui.get_control(slice_control_path)
            
            if slice_control is not None:
                # Inspect the control for debugging
                inspect_control(slice_control)
                
                # Try to get additional controls
                for child in slice_control.controls:
                    try:
                        inspect_control(child)
                    except Exception as e:
                        print("Error inspecting child control: {0}".format(str(e)))

        except Exception as e:
            print("Error inspecting slice control: {0}".format(str(e)))
            data['Y Distance'] = None

        # Get current time as reference
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

        return data
    except Exception as e:
        print("Error getting data: {0}".format(str(e)))
        return None

def monitor_current_data():
    """Continuously monitor current data"""
    try:
        print("Starting Zygo Data Monitoring with control methods...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)

        # Connect to Zygo
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        print("\nTrying to locate slice control and test control methods...")
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
                        if current_data['RMS'] is not None:
                            print("RMS Value: {0:.3f} um".format(current_data['RMS']))
                        if current_data.get('Y Distance') is not None:
                            print("Y Distance: {0:.3f} um".format(current_data['Y Distance']))
                        print("-" * 50)
                        last_data = current_data

                time.sleep(1)

            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print("Error in monitoring loop: {0}".format(str(e)))
                time.sleep(5)  # Wait longer if there's an error

    except Exception as e:
        print("Error occurred: {0}".format(str(e)))
    finally:
        connectionmanager.terminate()
        print("Disconnected from Zygo")
        print("Process completed!")

if __name__ == "__main__":
    monitor_current_data()

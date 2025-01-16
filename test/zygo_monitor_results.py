from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx
from zygo.units import Units
import time

def get_measurement_data():
    """Get current measurement results"""
    try:
        # Common measurement paths
        paths = {
            "PV": ("Analysis", "Surface", "Surface Parameters", "Height Parameters", "PV"),
            "Sa": ("Analysis", "Surface", "Areal ISO Parameters", "Height Parameters", "Sa"),
            "RMS": ("Analysis", "Surface", "Surface Parameters", "Height Parameters", "RMS"),
            "Measurement Time": ("System", "Load", "Data Time"),  # 獲取測量時間
            "Data Filename": ("System", "Load", "Data Filename")  # 獲取數據文件名
        }
        
        results = {}
        
        # Get numeric results
        for key in ["PV", "Sa", "RMS"]:
            try:
                results[key] = mx.get_result_number(paths[key], Units.MicroMeters)
            except Exception:
                results[key] = None
        
        # Get string results
        for key in ["Measurement Time", "Data Filename"]:
            try:
                results[key] = mx.get_attribute_string(paths[key])
            except Exception:
                results[key] = None
                
        return results
    except Exception as e:
        print("Error getting measurement data: {0}".format(str(e)))
        return None

def monitor_measurements():
    """Monitor measurements continuously"""
    try:
        print("Starting Zygo monitoring...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)
        
        # Connect to Zygo
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        
        # Store last measurement time to detect changes
        last_measurement_time = None
        
        while True:
            try:
                # Get current measurement data
                results = get_measurement_data()
                
                if results and results["Measurement Time"]:
                    current_measurement_time = results["Measurement Time"]
                    
                    # If measurement time has changed, we have new data
                    if current_measurement_time != last_measurement_time:
                        print("\nNew measurement detected at: {0}".format(current_measurement_time))
                        print("File: {0}".format(results["Data Filename"]))
                        print("Results:")
                        print("  PV: {0:.3f} um".format(results["PV"]) if results["PV"] else "  PV: N/A")
                        print("  Sa: {0:.3f} um".format(results["Sa"]) if results["Sa"] else "  Sa: N/A")
                        print("  RMS: {0:.3f} um".format(results["RMS"]) if results["RMS"] else "  RMS: N/A")
                        print("-" * 50)
                        
                        last_measurement_time = current_measurement_time
                
                # Sleep for a short time to prevent high CPU usage
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print("Error in monitoring loop: {0}".format(str(e)))
                time.sleep(5)  # Wait longer if there's an error
                
    except Exception as e:
        print("Error in monitor_measurements: {0}".format(str(e)))
    finally:
        try:
            connectionmanager.terminate()
            print("Disconnected from Zygo")
        except:
            pass
        print("Monitoring ended")

if __name__ == "__main__":
    monitor_measurements()

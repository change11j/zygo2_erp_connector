from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx
from zygo.units import Units
import time

def get_current_data():
    """Get current measurement data"""
    try:
        data = {}
        # 嘗試使用不同的可能路徑來獲取數據
        possible_paths = [
            # 可能的路徑1
            {
                'W1': ("Process Statistics", "Results", "W1"),
                'W2': ("Process Statistics", "Results", "W2"),
                'W3': ("Process Statistics", "Results", "W3"),
                'H1': ("Process Statistics", "Results", "H1"),
                'H2': ("Process Statistics", "Results", "H2"),
                'H3': ("Process Statistics", "Results", "H3")
            },
            # 可能的路徑2
            {
                'W1': ("Results", "Process Stats", "W1"),
                'W2': ("Results", "Process Stats", "W2"),
                'W3': ("Results", "Process Stats", "W3"),
                'H1': ("Results", "Process Stats", "H1"),
                'H2': ("Results", "Process Stats", "H2"),
                'H3': ("Results", "Process Stats", "H3")
            }
        ]
        
        # 遍歷所有可能的路徑
        for paths in possible_paths:
            try:
                for key, path in paths.items():
                    try:
                        value = mx.get_result_number(path, Units.MicroMeters)
                        if value is not None:
                            data[key] = value
                    except:
                        continue
                if data:  # 如果找到了任何數據，就跳出循環
                    break
            except:
                continue
                
        # 添加時間戳
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return data
    except Exception as e:
        print("Error getting data: {0}".format(str(e)))
        return None

def has_data_changed(old_data, new_data):
    """Compare if numeric data has changed"""
    if not old_data or not new_data:
        return True
    for key in ['W1', 'W2', 'W3', 'H1', 'H2', 'H3']:
        if key in old_data and key in new_data:
            if old_data.get(key) != new_data.get(key):
                return True
    return False

def format_data(data):
    """Format data for display"""
    output = []
    if not data:
        return "No data available"
        
    output.append("Time: {0}".format(data['timestamp']))
    
    # Width measurements
    output.append("\nWidth Measurements:")
    for key in ['W1', 'W2', 'W3']:
        if key in data:
            output.append("{0}: {1:.3f} um".format(key, data[key]))
    
    # Height measurements
    output.append("\nHeight Measurements:")
    for key in ['H1', 'H2', 'H3']:
        if key in data:
            output.append("{0}: {1:.3f} um".format(key, data[key]))
    
    return "\n".join(output)

def monitor_current_data():
    """Continuously monitor current data"""
    try:
        print("Starting Zygo W/H Values Monitoring...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)
        
        # Connect to Zygo
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        print("\nMonitoring W1-W3 and H1-H3 values...")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        last_data = None
        
        while True:
            try:
                # Get current data
                current_data = get_current_data()
                
                # If data exists and has changed, print it
                if current_data and has_data_changed(last_data, current_data):
                    print("\nNew values detected!")
                    print(format_data(current_data))
                    print("-" * 50)
                    
                    last_data = current_data
                
                # Sleep to prevent high CPU usage
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

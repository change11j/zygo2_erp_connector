from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx
from zygo.units import Units
import time

def get_process_statistics():
    """Get data from Process Statistics (2)"""
    data = {}
    
    try:
        # Define the base path for Process Statistics (2)
        base_paths = [
            ("Process Statistics (2)",),
            ("Process Statistics (2)", "Results"),
            ("AUTOMATE", "Pattern", "Pattern Editor", "Process Statistics (2)")
        ]
        
        # Items to monitor
        items = [
            'W1', 'W2', 'W3', 'L1', 'L2', 'L3', 'H1', 'H2', 'H3',
            'Mean', 'Min', 'Max', 'Range', 'Total', 'Cv %', 'Std Dev', '2 Sigma', '3 Sigma'
        ]
        
        # Try to get values using bulk method
        all_paths = []
        for base in base_paths:
            for item in items:
                all_paths.append(base + (item,))
        
        try:
            values = mx.get_bulk_result_values([(path, Units.MicroMeters) for path in all_paths])
            if values:
                for path, value in zip(all_paths, values):
                    try:
                        if value and value.strip():  # Check if value is not empty
                            key = "_".join(path)  # Create key from full path
                            data[key] = float(value)
                    except:
                        continue
        except Exception as e:
            print("Error getting bulk values: {0}".format(str(e)))
            
            # If bulk method fails, try individual gets
            for path in all_paths:
                try:
                    value = mx.get_result_number(path, Units.MicroMeters)
                    if value is not None:
                        key = "_".join(path)
                        data[key] = value
                except:
                    continue
        
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        print("Error in get_process_statistics: {0}".format(str(e)))
    
    return data

def format_data(data):
    """Format data for display"""
    if not data:
        return "No data available"
    
    output = []
    output.append("Time: {0}".format(data['timestamp']))
    output.append("\nProcess Statistics Data:")
    
    # Group measurements by type
    for category in ['W', 'L', 'H']:
        measurements = []
        for i in range(1, 4):  # 1 to 3
            key = "Process Statistics (2)_{0}{1}".format(category, i)
            if key in data:
                measurements.append("{0}{1}: {2:.3f}".format(category, i, data[key]))
        
        if measurements:
            output.append("\n{0} Measurements:".format(
                "Width" if category == 'W' else 
                "Length" if category == 'L' else 
                "Height"
            ))
            output.extend(["  " + m for m in measurements])
    
    # Statistics
    stats = []
    stat_keys = ['Mean', 'Min', 'Max', 'Range', 'Total', 'Cv %', 'Std Dev', '2 Sigma', '3 Sigma']
    for stat in stat_keys:
        key = "Process Statistics (2)_{0}".format(stat)
        if key in data:
            stats.append("{0}: {1:.3f}".format(stat, data[key]))
    
    if stats:
        output.append("\nStatistics:")
        output.extend(["  " + s for s in stats])
    
    return "\n".join(output)

def monitor_process_statistics():
    """Continuously monitor process statistics"""
    try:
        print("Starting Zygo Process Statistics Monitoring...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)
        
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        print("\nMonitoring Process Statistics (2)...")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        last_data = None
        
        while True:
            try:
                current_data = get_process_statistics()
                
                # Check if we have new data
                if current_data and (last_data is None or 
                   any(current_data.get(k) != last_data.get(k) 
                       for k in current_data if k != 'timestamp')):
                    print("\nNew data detected!")
                    print(format_data(current_data))
                    print("-" * 50)
                    last_data = current_data
                
                time.sleep(1)
                
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
    monitor_process_statistics()

from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx
from zygo.units import Units
import time

def get_all_possible_data():
    """Try to get all possible data using bulk methods"""
    data = {}
    
    # Define measurement items
    items = ['W1', 'W2', 'W3', 'L1', 'L2', 'L3', 'H1', 'H2', 'H3']
    
    # Define possible base paths
    base_paths = [
        ("Process Statistics", "Results"),
        ("Results", "Process Stats"),
        ("Process Statistics",)
    ]
    
    # Create all possible path combinations
    all_paths = []
    for base in base_paths:
        for item in items:
            all_paths.append(base + (item,))
    
    # Try to get values using bulk methods
    try:
        # Try bulk result values
        values = mx.get_bulk_result_values([(path, Units.MicroMeters) for path in all_paths])
        if values:
            for path, value in zip(all_paths, values):
                try:
                    if value and value.strip():  # Check if value is not empty
                        data[path[-1]] = float(value)
                except:
                    continue
                    
        # Also try summary statistics
        stat_paths = []
        for base in base_paths:
            for stat in ['Mean', 'Std Dev', '2 Sigma', '3 Sigma', 'Min', 'Max', 'Range']:
                for item in items:
                    # Try different possible paths for statistics
                    stat_paths.extend([
                        base + ("Summary Statistics", stat, item),
                        base + ("Statistics", stat, item),
                        base + (stat, item)
                    ])
        
        stat_values = mx.get_bulk_result_values([(path, Units.MicroMeters) for path in stat_paths])
        if stat_values:
            for path, value in zip(stat_paths, stat_values):
                try:
                    if value and value.strip():  # Check if value is not empty
                        key = "{0}_{1}".format(path[-2], path[-1])  # Combine stat name and item
                        data[key] = float(value)
                except:
                    continue
                    
    except Exception as e:
        print("Error getting bulk values: {0}".format(str(e)))
    
    data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    return data

def format_data(data):
    """Format data for display"""
    if not data:
        return "No data available"
    
    output = []
    output.append("Time: {0}".format(data['timestamp']))
    output.append("\nMeasurements Found:")
    
    # Main measurements
    categories = {
        'Width': ['W1', 'W2', 'W3'],
        'Length': ['L1', 'L2', 'L3'],
        'Height': ['H1', 'H2', 'H3']
    }
    
    for category, items in categories.items():
        found_items = False
        category_output = []
        for item in items:
            if item in data:
                if not found_items:
                    category_output.append("\n{0} Measurements:".format(category))
                    found_items = True
                category_output.append("  {0}: {1:.3f} um".format(item, data[item]))
        output.extend(category_output)
    
    # Statistics
    stats_found = False
    stats_output = []
    stat_types = ['Mean', 'Std Dev', '2 Sigma', '3 Sigma', 'Min', 'Max', 'Range']
    categories = ['W1', 'W2', 'W3', 'L1', 'L2', 'L3', 'H1', 'H2', 'H3']
    
    for category in categories:
        found_stats = False
        category_stats = []
        for stat in stat_types:
            key = "{0}_{1}".format(stat, category)
            if key in data:
                if not stats_found:
                    stats_output.append("\nStatistics Found:")
                    stats_found = True
                if not found_stats:
                    category_stats.append("\n  {0} Statistics:".format(category))
                    found_stats = True
                category_stats.append("    {0}: {1:.3f}".format(stat, data[key]))
        stats_output.extend(category_stats)
    
    output.extend(stats_output)
    return "\n".join(output)

def monitor_current_data():
    """Continuously monitor current data"""
    try:
        print("Starting Zygo Data Monitoring...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)
        
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        print("\nMonitoring all available data...")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        last_data = None
        
        while True:
            try:
                current_data = get_all_possible_data()
                
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
    monitor_current_data()

from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx
from zygo.units import Units
import time

# 全局定義測量項目，這樣所有函數都可以訪問
MEASURE_ITEMS = ['W1', 'W2', 'W3', 'L1', 'L2', 'L3', 'H1', 'H2', 'H3']

def try_get_result(path, unit=Units.MicroMeters):
    """嘗試獲取特定路徑的結果"""
    try:
        return mx.get_result_number(path, unit)
    except:
        return None

def get_current_data():
    """Get current measurement data"""
    try:
        data = {}
        
        # 可能的基礎路徑
        base_paths = [
            ("Process Statistics", "Results"),
            ("Results", "Process Stats"),
            ("Results",),
            ("Process Statistics",),
            ()  # 空路徑也試試
        ]
        
        # 遍歷所有可能的路徑組合
        for base_path in base_paths:
            for item in MEASURE_ITEMS:
                # 嘗試不同的路徑組合
                possible_paths = [
                    base_path + (item,),
                    base_path + (item + " (µm)",),
                    base_path + ("Sample", item),
                    base_path + ("Results", item),
                    base_path + ("Measurement", item)
                ]
                
                for path in possible_paths:
                    value = try_get_result(path)
                    if value is not None:
                        data[item] = value
                        break  # 如果找到值就跳出內層循環
                        
            # 如果找到了所有項目就跳出
            if len(data) >= len(MEASURE_ITEMS):
                break
                
        # 嘗試獲取統計數據
        stat_types = ['Mean', 'Std Dev', '2 Sigma', '3 Sigma', 'Min', 'Max', 'Range']
        for stat in stat_types:
            for item in MEASURE_ITEMS:
                for base_path in base_paths:
                    possible_stat_paths = [
                        base_path + ("Summary Statistics", stat, item),
                        base_path + (stat, item),
                        base_path + ("Statistics", stat, item)
                    ]
                    
                    for path in possible_stat_paths:
                        value = try_get_result(path)
                        if value is not None:
                            data["{0}_{1}".format(stat, item)] = value
                            break
        
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return data
        
    except Exception as e:
        print("Error getting data: {0}".format(str(e)))
        return None

def format_data(data):
    """Format data for display"""
    if not data:
        return "No data available"
    
    output = []
    output.append("Time: {0}".format(data['timestamp']))
    
    # 主要測量值
    categories = {
        'Width': ['W1', 'W2', 'W3'],
        'Length': ['L1', 'L2', 'L3'],
        'Height': ['H1', 'H2', 'H3']
    }
    
    for category, items in categories.items():
        output.append("\n{0} Measurements:".format(category))
        for item in items:
            if item in data:
                output.append("{0}: {1:.3f} um".format(item, data[item]))
    
    # 統計數據
    stat_types = ['Mean', 'Std Dev', '2 Sigma', '3 Sigma', 'Min', 'Max', 'Range']
    for item in MEASURE_ITEMS:
        stats = []
        for stat in stat_types:
            key = "{0}_{1}".format(stat, item)
            if key in data:
                stats.append("{0}: {1:.3f}".format(stat, data[key]))
        if stats:
            output.append("\n{0} Statistics:".format(item))
            output.extend("  " + s for s in stats)
    
    return "\n".join(output)

def monitor_current_data():
    """Continuously monitor current data"""
    try:
        print("Starting Zygo Statistics Monitoring...")
        print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        print("-" * 50)
        
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo. UID: {0}".format(uid))
        print("\nMonitoring process statistics...")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        last_data = None
        
        while True:
            try:
                current_data = get_current_data()
                
                # 檢查是否有新數據
                if current_data and (last_data is None or 
                   any(current_data.get(k) != last_data.get(k) 
                       for k in current_data if k != 'timestamp')):
                    print("\nNew values detected!")
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

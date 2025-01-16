#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zygo Realtime Measurement Test Program (Python 3.4.3)
監聽即時測量數據
"""

import sys
import time
from datetime import datetime
from zygo import (
    connectionmanager,
    mx,
    instrument,
    units
)

def monitor_measurement():
    """Monitor realtime measurement data"""
    try:
        # Connect to Zygo
        uid = connectionmanager.connect()
        print("Connected to Zygo. UID: {0}".format(uid))
        
        print("\nStarting measurement monitor...")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        # Continuous monitoring loop
        counter = 0
        while True:
            try:
                # Try to get current measurement data
                peak = mx.get_result_number(("Results", "Peak"), units.Units.MicroMeters)
                valley = mx.get_result_number(("Results", "Valley"), units.Units.MicroMeters)
                pv = mx.get_result_number(("Results", "PV"), units.Units.MicroMeters)
                rms = mx.get_result_number(("Results", "RMS"), units.Units.MicroMeters)

                # Print the results
                print("\nMeasurement #{0} at {1}:".format(
                    counter, 
                    datetime.now().strftime("%H:%M:%S")
                ))
                print("Peak: {0:.3f} um".format(peak) if peak is not None else "Peak: No Data")
                print("Valley: {0:.3f} um".format(valley) if valley is not None else "Valley: No Data")
                print("P-V: {0:.3f} um".format(pv) if pv is not None else "P-V: No Data")
                print("RMS: {0:.3f} um".format(rms) if rms is not None else "RMS: No Data")

                # Check measurement status
                is_measuring = False  # 這裡可以加入檢查是否正在測量的邏輯
                if is_measuring:
                    print("Status: Measuring...")
                else:
                    print("Status: Waiting for measurement")

            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print("Failed to get measurement: {0}".format(str(e)))
            
            counter += 1
            time.sleep(1)  # 等待1秒再檢查下一次

    except Exception as e:
        print("Monitor error: {0}".format(str(e)))
    finally:
        try:
            connectionmanager.terminate()
            print("\nDisconnected from Zygo")
        except:
            pass

def main():
    print("Starting Zygo Realtime Measurement Monitor...")
    print("Time: {0}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("-" * 50)
    
    monitor_measurement()
    
    print("\nMonitor completed!")

if __name__ == "__main__":
    main()

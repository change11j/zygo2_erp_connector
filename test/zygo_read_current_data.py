from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx
from zygo.units import Units
import time

try:
    print("Starting Zygo Data Reading...")
    print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
    print("-" * 50)
    
    # Connect to Zygo
    uid = connectionmanager.connect(host='localhost', port=8733)
    print("Connected to Zygo. UID: {0}".format(uid))
    
    # Directly read current results without measuring
    try:
        # Get measurement results
        pv = mx.get_result_number(("Analysis", "Surface", "Surface Parameters", "Height Parameters", "PV"), 
                                Units.MicroMeters)
        rms = mx.get_result_number(("Analysis", "Surface", "Surface Parameters", "Height Parameters", "RMS"), 
                                 Units.MicroMeters)
        ra = mx.get_result_number(("Analysis", "Surface", "Surface Parameters", "Height Parameters", "Ra"), 
                                Units.MicroMeters)
        
        print("\nCurrent Results:")
        print("PV Value: {0:.3f} um".format(pv))
        print("RMS Value: {0:.3f} um".format(rms))
        print("Ra Value: {0:.3f} um".format(ra))
        
    except Exception as e:
        print("Error reading results: {0}".format(str(e)))

except Exception as e:
    print("Error occurred: {0}".format(str(e)))
finally:
    connectionmanager.terminate()
    print("Disconnected from Zygo")
    print("Process completed!")

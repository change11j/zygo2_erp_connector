from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import connectionmanager, mx, instrument, units
import time

try:
    print("Starting Zygo Data Acquisition...")
    print("Time: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
    print("-" * 50)
    
    # Connect to Zygo
    uid = connectionmanager.connect(host='localhost', port=8733)
    print("Connected to Zygo. UID: {0}".format(uid))
    
    # Perform measurement
    measure_task = instrument.measure(wait=True)
    print("Measurement completed")
    
    # Get measurement results
    # Note: These paths need to be adjusted based on actual result items shown in your MX software
    pv = mx.get_result_number(("Results", "PV"), unit=units.Units.MicroMeters)
    rms = mx.get_result_number(("Results", "RMS"), unit=units.Units.MicroMeters)
    ra = mx.get_result_number(("Results", "Ra"), unit=units.Units.MicroMeters)
    
    print("\nMeasurement Results:")
    print("PV Value: {0:.3f} um".format(pv))
    print("RMS Value: {0:.3f} um".format(rms))
    print("Ra Value: {0:.3f} um".format(ra))

except Exception as e:
    print("Error occurred: {0}".format(str(e)))
finally:
    connectionmanager.terminate()
    print("Disconnected from Zygo")
    print("Process completed!")

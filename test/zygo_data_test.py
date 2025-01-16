import zygo.mx as mx
import zygo.core as zc
import zygo.ui as ui
from zygo.connectionmanager import connect, terminate
import logging
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
print("Starting Zygo connection and data test...")

try:
    # Establish connection
    uid = connect(force_if_active=True, host='localhost', port=8733)
    print('Connected successfully. UID: {0}'.format(uid))
    
    # Get application info
    print('Is application open? {0}'.format(mx.is_application_open()))
    print('Mx Version: {0}'.format(mx.get_mx_version()))
    
    # Basic data information
    try:
        # Get current data size if data is loaded
        # Using default control path and unit
        control_path = "Surface"  # 这个路径可能需要根据实际情况调整
        unit = "MicroMeters"  # 微米单位
        
        size_x = mx.get_data_size_x(control_path, unit)
        size_y = mx.get_data_size_y(control_path, unit)
        print('Current data size: {0} x {1} {2}'.format(size_x, size_y, unit))
        
        # Get data origin coordinates
        origin_x = mx.get_data_origin_x(control_path, unit)
        origin_y = mx.get_data_origin_y(control_path, unit)
        print('Data origin: ({0}, {1}) {2}'.format(origin_x, origin_y, unit))
        
        # Get data center coordinates
        center_x = mx.get_data_center_x(control_path, unit)
        center_y = mx.get_data_center_y(control_path, unit)
        print('Data center: ({0}, {1}) {2}'.format(center_x, center_y, unit))
        
        # Try to get some basic results if available
        print('\nAttempting to analyze data...')
        mx.analyze()
        time.sleep(1)  # Give some time for analysis
        
        # Get control values example
        try:
            control_value = mx.get_control_string("Measurement")
            print('Measurement control value: {0}'.format(control_value))
        except:
            print('Could not get measurement control value')
            
        # Get result example
        try:
            result_value = mx.get_result_number("PV")
            print('PV result: {0}'.format(result_value))
        except:
            print('Could not get PV result')
        
    except zc.ZygoError as e:
        print('Data operation error: {0}'.format(str(e)))
        
    # UI interaction example
    try:
        print('\nUI Operations:')
        tabs = ui.get_tabs()
        print('Available tabs:')
        for tab in tabs:
            print('- {0}'.format(tab))
            
    except zc.ZygoError as e:
        print('UI operation error: {0}'.format(str(e)))

except zc.ZygoError as e:
    print('Connection error: {0}'.format(str(e)))
except Exception as e:
    print('Other error: {0}'.format(str(e)))
finally:
    try:
        terminate()
        print('Connection terminated')
    except:
        pass
import zygo.mx as mx
import zygo.core as zc
from zygo.connectionmanager import connect, terminate
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
print("Starting connection attempt...")

try:
    # Establish connection
    uid = connect(force_if_active=True, host='localhost', port=8733)
    print('Connected successfully. UID: {0}'.format(uid))
    
    # Basic application check
    print('Is application open? {0}'.format(mx.is_application_open()))
    
    # Add more API calls here after confirming available methods
    
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
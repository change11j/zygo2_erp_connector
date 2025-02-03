from zygo import motion
from zygo.connectionmanager import connect, terminate
import time

try:
    # Establish connection
    print("Establishing connection...")
    uid = connect(host='localhost', port=8733)
    print("Connected, UID: {0}".format(uid))
    time.sleep(1)  # Wait for stable connection

    # Record start time
    print("Starting xy-home test...")
    start_time = time.time()
    motion.home_xy()


except Exception as e:
    print(e)
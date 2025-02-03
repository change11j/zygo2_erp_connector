from zygo.motion import move_x, move_y
from zygo.units import Units
from zygo.connectionmanager import connect, terminate
import time

try:
    # Establish connection
    print("Establishing connection...")
    uid = connect(host='localhost', port=8733)
    print("Connected, UID: {0}".format(uid))
    time.sleep(1)  # Wait for stable connection

    # Record start time
    print("Starting movement test...")
    start_time = time.time()

    # Move up (Y+) 5mm
    print("Moving up 5mm...")
    move_y(5, Units.MilliMeters, wait=True)
    time.sleep(1)  # Wait 1 second

    # Move right (X+) 5mm
    print("Moving right 5mm...")
    move_x(5, Units.MilliMeters, wait=True)
    time.sleep(1)  # Wait 1 second

    # Return to origin - X first, then Y
    print("Returning to origin...")
    move_x(0, Units.MilliMeters, wait=True)
    time.sleep(1)  # Wait 1 second
    move_y(0, Units.MilliMeters, wait=True)

    # Record end time and calculate duration
    duration = time.time() - start_time
    print("Test complete! Total time: {0:.2f} seconds".format(duration))

except Exception as e:
    print("Error occurred: {0}".format(str(e)))

finally:
    # Ensure connection is properly closed
    print("Closing connection...")
    terminate()
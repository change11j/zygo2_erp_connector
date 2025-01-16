#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zygo2 API Test Program (Python 3.4.3)
"""

import sys
import time
import locale
from datetime import datetime
from zygo import (
    connectionmanager,
    mx,
    instrument,
    motion,
    recipe,
    units,
    ui
)

def check_encoding():
    """Check system encodings"""
    print("System Encoding Information:")
    print("Default Encoding:", sys.getdefaultencoding())
    print("Filesystem Encoding:", sys.getfilesystemencoding())
    print("Preferred Encoding:", locale.getpreferredencoding())
    print("Stdout Encoding:", sys.stdout.encoding)
    print("-" * 50)

def test_connection():
    """Test connection to Zygo"""
    try:
        # Connect to Zygo (default: localhost:8733)
        uid = connectionmanager.connect()
        print("Successfully connected to Zygo! UID: {0}".format(uid))
        
        # Get MX version
        version = mx.get_mx_version()
        print("MX Version: {0}".format(version))
        
        # Check application status
        is_open = mx.is_application_open()
        print("Application Status: {0}".format("Open" if is_open else "Closed"))
        
        if is_open:
            app_path = mx.get_application_path()
            print("Current Application: {0}".format(app_path))
        
        return True
    except Exception as e:
        print("Connection failed: {0}".format(str(e)))
        return False

def test_z_motion():
    """Test Z-axis motion control"""
    try:
        # Get current Z position
        z = motion.get_z_pos(units.Units.MicroMeters)
        print("Current Z position: {0} um".format(z))
        
        # Test small movement
        test_move = 1000.0  # only move 10 microns for testing
        print("Testing Z-axis movement {0} um...".format(test_move))
        
        # Move up
        target_z = z + test_move
        motion.move_z(target_z, units.Units.MicroMeters, wait=True)
        time.sleep(10)  # wait for stabilization
        
        # Check position
        new_z = motion.get_z_pos(units.Units.MicroMeters)
        print("Z position after movement: {0} um".format(new_z))
        
        # Return to original position
        print("Returning to original position...")
        motion.move_z(z, units.Units.MicroMeters, wait=True)
        time.sleep(1)  # wait for stabilization
        
        # Verify return position
        final_z = motion.get_z_pos(units.Units.MicroMeters)
        print("Final Z position: {0} um".format(final_z))
        
        return True
    except Exception as e:
        print("Z-axis control failed: {0}".format(str(e)))
        return False
def test_y_motion():
    """Test y-axis motion control"""
    try:
        # Get current T position
        y = motion.get_y_pos(units.Units.MicroMeters)
        print("Current Y position: {0} um".format(y))

        # Test small movement
        test_move = 100.0  # only move 10 microns for testing
        print("Testing Y-axis movement {0} um...".format(test_move))

        # Move down
        target_y = y + test_move
        motion.move_z(target_y, units.Units.MicroMeters, wait=True)
        time.sleep(1)  # wait for stabilization

        # Check position
        new_y = motion.get_y_pos(units.Units.MicroMeters)
        print("Y position after movement: {0} um".format(new_y))

        # Return to original position
        print("Returning to original position...")
        motion.move_y(y, units.Units.MicroMeters, wait=True)
        time.sleep(1)  # wait for stabilization

        # Verify return position
        final_y = motion.get_y_pos(units.Units.MicroMeters)
        print("Final y position: {0} um".format(final_y))

        return True
    except Exception as e:
        print("Y-axis control failed: {0}".format(str(e)))
        return False

def test_current_status():
    """Test current status and parameters"""
    try:
        # Get camera resolution
        cam_res = instrument.get_cam_res(units.Units.MicroMeters)
        print("Camera Resolution: {0} um".format(cam_res))
        
        # Get camera size
        cam_x = instrument.get_cam_size_x(units.Units.Pixels)
        cam_y = instrument.get_cam_size_y(units.Units.Pixels)
        print("Camera Size: {0}x{1} pixels".format(cam_x, cam_y))
        
        # Get Z-axis position
        try:
            z = motion.get_z_pos(units.Units.MicroMeters)
            print("Z-axis Position: {0} um".format(z))
        except:
            print("Unable to get Z-axis position")
            
        # Check system logging
        try:
            mx.log_info("System Status Check")
            print("System logging is working")
        except:
            print("System logging failed")
        
        return True
    except Exception as e:
        print("Status check failed: {0}".format(str(e)))
        return False

def main():
    """Main function"""
    print("Starting Zygo API Test...")
    print("Test Time: {0}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("-" * 50)
    
    # Check system encoding
    check_encoding()
    
    try:
        # Test connection
        if not test_connection():
            print("Connection test failed, stopping further tests")
            return
            
        # Check current status
        print("\nChecking System Status:")
        print("-" * 50)
        test_current_status()
        
        # Test Z-axis motion
        print("\nTesting Z-axis Motion Control:")
        print("-" * 50)
        test_z_motion()
        # Test Y-axis motion
        print("\nTesting Y-axis Motion Control:")
        print("-" * 50)
        test_y_motion()
        
        print("\nBasic function tests completed")
        
    except Exception as e:
        print("\nTest process error: {0}".format(str(e)))
    
    finally:
        # Ensure disconnection
        try:
            connectionmanager.terminate()
            print("\nDisconnected from Zygo")
        except:
            pass
            
        print("\nTest completed!")

if __name__ == "__main__":
    main()

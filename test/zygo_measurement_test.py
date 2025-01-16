#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zygo Measurement Data Test Program (Python 3.4.3)
"""

import sys
import time
from datetime import datetime
from zygo import (
    connectionmanager,
    mx,
    instrument,
    motion,
    units,
    ui
)

def try_get_custom_results():
    """Try to get results using different control paths"""
    try:
        print("\nTrying different result paths...")
        print("-" * 50)
        
        # Try various common control path combinations
        test_paths = [
            ("Analysis", "Results"),
            ("Measurement", "Results"),
            ("Process", "Results"),
            ("Surface", "Results"),
            ("Results",)
        ]
        
        for path in test_paths:
            try:
                # Try to get result as number
                try:
                    value = mx.get_result_number(path, units.Units.MicroMeters)
                    print("Path {0}: {1} um".format(path, value))
                except:
                    # Try to get result as string
                    try:
                        value = mx.get_result_string(path)
                        print("Path {0}: {1}".format(path, value))
                    except:
                        print("Path {0}: Not available".format(path))
            except:
                continue

    except Exception as e:
        print("Failed to get custom results: {0}".format(str(e)))

def try_get_attributes():
    """Try to get various attributes"""
    try:
        print("\nTrying to get attributes...")
        print("-" * 50)
        
        # Try various attribute paths
        test_paths = [
            ("Application", "Name"),
            ("Data", "Name"),
            ("Measurement", "Status"),
            ("Process", "Status")
        ]
        
        for path in test_paths:
            try:
                value = mx.get_attribute_string(path)
                print("Attribute {0}: {1}".format(path, value))
            except:
                print("Attribute {0}: Not available".format(path))

    except Exception as e:
        print("Failed to get attributes: {0}".format(str(e)))

def try_get_controls():
    """Try to list available controls"""
    try:
        print("\nTrying to list controls...")
        print("-" * 50)
        
        # Try to get some common controls by path
        test_controls = [
            ("Surface Plot",),
            ("Results Grid",),
            ("Process Control",),
            ("Analysis Control",),
            ("Measurement Control",)
        ]
        
        for control_path in test_controls:
            try:
                control = ui.get_control(control_path)
                if control:
                    print("Found control: {0}".format(control_path))
            except:
                continue

    except Exception as e:
        print("Failed to list controls: {0}".format(str(e)))

def check_measurement_status():
    """Check current measurement status"""
    try:
        print("\nChecking measurement status...")
        print("-" * 50)
        
        # Try to get current status information
        app_open = mx.is_application_open()
        print("Application is open: {0}".format(app_open))
        
        if app_open:
            app_path = mx.get_application_path()
            print("Current application: {0}".format(app_path))
            
            # Try to get Z axis position as an indicator
            try:
                z_pos = motion.get_z_pos(units.Units.MicroMeters)
                print("Current Z position: {0} um".format(z_pos))
            except:
                print("Z position not available")

    except Exception as e:
        print("Failed to check status: {0}".format(str(e)))

def main():
    print("Starting Zygo Measurement Test...")
    print("Time: {0}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("-" * 50)
    
    try:
        # Connect to Zygo
        uid = connectionmanager.connect()
        print("Connected to Zygo. UID: {0}".format(uid))
        
        # # Check basic status
        # check_measurement_status()
        #
        # # Try different ways to get data
        # try_get_custom_results()
        # try_get_attributes()
        # try_get_controls()

        print('\nAttempting to analyze data...')
        mx.analyze()
    except Exception as e:
        print("Test error: {0}".format(str(e)))
    
    finally:
        try:
            connectionmanager.terminate()
            print("\nDisconnected from Zygo")
        except:
            pass
            
        print("\nTest completed!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zygo Acquire/Measure Test Program (Python 3.4.3)
Testing AcquisitionTask functionality
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

def test_acquire():
    """Test acquire function with proper task handling"""
    print("\nTesting acquire()...")
    print("-" * 50)
    
    try:
        print("Starting acquire...")
        # Get acquisition task
        acq_task = instrument.acquire(wait=False)  # Set wait=False for async operation
        print("Task ID: {0}".format(acq_task._task_id))
        
        print("Checking acquisition status...")
        if hasattr(acq_task, 'acquire_task'):
            # Wait for frame grab
            print("Waiting for frame grab...")
            acq_task.frame_grab_task.wait()
            
            # Wait for acquisition
            print("Waiting for acquisition...")
            acq_task.acquire_task.wait()
            
            print("Acquisition completed")
            return True
        else:
            print("Acquisition task format unknown, detailed task info:")
            print("Task attributes:", dir(acq_task))
            return False
            
    except Exception as e:
        print("Acquire failed: {0}".format(str(e)))
        return False

def test_measure():
    """Test measure function with proper task handling"""
    print("\nTesting measure()...")
    print("-" * 50)
    
    try:
        print("Starting measure...")
        # Get measurement task
        meas_task = instrument.measure(wait=False)  # Set wait=False for async operation
        print("Task ID: {0}".format(meas_task._task_id))
        
        print("Checking measurement status...")
        if hasattr(meas_task, 'measure_task'):
            # Wait for measurement
            print("Waiting for measurement...")
            meas_task.measure_task.wait()
            
            print("Measurement completed")
            return True
        else:
            print("Measurement task format unknown, detailed task info:")
            print("Task attributes:", dir(meas_task))
            return False
            
    except Exception as e:
        print("Measure failed: {0}".format(str(e)))
        return False

def check_auto_settings():
    """Test auto settings functions"""
    try:
        print("\nTesting auto settings...")
        print("-" * 50)
        
        try:
            print("Testing auto light level...")
            instrument.auto_light_level()
            print("Auto light level completed")
        except Exception as e:
            print("Auto light level failed: {0}".format(str(e)))
            
        try:
            print("\nTesting auto focus...")
            instrument.auto_focus()
            print("Auto focus completed")
        except Exception as e:
            print("Auto focus failed: {0}".format(str(e)))
            
    except Exception as e:
        print("Auto settings test failed: {0}".format(str(e)))

def main():
    print("Starting Zygo Acquisition Test...")
    print("Time: {0}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("-" * 50)
    
    try:
        # Connect to Zygo
        uid = connectionmanager.connect()
        print("Connected to Zygo. UID: {0}".format(uid))
        
        # Check auto settings first
        # check_auto_settings()
        
        # Test acquire
        acquire_success = test_acquire()
        print("Acquire test success:", acquire_success)
        

        # Wait a bit between tests
        time.sleep(2)

        # Test measure
        measure_success = test_measure()
        print("Measure test success:", measure_success)
        
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

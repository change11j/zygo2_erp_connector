from __future__ import print_function
import os
import json
import time
from datetime import datetime
from zygo import mx
from zygo.slices import (
    LinearSliceType,
    RadialSliceType,
    CircularSliceType,
    get_all_linear_slices,
    get_all_radial_slices,
    get_all_circular_slices
)
from zygo.units import Units
from zygo import ui
from zygo import connectionmanager


def connect_to_mx():
    """Connect to Mx"""
    try:
        print("Attempting to connect to Mx...")
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Successfully connected to Mx. UID: {0}".format(uid))
        return True
    except Exception as e:
        print("Failed to connect to Mx: {0}".format(str(e)))
        return False


def save_data_to_file(control, data_type="plot", metadata=None):
    """Save control data to file with optional metadata"""
    try:
        # Create data directory if not exists
        save_dir = os.path.join(os.getcwd(), 'slice_data')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dat_filename = os.path.join(save_dir, '{0}_data_{1}.dat'.format(data_type, timestamp))

        # Save data using control's save_data method
        control.save_data(dat_filename)
        print("Data saved to: {0}".format(dat_filename))

        # Save metadata if provided
        if metadata:
            json_filename = os.path.join(save_dir, '{0}_metadata_{1}.json'.format(
                data_type, timestamp))
            with open(json_filename, 'w') as f:
                json.dump(metadata, f, indent=2)
            print("Metadata saved to: {0}".format(json_filename))

        return dat_filename
    except Exception as e:
        print("Error saving data to file: {0}".format(str(e)))
        return None


def find_slice_control():
    """Find a control that supports slice operations"""
    try:
        print("\nSearching for controls that support slice operations...")
        tabs = ui.get_tabs()

        for tab in tabs:
            try:
                for group in tab.groups:
                    try:
                        for container in group.containers:
                            try:
                                for control in container.controls:
                                    # Try to get linear slices as a test
                                    try:
                                        slices = get_all_linear_slices(control)
                                        if slices:
                                            print("Found control with slice support!")
                                            return control
                                    except Exception:
                                        continue
                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception:
                continue

        return None
    except Exception as e:
        print("Error finding slice control: {0}".format(str(e)))
        return None


def get_slice_metadata(slice_obj, slice_type):
    """Extract metadata from a slice object"""
    metadata = {
        'type': slice_type,
        'timestamp': datetime.now().isoformat()
    }

    try:
        if hasattr(slice_obj, 'get_length'):
            metadata['length_um'] = slice_obj.get_length(Units.MicroMeters)
        if hasattr(slice_obj, 'get_radius'):
            metadata['radius_um'] = slice_obj.get_radius(Units.MicroMeters)
        if hasattr(slice_obj, 'get_angle'):
            metadata['angle_deg'] = slice_obj.get_angle(Units.Degrees)
        if hasattr(slice_obj, 'get_midpoint'):
            midpoint = slice_obj.get_midpoint(Units.MicroMeters)
            metadata['midpoint'] = {'x': midpoint.x, 'y': midpoint.y}
        if hasattr(slice_obj, 'get_endpoints'):
            start, end = slice_obj.get_endpoints(Units.MicroMeters)
            metadata['endpoints'] = {
                'start': {'x': start.x, 'y': start.y},
                'end': {'x': end.x, 'y': end.y}
            }
    except Exception as e:
        print("Warning: Could not get some slice metadata: {0}".format(str(e)))

    return metadata


def get_slice_data(control):
    """Get and save all available slice data with metadata"""
    if control is None:
        print("No control provided.")
        return

    print("\nGetting slice data...")

    # Save surface data first
    save_data_to_file(control, "surface")

    # Process different types of slices
    slice_types = {
        'linear': get_all_linear_slices,
        'radial': get_all_radial_slices,
        'circular': get_all_circular_slices
    }

    all_metadata = {}

    for slice_name, slice_getter in slice_types.items():
        try:
            slices = slice_getter(control)
            if slices:
                print("\nFound {0} {1} slices".format(len(slices), slice_name))
                slice_metadata = {}

                for label, slice_obj in slices.items():
                    print("Processing {0} slice: {1}".format(slice_name, label))
                    metadata = get_slice_metadata(slice_obj, slice_name)
                    slice_metadata[label] = metadata

                    # Print key measurements
                    if 'length_um' in metadata:
                        print("  Length: {0:.6f} µm".format(metadata['length_um']))
                    if 'radius_um' in metadata:
                        print("  Radius: {0:.6f} µm".format(metadata['radius_um']))
                    if 'angle_deg' in metadata:
                        print("  Angle: {0:.6f} degrees".format(metadata['angle_deg']))

                # Save data and metadata
                if slice_metadata:
                    all_metadata[slice_name] = slice_metadata
                    save_data_to_file(control, slice_name, slice_metadata)

        except Exception as e:
            print("Note: {0} slices not available: {1}".format(slice_name, str(e)))

    return all_metadata


def main():
    try:
        # Connect to Mx
        if not connect_to_mx():
            raise Exception("Failed to connect to Mx")

        # Check if application is open
        if not mx.is_application_open():
            raise Exception("Zygo application is not open")

        print("Looking for a control that supports slice operations...")
        slice_control = find_slice_control()

        if slice_control:
            print("\nFound slice control! Getting data...")
            metadata = get_slice_data(slice_control)

            if metadata:
                print("\nSuccessfully collected slice data!")
            else:
                print("\nNo slice data was collected. Check if slices are created in Mx.")
        else:
            print("\nNo control supporting slice operations was found.")
            print("You may need to create slices in the Mx interface first.")

    except Exception as e:
        print("Program error: {0}".format(str(e)))
    finally:
        try:
            connectionmanager.terminate()
            print("Connection terminated")
        except:
            pass


if __name__ == "__main__":
    main()
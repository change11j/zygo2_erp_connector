# -*- coding: utf-8 -*-

# THE SAMPLE CODE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ZYGO OR ANY AFFILIATED 
# COMPANY, ITS OR THEIR OFFICERS, EMPLOYEES OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) SUSTAINED BY YOU OR
# A  THIRD PARTY, HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT ARISING IN ANY WAY OUT OF THE USE OF THIS
# SAMPLE CODE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Sample script for intermediate mx module functionality,
e.g. application and data loading, retrieving results and attributes,
modifying control values, and saving application.
"""

import os.path
import time

from zygo.units import Units
from zygo import mx
import zygo.systemcommands as sc


# File below expected to exist in the current open directory
# for Application files
app_filename = 'Micro.appx'

# File below expected to exist in Samples subfolder of the
# current open directory for Data files.
data_filename = 'Plot3D.datx'

# Get and print application status
print('Is application open? {}'.format(mx.is_application_open()))

# Open application
open_app_dir = sc.get_open_dir(sc.FileTypes.Application)
app_file_path = os.path.join(open_app_dir, app_filename)
print('Opening application: "{}" ...'.format(app_file_path))
mx.open_application(app_file_path)

# Get and print application status
print('Is application open? {}'.format(mx.is_application_open()))

# Load a sample data file
open_data_dir = sc.get_open_dir(sc.FileTypes.Data)
data_file_path = os.path.join(open_data_dir, 'Samples', data_filename)
print('Loading data: "{}" ...'.format(data_file_path))
mx.load_data(data_file_path)

# Retrieve results and attributes

## Paths to the results and attributes of interest
pv_path = ("Analysis", "Surface", "Surface Parameters", "Height Parameters", "PV")
sa_path = ("Analysis", "Surface", "Areal ISO Parameters", "Height Parameters", "Sa") 
lat_res_path = ("Instrument", "Measurement Setup", "Acquisition", "Lateral Resolution")
data_filename_path = ("System", "Load", "Data Filename")

## Create aliases for Units to save typing
um_unit = Units.MicroMeters
nm_unit = Units.NanoMeters

## Retrieve the result and attribute data from Mx
pv = mx.get_result_number(pv_path, um_unit)
sa = mx.get_result_number(sa_path, nm_unit)
lat_res = mx.get_attribute_number(lat_res_path, um_unit)
data_file = mx.get_attribute_string(data_filename_path)

## Display the information
print("PV = {} {}".format(pv, um_unit.name))
print("Sa = {} {}".format(sa, nm_unit.name))
print("Lateral Resolution = {} {}".format(lat_res, um_unit.name))
print("Data Filename = {}".format(data_file))

# Change the Measurement Type control value
meas_type_path = ("Instrument", "Measurement Setup", "Acquisition", "Measurement Type")
print('Current Measurement Type: {}'.format(mx.get_control_string(meas_type_path)))
meas_type = 'Intensity SnapShot'
print('Changing Measurement Type to: {}'.format(meas_type))
mx.set_control_string(meas_type_path, meas_type)

# Save the application
save_app_dir = sc.get_save_dir(sc.FileTypes.Application)
save_app_filename = '{}_test.appx'.format(os.path.splitext(app_filename)[0])
save_app_path = os.path.join(save_app_dir, save_app_filename)
print('Saving application as: "{}" ...'.format(save_app_path))
mx.save_application_as(save_app_path)
print('Sleeping ...')
time.sleep(5)

# Close application, get and print application status
print('Closing application ...')
mx.close_application()
print('Is application open? {}'.format(mx.is_application_open()))
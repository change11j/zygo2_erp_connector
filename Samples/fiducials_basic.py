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
Sample script for basic fiducials module functionality.
"""

import os.path
import time

from zygo import mx, systemcommands, ui
from units import Units
from zygo.fiducials import *


# Files below expected to exist in current open, save directories
# for Application, Fiducial, Data files
app_file = 'Micro.appx'
source_fiducial_file = 'test1.fidx'
target_fiducial_file = 'test2.fidx'
source_data_file = 'Distortion.datx'

# Open application if not open
orig_app_open = mx.is_application_open()
if not orig_app_open:
    print('Opening application ...')
    app_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Application)
    mx.open_application(os.path.join(app_dir, app_file))

# Load data
print('Loading data ...')
data_open_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Application)
mx.load_data(os.path.join(data_open_dir, source_data_file))

# Open Fiducials editor, load fiducials
fiducial_editor = ui.show_fiducial_editor()
fiducials = Fiducials()
fiducial_open_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Fiducial)
fiducials.load(os.path.join(fiducial_open_dir, source_fiducial_file))

print('Sleeping ...')
time.sleep(3)

# Move, resize, rotate fiducials
for (set, fid) in fiducials:
    print('center = ({0.x:.2f}, {0.y:.2f})'.format(fid.center), end=', ')
    print('height = {0.height:.2f}, width = {0.width:.2f}'.format(fid))
    fid.move_relative(30.0, -10.0)
    fid.resize(fid.height + 30.0, fid.width + 30.0)
    print('center = ({0.x:.2f}, {0.y:.2f})'.format(fid.center), end=', ')
    print('height = {0.height:.2f}, width = {0.width:.2f}'.format(fid))
    fid.rotate(45, Units.Degrees)

# Remove a fiducial, save fiducials
print('Removing fiducial ...')
fiducial = fiducials.get_fiducial_closest_to(200, 200, 0)
fiducials.delete(fiducial[1])
fiducial_save_dir = systemcommands.get_save_dir(systemcommands.FileTypes.Fiducial)
fiducials.save(os.path.join(fiducial_save_dir, target_fiducial_file))

print('Sleeping ...')
time.sleep(3)

fiducial_editor.close()

# Close app if not open originally
if not orig_app_open:
    print('Closing application ...')
    mx.close_application()
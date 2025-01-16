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
Sample script for basic masks module functionality.
"""

import os.path
import time

from zygo import mx, systemcommands, ui
from zygo.masks import *
from zygo.units import Units


# Files below expected to exist in current open, save directories
# for Application, Mask, Data files.
# See systemcommands_basic.py for more details.
app_file = 'Micro.appx'
source_mask_file = 'test1.masx'
target_mask_file = 'test2.masx'
source_data_file = 'Distortion.datx'

# Open application if not open
orig_app_open = mx.is_application_open()
if not orig_app_open:
    print('Opening application ...')
    app_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Application)
    mx.open_application(os.path.join(app_dir, app_file))

print('Loading data ...')
data_open_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Data)
mx.load_data(os.path.join(data_open_dir, source_data_file))

# Open Masks editor, load masks
mask_window = ui.show_mask_editor()
masks = Masks()
mask_open_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Mask)
masks.load(os.path.join(mask_open_dir, source_mask_file))

# Move, resize, rotate masks
for m in masks:
    print('center = ({0.x:.2f}, {0.y:.2f})'.format(m.center), end=', ')
    print('height = {0.height:.2f}, width = {0.width:.2f}'.format(m))
    time.sleep(3)
    print("Moving mask ...")
    m.move_relative(30.0, -10.0)
    print("Resizing mask ...")
    m.resize(m.height + 30.0, m.width + 30.0)
    print('center = ({0.x:.2f}, {0.y:.2f})'.format(m.center), end=', ')
    print('height = {0.height:.2f}, width = {0.width:.2f}'.format(m))
    m.rotate(45, Units.Degrees)
    
print('Sleeping ...')
time.sleep(3)

# Remove a mask, save masks
print('Removing mask ...')
mask = masks.get_mask_closest_to(200, 200, 'Surface')
masks.delete(mask)
mask_save_dir = systemcommands.get_save_dir(systemcommands.FileTypes.Mask)
masks.save(os.path.join(mask_save_dir, target_mask_file))

# Analyze
mx.analyze()

print('Sleeping ...')
time.sleep(3)

mask_window.close()

# Close app if not open originally
if not orig_app_open:
    print('Closing application ...')
    mx.close_application()
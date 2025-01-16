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
Sample script for basic motion module functionality.
"""

import os.path

from zygo.units import Units
from zygo import instrument, mx, motion
import zygo.systemcommands as sc


# File below expected to exist in current open directory for Application files.
# See mx_basic.py for examples.
app_file = 'Micro.appx'

# Open application if not open
orig_app_open = mx.is_application_open()
if not orig_app_open:
    print('Opening application ...')
    app_dir = sc.get_open_dir(sc.FileTypes.Application)
    mx.open_application(os.path.join(app_dir, app_file))

# Create (x, y) coordinate pairs
targets = ((0.0, 0.0), (0.5, 0.0),
           (0.0, 0.5), (0.5, 0.5))

# Loop through each target coordinate pair
# CAUTION: This will move the XY stage to the absolute positions
# specified above, and will trigger an auto-focus at each position.
for target in targets:
    # Get current positions of x and y axes
    xy_unit = Units.MilliMeters
    x_pos = motion.get_x_pos(xy_unit)
    y_pos = motion.get_y_pos(xy_unit)
    print('XY position:')
    print('\tBefore = ({0} {2}, {1} {2})'.format(
        x_pos, y_pos, xy_unit.name))

    # Move stage to next position
    motion.move_xy(target[0], target[1], xy_unit)

    # Get new current positions of x and y axes.
    x_pos = motion.get_x_pos(xy_unit)
    y_pos = motion.get_y_pos(xy_unit)
    print('\tAfter = ({0} {2}, {1} {2})'.format(
        x_pos, y_pos, xy_unit.name))

    # Optimize focus and get before and after positions of the z-axis,
    # rounded to 3 decimal places.
    z_unit = Units.MicroMeters
    print('Z position:')
    print('\tBefore = {:.3f} {}'.format(
        motion.get_z_pos(z_unit), z_unit.name))
    instrument.auto_focus()
    print('\tAfter = {:.3f} {}'.format(
        motion.get_z_pos(z_unit), z_unit.name))

print("Done.")
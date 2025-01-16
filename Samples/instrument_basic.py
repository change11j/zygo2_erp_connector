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
Sample script for basic instrument module functionality.
"""

import time
import os.path

from zygo import mx, instrument, systemcommands


# File below expected to exist in current open directory for Application files
app_file = 'Micro.appx'

# Open application if not open
orig_app_open = mx.is_application_open()
if not orig_app_open:
    print('Opening application ...')
    app_dir = systemcommands.get_open_dir(systemcommands.FileTypes.Application)
    mx.open_application(os.path.join(app_dir, app_file))

# Auto focus
print('Auto focus ...')
instrument.auto_focus()
print('Sleeping ...')
time.sleep(3)

# Auto light level
print('Auto light level ...')
instrument.auto_light_level()
print('Sleeping ...')
time.sleep(3)

# Measure
print('Measuring ...')
instrument.measure()
print('Sleeping ...')
time.sleep(3)

# Acquire, Analyze
print('Acquiring ...')
instrument.acquire()
print('Sleeping ...')
time.sleep(3)
print('Analyzing ...')
mx.analyze()
print('Sleeping ...')
time.sleep(3)

# Close app if not open originally
if not orig_app_open:
    print('Closing application ...')
    mx.close_application()
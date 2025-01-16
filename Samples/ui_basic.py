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
Sample script for basic ui module functionality.
"""

import time
import os.path

from zygo import ui, mx
import zygo.systemcommands as sc


# File below expected to exist in current open directory
# for Application files
app_file = 'Micro.appx'

# Open application if not open
orig_app_open = mx.is_application_open()
if not orig_app_open:
    print('Opening application ...')
    app_dir = sc.get_open_dir(sc.FileTypes.Application)
    mx.open_application(os.path.join(app_dir, app_file))
    print('Sleeping ...')
    time.sleep(3)

# Iterate through all available UI Tabs
tabs = ui.get_tabs()
for tab in tabs:
    # Switch current Tab
    print('Changing tabs to "{0}"...'.format(tab.name))
    tab.show()
    # Display groups contained in current Tab
    print('Tab has groups: {0}'.format(tuple(i.name for i in tab.groups)))
    print('Sleeping ...')
    time.sleep(3)

# Close app if not open originally
if not orig_app_open:
    print('Closing application ...')
    mx.close_application()

print('Done.')
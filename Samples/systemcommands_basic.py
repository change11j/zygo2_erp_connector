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
Sample script for basic systemcommands module functionality.
"""

import os.path
import time

import zygo.systemcommands as sc

# Execute some system commands functions
#print('Binaries directory: {0}'.format(sc.get_bin_dir()))
print('Open directory for application files: {0}'.format(sc.get_open_dir(sc.FileTypes.Application)))
print('Save directory for application files: {0}'.format(sc.get_save_dir(sc.FileTypes.Application)))
print('Open directory for data files: {0}'.format(sc.get_open_dir(sc.FileTypes.Data)))
print('Save directory for data files: {0}'.format(sc.get_save_dir(sc.FileTypes.Data)))
print('Host RAM size: {0}'.format(sc.get_ram_size()))
print('Host OS name: {0}'.format(sc.get_os_name()))
print('Host computer name: {0}'.format(sc.get_computer_name()))
print('Host working directory: {0}'.format(sc.get_working_dir()))

# Store old application directories
open_app_dir = sc.get_open_dir(sc.FileTypes.Application)
save_app_dir = sc.get_save_dir(sc.FileTypes.Application)

# Set application directories to a sub-directory to current.  Sub-directory
# must exist. Note how systemcommands methods can take string parameters as file type.
sc.set_open_dir('Application', os.path.join(open_app_dir, 'NewSubDir'))
sc.set_save_dir('Application', os.path.join(save_app_dir, 'NewSubDir'))
print('Open directory for application files: {0}'.format(sc.get_open_dir('Application')))
print('Save directory for application files: {0}'.format(sc.get_save_dir('Application')))

# Set application directories back to original
sc.set_open_dir('Application', open_app_dir)
sc.set_save_dir('Application', save_app_dir)

print('Sleeping ...')
time.sleep(5)
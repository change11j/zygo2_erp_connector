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
Sample script for basic mx module functionality,
e.g. application loading, unloading, and status.
"""
 
import os.path
import time

from zygo import mx
import zygo.systemcommands as sc
 
 
# Get and print application status
print('Is application open? {0}'.format(mx.is_application_open()))
print('Sleeping ...')
time.sleep(5)
 
# Open application
app_file = r'C:\Users\zygo\Documents\Mx\Apps\Micro.appx'
print('Opening application: "{0}" ...'.format(app_file))
mx.open_application(app_file)
print('Sleeping ...')
time.sleep(5)
 
# Get and print application status
if mx.is_application_open():
    print('Application opened: "{0}"'.format(mx.get_application_path()))
else:
    print('Application is not open.')
print('Sleeping ...')
time.sleep(5)
 
# Close application, get and print application status
print('Closing application ...')
mx.close_application()
print('Is application open? {0}'.format(mx.is_application_open()))
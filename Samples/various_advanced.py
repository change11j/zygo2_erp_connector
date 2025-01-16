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
Sample script shows more advanced features by performing the following:

1. Take measurement
2. Get selected results
3. Write to file
4. Call executable that processes file and outputs new file
5. Read new results
6. Display new results in message box and prompt user for new measurement

Assumptions:
1. Application is loaded and has results of "Sa", "Sq", "PV", and "RMS" in Process Stats
2. Executable file can be called that takes in two command line arguments
    A. Command line arguments represent:
        i. Filename that this script will generate with Mx results separated by newlines
        ii. Filename that the executable file will generate in the same format
3. Write permissions exist for the given filenames
"""

import subprocess

from zygo import mx, instrument, ui
import zygo.systemcommands as sc

script_dir = sc.get_save_dir(sc.FileTypes.Script)

# Set below tor executable to run, file for Mx results, and file for executable
# results. A sample exec_file is provided in the support_files folder supplied
# with the sample scripts.
exec_file = script_dir + r'\Data\ProcessResults.exe'
mx_results_file = script_dir + r'\Data\testdata.txt'
exec_results_file = script_dir + r'\Data\testdata2.txt'

tabMeasure = ui.get_tab('Measure')
tabAnalyze = ui.get_tab('Analyze')

inputs = ((('Analysis', 'Surface', 'Areal ISO Parameters', 'Height Parameters', 'Sa'), 'MicroMeters'),
    (('Analysis', 'Surface', 'Areal ISO Parameters', 'Height Parameters', 'Sq'), 'MicroMeters'),
    (('Analysis', 'Surface', 'Surface Parameters', 'Height Parameters', 'PV'), 'MicroMeters'),
    (('Analysis', 'Surface', 'Surface Parameters', 'Height Parameters', 'RMS'), 'MicroMeters'))

# Iterate until user done
done = False
while not done:
    # Show Measure tab
    tabMeasure.show()

    # Measure
    print('Measuring ...')
    instrument.measure()

    # Show Analyze tab
    tabAnalyze.show()

    # Get results and output to file
    print('Retrieving results ...')
    with open(mx_results_file, 'w') as f:
        f.write('\n'.join(str(mx.get_result_number(v[0], v[1])) for v in inputs))

    # Call executable to process results
    print('Processing results ...')
    subprocess.call([exec_file, mx_results_file, exec_results_file])

    # Read new results from file and display in dialog
    with open(exec_results_file, 'r') as f:
        values = f.read().strip().split('\n')
    headers = (i[0][-1] for i in inputs)
    units = (' {0}'.format(i[1]) for i in inputs)
    msg = '\n'.join(':  '.join(j) for j in zip(headers, tuple(' '.join(i) for i in zip(values, units))))
    msg += '\n\nMeasure again?'
    print('Done.\n')
    done = not ui.show_dialog(msg, ui.DialogMode.confirm_yes_no)

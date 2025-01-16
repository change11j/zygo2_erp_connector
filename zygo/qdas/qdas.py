# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx Q-DAS functionality.
"""
# Standard lib imports
import subprocess
from threading import Thread, Lock
import os
from pprint import pprint
import datetime
import shutil
import xml.etree.ElementTree as ET
from enum import IntEnum as _IntEnum
from itertools import chain, product

# Mx scripting imports
from zygo.core import ZygoError
from zygo import ui as _ui
from zygo import systemcommands as _sc
from zygo import mx as _mx
from zygo.connectionmanager import send_request as _send_request
from zygo import utils as _utils
from zygo.qdas import config_manager as _config_manager


QDAS_SETTINGS = _config_manager.QdasConfiguration()


# =========================================================================
# ---Constants
# =========================================================================
# The required Talyseries SPC csv file header string
_SPC_HEADER = "ZygoQDAS;3.0"
_STATUS_FILE = os.path.join(os.path.dirname(QDAS_SETTINGS.spc_exe_path),
                            'TalyseriesSPCStatus.txt')
_MESSAGE_FONT = _ui.Font('Tahoma', 18, _ui.Font.FontStyle.regular)
_BUTTON_FONT = _ui.Font('Tahoma', 18, _ui.Font.FontStyle.regular)


# =========================================================================
# ---Enumerations
# =========================================================================
_STUDY_TYPES = {
        0: ['Standard Production', 'standard'],
        1: ['Type 1 Study', 'type_1'],
        2: ['Type 2 Study', 'type_2'],
        3: ['Type 3 Study', 'type_3']}
QdasStudyType = _IntEnum(
    value='QdasStudyType',
    names=chain.from_iterable(
        product(v, [k]) for k, v in _STUDY_TYPES.items()))


class OperationPromptType(_IntEnum):
    none = 0
    info = 1
    serial = 2
    unique_serial = 3


# =========================================================================
# ---Classes
# =========================================================================
class QdasCharacteristic(object):
    """Contains relevant Q-DAS characteristics data for a single entry
    in the SPC test plan.

    Parameters
    ----------
    uid : int
        The unique, sequential ID for the characteristic.
    name : str
        The unique name for the characteristic.
    groupname : str
        The Feature Name of the characteristic.
    unit : str
        The unit display string of the characteristic.
    nominal : float
        The nominal limit/tolerance value.
    ltol : float
        The lower limit/tolerance value.
    utol : float
        The upper limit/tolerance value.
    """

    def __init__(self, uid, name, groupname, unit, nominal, ltol, utol):
        """Initializes a QdasCharacteristic object.

        Parameters
        ----------
        uid : int
            The unique, sequential ID for the characteristic.
        name : str
            The unique name for the characteristic.
        groupname : str
            The Feature Name of the characteristic.
        unit : str
            The unit display string of the characteristic.
        nominal : float
            The nominal limit/tolerance value.
        ltol : float
            The lower limit/tolerance value.
        utol : float
            The upper limit/tolerance value.
        """
        self._uid = uid
        self._name = name
        self._groupname = groupname
        self._unit = unit
        self._nominal = nominal
        self._ltol = ltol
        self._utol = utol

    @property
    def uid(self):
        """int: The unique, sequential ID for the characteristic."""
        return self._uid

    @property
    def name(self):
        """str: The unique name for the characteristic."""
        return _utils._get_str_val(self._name)

    @property
    def groupname(self):
        """str: The Feature Name of the characteristic.

        Note
        ----
        The .testplan XML element is GroupName, which corresponds to the
        part's Feature Name.
        """
        return _utils._get_str_val(self._groupname)

    @property
    def unit(self):
        """str: The unit display string of the characteristic."""
        return _utils._get_str_val(self._unit)

    @property
    def nominal(self):
        """str: The nominal limit/tolerance value."""
        return _utils._get_str_val(self._nominal)

    @property
    def ltol(self):
        """str: The lower limit/tolerance value."""
        return _utils._get_str_val(self._ltol)

    @property
    def utol(self):
        """str: The upper limit/tolerance value."""
        return _utils._get_str_val(self._utol)


class ResultsData(object):
    """Process stats results data.

    Parameters
    ----------
    part_description : str
        The Part Description/free text field.
    header_row : list of str
        The csv header row.
    feature_names : list of str
        An ordered list of feature names.
    result_rows : list
        List of results rows, grouped by characteristic.
    """

    def __init__(self, part_description=None, header_row=None,
                 feature_names=None, result_rows=None):
        """Initializes a ResultsData object.

        Parameters
        ----------
        part_description : str
            The Part Description/free text field.
        header_row : list of str
            The csv header row.
        feature_names : list of str
            An ordered list of feature names.
        result_rows : list
            List of results rows, grouped by characteristic.
        """
        self._part_description = part_description
        self._header_row = header_row
        self._feature_names = feature_names
        self._result_rows = result_rows

    @property
    def part_description(self):
        """str: The Part Description/free text field."""
        return _utils._get_str_val(self._part_description)

    @part_description.setter
    def part_description(self, value):
        self._part_description = value

    @property
    def header_row(self):
        """list of str: The csv header row."""
        return self._header_row

    @header_row.setter
    def header_row(self, value):
        self._header_row = value

    @property
    def feature_names(self):
        """list of str: An ordered list of feature names."""
        return self._feature_names

    @feature_names.setter
    def feature_names(self, value):
        self._feature_names = value

    @property
    def result_rows(self):
        """list: List of results rows, grouped by characteristic."""
        return self._result_rows

    @result_rows.setter
    def result_rows(self, value):
        self._result_rows = value

    @property
    def rows_count(self):
        """int: The number of features/results rows."""
        return (len(self._result_rows)
                if self._result_rows is not None
                else None)

    @property
    def characteristics_count(self):
        """int: The number of characteristics/results columns per row."""
        if all([self._result_rows is not None,
                len(self._result_rows) > 0,
                self._result_rows[0] is not None]):
            return len(self._result_rows[0])
        else:
            return None


# =========================================================================
# ---Utility Methods
# =========================================================================
def _debug_print(str):
    if QDAS_SETTINGS.debug:
        print(str)


def _create_file_backup(file_path, new_path=None, keep_orig=True):
    """Creates a copy of the specified file, optionally deleting the original.

    Parameters
    ----------
    file_path : str
        The path to the file to copy.
    new_path : str
        The path of the new file copy; if None, the new path will be created
        by inserting the current timestamp into the original path.
    keep_orig : bool
        True to keep the original file; False to delete the original file.
    """
    if not QDAS_SETTINGS.backup_files:
        return

    if not new_path:
        root, ext = os.path.splitext(file_path)
        timestamp = '{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now())

        new_path = '{}_{}{}'.format(root, timestamp, ext)
    _debug_print(
        "Creating backup file '{}'...".format(new_path))
    if not keep_orig:
        os.replace(file_path, new_path)
    else:
        shutil.copyfile(file_path, new_path)

    _debug_print("Done!")


# =========================================================================
# ---Internal Implementation Methods
# =========================================================================
def _export_qdas_parameters(control, filename):
    """Export a Q-DAS parameters file from the specified process stats control.

    Parameters
    ----------
    control : tuple of str
        The path to the process stats control.
    filename : str
        The path of the .csv file to create.
    """
    params = {'controlId': control._id, 'filePath': filename}
    _send_request(_mx._SERVICE, 'ExportQdasConfigurationParameters', params)


def _export_qdas_results(control, filename, append=False, log_all=True):
    """Export a Q-DAS results file from the specified process stats control.

    Parameters
    ----------
    control : tuple of str
        The path to the process stats control.
    filename : str
        The path of the .csv file to create.
    append : bool
        True to append data to the file; False to overwrite the file. If the
        specified file does not exist, this parameter has no effect and a new
        file will be created.
    logAll : bool
        True to output all results; False to output only the last (most-recent)
        row.
    """
    params = {'controlId': control._id,
              'filePath': filename,
              'append': append,
              'logAll': log_all}
    _send_request(_mx._SERVICE, 'ExportQdasResults', params)


def _add_kfields(file_path, auto_kfields):
    """Append additional k-field information to the process statistics file.

    Parameters
    ----------
    file_path : str
        The path of the process statistics file to update.
    auto_kfields : collections.OrderedDict
        A dictionary of k-field keys to their corresponding string values.
    """
    if auto_kfields is None or len(auto_kfields) < 1:
        return
    add_header_data = ';{}'.format(';'.join(auto_kfields.keys()))
    add_row_data = ';{}'.format(';'.join(auto_kfields.values()))

    try:
        with open(file_path, 'r', encoding='utf-16') as f:
            # The Talyseries SPC header comes first
            line = f.readline().strip()
            if line != _SPC_HEADER:
                raise ZygoError("Invalid file header!")
            # The free text field/part description is next
            part_desc = f.readline().strip()
            # The third line is the csv header row
            header = f.readline().strip()
            # The remaining rows are data rows
            data_rows = []
            for line in f:
                data_rows.append(line.strip())
    except Exception as ex:
        raise ZygoError("Unable to read Q-DAS parameters file. '{}'"
                        .format(ex))

    with open(file_path, 'w', encoding='utf-16') as f:
        f.write(_SPC_HEADER + '\n')
        f.write(part_desc + '\n')
        f.write('{}{}\n'.format(header, add_header_data))
        for row in data_rows:
            f.write('{}{}\n'.format(row, add_row_data))


def _extract_testplan_parameters(testplan_path):
    """Extracts characteristics data from the testplan file.

    Parameters
    ----------
    testplan_path : str
        The path of the Q-DAS TestPlan file to create.

    Returns
    -------
    list of `QdasCharacteristic`
        List of `QdasCharacteristic` objects for the specified testplan.
    """
    ns = {"QDASTemplate": "http://tempuri.org/DataSetQDAS.xsd"}  # namespace
    characteristics_data = []

    # The Talyseries SPC .TestPlan file is XML, so we're going to crawl in and
    # grab the values we need
    tree = ET.ElementTree(file=testplan_path)
    elems = None
    if tree is not None:
        elems = tree.findall("QDASTemplate:CharacteristicsData", ns)
    if elems is not None:
        for elem in elems:
            try:
                e = elem.find("QDASTemplate:ID", ns)
                # We want the uid to be an int for sorting purposes
                uid = (None if e is None else
                       _utils._try_parse_int(e.text).int_val)
                e = elem.find("QDASTemplate:Name", ns)
                name = None if e is None else e.text
                e = elem.find("QDASTemplate:GroupName", ns)
                groupname = None if e is None else e.text
                e = elem.find("QDASTemplate:Unit", ns)
                unit = (None if e is None else
                        (str() if e.text is None else e.text))
                e = elem.find("QDASTemplate:Nominal", ns)
                nominal = None if e is None else e.text
                e = elem.find("QDASTemplate:LTol", ns)
                ltol = None if e is None else e.text
                e = elem.find("QDASTemplate:UTol", ns)
                utol = None if e is None else e.text
                characteristics_data.append(
                    QdasCharacteristic(
                        uid, name, groupname, unit, nominal, ltol, utol))
            except Exception as ex:
                print(ex)
    # Sort the list by uid before we return it, moving None values to the end
    # The list will most likely already be sorted, but I can't guarantee that
    return sorted(characteristics_data, key=lambda x: (x.uid is None, x.uid))


def _extract_results(results_path):
    """Creates a `ResultsData` object from the specified results file.

    Parameters
    ----------
    results_path : str
        Path to the process statistics .csv results output file.

    Returns
    -------
    `ResultsData`
        A `ResultsData` object containing the process statistics results data.
    """
    with open(results_path, 'r', encoding='utf-16') as f:
        # The Talyseries SPC header comes first
        line = f.readline().strip()
        if line != _SPC_HEADER:
            raise ZygoError("Invalid file header!")
        # The free text field/part description is next
        part_desc = f.readline().strip()
        # The third line is the csv header row
        header = f.readline().strip()
        result_rows = []
        features = []
        # The remaining lines contain proc stats data, one row per feature
        for line in f:
            # Split the line by the delimiter
            parts = line.strip().split(';')
            # Each row must have, at least, timestamp, feature name, terminator
            if len(parts) < 3:
                continue
            # Extract the feature name value for this row
            features.append(parts[1])
            # Exclude timestamp, feature name, and terminator
            results_data = parts[2:-1]
            # Group the row into individual results data
            # [value, unit, nominal, ltol, utol]
            chunks = [results_data[i:i+5]
                      for i in range(0, len(results_data), 5)]
            result_rows.append(chunks)
        results_data = ResultsData(
            part_desc, header, features, result_rows)
        return results_data


def _create_rebuilt_rows(characteristics_data, results_data):
    """Matches the results data to the test plan characteristics.

    Parameters
    ----------
    characteristics_data : list of `QdasCharacteristic`
        List of `QdasCharacteristic` objects for the specified test plan.
    results_data : `ResultsData`
        A `ResultsData` object containing the process statistics results.

    Returns
    -------
    list of str
        A list of the rebuilt row strings.
    """
    res_out = []

    # i rows, j characteristics
    for i in range(results_data.rows_count):
        # each result row corresponds to a single feature
        feature = results_data.feature_names[i]
        # Start a new output row with an empty timestamp and the feature name
        new_row = ";{};".format(feature)
        for j in range(results_data.characteristics_count):
            # get the result row
            res = results_data.result_rows[i][j]
            # get corresponding characteristic from the list
            idx = (i * results_data.characteristics_count) + j
            cdata = characteristics_data[idx]
            # We only want the value and unit for each result
            # Tolerance values are added-in from the characteristics data below
            res_val, res_unit = res[0], res[1]

            # Sanity checks
            if res_unit != cdata.unit:
                raise ZygoError(
                    "Invalid unit '{}', expected '{}'."
                    .format(res_unit, cdata.unit))
            if feature != cdata.groupname:
                raise ZygoError(
                    "Invalid feaure name '{}', expected '{}'"
                    .format(feature, cdata.groupname))
            # Append the current result/characteristic to the row
            new_row += "{};{};{};{};{};".format(
                res_val, res_unit, cdata.nominal, cdata.ltol, cdata.utol)
        # Add the line terminator
        new_row += "@"
        res_out.append(new_row)

    return res_out


def _rebuild_results(characteristics_data, results_data, qdas_results_path):
    """Rebuild results from gathered data to be fed into Talyseries SPC.

    Parameters
    ----------
    characteristics_data : list of `QdasCharacteristic`
        List of `QdasCharacteristic` objects for the specified test plan.
    results_data : `ResultsData`
        A `ResultsData` object containing the process statistics data.
    qdas_results_file : str
        The path to the process statistics results file.
    """
    if characteristics_data is None or results_data is None:
        raise ZygoError("Unable to rebuild results. " +
                        "Invalid input data.")

    root, ext = os.path.splitext(qdas_results_path)
    if not ext:
        raise ZygoError("Unable to rebuild results. " +
                        "Invalid results file path.")

    _create_file_backup(qdas_results_path, keep_orig=False)

    new_results = _create_rebuilt_rows(characteristics_data, results_data)

    with open(qdas_results_path, 'w', encoding='utf-16') as f:
        f.write(_SPC_HEADER + '\n')
        f.write(results_data.part_description + '\n')
        f.write(results_data.header_row + '\n')
        for row in new_results:
            f.write(row + '\n')


def _get_mx_testplan_settings_json(settings_list):
    """Creates a custom representation of this object for serialization.

    Parameters
    ----------
    settings_list : list of MxTestPlanSettings
        List of `MxTestPlanSettings` objects.

    Returns
    -------
    dict
        A JSON serializable object from the settings list.
    """
    # Create a JSON serializable dictionary from the settings list
    d = {}
    for tps in settings_list:
        s = {k: v for k, v in tps._asdict().items() if k != 'Name'}
        d[tps.Name] = s

    return d


def _reset_talyseries_monitor_status():
    _sc._exec_command(_mx._SERVICE,
                      "ResetStatusMonitor",
                      None)


status_exception = False
status_lock = Lock()


def _wait_for_status():
    global status_exception
    try:
        status_exception = False
        _sc._exec_command(_mx._SERVICE,
                          "WaitForStatusMonitor",
                          None)
    except Exception:
        with status_lock:
            status_exception = True


def _monitor_talyseries_spc():
    procname = "talyseriesspc.exe"
    vsprocname = "talyseriesspc.vshost.exe"
    t = Thread(target=_wait_for_status)
    t.start()
    while True:
        try:
            if not (_utils.process_exists(procname) or
                    _utils.process_exists(vsprocname)):
                params = {"status": False,
                          "message": "Talyseries SPC process terminated."}
                _sc._exec_command(_mx._SERVICE,
                                  "SetStatusMonitorStatus",
                                  params)
                return None
        except Exception as ex:
            try:
                params = {"status": False,
                          "message":
                              "Unable to communicate with Talyseries SPC."}
                _sc._exec_command(_mx._SERVICE,
                                  "SetStatusMonitorStatus",
                                  params)
            except Exception:
                pass
            raise ZygoError("Unable to check process.", ex)
        if not t.is_alive():
            with status_lock:
                if status_exception:
                    return None
            try:
                stat = _sc._exec_command(_mx._SERVICE,
                                         "GetStatusMonitorStatus",
                                         None)["GetStatusMonitorStatusResult"]
                return stat
            except Exception:
                return None


def _do_study_complete(spc_testplan, testplan_info):
    """Checks if study is complete and prompts to restart if necessary."""
    if testplan_info.get('is_finished', False):
        if _ui.show_dialog("Restart completed testplan?",
                           _ui.DialogMode.confirm_yes_no,
                           title=testplan_info['study_type'].name,
                           message_font=_MESSAGE_FONT,
                           button_font=_BUTTON_FONT):
            stat = reset_qdas_study()
            if stat is None or not stat.get("Status", False):
                return None
            testplan_info = get_testplan_info(spc_testplan)
        else:
            return None
    return testplan_info


def _do_study_restart(spc_testplan, testplan_info):
    """Checks if study is in progress and prompts to continue or restart."""
    if not _ui.show_dialog("Continue the test plan already in progress?",
                           _ui.DialogMode.confirm_yes_no,
                           title=testplan_info['study_type'].name,
                           message_font=_MESSAGE_FONT,
                           button_font=_BUTTON_FONT):
        if _ui.show_dialog("Restart the test plan?",
                           _ui.DialogMode.confirm_yes_no,
                           title=testplan_info['study_type'].name,
                           message_font=_MESSAGE_FONT,
                           button_font=_BUTTON_FONT):
            stat = reset_qdas_study()
            if stat is None or not stat.get("Status", False):
                return None
            testplan_info = get_testplan_info(spc_testplan)
        else:
            return None
    return testplan_info


# =========================================================================
# ---Public Methods
# =========================================================================
def create_qdas_testplan(testplan_path=None,
                         qdas_params_path=None,
                         auto_kfields=None):
    """Calls Mx to export Q-DAS parameters, then feeds the parameters into
    Talyseries SPC where the user will create the testplan.

    Parameters
    ----------
    testplan_path : str, optional
        The path of the Q-DAS TestPlan file to create.
    qdas_params_path : str, optional
        The path of the Q-DAS parameters file to create.
    auto_kfields : list of str, optional
        A list of K-Fields to add to the parameters file prior to testplan
        creation.

    Returns
    -------
    str
        The path to the newly-created testplan.
    """
    if not testplan_path:
        testplan_path = QDAS_SETTINGS.testplan_path
        _debug_print(
            "Using default TestPlan file path: '{}'".format(testplan_path))

    if os.path.isfile(testplan_path):
        msg = ("Unable to create a new testplan using the existing testplan "
               "file '{}'.".format(testplan_path))
        _debug_print(msg)
        raise ZygoError(msg)

    if not qdas_params_path:
        qdas_params_path = QDAS_SETTINGS.qdas_params_path
        _debug_print(
            "Using default Q-DAS Parameters file path: '{}'".
            format(qdas_params_path))

    # Export parameters file from Mx proc stats.
    _debug_print("Exporting Q-DAS Parameters file...")
    ps_ctl = _ui.get_control(QDAS_SETTINGS.ps_grid_path)
    _export_qdas_parameters(ps_ctl, qdas_params_path)
    _debug_print("Done!")

    if auto_kfields is not None:
        _create_file_backup(qdas_params_path)
        _add_kfields(qdas_params_path, auto_kfields)

    if not _ui.show_dialog("Click OK to continue testplan creation in "
                           "Talyseries SPC.",
                           _ui.DialogMode.message_ok_cancel):
        return None

    _reset_talyseries_monitor_status()

    _debug_print("Calling Talyseries SPC: '{}'...".format(
            QDAS_SETTINGS.spc_exe_path))
    if not os.path.isfile(QDAS_SETTINGS.spc_exe_path):
        raise ZygoError("Invalid Talyseries SPC path: '{}'.".format(
                QDAS_SETTINGS.spc_exe_path))
    # Non-blocking call; can continue without closing Talyseries SPC
    try:
        subprocess.Popen(
            [QDAS_SETTINGS.spc_exe_path, testplan_path, qdas_params_path])
    except Exception as ex:
        raise ZygoError("Unknown error executing Talyseries SPC: '{}'.".format(
                ex))

    _debug_print(_monitor_talyseries_spc())

    if not os.path.isfile(testplan_path):
        return None

    _create_file_backup(testplan_path)
    _create_file_backup(qdas_params_path, None, False)

    _debug_print("Done!")

    return testplan_path


def export_qdas_results(testplan_path=None,
                        qdas_results_path=None,
                        *,
                        auto_kfields=None,
                        study_type=QdasStudyType.standard,
                        silent=False):
    """Exports process statistics from Mx and invokes Talyseries SPC to create
    Q-DAS reports.

    Parameters
    ----------
    testplan_path : str, optional
        The path of the Q-DAS TestPlan file to run.
    qdas_results_path : str, optional
        The path of the Q-DAS results file to create.
    auto_kfields : collections.OrderedDict, optional
        K-Fields and values to add to the results output.
    study_type : QdasStudyType, optional
        The Q-DAS study type for this testplan.
    silent : bool, optional
        True to suppress the Talyseries SPC message balloon.

    Returns
    -------
    str
        The result of the export operation.
    """
    if not testplan_path:
        testplan_path = QDAS_SETTINGS.testplan_path
        _debug_print(
            "Using default TestPlan file path: '{}'".format(testplan_path))

    if not qdas_results_path:
        qdas_results_path = QDAS_SETTINGS.qdas_results_path
        _debug_print(
            "Using default Q-DAS Results file path: '{}'".
            format(qdas_results_path))

    characteristics_data = _extract_testplan_parameters(testplan_path)
    if QDAS_SETTINGS.debug:
        for c_data in characteristics_data:
            pprint(vars(c_data))

    _debug_print("Exporting Q-DAS Results file...")
    ps_ctl = _ui.get_control(QDAS_SETTINGS.ps_grid_path)
    if study_type == QdasStudyType.standard:
        _export_qdas_results(ps_ctl, qdas_results_path)
    else:
        _export_qdas_results(ps_ctl, qdas_results_path, False, False)

    results_data = _extract_results(qdas_results_path)
    _debug_print("{} rows, {} characteristics per row".format(
        results_data.rows_count, results_data.characteristics_count))
    _debug_print(vars(results_data))

    _rebuild_results(characteristics_data, results_data, qdas_results_path)

    if auto_kfields is not None:
        _create_file_backup(qdas_results_path)
        _add_kfields(qdas_results_path, auto_kfields)

    _create_file_backup(qdas_results_path)

    if study_type == QdasStudyType.standard:
        if not _ui.show_dialog("Click OK to continue in Talyseries SPC.",
                               _ui.DialogMode.message_ok_cancel):
            return None

    _reset_talyseries_monitor_status()

    _debug_print("Calling Talyseries SPC: '{}'...".format(
            QDAS_SETTINGS.spc_exe_path))
    if not os.path.isfile(QDAS_SETTINGS.spc_exe_path):
        raise ZygoError("Invalid Talyseries SPC path: '{}'.".format(
                QDAS_SETTINGS.spc_exe_path))

    # Non-blocking call; can continue without closing Talyseries SPC
    try:
        params = [QDAS_SETTINGS.spc_exe_path, testplan_path, qdas_results_path]
        if QDAS_SETTINGS.spc_prompt:
            params.append('/prompt')
        if silent:
            params.append('/silent')
        subprocess.Popen(params)
    except Exception as ex:
        raise ZygoError("Unknown error executing Talyseries SPC: '{}'.".format(
                ex))

    return _monitor_talyseries_spc()


def reset_qdas_study():
    _reset_talyseries_monitor_status()

    _debug_print("Calling Talyseries SPC: '{}'...".format(
            QDAS_SETTINGS.spc_exe_path))
    if not os.path.isfile(QDAS_SETTINGS.spc_exe_path):
        raise ZygoError("Invalid Talyseries SPC path: '{}'.".format(
                QDAS_SETTINGS.spc_exe_path))

    # Non-blocking call; can continue without closing Talyseries SPC
    try:
        subprocess.Popen(
            [QDAS_SETTINGS.spc_exe_path, '/reset'])
    except Exception as ex:
        raise ZygoError("Unknown error executing Talyseries SPC: '{}'.".format(
                ex))

    return _monitor_talyseries_spc()


def get_study_status(testplan_path):
    """Queries Talyseries SPC for the current Q-DAS study status.

    Parameters
    ----------
    testplan_path : str
        The path of the current Q-DAS TestPlan file.

    Returns
    -------
    str
        The Q-DAS study status.
    """
    _reset_talyseries_monitor_status()

    _debug_print("Calling Talyseries SPC: '{}'...".format(
            QDAS_SETTINGS.spc_exe_path))
    if not os.path.isfile(QDAS_SETTINGS.spc_exe_path):
        raise ZygoError("Invalid Talyseries SPC path: '{}'.".format(
                QDAS_SETTINGS.spc_exe_path))

    # Non-blocking call; can continue without closing Talyseries SPC
    try:
        subprocess.Popen(
            [QDAS_SETTINGS.spc_exe_path, testplan_path, '/info', '/silent'])
    except Exception as ex:
        raise ZygoError("Unknown error executing Talyseries SPC: '{}'.".
                        format(ex))

    return _monitor_talyseries_spc()


def do_standard(spc_testplan,
                testplan_info,
                operation,
                *,
                auto_kfields=None):
    """Perform a Standard Production run.

    Parameters
    ----------
    spc_testplan : str
        The path to the SPC .testplan file to run.
    testplan_info : dict
        Information pertaining to this testplan.
    operation : func
        The function to call for each iteration.
    auto_kfields : collections.OrderedDict, optional
        K-Fields and values to add to the results output.
    """
    operation()
    res = export_qdas_results(spc_testplan,
                              auto_kfields=auto_kfields,
                              study_type=QdasStudyType.standard,
                              silent=True)
    status = res.get("Status", None) if res is not None else None
    if not status:
        return False
    msg = res.get("Message", "")
    _debug_print(msg)
    testplan_info = get_testplan_info(spc_testplan)
    if testplan_info is None:
        return False
    _ui.show_dialog("Run Complete!", _ui.DialogMode.message_ok,
                    title="Standard Production",
                    message_font=_MESSAGE_FONT,
                    button_font=_BUTTON_FONT)
    return True


def do_type_1(spc_testplan,
              testplan_info,
              operation,
              *,
              auto_kfields=None,
              prompt=OperationPromptType.info,
              sequence_start=None):
    """Perform a Type 1 gauge capability study.

    Parameters
    ----------
    spc_testplan : str
        The path to the SPC .testplan file to run.
    testplan_info : dict
        Information pertaining to this testplan.
    operation : func
        The function to call for each iteration.
    auto_kfields : collections.OrderedDict, optional
        K-Fields and values to add to the results output.
    prompt : `OperationPromptType`, optional
        The type of prompt for each iteration.
    sequence_start : int, optional
        The starting value for sequential serial numbers; if None, sequential
        serial numbers will be disabled.
    """
    # Check for completed study
    testplan_info = _do_study_complete(spc_testplan, testplan_info)
    if testplan_info is None:
        return False

    # Check for in-progress study
    if testplan_info.get('ref_idx', 0) > 0:
        testplan_info = _do_study_restart(spc_testplan, testplan_info)
        if testplan_info is None:
            return False

    ref_idx = testplan_info['ref_idx']
    ref_count = testplan_info['ref_count']
    is_finished = testplan_info.get('is_finished', True)

    serial_number = (
            auto_kfields.get(
                    QDAS_SETTINGS.serial_number_field.lower(), None)
            if sequence_start is None
            else str(sequence_start))
    prompt_for_serial = (prompt == OperationPromptType.serial or
                         prompt == OperationPromptType.unique_serial)
    while not is_finished:
        if prompt == OperationPromptType.info:
            dlg_msg = "Measure Reference {}/{}".format(
                    ref_idx+1, ref_count)
            if not _ui.show_dialog(dlg_msg,
                                   _ui.DialogMode.message_ok_cancel,
                                   title="Type 1 Study",
                                   message_font=_MESSAGE_FONT,
                                   button_font=_BUTTON_FONT):
                return False
            if sequence_start is not None:
                auto_kfields[QDAS_SETTINGS.serial_number_field.lower()] = \
                    serial_number
        elif prompt_for_serial:
            dlg_msg = "Measure Reference {}/{}\nEnter Part Serial Number" \
                .format(ref_idx+1, ref_count)

            serial_number = _ui.show_input_dialog(
                    dlg_msg,
                    serial_number if serial_number is not None
                    else '',
                    _ui.DialogMode.message_ok_cancel,
                    title="Type 1 Study",
                    message_font=_MESSAGE_FONT,
                    button_font=_BUTTON_FONT,
                    input_font=_MESSAGE_FONT)
            if serial_number is None:
                return False
            else:
                auto_kfields[QDAS_SETTINGS.serial_number_field.lower()] = \
                    serial_number
        elif prompt == OperationPromptType.none:
            if sequence_start is not None:
                auto_kfields[QDAS_SETTINGS.serial_number_field.lower()] = \
                    serial_number
        operation()
        res = export_qdas_results(spc_testplan,
                                  auto_kfields=auto_kfields,
                                  study_type=QdasStudyType.type_1,
                                  silent=True)
        status = res.get("Status", None) if res is not None else None
        if not status:
            return False
        msg = res.get("Message", "")
        _debug_print(msg)
        testplan_info = get_testplan_info(spc_testplan)
        if testplan_info is None:
            return False
        ref_idx = testplan_info['ref_idx']
        is_finished = testplan_info.get('is_finished', True)
        if (sequence_start and serial_number) is not None:
            serial_number = str(int(serial_number) + 1)
            auto_kfields[QDAS_SETTINGS.serial_number_field.lower()] = \
                serial_number
    _ui.show_dialog("Type 1 Study Complete!", _ui.DialogMode.message_ok,
                    title="Type 1 Study",
                    message_font=_MESSAGE_FONT,
                    button_font=_BUTTON_FONT)
    return True


def do_type_2(spc_testplan,
              testplan_info,
              operation,
              *,
              auto_kfields=None,
              prompt=OperationPromptType.info,
              sequence_start=None):
    """Perform a Type 2 gauge capability study.

    Parameters
    ----------
    spc_testplan : str
        The path to the SPC .testplan file to run.
    testplan_info : dict
        Information pertaining to this testplan.
    operation : func
        The function to call for each iteration.
    auto_kfields : collections.OrderedDict, optional
        K-Fields and values to add to the results output.
    prompt : `OperationPromptType`, optional
        The type of prompt for each iteration.
    sequence_start : int, optional
        The starting value for sequential serial numbers; if None, sequential
        serial numbers will be disabled.
    """
    if prompt == OperationPromptType.none:
        raise ValueError("Unsupported prompt type for a Type 2 Study.")

    # Check for completed study
    testplan_info = _do_study_complete(spc_testplan, testplan_info)
    if testplan_info is None:
        return False

    # Check for in-progress study
    oper_idx = testplan_info.get('oper_idx', 0)
    part_idx = testplan_info.get('part_idx', 0)
    trial_idx = testplan_info.get('trial_idx', 0)
    if (oper_idx + part_idx + trial_idx) > 0:
        testplan_info = _do_study_restart(spc_testplan, testplan_info)
        if testplan_info is None:
            return False

    if auto_kfields is None:
        auto_kfields = dict()

    is_finished = testplan_info.get('is_finished', True)
    oper_idx = testplan_info['oper_idx']
    oper_count = testplan_info['oper_count']
    part_idx = testplan_info['part_idx']
    part_count = testplan_info['part_count']
    trial_idx = testplan_info['trial_idx']
    trial_count = testplan_info['trial_count']

    # Set-up serial numbers, one per part
    serial_numbers = [None] * part_count
    if sequence_start is not None:
        # Sequential serial numbers
        serial_numbers = [str(sequence_start + i) for i in range(part_count)]
    else:
        # Static serial number
        sn = auto_kfields.get(QDAS_SETTINGS.serial_number_field.lower(), None)
        if sn is not None:
            serial_numbers = [sn] * part_count

    while not is_finished:
        serial_number = serial_numbers[part_idx]
        prompt_for_serial = (prompt == OperationPromptType.serial
                             or (prompt == OperationPromptType.unique_serial
                                 and serial_number is None))

        if not prompt_for_serial:
            dlg_msg = "Operator {}/{}\nPart {}/{}\nTrial {}/{}".format(
                    oper_idx+1, oper_count,
                    part_idx+1, part_count,
                    trial_idx+1, trial_count)
            if not _ui.show_dialog(dlg_msg,
                                   _ui.DialogMode.message_ok_cancel,
                                   title="Type 2 Study",
                                   message_font=_MESSAGE_FONT,
                                   button_font=_BUTTON_FONT):
                return False
            if sequence_start is not None:
                auto_kfields[QDAS_SETTINGS.serial_number_field.lower()] = \
                    serial_number
        else:
            dlg_msg = "Operator {}/{}\nPart {}/{}\nTrial {}/{}\n" \
                      "Enter Part Serial Number".format(
                              oper_idx+1, oper_count,
                              part_idx+1, part_count,
                              trial_idx+1, trial_count)

            serial_number = _ui.show_input_dialog(
                    dlg_msg,
                    serial_number if serial_number is not None
                    else '',
                    _ui.DialogMode.message_ok_cancel,
                    title="Type 2 Study",
                    message_font=_MESSAGE_FONT,
                    button_font=_BUTTON_FONT,
                    input_font=_MESSAGE_FONT)
            if serial_number is None:
                return False
            else:
                auto_kfields[QDAS_SETTINGS.serial_number_field.lower()] = \
                    serial_number
                serial_numbers[part_idx] = serial_number

        # Do operation and export results
        operation()
        res = export_qdas_results(spc_testplan,
                                  auto_kfields=auto_kfields,
                                  study_type=QdasStudyType.type_2,
                                  silent=True)

        # Refresh testplan status
        status = res.get("Status", None) if res is not None else None
        if not status:
            return False
        msg = res.get("Message", "")
        _debug_print(msg)
        testplan_info = get_testplan_info(spc_testplan)
        if testplan_info is None:
            return False

        is_finished = testplan_info.get('is_finished', True)
        oper_idx = testplan_info['oper_idx']
        part_idx = testplan_info['part_idx']
        trial_idx = testplan_info['trial_idx']

    _ui.show_dialog("Type 2 Study Complete!", _ui.DialogMode.message_ok,
                    title="Type 2 Study",
                    message_font=_MESSAGE_FONT,
                    button_font=_BUTTON_FONT)
    return True


def get_testplan_info(spc_testplan):
    stat = get_study_status(spc_testplan)
    try:
        if not stat.get('Status', False):
            return None
        info = stat.get('Message', None)
        if not info:
            return None
        split_info = info.split(';')
        ret = {}
        study_type = split_info[0]
        if study_type == '0':
            ret['study_type'] = QdasStudyType.standard
        elif study_type == '1':
            ret['study_type'] = QdasStudyType.type_1
            ret['is_finished'] = split_info[1] == "True"
            ret['ref_idx'] = int(split_info[2])
            ret['ref_count'] = int(split_info[3])
        elif study_type == '2':
            ret['study_type'] = QdasStudyType.type_2
            ret['is_finished'] = split_info[1] == "True"
            ret['oper_idx'] = int(split_info[2])
            ret['oper_count'] = int(split_info[3])
            ret['part_idx'] = int(split_info[4])
            ret['part_count'] = int(split_info[5])
            ret['trial_idx'] = int(split_info[6])
            ret['trial_count'] = int(split_info[7])
        elif study_type == '3':
            ret['study_type'] = QdasStudyType.type_3
            ret['is_finished'] = split_info[1] == "True"
            ret['part_idx'] = int(split_info[2])
            ret['part_count'] = int(split_info[3])
            ret['trial_idx'] = int(split_info[4])
            ret['trial_count'] = int(split_info[5])
        elif study_type == '':
            return None
        else:
            return None
        return ret
    except Exception:
        return None


def show_select_testplan():
    plans = [p.Name for p in QDAS_SETTINGS.mx_test_plans
             if p.SpcTestPlan is not None and os.path.isfile(p.SpcTestPlan)]
    idx = _ui.show_dropdown_dialog("Select Test Plan",
                                   plans,
                                   _ui.DialogMode.message_ok_cancel)
    plan_name = None if idx == -1 else plans[idx]
    plan = next((p for p in QDAS_SETTINGS.mx_test_plans
                 if p.Name == plan_name), None)

    return plan

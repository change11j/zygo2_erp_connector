# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Mx Ford QLS-CM Utilities.
"""
import re as _re
from enum import IntEnum as _IntEnum
import json
from collections import namedtuple
import itertools
import csv
from datetime import datetime

from zygo.core import ZygoError
from zygo import ui as _ui
from zygo import mx as _mx
from zygo.connectionmanager import get_send_request as _get_send_request
import zygo.systemcommands as _sc
import zygo.qdas as _qdas
from zygo.qdas.config_manager import MxTestPlanSettings


# =========================================================================
# ---Enumerations
# =========================================================================
# Trick to manually create enumeration to allow for descriptive aliases.
_OPERATION_STATUS_RESULTS = {
        1: ['No data found',
            'no_data'],
        0: ['Success',
            'success'],
        -1: ['Cannot connect to QLS-CM',
             'connect_error'],
        -2: ['Error sending message to QLS-CM',
             'comm_error'],
        -3: ['Invalid reply message from QLS-CM',
             'invalid_reply'],
        -4: ['Qlscm returned an error code',
             'qlscm_error'],
        -5: ['Error processing updates',
             'update_error'],
        -6: ['Bad parameters passed to function',
             'invalid_parameters'],
        -7: ['Communication dropped during processing or timeout',
             'comm_timeout'],
        -8: ['Unknown error',
             'unknown'],
        -99: ['Could not connect to server',
              'server_connect_error']
        }

OperationStatusResult = _IntEnum(
        value="OperationStatusResult",
        names=itertools.chain.from_iterable(
                itertools.product(v, [k]) for k, v in
                _OPERATION_STATUS_RESULTS.items()))


class ReasonForTestCode(_IntEnum):
    """
    Reasons why the part was sent to the guage.

    This code is the returned value for data item ID 10.
    """
    standard_check = 1
    capability_study = 2
    tool_change_check = 3
    zero_loss_tool_change = 4
    in_process_check = 5
    offset_verification = 6
    maint_verification = 7
    special_checks = 8
    teardown_analysis = 9
    thermal_verification = 10


class DataItemId(_IntEnum):
    """
    Data Item IDs for various attributes returned by QLS-CM.

    Note that these codes are offset by 9 from their documented value.
    """
    reason_code = 10
    machine_offset_x = 11
    machine_offset_y = 12
    machine_offset_z = 13
    start_temp = 14
    end_temp = 15
    machine_temp = 16
    part_temp = 17
    ambient_temp = 18


QlscmUnitResult = _IntEnum(value="QlscmUnitResult",
                           names={'complete': 1,
                                  'complete_nc': 2,
                                  'abort': 3,
                                  'bypass': 4,
                                  'buy_off': 5,
                                  'offloaded': 6,
                                  'scrap': 7,
                                  'offloaded_strip_back': 8,
                                  'reload': 9,
                                  'reload_repair': 10,
                                  'reload_strip_back': 11,
                                  'reload_customer_return': 12,
                                  'reload_rework': 13,
                                  'repaired': 14,
                                  'check_point': 15,
                                  'quarantine': 16,
                                  'complete_retry': 17,
                                  'accept':
                                      _qdas.QDAS_SETTINGS.accept_result_code,
                                  'reject':
                                      _qdas.QDAS_SETTINGS.reject_result_code},
                           module=__name__)


class QlscmUnitResult(_IntEnum):
    """QLS-CM unit result values."""
    complete = 1
    complete_nc = 2
    abort = 3
    bypass = 4
    buy_off = 5
    offloaded = 6
    scrap = 7
    offloaded_strip_back = 8
    reload = 9
    reload_repair = 10
    reload_strip_back = 11
    reload_customer_return = 12
    reload_rework = 13
    repaired = 14
    check_point = 15
    quarantine = 16
    complete_retry = 17


def _validate_qlscm_unit_result(unit_result):
    """Validate input as a valid QLS-CM unit result value.

    Parameters
    ----------
    unit_result : QlscmUnitResult or str
       QLS-CM unit result to validate.

    Returns
    -------
    str
        String representation of the specified QLS-CM unit result.

    Raises
    ------
    TypeError
        If the input is not a QlscmUnitResult or str type.
    ValueError
        If the input string is not convertable to a QlscmUnitResult member.
    """
    if isinstance(unit_result, QlscmUnitResult):
        return unit_result.name
    if isinstance(unit_result, str):
        for res in QlscmUnitResult.__members__:
            if unit_result.lower() == res.lower():
                return res
        raise ValueError(
            '`unit_result` string not a valid `QlscmUnitResult` member.')
    raise TypeError(
        '`unit_result` must be of type `QlscmUnitResult` or a valid '
        'string value.')


class QlscmPartType(_IntEnum):
    """QLS-CM part type values."""
    regular = 1
    master = 2
    pv_ppap_part = 3
    gauge = 4
    customer_return = 5
    service_unit = 6
    float_part = 7
    # spare = 8-19
    left = 20
    right = 21


def _validate_qlscm_part_type(part_type):
    """Validate input as a valid QLS-CM part type value.

    Parameters
    ----------
    unit_result : QlscmPartType or str
       QLS-CM part type to validate.

    Returns
    -------
    str
        String representation of the specified QLS-CM part type.

    Raises
    ------
    TypeError
        If the input is not a QlscmPartType or str type.
    ValueError
        If the input string is not convertable to a QlscmPartType member.
    """
    if isinstance(part_type, QlscmPartType):
        return part_type.name
    if isinstance(part_type, str):
        for part in QlscmPartType.__members__:
            if part_type.lower() == part.lower():
                return part
        raise ValueError(
            '`part_type` string not a valid `QlscmPartType` member.')
    raise TypeError(
        '`part_type` must be of type `QlscmPartType` or a valid '
        'string value.')


# =========================================================================
# ---Named Tuples
# =========================================================================
QlscmResult = namedtuple('QlscmResult',
                         ['OperationId',
                          'StationId',
                          'Timestamp',
                          'PalletId',
                          'OperationResult'])


QlscmAttribute = namedtuple('QlscmAttribute',
                            ['OperationId',
                             'StationId',
                             'AttributeIndex',
                             'AttributeValue'])


QlscmComponent = namedtuple('QlscmComponent',
                            ['Part', 'Result', 'Entry'])


# =========================================================================
# ---Custom Exceptions
# =========================================================================
class OperationStatusError(Exception):
    """Exception for errors returned by QLS-CM GetOperationStatus()."""
    pass


class BarcodeDatabaseError(Exception):
    """Exception for barcode database errors."""
    pass


# =========================================================================
# ---Classes
# =========================================================================
class PartEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Part):
            return super(PartEncoder, self).default(obj)

        part_dict = {'UnitId': obj.unit_id,
                     'Source': obj.source,
                     'BuildDate': obj.build_date,
                     'RunningNo': obj.running_no,
                     'WersPrefix': obj.wers_prefix,
                     'WersBase': obj.wers_base,
                     'WersSuffix': obj.wers_suffix,
                     'ProcessData': obj.process_data,
                     'PartSerialNumber': obj.part_serial_number,
                     'PartNumber': obj.part_number,
                     'UnitType': obj.unit_type}
        return part_dict


class PartBirthHistory(object):
    # =========================================================================
    # ---Private Member Attributes
    # =========================================================================
    _results = None
    _attributes = None
    _error = None

    def _make_properties(self, mx_operation_status):
        self._error = mx_operation_status.get("Error", None)

        result_list = mx_operation_status.get("ResultList", [])
        if result_list is None:
            self._results = []
        else:
            self._results = [QlscmResult._make(r) for r in result_list]

        attribute_list = mx_operation_status.get("AttributeList", [])
        if attribute_list is None:
            self._attributes = []
        else:
            self._attributes = [QlscmAttribute._make(a)
                                for a in attribute_list]

    def __init__(self, mx_operation_status):
        if mx_operation_status is None:
            return
        self._make_properties(mx_operation_status)

    @property
    def results(self):
        return self._results

    @property
    def attributes(self):
        return self._attributes

    @property
    def error(self):
        return self._error


class Part(object):
    # =========================================================================
    # ---Internal Static Methods
    # =========================================================================
    @staticmethod
    def _get_regex_pattern():
        """Creates and compiles the regex pattern for parsing.

        Returns
        -------
        object
            The compiled regular expression object.
        """
        # Unit ID/Barcode: F960G12165321631BSCV6P 7006 CE
        # Supplier Code: F960G
        # Julian Date: 12165
        # Serial No: 321631
        # Part Number: BSCV6P 7006 CE
        re_string = r"""
            (?P<source>
             [A-Z0-9]{5}
            )
            (?P<build_date>
             [A-Z0-9]{5}
            )
            (?P<running_no>
             [A-Z0-9]{6}
            )
            (?P<wers_prefix>
             [A-Z0-9]+
            )
            \s
            (?P<wers_base>
             [A-Z0-9]+
            )
            \s
            (?P<wers_suffix>
             [A-Z0-9]+
            )
            (?:\x1D
             (?P<process_data>
              .+
             )
            )?
        """
        return _re.compile(re_string, _re.VERBOSE)

    # =========================================================================
    # ---Private Member Attributes
    # =========================================================================
    _unit_id = None
    _regex_pattern = _get_regex_pattern.__func__()

    _operation_id = None
    _operation_desc = None
    _station_id = None
    _station_desc = None
    _datetime = None
    _pallet_id = None
    _location_id = None
    _part_level_id = None

    # =========================================================================
    # ---Private Methods
    # =========================================================================
    def _parse(self, barcode_string):
        """Parse and group the barcode string.

        Parameters
        ----------
        barcode_string : str
            The barcode string (Unit ID) to parse.

        Returns
        -------
        dict
            The match group dictionary of the validated barcode.

        Raises
        ------
        zygo.qdas.barcode.BarcodeParseError
            If barcode parsing fails to find a match.
        ValueError
            If the barcode string is None or empty.
        """
        if barcode_string:
            barcode_match = self.__class__._regex_pattern.match(barcode_string)
            if not barcode_match:
                raise _qdas.barcode.BarcodeParseError(
                        "No barcode match found!")
            return barcode_match.groupdict()
        else:
            raise ValueError('Barcode string cannot be None or empty.')

    def _get_value(self, key):
        if (self._barcode_match is None or
                not isinstance(self._barcode_match, dict)):
            return None
        else:
            return self._barcode_match.get(key)

    def __str__(self):
        """Return a printable string representation of this object."""
        fmt_str = 'unit_id = {0.unit_id!s}\n' \
            'source = {0.source!s}\n' \
            'build_date = {0.build_date!s}\n' \
            'running_no = {0.running_no!s}\n' \
            'wers_prefix = {0.wers_prefix!s}\n' \
            'wers_base = {0.wers_base!s}\n' \
            'wers_suffix = {0.wers_suffix!s}\n' \
            'process_data = {0.process_data!s}\n' \
            'part_serial_number = {0.part_serial_number!s}\n' \
            'part_number = {0.part_number!s}\n' \
            'unit_type = {0.unit_type!s}\n'
        return fmt_str.format(self)

    # =========================================================================
    # ---Instance Initialization
    # =========================================================================
    def __init__(self, barcode_string):
        """Initializes a Part object.

        Parameters
        ----------
        barcode_string : str
            The barcode string (Unit ID) associated with this part.
        """
        self._barcode_match = self._parse(barcode_string)
        self._unit_id = barcode_string

    # =========================================================================
    # ---Public Methods
    # =========================================================================
    def to_dict(self):
        """Create a serializable dictionary containing this Part's properties.
        """
        part_dict = {'UnitId': self.unit_id,
                     'Source': self.source,
                     'BuildDate': self.build_date,
                     'RunningNo': self.running_no,
                     'WersPrefix': self.wers_prefix,
                     'WersBase': self.wers_base,
                     'WersSuffix': self.wers_suffix,
                     'ProcessData': self.process_data,
                     'PartSerialNumber': self.part_serial_number,
                     'PartNumber': self.part_number,
                     'UnitType': self.unit_type}
        return part_dict

    @classmethod
    def from_dict(cls, part_dict):
        """Create a new Part from the supplied dictionary.
        """
        # We don't want Part.__init__() to be called
        p = cls.__new__(cls)
        if part_dict is not None:
            barcode_match = {
                    'wers_prefix': part_dict.get('WersPrefix', None),
                    'wers_suffix': part_dict.get('WersSuffix', None),
                    'wers_base': part_dict.get('WersBase', None),
                    'running_no': part_dict.get('RunningNo', None),
                    'build_date': part_dict.get('BuildDate', None),
                    'process_data': part_dict.get('ProcessData', None),
                    'source': part_dict.get('Source', None)}

            setattr(p, '_barcode_match', barcode_match)
            setattr(p, '_unit_id', part_dict.get('UnitId', None))

        return p

    # =========================================================================
    # ---Public Properties
    # =========================================================================
    @property
    def unit_id(self):
        """str: This part's Unit ID."""
        return self._unit_id

    @property
    def source(self):
        """str: The Source portion of the Unit ID."""
        return self._get_value("source")

    @property
    def build_date(self):
        """str: The Build Date portion of the Unit ID."""
        return self._get_value("build_date")

    @property
    def running_no(self):
        """str: The Running Number portion of the Unit ID."""
        return self._get_value("running_no")

    @property
    def wers_prefix(self):
        """str: The WERS Prefix portion of the Unit ID."""
        return self._get_value("wers_prefix")

    @property
    def wers_base(self):
        """str: The WERS base portion of the Unit ID."""
        return self._get_value("wers_base")

    @property
    def wers_suffix(self):
        """str: The WERS suffix portion of the Unit ID."""
        return self._get_value("wers_suffix")

    @property
    def process_data(self):
        """str: The Process Data portion of the Unit ID."""
        return self._get_value("process_data")

    @property
    def part_serial_number(self):
        """str: The Serial Number of this part."""
        return '{}{}'.format(self.build_date, self.running_no)

    @property
    def part_number(self):
        """str: The Part Number of this part."""
        return '{} {} {}'.format(
                self.wers_prefix, self.wers_base, self.wers_suffix)

    @property
    def unit_type(self):
        """str: The Unit Type of this part."""
        return self.part_number


class Qlscm(object):
    # =========================================================================
    # ---Initialization
    # =========================================================================
    def __init__(self):
        self._part = None
        self._history = None
        self._entry = None
        self._plan = None
        try:
            self._auto_kfields = _qdas.qdas.QDAS_SETTINGS.auto_kfields
        except Exception:
            self._auto_kfields = None

    def _reset(self):
        self._part = None
        self._history = None
        self._entry = None
        self._plan = None
        self._auto_kfields = None

    # =========================================================================
    # ---Public Properties
    # =========================================================================
    @property
    def part(self):
        """qlscm.Part: The scanned part."""
        return self._part

    @property
    def history(self):
        return self._history

    @property
    def entry(self):
        return self._entry

    @property
    def plan(self):
        return self._plan

    @property
    def auto_kfields(self):
        return self._auto_kfields

    # =========================================================================
    # ---QLS-CM DLL Methods
    # =========================================================================
    def _get_operation_status(
            self,
            unit_id,
            unit_type,
            operation_id,
            station_id,
            data_item_id):
        """QLS-CM GetOperationStatus.

        Parameters
        ----------
        unit_id : str
            Unit ID.
        unit_type : str
            Unit Type.
        operation_id : str
            Operation ID.
        station_id : str
            Station ID.
        data_item_id : str
            Data Item ID.

        Returns
        -------
        PartBirthHistory
            The result of the GetOperationStatus call.
        """
        params = {'unitId': unit_id,
                  'unitType': unit_type,
                  'operationId': operation_id,
                  'stationId': station_id,
                  'dataItemId': data_item_id}
        res = _get_send_request(
                _mx._SERVICE,
                'QlscmGetOperationStatus',
                params)
        if res is None:
            return None
        return PartBirthHistory(res)

    def _qlscm_update_birth_history(
            self,
            unit_id,
            unit_type,
            unit_result,
            pallet_id,
            part_type):
        """QLS-CM UpdateBirthHistory.

        Parameters
        ----------
        unit_id : str
            Unit ID.
        unit_type : str
            Unit Type.
        unit_result : int
            The result of the part.
        pallet_id : str
            Pallet ID.
        part_type : int
            20 for left-hand parts, 21 for right-hand parts, 0 for all others.

        Returns
        -------
        string
            The result.
        """
        params = {'unitId': unit_id,
                  'unitType': unit_type,
                  'unitResult': unit_result,
                  'palletId': pallet_id,
                  'part_type': part_type}
        return _get_send_request(
                _mx._SERVICE,
                'QlscmUpdateBirthHistory',
                params)

    # =========================================================================
    # ---Private Implementation Methods
    # =========================================================================
    def _scan_barcode(self, manual_entry=False):
        """Scan, validate, and parse the barcode.

        Parameters
        ----------
        manual_entry : bool
            If True, allow a user to manually entry the Unit ID. Used when,
            e.g., the barcode scanner is unavailable.

        Returns
        -------
        Part or None
            A Part object representing the scanned Unit ID.
        """
        try:
            barcode_string = _qdas.barcode.scan(manual_entry=manual_entry)
            if barcode_string is None:
                # Dialog canceled
                _mx.log_info("Scan barcode dialog canceled.")
                return None
            return Part(barcode_string)
        except _qdas.barcode.BarcodeValidationError as bve:
            _mx.log_error("BarcodeValidationError: {}".format(bve))
            msg = "Invalid Barcode"
            args = ["Invalid barcode data.\n\nPlease Notify Supervisor.",
                    msg, _ui.DialogMode.error_ok]
            _sc._execute_command("UserInterface", "ShowDialog", args)
        except ZygoError as ze:
            _mx.log_error(repr(ze))
            msg = "Script Error"
            args = ["Mx returned an error.\n\nPlease Notify Supervisor.",
                    msg, _ui.DialogMode.error_ok]
            _sc._execute_command("UserInterface", "ShowDialog", args)
        except ValueError as ve:
            _mx.log_error(repr(ve))
            msg = "Value Error"
            args = ["Invalid value.\n\nPlease Notify Supervisor.",
                    msg, _ui.DialogMode.error_ok]
            _sc._execute_command("UserInterface", "ShowDialog", args)
        except Exception as ex:
            msg = "Unexpected Error"
            _mx.log_error(str(ex))
            args = ["Unexpected error.\n\nPlease Notify Supervisor.",
                    msg, _ui.DialogMode.error_ok]
            _sc._execute_command("UserInterface", "ShowDialog", args)
        return None

    def _show_qlscm_dialog(self, component, testplans):
        """Show the QLS-CM dialog populated with the component info.
        """
        params = {'qlscmComponent': component._asdict(),
                  'testPlans': [s._asdict() for s in testplans]}
        return _get_send_request(_mx._SERVICE, 'ShowQlscmDialog', params)

    def _search_barcode_catalog(self, part_number, station_id):
        """Find the first line inf the barcode catalog matching the part
        number and station id.
        """
        with open(_qdas.qdas.QDAS_SETTINGS.birth_history_catalog, 'r') as f:
            # Filter out comment lines.
            reader = csv.DictReader(row for row in f
                                    if not row.lstrip().startswith('#'))
            # Return the first matching entry in the catalog.
            return next((row for row in reader
                         if row['PartId'] == part_number
                         and row['StationId'] == station_id), None)

    def _get_birth_history(self, part):
        """Gets the QLS-CM part birth history from the DLL.

        Parameters
        ----------
        part : Part
            The part subject of the database query.

        Returns
        -------
        PartBirthHistory
            The QLS-CM birth history, or None if error.
        """
        # ***This particular call requests test data from Mx.
        birth_history = self._get_operation_status(
                None,
                1,
                _qdas.qdas.QDAS_SETTINGS.operation_id,
                _qdas.qdas.QDAS_SETTINGS.station_id,
                _qdas.qdas.QDAS_SETTINGS.data_id)

        # Handle any errors.
        if birth_history is None:
            msg = "Unexpected Error"
            args = ["Unexpected error.\n\nPlease Notify Supervisor.",
                    msg, _ui.DialogMode.error_ok]
            _sc._execute_command(_ui._SERVICE, "ShowDialog", args)
            return None
        if birth_history.error != 0:
            msg = "QLS-CM Database Error"
            args = ["{}.\n\nPlease Notify Supervisor.".format(
                    OperationStatusResult(birth_history.error).name),
                    msg, _ui.DialogMode.error_ok]
            _sc._execute_command(_ui._SERVICE, "ShowDialog", args)
            return None

        return birth_history

    def _get_latest_station_results(self, birth_history_results):
        """Gets a list of the most recent result for each unique station.

        Parameters
        ----------
        birth_history_results : list of qlscm.QlscmResult
            A list of the results returned from the birth history lookup.

        Returns
        -------
        list of qlscm.QlscmResult
            A list of the most recent results for each unique station, sorted
            by timestamp.

        Note
        ----
        Additional filtering can be done here as well, e.g., most recent result
        where the status was "23".
        """
        DT_FRMT = "%m/%d/%Y %I:%M:%S %p"  # The datetime format string
        # Create a set of all unique station IDs in the birth history results.
        stations = {r.StationId for r in birth_history_results}
        filtered_list = []
        for s in stations:
            filtered_list.append(
                    max([r for r in birth_history_results if r.StationId == s],
                        key=lambda i: datetime.strptime(i.Timestamp, DT_FRMT)))
        # Sort the new list by timestamp.
        filtered_list.sort(
                key=lambda i: datetime.strptime(i.Timestamp, DT_FRMT),
                reverse=True)
        return filtered_list

    def _query_birth_history_catalog(self, part_number, birth_history_results):
        """Perform a lookup in the birth history catalog to find the first
        entry which matches the birth history results.

        Parameters
        ----------
        part_number : str
            The WERS part number of the scanned part.
        birth_history_results :  list of qlscm.QlscmResult
            A list of the results returned from the birth history lookup.

        Returns
        -------
        tuple of dictionary, dictionary
            The birth history result and catalog row which match
            the given criteria.
        """
        # Filter the birth history results to get the latest for each station.
        filtered_results = self._get_latest_station_results(
                birth_history_results)
        # Find the first row which matches a station/part # pair.
        retval = None
        for res in filtered_results:
            cat_entry = self._search_barcode_catalog(
                    part_number,
                    res.StationId)
            if cat_entry is not None:
                retval = (res._asdict(), cat_entry)
                break
        return retval

    def _extract_qlscm_dialog_results(self, results):
        component = results.get('Component', None)
        self._part = Part.from_dict(component.get('Part', None))
        self._history = QlscmResult(**component.get('Result', None))
        self._entry = component.get('Entry', None)
        plan_dict = results.get('Plan', None)
        self._plan = MxTestPlanSettings(**plan_dict) if plan_dict else None

    # =========================================================================
    # ---Public Methods
    # =========================================================================
    def do_qlscm(self, manual_entry=False):
        """Execute QLS-CM.

        Parameters
        ----------
        manual_entry : bool
            True to enable manual user entry.

        Returns
        -------
        bool
            True on success, False on failure.
        """
        try:
            # Scan and parse the barcode into a Part object.
            part = self._scan_barcode(manual_entry)
            if part is None:
                self._reset()
                return False

            birth_history = self._get_birth_history(part)
            if birth_history is None:
                self._reset()
                return False

            ret = self._query_birth_history_catalog(
                    part.part_number,
                    birth_history.results)
            if ret is None:
                self._reset()
                return False

            bh_res, cat_entry = ret
            if bh_res is None or cat_entry is None:
                self._reset()
                return False

            component = QlscmComponent(
                part.to_dict(),
                bh_res,
                cat_entry)

            testplans = _qdas.qdas.QDAS_SETTINGS.mx_test_plans

            ret = self._show_qlscm_dialog(component, testplans)
            if ret is None:
                self._reset()
                return False

            self._extract_qlscm_dialog_results(ret)

            # Populate auto k-fields with the appropriate values.
            try:
                self._auto_kfields['k0006'] = self._entry.get('PalletId', '')
                self._auto_kfields['k0010'] = self._entry.get('MachineId', '')
                self._auto_kfields['k0016'] = self._entry.get('Department', '')
                self._auto_kfields['k0017'] = self._entry.get('Area', '')
                self._auto_kfields['k0053'] = self._part.part_serial_number
                self._auto_kfields['k0054'] = self._history.Timestamp
                self._auto_kfields['k0055'] = self._plan.Name or ''
                self._auto_kfields['k1001'] = self._part.part_number
                self._auto_kfields['k0011'] = self._entry.get('ProcessId', '')
            except NameError:
                # Ignore if not defined
                pass

            return True
        except Exception as ex:
            raise ZygoError(ex)

    def upload_history(self, qlscm_unit_result):
        """Update QLS-CM birth history.

        Parameters
        ----------
        qlscm_unit_result : qlscm.QlscmUnitResult
            The QLS-CM unit result.

        Returns
        -------
        bool
            True on success, False on failure.
        """

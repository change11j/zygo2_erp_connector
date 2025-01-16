# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Support basic high-level Mx functionality.
"""
from enum import IntEnum

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.connectionmanager import get_uid as _get_uid
from zygo.units import Units as _Units, _validate_unit


_SERVICE = 'MxService'
"""str: The service name for this module."""


# =============================================================================
# ---Enumerations
# =============================================================================
class DataAlignmentScalingMode(IntEnum):
    """Data alignment scaling modes."""
    isomorphic = 0
    anamorphic = 1


def _validate_scaling_mode(scaling_mode):
    """Validate input as a valid scaling mode value.

    Parameters
    ----------
    scaling_mode : DataAlignmentScalingMode or str
        Data alignment scaling mode to validate.

    Returns
    -------
    str
        String representation of the specified data alignment scaling mode.

    Raises
    ------
    TypeError
        If the input is not a DataAlignmentScalingMode or str type.
    ValueError
        If the input string is not convertable to a DataAlignmentScalingMode
        member.
    """
    if isinstance(scaling_mode, DataAlignmentScalingMode):
        return scaling_mode.name
    if isinstance(scaling_mode, str):
        for mode in DataAlignmentScalingMode.__members__:
            if scaling_mode.lower() == mode.lower():
                return mode
        raise ValueError(
            '`scaling_mode` string is not a valid `DataAlignmentScalingMode`'
            'member.')
    raise TypeError(
        '`scaling_mode` must be of type `DataAlignmentScalingMode`'
        'or a valid string value.')


class FiducialAlignmentType(IntEnum):
    """Alignment types used for fiducial alignment."""
    fixed = 0
    variable = 1


def _validate_fiducial_alignment_type(alignment_type):
    """Validate input as a valid fiducial alignment type value.

    Parameters
    ----------
    alignment_type : FiducialAlignmentType or str
        Fiducial alignment type to validate.

    Returns
    -------
    str
        String representation of the specified fiducial alignment type.

    Raises
    ------
    TypeError
        If the input is not a FiducialAlignmentType or str type.
    ValueError
        If the input string is not convertable to a FiducialAlignmentType
        member.
    """
    if isinstance(alignment_type, FiducialAlignmentType):
        return alignment_type.name
    if isinstance(alignment_type, str):
        for align in FiducialAlignmentType.__members__:
            if alignment_type.lower() == align.lower():
                return align
        raise ValueError(
            '`alignment_type` string not a valid `FiducialAlignmentType`'
            'member.')
    raise TypeError(
        '`alignment_type` must be of type `FiducialAlignmentType`'
        'or a valid string value.')


class AxisFlipType(IntEnum):
    """Axis flip selection used for flip data."""
    xaxis = 0
    yaxis = 1


def _validate_axis_flip_type(axis_type):
    """Validate input as a valid axis flip type value.

    Parameters
    ----------
    axis_type : AxisFlipType or str
        Axis flip type to validate.

    Returns
    -------
    str
        String representation of the specified axis flip type.

    Raises
    ------
    TypeError
        If the input is not a AxisFlipType or str type.
    ValueError
        If the input string is not convertable to a AxisFlipType member.
    """
    if isinstance(axis_type, AxisFlipType):
        return axis_type.name
    if isinstance(axis_type, str):
        for flip in AxisFlipType.__members__:
            if axis_type.lower() == flip.lower():
                return flip
        raise ValueError(
            '`axis_type` string not a valid `AxisFlipType` member.')
    raise TypeError(
        '`axis_type` must be of type `AxisFlipType` or a valid string value.')


class TrimType(IntEnum):
    """Edge trim type selection."""
    all = 0
    outside = 1


def _validate_trim_type(trim_type):
    """Validate input as a valid edge trim type value.

    Parameters
    ----------
    trim_type : TrimType or str
        Edge trim type to validate.

    Returns
    -------
    str
        String representation of the specified edge trim type.

    Raises
    ------
    TypeError
        If the input is not a TrimType or str type.
    ValueError
        If the input string is not convertable to a TrimType member.
    """
    if isinstance(trim_type, TrimType):
        return trim_type.name
    if isinstance(trim_type, str):
        for trim in TrimType.__members__:
            if trim_type.lower() == trim.lower():
                return trim
        raise ValueError('`trim_type` string not a valid `TrimType` member.')
    raise TypeError(
        '`trim_type` must be of type `TrimType` or a valid string value.')


class SettingsOption(IntEnum):
    """Load settings options."""
    acquisition = 0
    analysis = 1
    stitch = 2
    pattern = 3
    auto_sequence = 4
    masks = 5
    process_stats = 6
    pattern_origin = 7
    pattern_rotation = 8


def _validate_load_settings_options(option):
    """Validate input as a valid settings option value.

    Parameters
    ----------
    option : SettingsOption or str
        Settings option to validate.

    Returns
    -------
    str
        String representation of the specified settings option.

    Raises
    ------
    TypeError
        If the input is not a SettingsOption or str type.
    ValueError
        If the input string is not convertable to a SettingsOption member.
    """
    if isinstance(option, SettingsOption):
        return option.name
    if isinstance(option, str):
        for opt in SettingsOption.__members__:
            if option.lower() == opt.lower():
                return opt
        raise ValueError(
            '`option` string not a valid `SettingsOption` member.')
    raise TypeError(
        '`option` must be of type `SettingsOption` or a valid string value')


# =============================================================================
# ---Application Methods
# =============================================================================
def is_application_open():
    """Get whether or not an Mx application is open.

    Returns
    -------
    bool
        True if an application is open; False otherwise.
    """
    return _get_send_request(_SERVICE, 'IsApplicationOpen')


def get_application_path():
    """Get the full path of the current application.

    Returns
    -------
    str
        The full path of the current application if open; None otherwise.
    """
    return _get_send_request(_SERVICE, 'GetApplicationPath')


def open_application(filename):
    """Open the specified Mx application.

    Parameters
    ----------
    filename : str
        The path of the Mx application file to load.
    """
    params = {'fileName': filename, 'uid': _get_uid()}
    _send_request(_SERVICE, 'OpenApplication', params)


def close_application():
    """Close the current Mx application."""
    _send_request(_SERVICE, 'CloseApplication')


def save_application_as(filename):
    """Save the current Mx application as the specified filename.

    Parameters
    ----------
    filename : str
        The path of the file to save as.
    """
    _send_request(_SERVICE, 'SaveApplicationAs', {'fileName': filename})


# =============================================================================
# ---Settings Methods
# =============================================================================
def load_settings(filename):
    """Load an Mx settings file.

    Parameters
    ----------
    filename : str
        The path of the Mx settings file to load.
    """
    params = {'fileName': filename, 'uid': _get_uid()}
    _send_request(_SERVICE, 'LoadSettings', params)


def load_settings_using_options(filename,
                                options_list=[SettingsOption.acquisition,
                                              SettingsOption.analysis,
                                              SettingsOption.masks,
                                              SettingsOption.pattern,
                                              SettingsOption.pattern_origin,
                                              SettingsOption.pattern_rotation,
                                              SettingsOption.process_stats,
                                              SettingsOption.stitch]):
    """Load an Mx settings file using the specified options.

    This function selectively loads sections of a settings file based on the
    options passed in the list. This is similar to the Mx Load Settings recipe
    step.

    Parameters
    ----------
    filename : str
        The path of the Mx settings file to load.
    options_list : list of SettingsOption, optional
        List of settings options to load.
    """
    lst = []
    if isinstance(options_list, SettingsOption):
        options_list = [options_list]
    for item in options_list:
        lst.append(_validate_load_settings_options(item))
    params = {'fileName': filename, 'options': lst, 'uid': _get_uid()}
    _send_request(_SERVICE, 'LoadSettingsUsingOptions', params)


def save_settings(filename):
    """Save the current Mx settings to a file.

    Parameters
    ----------
    filename : str
        The path of the settings file to save to.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'SaveSettings', params)


# =============================================================================
# ---Data Methods
# =============================================================================
def analyze():
    """Analyze the current data."""
    _send_request(_SERVICE, 'Analyze', {'uid': _get_uid()})


def auto_save_data(update_sequence=False):
    """Save the current data using the values in the AutoSequence
       AutoSaveData controls.

    Parameters
    ----------
    update_sequence : bool, optional
        If True, increments any auto generate sequential components.

    Returns
    -------
    str
        The path of the saved data; None if no data saved.
    """
    params = {'updateSequence': update_sequence}
    return _get_send_request(_SERVICE, 'AutoSaveData', params)


def load_data(filename):
    """Load Mx data from the specified filename.

    Parameters
    ----------
    filename : str
        The path of the data file to load.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'LoadData', params)


def save_data(filename):
    """Save the current Mx data to the specified file.

    Parameters
    ----------
    filename : str
        The path of the data file to save to.
    """
    params = {'fileName': filename, 'uid': _get_uid()}
    _send_request(_SERVICE, 'SaveData', params)


def load_signal_data(filename):
    """Load Mx signal data from specified filename.

    Parameters
    ----------
    filename : str
        The path of the signal data file to load.
    """
    _send_request(_SERVICE, 'LoadSignalData', {'fileName': filename})


def save_signal_data(filename):
    """Save the current Mx signal data to the specified file.

    Parameters
    ----------
    filename :
        The path of the signal data file to save to.
    """
    _send_request(_SERVICE, 'SaveSignalData', {'fileName': filename})


def load_and_average_data(file_pathnames,
                          min_valid_pct,
                          use_fiducial_alignment=False,
                          scaling_mode=DataAlignmentScalingMode.isomorphic):
    """Load and average the specified Mx data files.

    Parameters
    ----------
    file_pathnames : list of str
        List of Mx data filenames to load from.
    min_valid_pct : float
        The minimum valid percent at a pixel location in the data matrix when
        averaging.
    use_fiducial_alignment : bool, optional
        Whether to use fiducial alignment to align the data when averaging.
    scaling_mode : DataAlignmentScalingMode, optional
        The data alignment scaling mode to use to align the data; only used
        with fiducial alignment.
    """
    if scaling_mode is None:
        scaling_mode = DataAlignmentScalingMode.isomorphic
    scaling_mode_string = _validate_scaling_mode(scaling_mode)
    params = {'fileNames': file_pathnames,
              'minValid': min_valid_pct,
              'useFiducialAlignment': use_fiducial_alignment,
              'scaling': scaling_mode_string}
    _send_request(_SERVICE, 'LoadAndAverageData', params)


def reset_data():
    """Resets the current Mx data and clears all plots."""
    _send_request(_SERVICE, 'ResetData')


# =============================================================================
# ---Data Manipulate Methods
# =============================================================================
def subtract_data(filename, ignore_lateral_res=True,
                  use_input_size=False,
                  use_system_size=False,
                  use_fiducial_alignment=False,
                  alignment_type=FiducialAlignmentType.fixed,
                  alignment_tolerance=1.0):
    """Subtracts the given file from the current data.

    Parameters
    ----------
    filename : string
        The path of the data file to subtract.
    ignore_lateral_res : bool, optional
        Whether to ignore lateral resolution.
    use_input_size : bool, optional
        Whether to use the input matrix data size.
    use_system_size : bool, optional
        Whether to use the system reference data size.
    use_fiducial_alignment : bool, optional
        Whether to use fiducial alignment.
    alignment_type : FiducialAlignmentType, optional
        The alignment type; only used with fiducial alignment.
    alignment_tolerance : float, optional
        The alignment tolerance in pixels; only used with fiducial alignment.
    """
    align_type_string = _validate_fiducial_alignment_type(alignment_type)
    params = {'dataFileName': filename,
              'ignoreLateralRes': ignore_lateral_res,
              'useInputSize': use_input_size,
              'useSystemSize': use_system_size,
              'useFiducialAlignment': use_fiducial_alignment,
              'alignmentType': align_type_string,
              'alignmentTolerance': alignment_tolerance}
    _send_request(_SERVICE, 'SubtractData', params)


def scale_data(scale_value):
    """Scales the current data.

    Parameters
    ----------
    scale_value : float
        The scale factor value.
    """
    params = {'scaleValue': scale_value}
    _send_request(_SERVICE, 'ScaleData', params)


def add_data(filename,
             use_input_size=False,
             use_add_size=False,
             use_fiducial_alignment=False,
             alignment_type=FiducialAlignmentType.fixed,
             alignment_tolerance=1.0):
    """Adds the given file to the current data.

    Parameters
    ----------
    filename : string
        The path of the data file to add.
    use_input_size : bool, optional
        Whether to use the input matrix data size.
    use_add_size : bool, optional
        Whether to use the added data size.
    use_fiducial_alignment : bool, optional
        Whether to use fiducial alignment.
    alignment_type : FiducialAlignmentType, optional
        The alignment type; only used with fiducial alignment.
    alignment_tolerance : float, optional
        The alignment tolerance in pixels; only used with fiducial alignment.
    """

    align_type_string = _validate_fiducial_alignment_type(alignment_type)
    params = {'dataFileName': filename,
              'useInputSize': use_input_size,
              'useAddSize': use_add_size,
              'useFiducialAlignment': use_fiducial_alignment,
              'alignmentType': align_type_string,
              'alignmentTolerance': alignment_tolerance}
    _send_request(_SERVICE, 'AddData', params)


def invert_data(z_datum, unit):
    """Inverts the current data about the given Z datum.

    Parameters
    ----------
    z_datum : float
        Z datum height value to invert about.
    unit : units.Units
        The units of the z datum. Set to None to use the base units of the
        current data.
    """
    unit_str = _validate_unit(unit)
    params = {'zDatum': z_datum, 'units': unit_str}
    _send_request(_SERVICE, 'InvertData', params)


def rotate_data(angle, unit, no_clip):
    """Rotates the current data by the given angle.

    Parameters
    ----------
    angle : float
        The angle to rotate by.
    unit : units.Units
        The units of the angle.
    no_clip : bool
        Whether or not to clip the data after rotation.
    """
    unit_str = _validate_unit(unit)
    params = {'angle': angle, 'units': unit_str, 'noClip': no_clip}
    _send_request(_SERVICE, 'RotateData', params)


def flip_data(axis_type=AxisFlipType.xaxis):
    """Flips the current data about the specified axis.

    Parameters
    ----------
    axis_type : AxisFlipType, optional
        The axis to flip about.
    """
    axis_type_string = _validate_axis_flip_type(axis_type)
    params = {'axisType': axis_type_string}
    _send_request(_SERVICE, 'FlipData', params)


def trim_data(trim_size, trim_type=TrimType.outside):
    """Trims the current data.

    Parameters
    ----------
    trim_size : int
        The size for trimming, must be >= 0.
    trim_type : TrimType, optional
        The type of trim to perform.
    """
    trim_type_string = _validate_trim_type(trim_type)
    params = {'trimSize': trim_size, 'trimType': trim_type_string}
    _send_request(_SERVICE, 'TrimData', params)


def translate_data(x_translation, x_unit, y_translation, y_unit):
    """Translates the current data.

    Parameters
    ----------
    x_translation : float
        The x translation distance.
    x_unit : units.Units
        The units of the x translation.
    y_translation : float
        The y translation distance.
    y_unit : units.Units
        The units of the y translation.
    """
    x_unit_str = _validate_unit(x_unit)
    y_unit_str = _validate_unit(y_unit)

    params = {'xTranslation': x_translation,
              'xUnits': x_unit_str,
              'yTranslation': y_translation,
              'yUnits': y_unit_str}
    _send_request(_SERVICE, 'TranslateData', params)


# =============================================================================
# ---Result, Attribute, and Control Getter Methods
# =============================================================================
def get_attribute_bool(path):
    """Get the boolean value of the specified attribute.

    Parameters
    ----------
    path : tuple of str
        Path to the attribute.

    Returns
    -------
    bool
        The attribute value.
    """
    params = {'path': path, 'uid': _get_uid()}
    return _get_send_request(_SERVICE, 'GetAttributeBool', params)


def get_attribute_number(path, unit=None):
    """Get the numeric value of the specified attribute.

    Parameters
    ----------
    path : tuple of str
        Path to the attribute.
    unit : units.Units, optional
        Desired units for the returned value (the default is None, which is
        equivalent to units.Units.NoUnits and is appropriate for unitless
        numbers).

    Returns
    -------
    float
        The attribute value in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'path': path, 'units': unit_str, 'uid': _get_uid()}
    return _get_send_request(_SERVICE, 'GetAttributeNumber', params)


def get_attribute_string(path):
    """Get the string value of the specified attribute.

    Parameters
    ----------
    path : tuple of str
        Path to the attribute.

    Returns
    -------
    str
        The attribute value.
    """
    params = {'path': path, 'uid': _get_uid()}
    return _get_send_request(_SERVICE, 'GetAttributeString', params)


def get_control_bool(path):
    """Get the boolean value of the specified control.

    Parameters
    ----------
    path : tuple of str
        Path to the control.

    Returns
    -------
    bool
        The control value.
    """
    params = {'path': path}
    return _get_send_request(_SERVICE, 'GetControlBool', params)


def get_control_number(path, unit=None):
    """Get the numeric value of the specified control.

    Parameters
    ----------
    path : tuple of str
        Path to the control.
    unit : units.Units, optional
        Desired units for the returned value (the default is None, which is
        equivalent to units.Units.NoUnits and is appropriate for unitless
        numbers).

    Returns
    -------
    float
        The control value in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'path': path, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetControlNumber', params)


def get_control_string(path):
    """Get the string value of the specified control.

    Parameters
    ----------
    path : tuple of str
        Path to the control.

    Returns
    -------
    str
        The control value.
    """
    params = {'path': path}
    return _get_send_request(_SERVICE, 'GetControlString', params)


def get_result_bool(path):
    """Get the boolean value of the specified result.

    Parameters
    ----------
    path : tuple of str
        Path to the result.

    Returns
    -------
    bool
        The result value.
    """
    params = {'path': path}
    return _get_send_request(_SERVICE, 'GetResultBool', params)


def get_result_number(path, unit=None):
    """Get the numeric value of the specified result.

    Parameters
    ----------
    path : tuple of str
        Path to the result.
    unit : units.Units, optional
        Desired units for the returned value (the default is None, which is
        equivalent to units.Units.NoUnits and is appropriate for unitless
        numbers).

    Returns
    -------
    float
        The result value in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'path': path, 'units': unit_str, 'uid': _get_uid()}
    return _get_send_request(_SERVICE, 'GetResultNumber', params)


def get_result_string(path):
    """Get the string value of the specified result.

    Parameters
    ----------
    path : tuple of str
        Path to the result.

    Returns
    -------
    str
        The result value.
    """
    params = {'path': path, 'uid': _get_uid()}
    return _get_send_request(_SERVICE, 'GetResultString', params)


# =============================================================================
# ---Result, Attribute, and Control Setter Methods
# =============================================================================
def set_control_bool(path, value):
    """Set the boolean value of the specified control.

    Parameters
    ----------
    path : tuple of str
        Path to the control.
    value : bool
        The control value to set.
    """
    params = {'path': path, 'value': value}
    _send_request(_SERVICE, 'SetControlBool', params)


def set_control_number(path, value, unit=None):
    """Set the numeric value of the specified control.

    Parameters
    ----------
    path : tuple of str
        Path to the control.
    value : float
        The control value to set in the specified units.
    unit : units.Units, optional
        Specified units for the value to set (the default is None, which is
        equivalent to units.Units.NoUnits and is appropriate for unitless
        numbers).
    """
    unit_str = _validate_unit(unit)
    params = {'path': path, 'numberValue': value, 'units': unit_str}
    _send_request(_SERVICE, 'SetControlNumber', params)


def set_control_string(path, value):
    """Set the string value of the specified control.

    Parameters
    ----------
    path : tuple of str
        Path to the control.
    value : str
        The control value to set.
    """
    params = {'path': path, 'stringValue': value}
    _send_request(_SERVICE, 'SetControlString', params)


def set_result_bool(path, value):
    """Set the boolean value of the specified result.

    This function will only operate on Mx custom results.

    Parameters
    ----------
    path : tuple of str
        Path to the result.
    value : bool
        The result value to set.
    """
    params = {'path': path, 'value': value}
    _send_request(_SERVICE, 'SetResultBool', params)


def set_result_number(path, value, unit=None):
    """Set the numeric value of the specified result.

    This function will only operate on Mx custom results.

    Parameters
    ----------
    path : tuple of str
        Path to the result.
    value : float
        The result value to set in the specified units.
    unit : units.Units, optional
        Specified units for the value to set (the default is None, which is
        equivalent to units.Units.NoUnits and is appropriate for unitless
        numbers).
    """
    unit_str = _validate_unit(unit)
    params = {'path': path, 'numberValue': value, 'units': unit_str}
    _send_request(_SERVICE, 'SetResultNumber', params)


def set_result_string(path, value):
    """Set the string value of the specified result.

    This function will only operate on Mx custom results.

    Parameters
    ----------
    path : tuple of str
        Path to the result.
    value : str
        The result value to set.
    """
    params = {'path': path, 'stringValue': value}
    _send_request(_SERVICE, 'SetResultString', params)


def set_bulk_control_string(paths_and_values):
    """Set the values associated with the specified string controls.

    Parameters
    ----------
    paths_and_values : list of tuple
        A list of control paths and their corresponding values as (path, value)
        tuples;

    """
    param_list = [
        {'m_Item1': p, 'm_Item2': u}
        for p, u in paths_and_values]
    params = {'pathAndValueList': param_list}
    return _send_request(_SERVICE, 'SetBulkControlString', params)


# =============================================================================
# ---Miscellaneous Results Methods
# =============================================================================
def clear_process_stats():
    """Clear process stats."""
    _send_request(_SERVICE, 'ClearProcessStatistics')


def store_process_stats():
    """Store process stats.

    This will cause Mx to sample the current data and add a new row to process
    stats.
    """
    _send_request(_SERVICE, 'StoreProcessStatistics')


def clear_custom_result(path):
    """Clears the specified custom result.

    Parameters
    ----------
    path : tuple of str
        The path to the custom result to clear.
    """
    _send_request(_SERVICE, 'ClearCustomResult', {'path': path})


def set_tolerance(path, is_on=True, low="", high="", unit=_Units.NotSet):
    """Set a result or custom result limits.

    Parameters
    ----------
    path : tuple of str
        Path to the result.
    is_on : bool, optional
        True to turn limits monitoring ON; False to turn OFF.
    low : float, optional
        The low limit value.
    high : float, optional
        The high limit value.
    unit : units.Units
        The unit of the low and high values.

    Notes
    -----
    Leaving `low` or `high` as the default value will cause the parameter to be
    ignored, which is useful for setting individual low or high limits.

    Setting `low` or `high` to None will clear the respective limit.
    """
    params = {'path': path,
              'isOn': is_on,
              'low': str(low),
              'high': str(high),
              'units': _validate_unit(unit)}
    _send_request(_SERVICE, 'SetLimits', params)


def get_tolerance(path, unit=_Units.NotSet):
    """Get a result or custom result limit value.

    Parameters
    ----------
    path : tuple of str
        Path to the result.

    Returns
    -------
    dict
        Limits dictionary for the specified result. This dictionary contains
        three keys: 'is_on', 'low', and 'high', which correspond to the same
        three parameters in `set_tolerance`.

    See Also
    --------
    set_tolerance
    """
    params = {'path': path, 'units': _validate_unit(unit)}
    return _get_send_request(_SERVICE, 'GetLimits', params)


def get_tolerance_pass_fail():
    """Get the global tolerance Pass/Fail state.

    Returns
    -------
    bool
        True if no failures; False otherwise.
    """
    return _get_send_request(_SERVICE, 'GetTolerancePassFail')


def is_tolerance_enabled():
    """Gets whether or not the tolerance tool is enabled.

    Returns
    -------
    bool
        True if the tolerance tool is enabled; False otherwise.
    """
    return _get_send_request(_SERVICE, 'IsToleranceEnabled')


def log_reports():
    """Trigger reports to run, if configured."""
    _send_request(_SERVICE, 'LogReports')


def _get_selection_control_items(path):
    """Get a list of items in the specified selection control.

    Parameters
    ----------
    path : tuple of str
        Path to the selection control.

    Returns
    -------
    list of str
        Items in the selection control.
    """
    params = {'path': path}
    return _get_send_request(_SERVICE, 'GetSelectionControlItems', params)


def get_bulk_attribute_values(paths_and_units):
    """Get the values associated with the specified attributes.

    Parameters
    ----------
    paths_and_units : list of tuple
        A list of attribute paths and their corresponding units as (path, unit)
        tuples; Set units to None when the attribute is not a unit number.

    Returns
    -------
    list of str
        List of requested attribute values as strings, in the order they were
        requested.
    """
    param_list = [
        {'m_Item1': p, 'm_Item2': _validate_unit(u)}
        for p, u in paths_and_units]
    params = {'pathAndUnitsList': param_list}
    return _get_send_request(_SERVICE, 'GetBulkAttributeValues', params)


def get_bulk_control_values(paths_and_units):
    """Get the values associated with the specified controls.

    Parameters
    ----------
    paths_and_units : list of tuple
        A list of control paths and their corresponding units as (path, unit)
        tuples; Set units to None when the control is not a unit number.

    Returns
    -------
    list of str
        List of requested control values as strings, in the order they were
        requested.
    """
    param_list = [
        {'m_Item1': p, 'm_Item2': _validate_unit(u)}
        for p, u in paths_and_units]
    params = {'pathAndUnitsList': param_list}
    return _get_send_request(_SERVICE, 'GetBulkControlValues', params)


def get_bulk_result_values(paths_and_units):
    """Get the values associated with the specified results.

    Parameters
    ----------
    paths_and_units : list of tuple
        A list of result paths and their corresponding units as (path, unit)
        tuples; Set units to None when the result is not a unit number.

    Returns
    -------
    list of str
        List of requested result values as strings, in the order they were
        requested.
    """
    param_list = [
        {'m_Item1': p, 'm_Item2': _validate_unit(u)}
        for p, u in paths_and_units]
    params = {'pathAndUnitsList': param_list}
    return _get_send_request(_SERVICE, 'GetBulkResultValues', params)


# =============================================================================
# ---Annotations Grid Methods
# =============================================================================
def create_annotation(name, value):
    """Create a new Mx annotation.

    Parameters
    ----------
    name : str
        The name of the new annotation to create.
    value : str
        The value of the new annotation.
    """
    params = {'annotationLabel': name, 'annotationValue': value}
    _send_request(_SERVICE, 'CreateAnnotation', params)


def delete_annotation(path):
    """Delete an Mx annotation.

    Parameters
    ----------
    path : tuple of str
        The path to the annotation.
    """
    params = {'path': path}
    _send_request(_SERVICE, 'DeleteAnnotation', params)


def get_annotation(path):
    """Gets the string value associated with the specified Mx annotation.

    Parameters
    ----------
    path :
        The path to the annotation.

    Returns
    -------
    str
        The value of the specified Mx annotation.
    """
    params = {'path': path}
    return _get_send_request(_SERVICE, 'GetAnnotation', params)


def set_annotation(path, value):
    """Modify an existing Mx annotation.

    Parameters
    ----------
    path : tuple of str
        The path to the annotation.
    value : str
        The new value for the specified annotation.
    """
    params = {'path': path, 'value': value}
    _send_request(_SERVICE, 'SetAnnotation', params)


# =============================================================================
# ---Data Matrix Methods
# =============================================================================
def get_data_center_x(control, unit):
    """Retrieves the x-coordinate of the geometric center of the specified plot
    control.

    Parameters
    ----------
    control : ui.Control
        The plot control to query.
    unit : units.Units
        The desired unit for the returned coordinate value.

    Returns
    -------
    float
        The center x-coordinate of the specified plot in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'controlId': control._id, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetDataCenterX', params)


def get_data_center_y(control, unit):
    """Retrieves the y-coordinate of the geometric center of the specified plot
    control.

    Parameters
    ----------
    control : ui.Control
        The plot control to query.
    unit : units.Units
        The desired unit for the returned coordinate value.

    Returns
    -------
    float
        The center y-coordinate of the specified plot in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'controlId': control._id, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetDataCenterY', params)


def get_data_origin_x(control, unit):
    """Retrieves the x-coordinate of the geometric origin of the specified plot
    control.

    Parameters
    ----------
    control : ui.Control
        The plot control to query.
    unit : units.Units
        The desired unit for the returned coordinate value.

    Returns
    -------
    float
        The origin x-coordinate of the specified plot in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'controlId': control._id, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetDataOriginX', params)


def get_data_origin_y(control, unit):
    """Retrieves the y-coordinate of the geometric origin of the specified plot
    control.

    Parameters
    ----------
    control : ui.Control
        The plot control to query.
    unit : units.Units
        The desired unit for the returned coordinate value.

    Returns
    -------
    float
        The origin y-coordinate of the specified plot in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'controlId': control._id, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetDataOriginY', params)


def get_data_size_x(control, unit):
    """Retrieves the width of the specified plot control.

    Parameters
    ----------
    control : ui.Control
        The plot control to query.
    unit : units.Units
        The desired unit for the returned plot width.

    Returns
    -------
    float
        The width of the specified plot in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'controlId': control._id, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetDataSizeX', params)


def get_data_size_y(control, unit):
    """Retrieves the height of the specified plot control.

    Parameters
    ----------
    control : ui.Control
        The plot control to query.
    unit : units.Units
        The desired unit for the returned plot height.

    Returns
    -------
    float
        The height of the specified plot in the requested units.
    """
    unit_str = _validate_unit(unit)
    params = {'controlId': control._id, 'units': unit_str}
    return _get_send_request(_SERVICE, 'GetDataSizeY', params)


# =============================================================================
# Processing Sequence Methods
# =============================================================================
def get_sequence_step_status(path):
    """Get the on/off state of the specified sequence step.

    Parameters
    ----------
    path : tuple of str
        Path to the sequence step.

    Returns
    -------
    bool
        True if the specified step is on; False otherwise.
    """
    params = {'path': path}
    return _get_send_request(_SERVICE, 'GetSequenceStepStatus', params)


def set_sequence_step_status(path, value):
    """Set the specified sequence step state to on or off.

    Parameters
    ----------
    path : tuple of str
        Path to the sequence step.
    value : bool
        True to turn the specified step on, or False to turn off.
    """
    params = {'path': path, 'value': value}
    _send_request(_SERVICE, 'SetSequenceStepStatus', params)


# =============================================================================
# Logging Methods
# =============================================================================
def log_trace(message):
    """Log a message at the TRACE level to the Mx system log.

    Parameters
    ----------
    message : str
        The message to write to the system log.
    """
    _send_request(_SERVICE, 'LogTrace', {'message': message})


def log_debug(message):
    """Log a message at the DEBUG level to the Mx system log.

    Parameters
    ----------
    message : str
        The message to write to the system log.
    """
    _send_request(_SERVICE, 'LogDebug', {'message': message})


def log_info(message):
    """Log a message at the INFO level to the Mx system log.

    Parameters
    ----------
    message : str
        The message to write to the system log.
    """
    _send_request(_SERVICE, 'LogInfo', {'message': message})


def log_warn(message):
    """Log a message at the WARN level to the Mx system log.

    Parameters
    ----------
    message : str
        The message to write to the system log.
    """
    _send_request(_SERVICE, 'LogWarn', {'message': message})


def log_error(message):
    """Log a message at the ERROR level to the Mx system log.

    Parameters
    ----------
    message : str
        The message to write to the system log.
    """
    _send_request(_SERVICE, 'LogError', {'message': message})


def log_fatal(message):
    """Log a message at the FATAL level to the Mx system log.

    Parameters
    ----------
    message : str
        The message to write to the system log.
    """
    _send_request(_SERVICE, 'LogFatal', {'message': message})


# =============================================================================
# ---Miscellaneous Methods
# =============================================================================
def get_mx_version():
    """Get the Mx version number.

    Returns
    -------
    str
        The Mx version as a string.
    """
    return _get_send_request(_SERVICE, 'GetMxVersion')


def clear_script_console():
    """Clear the Mx scripting console/output window.
    """
    return _send_request(_SERVICE, 'ClearScriptConsole')


def run_script(script_path, command_line_args=''):
    """Run the specified script through Mx.

    Parameters
    ----------
    script_path : str
        Path to the script to execute. This script must exist on the host
        Mx machine.
        """
    params = {'fileName': script_path,
              'commandLineArguments': command_line_args,
              'uid': ''}
    _send_request(_SERVICE, 'RunScriptWithArgs', params)


def _get_plot_image_stream(control):
    """Get the plot control image, in PNG format, as a binary sequence.

    Parameters
    ----------
    control : tuple of str
        The plot control to save from.

    Returns
    -------
    bytes
        The plot control image as a bytes object.
    """
    params = {'controlId': control._id}
    return _send_request(_SERVICE,
                         'GetPlotImageStream',
                         params,
                         decode=False)


def _get_native_image_stream(control, sub_sample=1):
    """Get the full-resolution plot image, in PNG format, as a binary sequence.

    Parameters
    ----------
    control : tuple of str
        The plot control to save from.
    sub_sample : int
        The subsample value.

    Returns
    -------
    bytes
        The full-resolution plot control image as a bytes object.
    """
    if not isinstance(sub_sample, int):
        raise TypeError('sub_sample must be an integer.')
    params = {'controlId': control._id, 'subSample': sub_sample}
    return _send_request(_SERVICE,
                         'GetNativeImageStream',
                         params,
                         decode=False)


def _get_configured_plot_output_strings(control):
    """Get the list of configured result, attribute, and annotation output
    strings as displayed on the plot.

    Parameters
    ----------
    control : tuple of str
        The plot control to query.

    Returns
    -------
    list of str
        The list of configured plot output strings.
    """
    params = {'controlId': control._id}
    return _get_send_request(_SERVICE,
                             'GetConfiguredPlotOutputStrings',
                             params)


def _get_configured_plot_output_part_strings(control):
    """Get the list of configured result, attribute, and annotation output
    strings as displayed on the plot, separated into name, value, and unit
    components.

    Parameters
    ----------
    control : tuple of str
        The plot control to query.

    Returns
    -------
    list of dict
        A list of configured plot output strings. Each plot output is contained
        in an individual dictionary with entries for the name, value, and unit
        of the output.
    """
    params = {'controlId': control._id}
    res = _get_send_request(_SERVICE,
                            'GetConfiguredPlotOutputPartStrings',
                            params)
    part_map = {'m_Item1': 'name', 'm_Item2': 'value', 'm_Item3': 'unit'}
    retval = [{part_map[k]: v for k, v in output.items()} for output in res]
    return retval

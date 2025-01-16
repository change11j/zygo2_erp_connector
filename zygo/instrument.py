# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Support Mx instrument functionality.
"""
from enum import IntEnum as _IntEnum

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.connectionmanager import get_uid as _get_uid
from zygo.core import ZygoTask as _ZygoTask
from zygo import units as _units

_SERVICE = 'InstrumentService'
"""str: The service name for the instrument module."""
_MSEC = _units.Units.MilliSeconds
"""units.Units: Internal alias for the MilliSeconds unit."""


# =============================================================================
# ---Internal Support Methods
# =============================================================================
def _frame_grab_async_wait(task_id, timeout):
    """Wait for the asynchronous frame grab task to complete.

    Parameters
    ----------
    task_id : str
        Unique task identifier.
    timeout : int
        Maximum time to wait in milliseconds, None for infinite.
    """
    if timeout is None:
        timeout = -1  # Mx treats negative value as infinite
    param_timeout = {'m_Item1': timeout, 'm_Item2': _MSEC.name}
    params = {'taskId': task_id, 'timeout': param_timeout}
    _send_request(_SERVICE, 'WaitForFrameGrabComplete', params)


def _frame_grab_async_done(task_id):
    """Get the completion status of the asynchronous frame grab task.

    Parameters
    ----------
    task_id : str
        Unique task identifier.

    Returns
    -------
    bool
        True if the task is complete; False otherwise.
    """
    params = {'taskId': task_id}
    return _get_send_request(_SERVICE, 'IsFrameGrabComplete', params)


def _acquire_async_wait(task_id, timeout):
    """Wait for the asynchronous acquire task to complete.

    Parameters
    ----------
    task_id : str
        Unique task identifier.
    timeout : int
        Maximum time to wait in milliseconds, None for infinite.
    """
    if timeout is None:
        timeout = -1  # Mx treats negative value as infinite
    param_timeout = {'m_Item1': timeout, 'm_Item2': _MSEC.name}
    params = {'taskId': task_id, 'timeout': param_timeout}
    _send_request(_SERVICE, 'WaitForAcquisitionComplete', params)


def _acquire_async_done(task_id):
    """Get the completion status of the asynchronous acquire task.

    Parameters
    ----------
    task_id : str
        Unique task identifier.

    Returns
    -------
    bool
        True if the task is complete; False otherwise.
    """
    params = {'taskId': task_id}
    return _get_send_request(_SERVICE, 'IsAcquisitionComplete', params)


def _measure_async_wait(task_id, timeout):
    """Wait for the asynchronous measure task to complete.

    Parameters
    ----------
    task_id : str
        Unique task identifier.
    timeout : int
        Maximum time to wait in milliseconds, None for infinite.
    """
    if timeout is None:
        timeout = -1  # Mx treats negative value as infinite
    param_timeout = {'m_Item1': timeout, 'm_Item2': _MSEC.name}
    params = {'taskId': task_id, 'timeout': param_timeout}
    _send_request(_SERVICE, 'WaitForMeasureComplete', params)


def _measure_async_done(task_id):
    """Get the completion status of the asynchronous measure task.

    Parameters
    ----------
    task_id : str
        Unique task identifier.

    Returns
    -------
    bool
        True if the task is complete; False otherwise.
    """
    params = {'taskId': task_id}
    return _get_send_request(_SERVICE, 'IsMeasureComplete', params)


def _validate_alignview_mode(alignview_mode):
    """Validate input as a valid Align/View mode value.

    Parameters
    ----------
    alignment_type : AlignViewMode or str
        Align/View mode to validate.

    Returns
    -------
    str
        String representation of the specified Align/View mode.

    Raises
    ------
    TypeError
        If the input is not an AlignViewMode or str type.
    ValueError
        If the input string is not convertable to an AlignViewMode member.
    """
    if isinstance(alignview_mode, AlignViewMode):
        return alignview_mode.name
    if isinstance(alignview_mode, str):
        for mode in AlignViewMode.__members__:
            if alignview_mode.lower() == mode.lower():
                return mode
        raise ValueError(
            'alignview_mode string not a valid "AlignViewMode" member')
    raise TypeError(
        'alignview_mode must be of type "AlignViewMode" '
        'or string with valid value')


def _validate_ringspot_mode(ringspot_mode):
    """Validate input as a valid Ring/Spot mode value.

    Parameters
    ----------
    ringspot_mode : RingSpotMode or str
        Ring/Spot mode to validate.

    Returns
    -------
    str
        String representation of the specified Ring/Spot mode.

    Raises
    ------
    TypeError
        If the input is not a RingSpotMode or str type.
    ValueError
        If the input string is not convertable to an RingSpotMode member.
    """
    if isinstance(ringspot_mode, RingSpotMode):
        return ringspot_mode.name
    if isinstance(ringspot_mode, str):
        for mode in RingSpotMode.__members__:
            if ringspot_mode.lower() == mode.lower():
                return mode
        raise ValueError(
            'ringspot_mode string not a valid "RingSpotMode" member')
    raise TypeError(
        'ringspot_mode must be of type "RingSpotMode" '
        'or string with valid value')


# =============================================================================
# ---Instrument Acquisition
# =============================================================================
class AcquisitionTask(object):
    """Represents information pertaining to an asynchronous acquisition
    operation.

    Parameters
    ----------
    task_id : str
        Unique task identifier.
    """
    def __init__(self, task_id):
        """Initialize task.

        Parameters
        ----------
        task_id : str
            Unique task identifier.
        """
        self._task_id = task_id
        self._frame_grab_task = _ZygoTask(
            task_id, _frame_grab_async_done, _frame_grab_async_wait)
        self._acquire_task = _ZygoTask(
            task_id, _acquire_async_done, _acquire_async_wait)
        self._measure_task = _ZygoTask(
            task_id, _measure_async_done, _measure_async_wait)

    @property
    def frame_grab_task(self):
        """core.ZygoTask : The task that checks for frame grab complete."""
        return self._frame_grab_task

    @property
    def acquire_task(self):
        """core.ZygoTask : The task that checks for acquire complete."""
        return self._acquire_task

    @property
    def measure_task(self):
        """core.ZygoTask : The task that checks for measure complete."""
        return self._measure_task


def acquire(wait=True):
    """Acquire data on the host instrument.

    This performs a full acquisition but does not trigger an Mx Analyze.

    Parameters
    ----------
    wait : bool
        True to wait for acquisition to complete; False for asynchronous
        acquisition.

    Returns
    -------
    AcquisitionTask
        The unique task object for this acquisition.
    """
    params = {'wait': wait}
    task_id = _get_send_request(_SERVICE, 'Acquire', params)
    return AcquisitionTask(task_id)


def measure(wait=True):
    """Measure data on the host instrument.

    This is the equivalent of an acquire followed by an analyze.

    Parameters
    ----------
    wait : bool
        True to wait for measurement to complete; False for asynchronous
        measurement.

    Returns
    -------
    AcquisitionTask
        The unique task object for this measurement.
    """
    params = {'wait': wait, 'uid': _get_uid()}
    task_id = _get_send_request(_SERVICE, 'Measure', params)
    return AcquisitionTask(task_id)


# =============================================================================
# ---Optimization Methods
# =============================================================================
def auto_focus():
    """Perform auto focus on the host instrument."""
    _send_request(_SERVICE, 'AutoFocus')


def auto_tilt():
    """Perform auto tilt on the host instrument."""
    _send_request(_SERVICE, 'AutoTilt')


def auto_focus_tilt():
    """Perform auto focus and then auto tilt on the host instrument."""
    _send_request(_SERVICE, 'AutoFocusTilt')


def auto_light_level():
    """Perform auto light level on the host instrument."""
    _send_request(_SERVICE, 'AutoLightLevel')


def auto_lat_cal(value, unit):
    """Perform auto lateral calibration.

    Parameters
    ----------
    value : float
        Numeric value of the size of the calibration artifact
    unit : units.Units
        Mx unit corresponding to the value parameter.
    """
    unit_str = _units._validate_unit(unit)
    params = {'length': value, 'units': unit_str}
    _send_request(_SERVICE, 'AutoLateralCalibration', params)


def perform_wavelength_scan_cal(force_run=False):
    """Begins a single Wavelength Scan Calibration.

    Parameters
    ----------
    force_run : bool, optional
        True to ignore aperture settings and force the command to run.

    Returns
    -------
    str
        The command's last status message.
    """
    params = {'forceRun': force_run}
    return _get_send_request(_SERVICE, 'PerformWavelengthScanCal', params)


def auto_center():
    """Performs an auto center acquisition, if available and configured."""
    _send_request(_SERVICE, 'AutoCenter')


def find_part():
    """Runs part finder."""
    _send_request(_SERVICE, 'FindPart')


def smart_setup():
    """Runs smart setup."""
    params = {'uid': _get_uid()}
    _send_request(_SERVICE, 'SmartSetup', params)


# =============================================================================
# ---Turret Methods
# =============================================================================
def get_turret():
    """Get the current turret position on the host instrument.

    Returns
    -------
    int
        The current turret position.
    """
    return _get_send_request(_SERVICE, 'GetTurret')


def move_turret(position):
    """Move the turret to specified position on the host instrument.

    Parameters
    ----------
    position : int
        The target turret position.
    """
    params = {'position': position}
    _send_request(_SERVICE, 'MoveTurret', params)


# =============================================================================
# ---Zoom Methods
# =============================================================================
def get_zoom():
    """Get the current zoom value on the host instrument.


    Returns
    -------
    float
        The current zoom value.
    """
    return _get_send_request(_SERVICE, 'GetZoom')


def set_zoom(zoom):
    """Set zoom to the specified value on the host instrument.

    Parameters
    ----------
    zoom : float
        The target zoom value.
    """
    params = {'zoom': zoom}
    _send_request(_SERVICE, 'SetZoom', params)


def get_min_zoom():
    """Get the minimum zoom value allowable on the host instrument.


    Returns
    -------
    float
        The minimum allowable zoom value.
    """
    return _get_send_request(_SERVICE, 'GetMinimumZoom')


def get_max_zoom():
    """Get the maximum zoom value allowable on the host instrument.


    Returns
    -------
    float
        The maximum allowable zoom value.
    """
    return _get_send_request(_SERVICE, 'GetMaximumZoom')


def lock_zoom():
    """Lock zoom on the host instrument."""
    _send_request(_SERVICE, 'LockZoom')


def unlock_zoom():
    """Unlock zoom on the host instrument."""
    _send_request(_SERVICE, 'UnlockZoom')

# =============================================================================
# ---Encoded Focus Methods
# =============================================================================
def get_encoded_focus():
    """Gets current encoded focus position as a string.


    Returns
    -------
    str
        The current encoded focus position.
    """
    return _get_send_request(_SERVICE, 'GetEncodedFocus')

def set_encoded_focus(focus):
    """Set encoded focus to the specified position on the host instrument.

    Parameters
    ----------
    focus : str
        The target focus position.
    """
    params = {'focus': focus}
    _send_request(_SERVICE, 'SetEncodedFocus', params)

def lock_encoded_focus():
    """Lock encoded focus on the host instrument."""
    _send_request(_SERVICE, 'LockEncodedFocus')

def unlock_encoded_focus():
    """Unlock encoded focus on the host instrument."""
    _send_request(_SERVICE, 'UnlockEncodedFocus')


def get_encoded_focus_positions():
    """Gets the current list of saved encoded focus positions.

    Returns
    -------
    list of str
        The list of currently saved encoded focus positions.
    """
    return _get_send_request(_SERVICE, 'GetEncodedFocusPositions')

def get_encoded_focus_counts():
    """Gets the current encoded focus position.

    Returns
    -------
    int
        The current motor position in motor counts.
    """
    return _get_send_request(_SERVICE, 'GetEncodedFocusCounts')

def set_encoded_focus_counts(counts):
    """Sets the current encoded focus position.

    Parameters
    ----------
    counts : int
        The target position in motor counts.
    """
    params = {'motorCounts': counts}
    _send_request(_SERVICE, 'SetEncodedFocusCounts', params)

# =============================================================================
# ---Light Level Methods
# =============================================================================
def get_light_level():
    """Get the current light level on the host instrument.

    Returns
    -------
    float
        The current light level as a percentage.
    """
    return _get_send_request(_SERVICE, 'GetLightLevel')


def set_light_level(light_level):
    """Set light to the specified level on the host instrument.

    Parameters
    ----------
    light_level : float
        Target light level as a percentage.
    """
    params = {'lightLevel': light_level}
    _send_request(_SERVICE, 'SetLightLevel', params)


# =============================================================================
# ---Wand Methods
# =============================================================================
def is_wand_enabled():
    """Get whether or not the wand is enabled.

    Returns
    -------
    bool
        True if the wand is enabled; False otherwise.
    """
    return _get_send_request(_SERVICE, 'IsWandEnabled')


def set_wand_enabled(enabled):
    """Enable or disable the wand on the host instrument.

    Parameters
    ----------
    enabled : bool
        True to enable the wand; False otherwise.
    """
    params = {'enabled': enabled}
    _send_request(_SERVICE, 'SetWandEnabled', params)


# =============================================================================
# ---Align/View Mode
# =============================================================================
class AlignViewMode(_IntEnum):
    """Align/View mode of the host instrument."""
    none = 0  # Unknown or invalid
    align = 1
    view = 2


def get_align_view_mode():
    """Get the current align/view mode of the host instrument.

    Returns
    -------
    AlignViewMode
        The current align/view mode.
    """
    return AlignViewMode(_get_send_request(_SERVICE, 'GetAlignViewMode'))


def set_align_view_mode(mode):
    """Set the align/view mode of the host instrument.

    Parameters
    ----------
    mode : AlignViewMode
        The align/view mode to set.
    """
    params = {'mode': AlignViewMode[_validate_alignview_mode(mode)].value}
    _send_request(_SERVICE, 'SetAlignViewMode', params)


# =============================================================================
# ---Ring/Spot Mode
# =============================================================================
class RingSpotMode(_IntEnum):
    """Ring/spot mode of the host instrument."""
    none = 0  # Unknown or invalid
    ring = 1
    spot = 2


def get_ring_spot_mode():
    """Get the current ring/spot mode of the host instrument.

    Returns
    -------
    RingSpotMode
        The current ring/spot mode.
    """
    return RingSpotMode(_get_send_request(_SERVICE, 'GetRingSpotMode'))


def set_ring_spot_mode(mode):
    """Set the ring/spot mode on the host instrument.

    Parameters
    ----------
    mode : RingSpotMode
        The ring/spot mode to set.
    """
    params = {'mode': RingSpotMode[_validate_ringspot_mode(mode)].value}
    _send_request(_SERVICE, 'SetRingSpotMode', params)


# =============================================================================
# ---Camera Information Methods
# =============================================================================
def get_cam_res(unit):
    """Returns the camera resolution in the specified unit. If there is valid
       measured or loaded data, the returned value is the lateral resolution
       of the data. Otherwise, the current camera resolution of the active
       instrument is returned.

    Parameters
    ----------
    unit : units.Units
        Desired Mx unit for the return value.

    Returns
    -------
    float
        The lateral resolution in the requested units.
    """
    unit_str = _units._validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetCameraResolution', params)


def get_cam_size_x(unit):
    """Gets the camera width in the specified unit. If there is valid measured
       or loaded data, the returned value is the effective width of an image
       from the camera used to measure the data. Otherwise, if there is an
       active instrument, the value returned is the effective width of an image
       from the camera with the current configuration.

    Parameters
    ----------
    unit : units.Units
        Desired Mx unit for the return value.

    Returns
    -------
    float
        The camera width in the requested units.
    """
    unit_str = _units._validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetCameraSizeX', params)


def get_cam_size_y(unit):
    """Gets the camera height in the specified unit. If there is valid measured
       or loaded data, the returned value is the effective height of an image
       from the camera used to measure the data. Otherwise, if there is an
       active instrument, the value returned is the effective height of an
       image from the camera with the current configuration.

    Parameters
    ----------
    unit : units.Units
        Desired Mx units for the return value.

    Returns
    -------
    float
        The camera height in the requested units.
    """
    unit_str = _units._validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetCameraSizeY', params)


# =============================================================================
# ---Instrument Hardware Methods
# =============================================================================
def get_system_serial_number():
    """Get the system serial number.

    Returns
    -------
    str
        The system serial number; empty string if no instrument.
    """
    return _get_send_request(_SERVICE, 'GetSystemSerialNumber')


def get_system_type():
    """Get the current system type.

    Returns
    -------
    str
        The string representation of the current system type.
    """
    return _get_send_request(_SERVICE, 'GetSystemType')


def set_sleep_mode_enabled(enabled):
    """Enable/Disable sleep mode on the host instrument.

    Parameters
    ----------
    enabled : bool
        True to enable the instrument to sleep; False to prevent sleeping.
    """
    params = {'enabled': enabled, 'uid': _get_uid()}
    _send_request(_SERVICE, 'SetSleepModeEnabled', params)

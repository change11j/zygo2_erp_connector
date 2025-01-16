# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx motion functionality.
"""
from enum import IntEnum as _IntEnum

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.core import ZygoTask as _ZygoTask
from zygo import units as _units


_SERVICE = 'MotionService'
"""str: The service name for the motion module."""


# =============================================================================
# ---Enumerations
# =============================================================================
class AxisType(_IntEnum):
    """Axis names."""
    unknown = 0
    x = 1
    y = 2
    z = 3
    rx = 4  # Pitch, rotation about x-axis
    ry = 5  # Roll, rotation about y-axis
    rz = 6  # Theta, rotation about z-axis
    x2 = 7  # Secondary x-axis
    y2 = 8  # Secondary y-axis
    z2 = 9  # Secondary z-axis
    rx2 = 10  # Secondary Pitch, rotation about secondary x-axis
    ry2 = 11  # Secondary Roll, rotation about secondary y-axis
    rz2 = 12  # Secondary Theta, rotation about secondary z-axis


def _validate_axis(axis):
    """Validate input as a valid axis type value.

    Parameters
    ----------
    axis : AxisType or str
        Axis type to validate.

    Returns
    -------
    str
        String representation of the specified axis type.

    Raises
    ------
    TypeError
        If the input is not a AxisType or str type.
    ValueError
        If the input string is not convertable to a AxisType member.
    """
    if isinstance(axis, AxisType):
        return axis.name
    if isinstance(axis, str):
        for axis_type in AxisType.__members__:
            if axis.lower() == axis_type.lower():
                return axis_type
        raise ValueError('`axis` string is not a valid `AxisType` member.')
    raise TypeError('`axis` must be of type `AxisType` or valid string value.')


class StageType(_IntEnum):
    """Stage names."""
    stage_all = 0
    stage1 = 1
    stage2 = 2


def _validate_stage(stage):
    """Validate input as a valid stage type value.

    Parameters
    ----------
    stage : StageType or str
        Stage type to validate.

    Returns
    -------
    str
        String representation of the specified stage type.

    Raises
    ------
    TypeError
        If the input is not a StageType or str type.
    ValueError
        If the input string is not convertable to a StageType member.
    """
    if isinstance(stage, StageType):
        return stage.name
    if isinstance(stage, str):
        for stage_type in StageType.__members__:
            if stage.lower() == stage_type.lower():
                return stage_type
        raise ValueError('`stage` string is not a valid `StageType` member.')
    raise TypeError(
        '`stage` must be of type `StageType` or valid string value.')


# =============================================================================
# ---Retrieve Current Axes Positions
# =============================================================================
def get_positions_ex(axes_unit_dict):
    """Retrieve positions of the requested axes in the specified units.

    Parameters
    ----------
    axes_unit_dict : dict
        Dictionary of AxisType keys to units.Units values.

    Returns
    -------
    dict
        Dictionary of AxisType keys to positions as (value, units.Units)
        tuples.

    Notes
    -----
    This function has been superseded by the simplified position commands
    specified in the official documentation. It has been kept for backward
    compatibility and internal use and should not be called by new user code.

    See Also
    --------
    get_x_pos, get_y_pos, get_z_pos, get_r_pos, get_p_pos, get_t_pos
    """
    if not isinstance(axes_unit_dict, dict):
        raise TypeError('`axes_unit_dict` is not a valid dictionary')
    params_list = []
    for k, v in axes_unit_dict.items():
        params_list.append({'m_Item1': _validate_axis(k),
                            'm_Item2': _units._validate_unit(v)})
    params = {'axes': params_list}
    axes_pos = _get_send_request(_SERVICE, 'GetPositions', params)
    return {AxisType[_validate_axis(pos['m_Item1'])]:
            (pos['m_Item2'],
             _units.Units[_units._validate_unit(pos['m_Item3'])])
            for pos in axes_pos}


def get_positions(axes, unit):
    """Retrieve positions of the requested axes in the requested unit.

    Parameters
    ----------
    axes : list of AxisType
        List of axes to query.
    unit : units.Units
        Desired unit for all requested axes.

    Returns
    -------
    dict
        Dictionary of AxisType keys to positions as (value, Units) tuples.

    See Also
    --------
    get_x_pos, get_y_pos, get_z_pos, get_r_pos, get_p_pos, get_t_pos
    """
    axes_unit_dict = {}
    if isinstance(axes, (AxisType, str)):
        axes_unit_dict[axes] = unit
    else:
        axes_unit_dict = {axis: unit for axis in axes}
    return get_positions_ex(axes_unit_dict)


def get_x_pos(unit, stage=StageType.stage1):
    """Retrieve position of the x-axis in the requested unit.

    Parameters
    ----------
    unit : units.Units
        Desired unit for the returned position value.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    float
        x-axis position in the requested unit.
    """
    axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    return get_positions(axis_type, unit)[axis_type][0]


def get_y_pos(unit, stage=StageType.stage1):
    """Retrieve position of the y-axis in the requested unit.

    Parameters
    ----------
    unit : units.Units
        Desired unit for the returned position value.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    float
        y-axis position in the requested unit.
    """
    axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    return get_positions(axis_type, unit)[axis_type][0]


def get_z_pos(unit, stage=StageType.stage1):
    """Retrieve position of the z-axis in the requested unit.

    Parameters
    ----------
    unit : units.Units
        Desired unit for the returned position value.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    float
        z-axis position in the requested unit.
    """
    axis_type = AxisType.z2 if stage == StageType.stage2 else AxisType.z
    return get_positions(axis_type, unit)[axis_type][0]


def get_p_pos(unit, stage=StageType.stage1):
    """Retrieve position of the pitch-axis in the requested unit.

    Parameters
    ----------
    unit : units.Units
        Desired unit for the returned position value.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    float
        pitch-axis position in the requested unit.
    """
    axis_type = AxisType.rx2 if stage == StageType.stage2 else AxisType.rx
    return get_positions(axis_type, unit)[axis_type][0]


def get_r_pos(unit, stage=StageType.stage1):
    """Retrieve position of the roll-axis in the requested unit.

    Parameters
    ----------
    unit : units.Units
        Desired unit for the returned position value.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    float
        roll-axis position in the requested unit.
    """
    axis_type = AxisType.ry2 if stage == StageType.stage2 else AxisType.ry
    return get_positions(axis_type, unit)[axis_type][0]


def get_t_pos(unit, stage=StageType.stage1):
    """Retrieve position of the theta-axis in the requested unit.

    Parameters
    ----------
    unit : units.Units
        Desired unit for the returned position value.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    float
        theta-axis position in the requested unit.
    """
    axis_type = AxisType.rz2 if stage == StageType.stage2 else AxisType.rz
    return get_positions(axis_type, unit)[axis_type][0]


# =============================================================================
# ---Move Axes
# =============================================================================
def _stage_async_wait(task_id, timeout):
    """Wait for the asynchronous stage task to complete.

    Parameters
    ----------
    task_id : str
        Unique stage task identifier
    timeout : int
        Maximum time to wait in milliseconds, None for infinite.
    """
    if timeout is None:
        timeout = -1  # Mx treats negative value as infinite
    params = {'taskId': task_id,
              'timeout': timeout,
              'units': _units.Units.MilliSeconds.name}
    _send_request(_SERVICE, 'WaitForStageTaskComplete', params)


def _stage_async_done(task_id):
    """Get the completion status of the asynchronous stage task.

    Parameters
    ----------
    task_id : str
        Unique stage task identifier.

    Returns
    -------
    bool
        True if the task is complete; False otherwise.
    """
    params = {'taskId': task_id}
    return _get_send_request(_SERVICE, 'IsStageTaskComplete', params)


def move_absolute_ex(axes_pos_dict, wait=True):
    """Move the requested axes to the specified positions.

    Parameters
    ----------
    axes_pos_dict : dict
        Dictionary of AxisType keys to positions as (value, units.Units)
        tuples.
    wait : bool
        True to wait for the requested axes to complete the move; False for
        asynchronous motion.

    Returns
    -------
    ZygoTask
        The unique task object for this move.

    Notes
    -----
    This function has been superseded by the simplified motion commands
    specified in the official documentation. It has been kept for backward
    compatibility and internal use and should not be called by new user code.

    See Also
    --------
    move_x, move_xy, move_xyz, move_r, move_p, move_rp, move_t
    """
    if not isinstance(axes_pos_dict, dict):
        raise TypeError('"axes_pos_dict" not a valid dictionary')
    axes_list = []
    for k, pos in axes_pos_dict.items():
        if len(pos) != 2:
            raise ValueError('Position must be a (value, Units) tuple')
        value = pos[0]
        unit = _units._validate_unit(pos[1])
        axis = _validate_axis(k)
        axes_list.append({'m_Item1': axis, 'm_Item2': value, 'm_Item3': unit})
    params = {'axes': axes_list, 'wait': wait, 'isSafeMove': True}
    task_id = _get_send_request(_SERVICE, 'MoveAbsolute', params)
    return _ZygoTask(task_id, _stage_async_done, _stage_async_wait)


def move_absolute(axes_value_dict, unit, wait=True):
    """Move the requested axes to specified positions using a single unit for
    all axes.

    Parameters
    ----------
    axes_value_dict : dict
        Dictionary of AxisType keys to position values.
    unit : units.Units
        Desired unit for all specified axes.
    wait : bool
        True to wait for the requested axes to complete the move; False for
        asynchronous motion.

    Returns
    -------
    ZygoTask
        The unique task object for this move.

    Notes
    -----
    This function has been superseded by the simplified motion commands
    specified in the official documentation. It has been kept for backward
    compatibility and internal use and should not be called by new user code.

    See Also
    --------
    move_x, move_xy, move_xyz, move_r, move_p, move_rp, move_t
    """
    if not isinstance(axes_value_dict, dict):
        raise TypeError('"axes_value_dict" not a valid dictionary')
    axes_pos_dict = {}
    for k, v in axes_value_dict.items():
        axes_pos_dict[k] = (v, unit)
    return move_absolute_ex(axes_pos_dict, wait)


def move_parcentric(axes_value_dict, unit, wait=True):
    """Move the requested axes, with parcentric correction enabled, to
    specified positions using a single unit for all axes.

    Parameters
    ----------
    axes_value_dict : dict
        Dictionary of AxisType keys to position values.
    unit : units.Units
        Desired unit for all specified axes.
    wait : bool
        True to wait for the requested axes to complete the move; False for
        asynchronous motion.

    Returns
    -------
    ZygoTask
        The unique task object for this move.

    Notes
    -----
    This function has been superseded by the simplified motion commands
    specified in the official documentation. It has been kept for backward
    compatibility and internal use and should not be called by new user code.

    See Also
    --------
    move_r, move_p, move_rp
    """
    if not isinstance(axes_value_dict, dict):
        raise TypeError('"axes_value_dict" not a valid dictionary')
    axes_pos_dict = {}
    for k, v in axes_value_dict.items():
        axes_pos_dict[k] = (v, unit)
    axes_list = []
    for k, pos in axes_pos_dict.items():
        if len(pos) != 2:
            raise ValueError('Position must be a (value, Units) tuple')
        value = pos[0]
        unit = _units._validate_unit(pos[1])
        axis = _validate_axis(k)
        axes_list.append({'m_Item1': axis, 'm_Item2': value, 'm_Item3': unit})
    params = {'axes': axes_list, 'wait': wait}
    task_id = _get_send_request(_SERVICE, 'MoveParcentric', params)
    return _ZygoTask(task_id, _stage_async_done, _stage_async_wait)


def move_x(x_pos, unit, wait=True, stage=StageType.stage1):
    """Move the x-axis to the specified position.

    Parameters
    ----------
    x_pos : float
        x-axis position value.
    unit : units.Units
        Unit for the position value.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    return move_absolute({axis_type: x_pos}, unit, wait)


def move_y(y_pos, unit, wait=True, stage=StageType.stage1):
    """Move the y-axis to the specified position.

    Parameters
    ----------
    y_pos : float
        y-axis position value.
    unit : units.Units
       Unit for the position value.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    return move_absolute({axis_type: y_pos}, unit, wait)


def move_z(z_pos, unit, wait=True, stage=StageType.stage1):
    """Move the z-axis to the specified position.

    Parameters
    ----------
    z_pos : float
        z-axis position value.
    unit : units.Units
        Unit for the position value.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.z2 if stage == StageType.stage2 else AxisType.z
    return move_absolute({axis_type: z_pos}, unit, wait)


def move_xy(x_pos, y_pos, unit, wait=True, stage=StageType.stage1):
    """Move the x- and y-axes to the specified positions.

    Parameters
    ----------
    x_pos : float
        x-axis position value.
    y_pos : float
        y-axis position value.
    unit : units.Units
        Unit for the position values.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    stage : StageType
        Identifies which stage contains the specified axes.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    x_axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    y_axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    axes_val = {x_axis_type: x_pos, y_axis_type: y_pos}
    return move_absolute(axes_val, unit, wait)


def move_xyz(x_pos, y_pos, z_pos, unit, wait=True, stage=StageType.stage1):
    """Move the x-, y-, and z-axes to the specified positions.

    Parameters
    ----------
    x_pos : float
        x-axis position value.
    y_pos : float
        y-axis position value.
    z_pos : float
        z-axis position value.
    unit : units.Units
        Unit for the position values.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    stage : StageType
        Identifies which stage contains the specified axes.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    x_axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    y_axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    z_axis_type = AxisType.z2 if stage == StageType.stage2 else AxisType.z
    axes_val = {x_axis_type: x_pos, y_axis_type: y_pos, z_axis_type: z_pos}
    return move_absolute(axes_val, unit, wait)


def move_p(p_pos, unit, wait=True, parcentric=False, stage=StageType.stage1):
    """Move the pitch-axis to the specified position.

    Parameters
    ----------
    p_pos : float
        Pitch-axis position value.
    unit : units.Units
        Unit for the position value.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    parcentric : bool
        True to perform a parcentric move; False otherwise.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.rx2 if stage == StageType.stage2 else AxisType.rx
    if parcentric:
        return move_parcentric({axis_type: p_pos}, unit, wait)
    return move_absolute({axis_type: p_pos}, unit, wait)


def move_r(r_pos, unit, wait=True, parcentric=False, stage=StageType.stage1):
    """Move the roll-axis to the specified position.

    Parameters
    ----------
    r_pos : float
        Roll-axis position value.
    unit : units.Units
        Unit for the position value.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    parcentric : bool
        True to perform a parcentric move; False otherwise.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.ry2 if stage == StageType.stage2 else AxisType.ry
    if parcentric:
        return move_parcentric({axis_type: r_pos}, unit, wait)
    return move_absolute({axis_type: r_pos}, unit, wait)


def move_rp(r_pos, p_pos, unit,
            wait=True, parcentric=False, stage=StageType.stage1):
    """Move the roll- and pitch-axes to the specified positions.

    Parameters
    ----------
    r_pos : float
        Roll-axis position value.
    p_pos : float
        Pitch-axis position value.
    unit : units.Units
        Unit for the position values.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    parcentric : bool
        True to perform a parcentric move; False otherwise.
    stage : StageType
        Identifies which stage contains the specified axes.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    rx_axis_type = AxisType.rx2 if stage == StageType.stage2 else AxisType.rx
    ry_axis_type = AxisType.ry2 if stage == StageType.stage2 else AxisType.ry
    axes_val = {ry_axis_type: r_pos, rx_axis_type: p_pos}
    if parcentric:
        return move_parcentric(axes_val, unit, wait)
    return move_absolute(axes_val, unit, wait)


def move_t(t_pos, unit, wait=True, stage=StageType.stage1):
    """Move the theta-axis to the specified position.

    Parameters
    ----------
    t_pos : float
        Theta-axis position value.
    unit : units.Units
        Unit for the position value.
    wait : bool
        True to wait for the axis to complete the move; False for asynchronous
        motion.
    parcentric : bool
        True to perform a parcentric move; False otherwise.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.rz2 if stage == StageType.stage2 else AxisType.rz
    return move_absolute({axis_type: t_pos}, unit, wait)


# =============================================================================
# ---Home Axes
# =============================================================================
def home(axes, wait=True):
    """Home the requested axes.

    Parameters
    ----------
    axes : AxisType or list of AxisType
        Axis type(s) to home.
    wait : bool
        True to wait for the home to complete; False for asynchronous home.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    if isinstance(axes, (AxisType, str)):
        axes_list = [_validate_axis(axes)]
    else:
        axes_list = [_validate_axis(axis) for axis in axes]
    params = {'axes': axes_list, 'wait': wait}
    task_id = _get_send_request(_SERVICE, 'Home', params)
    return _ZygoTask(task_id, _stage_async_done, _stage_async_wait)


def home_x(wait=True, stage=StageType.stage1):
    """Home the x-axis.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    return home([axis_type], wait)


def home_y(wait=True, stage=StageType.stage1):
    """Home the y-axis.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    return home([axis_type], wait)


def home_z(wait=True, stage=StageType.stage1):
    """Home the z-axis.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.z2 if stage == StageType.stage2 else AxisType.z
    return home([axis_type], wait)


def home_xy(wait=True, stage=StageType.stage1):
    """Home the x- and y-axes.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axes.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    x_axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    y_axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    return home([x_axis_type, y_axis_type], wait)


def home_xyz(wait=True, stage=StageType.stage1):
    """Home the x-, y-, and z-axes.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axes.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    x_axis_type = AxisType.x2 if stage == StageType.stage2 else AxisType.x
    y_axis_type = AxisType.y2 if stage == StageType.stage2 else AxisType.y
    z_axis_type = AxisType.z2 if stage == StageType.stage2 else AxisType.z
    return home([x_axis_type, y_axis_type, z_axis_type], wait)


def home_p(wait=True, stage=StageType.stage1):
    """Home the pitch-axis.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.rx2 if stage == StageType.stage2 else AxisType.rx
    return home([axis_type], wait)


def home_r(wait=True, stage=StageType.stage1):
    """Home the roll-axis.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.ry2 if stage == StageType.stage2 else AxisType.ry
    return home([axis_type], wait)


def home_rp(wait=True, stage=StageType.stage1):
    """Home the roll- and pitch-axes.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axes.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    rx_axis_type = AxisType.rx2 if stage == StageType.stage2 else AxisType.rx
    ry_axis_type = AxisType.ry2 if stage == StageType.stage2 else AxisType.ry
    return home([ry_axis_type, rx_axis_type], wait)


def home_t(wait=True, stage=StageType.stage1):
    """Home the theta-axis.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which stage contains the specified axis.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    axis_type = AxisType.rz2 if stage == StageType.stage2 else AxisType.rz
    return home([axis_type], wait)


def home_all(wait=True, stage=StageType.stage_all):
    """Home all active axes.

    Parameters
    ----------
    wait : bool
        True to wait for the home to complete; False for asynchronous home.
    stage : StageType
        Identifies which set of axes to home.

    Returns
    -------
    ZygoTask
        The unique task object for this move.
    """
    params = {'wait': wait}
    if stage == StageType.stage1:
        task_id = _get_send_request(_SERVICE, 'HomeStage1', params)
    elif stage == StageType.stage2:
        task_id = _get_send_request(_SERVICE, 'HomeStage2', params)
    else:
        task_id = _get_send_request(_SERVICE, 'HomeAll', params)
    return _ZygoTask(task_id, _stage_async_done, _stage_async_wait)


# =============================================================================
# ---Motion Status
# =============================================================================
def wait(axes, timeout=None):
    """Wait for all requested axes to finish moving.

    Parameters
    ----------
    axes : AxisType or list of AxisType
        Axis or axes to wait on for motion to complete.
    timeout : int, optional
        Maximum time to wait in milliseconds, None for infinite.
    """
    if isinstance(axes, (AxisType, str)):
        param_axes = [_validate_axis(axes)]
    else:
        param_axes = [_validate_axis(axis) for axis in axes]
    if timeout is None:
        timeout = -1  # Mx treats negative value as infinite
    params = {'axes': param_axes,
              'timeout': timeout,
              'units': _units.Units.MilliSeconds.name}
    _send_request(_SERVICE, 'Wait', params)


def is_active(axis):
    """Return whether or not the specified axis is available.

    Parameters
    ----------
    axis : AxisType
        The axis for which to request availability status.

    Returns
    -------
    bool
        True if the specified axis is available; False otherwise.
    """
    params = {'axis': _validate_axis(axis)}
    return _get_send_request(_SERVICE, 'IsActive', params)


def is_homed(axis):
    """Return whether or not the specified axis is homed.

    Parameters
    ----------
    axis : AxisType
        The axis for which to request home status.

    Returns
    -------
    bool
        True is the specified axis is homed; False otherwise.
    """
    params = {'axis': _validate_axis(axis)}
    return _get_send_request(_SERVICE, 'IsHomed', params)


def is_zstop_set():
    """Return whether or not the z-stop is set.

    Returns
    -------
    bool
        True is z-stop is set; False otherwise.
    """
    return _get_send_request(_SERVICE, 'IsZStopSet')


def set_pendant_enabled(enabled):
    """Enable or disable the pendant.

    Parameters
    ----------
    enabled : bool
        True to enable the pendant; False to disable.
    """
    params = {'enabled': True if enabled else False}
    _send_request(_SERVICE, 'SetPendantEnabled', params)

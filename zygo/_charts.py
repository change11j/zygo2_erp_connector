# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx chart user interface functionality.
"""

from enum import IntEnum as _IntEnum

from zygo.connectionmanager import send_request as _send_request
from zygo import units as _units

_SERVICE = 'UserInterfaceService'
"""str: The service name for the charts module."""


# =============================================================================
# ---Chart Enumerations
# =============================================================================
class ChartAxis(_IntEnum):
    """Axis of the charts."""
    X = 1
    Y = 2
    All = 3


class ChartLimit(_IntEnum):
    """Limits bound."""
    Low = 1
    High = 2
    All = 3


# =============================================================================
# ---Internal Support Methods
# =============================================================================
def _validate_axis(axis):
    """Validate input as a valid chart axis value.

    Parameters
    ----------
    axis : ChartAxis or str
        Axis to validate.

    Returns
    -------
    str
        String representation of the specified axis.

    Raises
    ------
    TypeError
        If the input is not a ChartAxis or string type.
    ValueError
        If the input string is not convertable to a ChartAxis member.
    """
    if isinstance(axis, ChartAxis):
        return axis.name
    if isinstance(axis, str):
        for caxis in ChartAxis.__members__:
            if axis.lower() == caxis.lower():
                return caxis
        raise ValueError('`axis` string is not a valid `ChartAxis` member.')
    raise TypeError(
        '`axis` must be of type `ChartAxis` or valid string value.')


def _validate_limit(limit):
    """Validate input as a valid chart limit value.

    Parameters
    ----------
    limit : ChartLimit or str
        Chart limit bound to validate.

    Returns
    -------
    str
        String representation of the specified chart limit bound.

    Raises
    ------
    TypeError
        If the input is not a ChartLimit or string type.
    ValueError
        If the input string is not convertable to a ChartLimit member.
    """
    if isinstance(limit, ChartLimit):
        return limit.name
    if isinstance(limit, str):
        for clim in ChartLimit.__members__:
            if limit.lower() == clim.lower():
                return clim
        raise ValueError('`limit` string is not a valid `ChartLimit` member.')
    raise TypeError(
        '`limit` must be of type `ChartLimit` or valid string value.')


# =============================================================================
# ---Chart Limit Methods
# =============================================================================
def clear_chart_limit(control,
                      axis_name=ChartAxis.All,
                      limit_name=ChartLimit.All):
    """Clear a chart's limit(s).

    Parameters
    ----------
    control : ui.Control
        The chart Control object.
    axis_name : ChartAxis, optional
        The name of the chart axis limit to clear; Defaults to All.
    limit_name : ChartLimit, optional
        The name of the chart limit bound; Defaults to All.
    """
    params = {'controlId': control._id,
              'axis': _validate_axis(axis_name),
              'limit': _validate_limit(limit_name)}
    _send_request(_SERVICE, 'ClearChartLimits', params)


def set_chart_high_limit(control,
                         axis_name=ChartAxis.Y,
                         limit_value=0,
                         unit=_units.Units.MicroMeters):
    """Set the chart high limit.

    Parameters
    ----------
    control : ui.Control
        The chart Control object.
    axis_name : ChartAxis, optional
        The chart axis to set; Defaults to Y.
    limit_value : float, optional
        The high limit value; Default to 0.
    unit : units.Units, optional
        The unit of the limit value; Defaults to MicroMeters.
    """
    params = {'controlId': control._id,
              'axis': _validate_axis(axis_name),
              'low': float("NaN"),
              'high': limit_value,
              'unit': _units._validate_unit(unit)}
    _send_request(_SERVICE, 'SetChartLimits', params)


def set_chart_low_limit(control,
                        axis_name=ChartAxis.Y,
                        limit_value=0,
                        unit=_units.Units.MicroMeters):
    """Set the chart low limit.

    Parameters
    ----------
    control : ui.Control
        The chart Control object.
    axis_name : ChartAxis, optional
        The chart axis to set; Defaults to Y.
    limit_value : float, optional
        The low limit value; default to 0.
    unit : units.Units, optional
        The unit of the limit value; Defaults to MicroMeters.
    """
    params = {'controlId': control._id,
              'axis': _validate_axis(axis_name),
              'low': limit_value,
              'high': float("NaN"),
              'unit': _units._validate_unit(unit)}
    _send_request(_SERVICE, 'SetChartLimits', params)


def set_chart_limits(control,
                     axis_name=ChartAxis.Y,
                     low_value=0,
                     high_value=100,
                     unit=_units.Units.MicroMeters):
    """Set the chart limits.

    Parameters
    ----------
    control : ui.Control
        The chart Control object.
    axis_name : ChartAxis, optional
        The chart axis to set; Defaults to Y.
    low_value : float, optional
        The low limit value; default to 0.
    high_value : float, optional
        The high limit value; default to 100.
    unit : units.Units, optional
        The unit of the limit values; Defaults to MicroMeters.
    """
    params = {'controlId': control._id,
              'axis': _validate_axis(axis_name),
              'low': low_value,
              'high': high_value,
              'unit': _units._validate_unit(unit)}
    _send_request(_SERVICE, 'SetChartLimits', params)

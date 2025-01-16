# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx MST instrument functionality.
"""

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.units import _validate_unit
from zygo.units import Units as _Units

_SERVICE = 'InstrumentService'
"""str: The service name for the mst module."""


def get_ftpsi_peak(peak_num, num_peaks, range_min, range_max, unit):
    """Get the location of a peak based upon an OPD spectrum calculation of a
    pixel at the location of the test calibration marker.

    Parameters
    ----------
    peak_num : int
        Specifies which peak (out of the number of peaks specified by
        num_peaks) to find.
    num_peaks : int
        Specifies the number of expected peaks. Peaks are found based upon the
        highest signal strength first.
    range_min : float
        Specifies the optical path length that is the lower boundary when
        searching for peaks.
    range_max : float
        Specifies the optical path length that is the upper boundary when
        searching for peaks.
    unit : units.Units
        Specifies the units for the range input parameters and the returned
        value.

    Returns
    -------
    float
        The optical path distance for the requested peak.
    """
    unit_str = _validate_unit(unit)
    params = {'peakNumber': peak_num, 'numberOfPeaks': num_peaks,
              'rangeMinumum': range_min, 'rangeMaximum': range_max,
              'units': unit_str}
    return _get_send_request(_SERVICE, 'GetFtpsiPeak', params)

def get_averaged_ftpsi_peak(peak_num, num_peaks, range_min, range_max, unit, averages):
    """Get the location of a peak based upon an OPD spectrum calculation of a
    pixel at the location of the test calibration marker.

    Parameters
    ----------
    peak_num : int
        Specifies which peak (out of the number of peaks specified by
        num_peaks) to find.
    num_peaks : int
        Specifies the number of expected peaks. Peaks are found based upon the
        highest signal strength first.
    range_min : float
        Specifies the optical path length that is the lower boundary when
        searching for peaks.
    range_max : float
        Specifies the optical path length that is the upper boundary when
        searching for peaks.
    unit : units.Units
        Specifies the units for the range input parameters and the returned
        value.
    averages : int
        Specifies the number of points to sample.

    Returns
    -------
    float
        The optical path distance, in the specified units, for the requested
        peak.
    """
    unit_str = _validate_unit(unit)
    params = {'peakNumber': peak_num, 'numberOfPeaks': num_peaks,
              'rangeMinumum': range_min, 'rangeMaximum': range_max,
              'units': unit_str, 'averages' : averages }
    return _get_send_request(_SERVICE, 'GetAveragedFtpsiPeak', params)

def analyze_ftpsi_peak(peak_location, unit):
    """Generate a phase map by performing MST analysis at the specified
    optical distance.

    Parameters
    ----------
    peak_location :  float
        The optical path distance for the peak of interest.
    unit : units.Units
        Specifies the unit for the peak location value.
    """
    unit_str = _validate_unit(unit)
    params = {'peakLocation': peak_location, 'units': unit_str}
    _send_request(_SERVICE, 'AnalyzeFtpsiPeak', params)

def get_min_excursion(unit):
    """Gets the FTPSI minimum ramp excursion (Tuning Range).

    Parameters
    ----------
    unit : units.Units
        Specifies the units for the range input parameters and the returned
        value.

    Returns
    -------
    float
        Minimum Tuning Range in the specified units.
    """
    unit_str = _validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetFtpsiMinExcursion', params)

def get_max_excursion(unit):
    """Gets the FTPSI maximum ramp excursion (Tuning Range).

    Parameters
    ----------
    unit : units.Units
        Specifies the units for the range input parameters and the returned
        value.

    Returns
    -------
    float
        Maximum Tuning Range in the specified units.
    """
    unit_str = _validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetFtpsiMaxExcursion', params)

def get_min_rate(unit):
    """Gets the FTPSI minimum ramp rate.

    Parameters
    ----------
    unit : units.Units
        Specifies the units for the range input parameters and the returned
        value.

    Returns
    -------
    float
        The minimum ramp rate in the specified units per second.
    """
    unit_str = _validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetFtpsiMinRate', params)

def get_max_rate(unit):
    """Gets the FTPSI maximum ramp rate.

    Parameters
    ----------
    unit : units.Units
        Specifies the units for the range input parameters and the returned
        value.

    Returns
    -------
    float
        The maximum ramp rate in the specified units per second.
    """
    unit_str = _validate_unit(unit)
    params = {'units': unit_str}
    return _get_send_request(_SERVICE, 'GetFtpsiMaxRate', params)

def get_min_frames():
    """Gets the FTPSI minimum number of frames for a ramp.

    Returns
    -------
    int
        The minimum number of frames for a ramp.
    """
    return _get_send_request(_SERVICE, 'GetFtpsiMinFrames')

def get_max_frames():
    """Gets the FTPSI maximum number of frames for a ramp.

    Returns
    -------
    int
        The maximum number of frames for a ramp.
    """
    return _get_send_request(_SERVICE, 'GetFtpsiMaxFrames')

def get_test_x():
    """Gets the X coordinate of the FTPSI test pixel in pixels.

    Returns
    -------
    int
        The X coordinate of the FTPSI test pixel in pixels, or None if not set.
    """
    val = _get_send_request(_SERVICE, 'GetFtpsiTestX')
    if val == 2147483647:
        return None
    else:
        return val

def get_test_y():
    """Gets the Y coordinate of the FTPSI test pixel in pixels.

    Returns
    -------
    int
        The Y coordinate of the FTPSI test pixel in pixels, or None if not set.
    """
    val = _get_send_request(_SERVICE, 'GetFtpsiTestY')
    if val == 2147483647:
        return None
    else:
        return val

def get_reference_x():
    """Gets the X coordinate of the FTPSI reference pixel in pixels.

    Returns
    -------
    int
        The X Coordinate of the FTPSI reference pixel in pixels,
        or None if not set.
    """
    val = _get_send_request(_SERVICE, 'GetFtpsiReferenceX')
    if val == 2147483647:
        return None
    else:
        return val

def get_reference_y():
    """Gets the Y coordinate of the FTPSI reference pixel in pixels.

    Returns
    -------
    int
        The Y Coordinate of the FTPSI reference pixel in pixels,
        or None if not set.
    """
    val = _get_send_request(_SERVICE, 'GetFtpsiReferenceY')
    if val == 2147483647:
        return None
    else:
        return val

def set_test(x, y):
    """Sets the FTPSI test pixel location.

    Parameters
    ----------
    x : int
        X coordinate of the test pixel.
    y : int
        Y coordinate of the test pixel.
    """
    params = {'x': x, 'y': y}
    _send_request(_SERVICE, 'SetFtpsiTest', params)

def set_reference(x, y):
    """Sets the FTPSI reference pixel location.

    Parameters
    ----------
    x : int
        X coordinate of the reference pixel.
    y : int
        Y coordinate of the reference pixel.
    """
    params = {'x': x, 'y': y}
    _send_request(_SERVICE, 'SetFtpsiReference', params)

def clear_test():
    """Clears the FTPSI Test Pixel."""
    _send_request(_SERVICE, 'ClearFtpsiTest')

def clear_reference():
    """Clears the FTPSI Reference Pixel."""
    _send_request(_SERVICE, 'ClearFtpsiReference')


def estimate_ramp_excursion(maximum_opd_gap,
                            tuning_factor,
                            opd_units,
                            minimum_opd_gap=0,
                            result_units=_Units.GigaHertz):
    """Estimates the FTPSI ramp excursion for a multiple surface investigation
    measurement.

    Parameters
    ----------
    maximum_opd_gap : float
        Maximum OPD gap in opd_units units.
    tuning_factor : int
        Tuning factor multiplier.
    opd_units : units.Units
        Distance units for OPD gaps.
    minimum_opd_gap : float, optional
        Minimum OPD gap in opd_units units.
    result_units : units.Units, optional
        Units for result.

    Returns
    -------
    float
        The estimated ramp excursion in the specified units.
    """
    unit_str = _validate_unit(opd_units)
    result_unit_str = _validate_unit(result_units)
    params = {'maximumOpdGap': maximum_opd_gap,
              'tuningFactor': tuning_factor,
              'opdUnits': unit_str,
              'minimumOpdGap': minimum_opd_gap,
              'resultUnits':  result_unit_str}
    return _get_send_request(_SERVICE, 'EstimateFtpsiExcursion', params)


def estimate_ramp_frames(maximum_opd_gap,
                         tuning_factor,
                         opd_units,
                         minimum_opd_gap=0):
    """Estimates the FTPSI ramp frames for a multiple surface investigation
    measurement.

    Parameters
    ----------
    maximum_opd_gap : float
        Maximum OPD gap in opd_units units.
    tuning_factor : int
        Tuning factor multiplier.
    opd_units : units.Units
        Distance units for OPD gaps.
    minimum_opd_gap : float, optional
        Minimum OPD gap in opd_units units.

    Returns
    -------
    int
        Estimate ramp frames.
    """
    unit_str = _validate_unit(opd_units)
    params = {'maximumOpdGap': maximum_opd_gap,
              'tuningFactor': tuning_factor,
              'opdUnits': unit_str,
              'minimumOpdGap': minimum_opd_gap}
    return _get_send_request(_SERVICE, 'EstimateFtpsiFrames', params)

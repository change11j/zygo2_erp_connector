# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx slice functionality.
"""

from enum import IntEnum as _IntEnum

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.ui import Control as _Control
from zygo.units import _validate_unit
from zygo.core import Point2D as _Point2D


# Slices are currently implemented in the UserInterfaceService.
# This is likely to change.
_SERVICE = 'UserInterfaceService'
"""str: The service name for the slice module."""


class LinearSliceType(_IntEnum):
    """Linear slice subtypes."""

    linear = 1  # Standard linear slice
    # poly = 2


class RadialSliceType(_IntEnum):
    """Radial slice subtypes."""

    radial = 1  # Standard radial slice
    radial_center = 2
    average_radial = 3
    average_radial_center = 4


class CircularSliceType(_IntEnum):
    """Circular slice subtypes."""

    circular = 1    # Standard circular slice
    circular_center = 2
    circular_min_pv = 3


def _mx_linear_slice_kind_to_enum(linear_slice_type):
    """Converts the slice kind string returned from Mx to the corresponding
    `LinearSliceType` value.

    Parameters
    ----------
    linear_slice_type : str
        The Mx linear slice kind string to convert.

    Returns
    -------
    LinearSliceType
        The linear slice type value representing the given Mx linear slice
        kind string.

    Raises
    ------
    ValueError
        If the input string is not a valid linear slice type.
    """
    stype = linear_slice_type.lower()
    if stype == "single":
        return LinearSliceType.linear
    elif stype == "polygon":
        return LinearSliceType.poly
    else:
        raise ValueError('`linear_slice_type` string "{}" is not a valid '
                         'linear slice type.'.format(linear_slice_type))


def _mx_radial_slice_kind_to_enum(radial_slice_type):
    """Converts the slice kind string returned from Mx to the corresponding
    `RadialSliceType` value.

    Parameters
    ----------
    radial_slice_type : str
        The Mx radial slice kind string to convert.

    Returns
    -------
    RadialSliceType
        The radial slice type value representing the given Mx radial slice
        kind string.

    Raises
    ------
    ValueError
        If the input string is not a valid radial slice type.
    """
    stype = radial_slice_type.lower()
    if stype == "standard":
        return RadialSliceType.radial
    elif stype == "centered":
        return RadialSliceType.radial_center
    elif stype == "averagestandard":
        return RadialSliceType.average_radial
    elif stype == "averagecentered":
        return RadialSliceType.average_radial_center
    else:
        raise ValueError('`radial_slice_type` string "{}" is not a valid '
                         'radial slice type.'.format(radial_slice_type))


def _mx_circular_slice_kind_to_enum(circular_slice_type):
    """Converts the slice kind string returned from Mx to the corresponding
    `CircularSliceType` value.

    Parameters
    ----------
    circular_slice_type : str
        The Mx circular slice kind string to convert.

    Returns
    -------
    CircularSliceType
        The circular slice type value representing the given Mx circular slice
        kind string.

    Raises
    ------
    ValueError
        If the input string is not a valid circular slice type.
    """
    stype = circular_slice_type.lower()
    if stype == "standard":
        return CircularSliceType.circular
    elif stype == "centered":
        return CircularSliceType.circular_center
    elif stype == "minpv":
        return CircularSliceType.circular_min_pv
    else:
        raise ValueError('`circular_slice_type` string "{}" is not a valid '
                         'circular slice type.'.format(circular_slice_type))


def get_linear_slices(control, linear_slice_type):
    """Get the linear slices of the requested subtype defined in the specified
    plot control.

    Parameters
    ----------
    control : ui.Control
        The plot to query.
    linear_slice_type : LinearSliceType
        The subtype of linear slice to retrieve.

    Returns
    -------
    tuple of LinearSlice
        The collection of requested linear slices.
    """
    if not isinstance(control, _Control):
        raise TypeError('`control` must be of type `ui.Control`.')
    if linear_slice_type is None:
        slice_type = None
    else:
        slice_type = LinearSlice._validate_slice_type(linear_slice_type)
    params = {'controlId': control._id,
              'sliceCategory': Slice.SliceCategory.linear.name,
              'sliceType': slice_type}
    slices = _get_send_request(_SERVICE, 'GetSlices', params)
    return tuple(
        LinearSlice(control._id, s['m_Item1'],
                    _mx_linear_slice_kind_to_enum(s['m_Item2']))
        for s in slices)


def get_all_linear_slices(control):
    """Get all linear slices defined in the specified plot control.

    Parameters
    ----------
    control : ui.Control
        The plot to query.

    Returns
    -------
    dict
        A dictionary of `LinearSlice` objects indexed by their label.
    """
    slices = get_linear_slices(control, None)
    return {s.label: s for s in slices}


def get_radial_slices(control, radial_slice_type):
    """Get the radial slices of the requested subtype defined in the specified
    plot control.

    Parameters
    ----------
    control : ui.Control
        The plot to query.
    radial_slice_type : RadialSliceType
        The subtype of radial slice to retrieve.

    Returns
    -------
    tuple of RadialSlice
        The collection of requested radial slices.
    """
    if not isinstance(control, _Control):
        raise TypeError('`control` must be of type `ui.Control`.')
    if radial_slice_type is None:
        slice_type = None
    else:
        slice_type = RadialSlice._validate_slice_type(radial_slice_type)
    params = {'controlId': control._id,
              'sliceCategory': Slice.SliceCategory.radial.name,
              'sliceType': slice_type}
    slices = _get_send_request(_SERVICE, 'GetSlices', params)
    return tuple(
        RadialSlice(control._id, s['m_Item1'],
                    _mx_radial_slice_kind_to_enum(s['m_Item2']))
        for s in slices)


def get_all_radial_slices(control):
    """Get all radial slices defined in the specified plot control.

    Parameters
    ----------
    control : ui.Control
        The plot to query.

    Returns
    -------
    dict
        A dictionary of `RadialSlice` objects indexed by their label.
    """
    slices = get_radial_slices(control, None)
    return {s.label: s for s in slices}


def get_circular_slices(control, circular_slice_type):
    """Get the circular slices of the requested subtype defined in the
    specified plot control.

    Parameters
    ----------
    control : ui.Control
        The plot to query.
    circular_slice_type : CircularSliceType
        The subtype of circular slice to retrieve.

    Returns
    -------
    tuple of CircularSlice
        The collection of requested circular slices.
    """
    if not isinstance(control, _Control):
        raise TypeError('`control` must be of type `ui.Control`.')
    if circular_slice_type is None:
        slice_type = None
    else:
        slice_type = CircularSlice._validate_slice_type(circular_slice_type)
    params = {'controlId': control._id,
              'sliceCategory': Slice.SliceCategory.circular.name,
              'sliceType': slice_type}
    slices = _get_send_request(_SERVICE, 'GetSlices', params)
    return tuple(
        CircularSlice(control._id, s['m_Item1'],
                      _mx_circular_slice_kind_to_enum(s['m_Item2']))
        for s in slices)


def get_all_circular_slices(control):
    """Get all circular slices defined in the specified plot control.

    Parameters
    ----------
    control : ui.Control
        The plot to query.

    Returns
    -------
    dict
        A dictionary of `CircularSlice` objects indexed by their label.
    """
    slices = get_circular_slices(control, None)
    return {s.label: s for s in slices}


class Slice(object):
    """Represents a single slice in Mx.

    Parameters
    ----------
    control_id : str
        Unique ID of the control containing the slice.
    slice_id : str
        The display label of the slice.
    """

    class SliceCategory(_IntEnum):
        """Mx slice categories."""
        linear = 1
        circular = 2
        radial = 3
        # crosshair = 4

    @staticmethod
    def _validate_slice_category(slice_category):
        """Validate input as a valid slice category value.

        Parameters
        ----------
        slice_category : SliceCategory or str
            Slice category to validate.

        Returns
        -------
        str
            String representation of the specified slice category value.

        Raises
        ------
        TypeError
            If the input is not a SliceCategory or str type.
        ValueError
            If the input string is not convertable to a SliceCategory member.
        """
        if isinstance(slice_category, Slice.SliceCategory):
            return slice_category.name
        if isinstance(slice_category, str):
            for cat in Slice.SliceCategory.__members__:
                if slice_category.lower() == cat.lower():
                    return cat
            raise ValueError('`slice_category` string is not a valid '
                             '`SliceCategory` member.')
        raise TypeError('`slice_category` must be of type `SliceCategory` '
                        'or valid string value.')

    _category = None
    """SliceCategory: The category of the slice."""
    _slice_type = None
    """enum.IntEnum:  The subtype of the slice."""

    def __init__(self, control_id, slice_id):
        """Initialize the slice.

        Parameters
        ----------
        control_id : str
            Unique ID of the control containing the slice.
        slice_id : str
            The display label of the slice.
        """
        self._control_id = control_id
        self._id = slice_id

    @property
    def label(self):
        """str: The label of the slice."""

        return self._id

    def get_dimension(self, units):
        """Get the dimension value of the slice.

        The property that the slice dimension refers to depends on the slice
        type and subtype:

            Linear
                Linear                  Slice Length
                Poly                    N/A
            Circular
                Circular                Slice Radius
                Circular Center         Slice Radius
                Circular Min PV         Slice Radius
            Radial
                Radial                  Slice Length
                Radial Center           Slice Length
                Average Radial          Slice Radius
                Average Radial Center   Slice Radius

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned dimension value.

        Returns
        -------
        float
            The slice dimension in the requested unit.
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'units': _validate_unit(units)}
        dimension = _get_send_request(_SERVICE, 'GetDimension', params)
        return dimension

    def set_dimension(self, value, units):
        """Set the dimension of the slice.

        The property that the slice dimension refers to depends on the slice
        type and subtype:

            Linear
                Linear                  Slice Length
                Poly                    N/A
            Circular
                Circular                Slice Radius
                Circular Center         Slice Radius
                Circular Min PV         Slice Radius
            Radial
                Radial                  Slice Length
                Radial Center           Slice Length
                Average Radial          Slice Radius
                Average Radial Center   Slice Radius

        Parameters
        ----------
        value : float
            The new slice dimension value.
        units : units.Units
            The desired units for the dimension value.
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'value': value,
                  'units': _validate_unit(units)}
        _send_request(_SERVICE, 'SetDimension', params)

    def get_midpoint(self, units):
        """Get the midpoint of the slice.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned midpoint value.

        Returns
        -------
        core.Point2D
            The slice midpoint in the requested units.
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'units': _validate_unit(units)}
        midpoint = _get_send_request(_SERVICE, 'GetMidpoint', params)
        return _Point2D(midpoint['m_Item1'], midpoint['m_Item2'])

    def set_midpoint(self, position, units):
        """Set the midpoint of the slice.

        Parameters
        ----------
        position : core.Point2D
            The new slice midpoint value.
        units : units.Units
            The desired unit for the midpoint value.
        """
        if not isinstance(position, _Point2D):
            raise TypeError('`position` must be a Point2D value.')
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'position': {'m_Item1': position.x, 'm_Item2': position.y},
                  'units': _validate_unit(units)}
        _send_request(_SERVICE, 'SetMidpoint', params)

    def get_angle(self, units):
        """Get the angle of the slice in the specified units.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned angle value.

        Returns
        -------
        float
            The slice angle in the requested units.
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'units': _validate_unit(units)}
        angle = _get_send_request(_SERVICE, 'GetAngle', params)
        return angle

    def set_angle(self, value, units):
        """Set the angle of the slice relative to the start point.

        Parameters
        ----------
        value : float
            The new slice angle value.
        units : units.Units
            The desired unit for the angle value.
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'angle': value,
                  'units': _validate_unit(units)}
        _send_request(_SERVICE, 'SetAngle', params)


class LinearSlice(Slice):
    """Represents one Mx linear slice.

    Parameters
    ----------
    control_id : str
        Unique ID of the control containing the slice.
    id_ : str
        The display label of the slice.
    slice_type : LinearSliceType
        The subtype of the linear slice.
    """

    @staticmethod
    def _validate_slice_type(slice_type):
        """Validate input as a valid linear slice type.

        Parameters
        ----------
        slice_type : LinearSliceType or str
            Linear slice type to validate.

        Returns
        -------
        str
            String representation of the specified linear slice type.

        Raises
        ------
        TypeError
            If the input is not a LinearSliceType or str type.
        ValueError
            If the input string is not convertable to a LinearSliceType member.
        """
        if isinstance(slice_type, LinearSliceType):
            return slice_type.name
        if isinstance(slice_type, str):
            for stype in LinearSliceType.__members__:
                if slice_type.lower() == stype.lower():
                    return stype
            raise ValueError('`slice_type` string is not a valid '
                             '`LinearSliceType` member.')
        raise TypeError('`slice_type` must be of type `LinearSliceType` or '
                        'valid string value.')

    def __init__(self, control_id, slice_id, slice_type):
        """Initialize the linear slice.

        Parameters
        ----------
        control_id : str
            Unique ID of the control containing the slice.
        id_ : str
            The display label of the slice.
        slice_type : LinearSliceType
            The subtype of the linear slice.
        """
        super().__init__(control_id, slice_id)
        self._slice_type = LinearSlice._validate_slice_type(slice_type)
        self._category = Slice._validate_slice_category(
            Slice.SliceCategory.linear)

    def get_endpoints(self, units):
        """Get the start and end points of the linear slice.

        Parameters
        ----------
        units : units.Units
            The desired unit for the returned endpoint values.

        Returns
        -------
        tuple of core.Point2D
            The slice endpoints in the requested units.

        See Also
        --------
        get_start, get_end
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'units': _validate_unit(units)}
        endpoints = _get_send_request(_SERVICE, 'GetEndpoints', params)
        return (
            _Point2D(endpoints['m_Item1']['m_Item1'],
                     endpoints['m_Item1']['m_Item2']),
            _Point2D(endpoints['m_Item2']['m_Item1'],
                     endpoints['m_Item2']['m_Item2']))

    def get_start(self, units):
        """Get the start point of the linear slice.

        Parameters
        ----------
        units : units.Units
            The desired unit for the returned start point value.

        Returns
        -------
        core.Point2D
            The slice start point in the requested units.

        Note
        ----
        Equivalent to get_endpoints(units)[0]

        See Also
        --------
        get_end, get_endpoints
        """
        return self.get_endpoints(units)[0]

    def set_start(self, position, units):
        """Set the start point of the linear slice.

        The existing end point remains unchanged.

        Parameters
        ----------
        units : units.Units
            The desired unit for the start point value.
        """
        if not isinstance(position, _Point2D):
            raise TypeError('`position` must be a Point2D value.')
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'position': {'m_Item1': position.x, 'm_Item2': position.y},
                  'units': _validate_unit(units)}
        _send_request(_SERVICE, 'SetStart', params)

    def get_end(self, units):
        """Get the end point of the linear slice.

        Parameters
        ----------
        units : units.Units
            The desired unit for the returned end point value.

        Returns
        -------
        core.Point2D
            The slice end point in the requested units.

        Note
        ----
        Equivalent to get_endpoints(units)[1]

        See Also
        --------
        get_start, get_endpoints
        """
        return self.get_endpoints(units)[1]

    def set_end(self, position, units):
        """Set the end point of the linear slice.

        The existing start point remains unchanged.

        Parameters
        ----------
        units : units.Units
            The desired unit for the end point value.
        """
        if not isinstance(position, _Point2D):
            raise TypeError('`position` must be a Point2D value.')

        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'position': {'m_Item1': position.x, 'm_Item2': position.y},
                  'units': _validate_unit(units)}
        _send_request(_SERVICE, 'SetEnd', params)

    def get_length(self, units):
        """Get the length (dimension) of the linear slice.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned length value.

        Returns
        -------
        float
            The slice length (dimension) in the requested unit.
        """
        return self.get_dimension(units)

    def set_length(self, value, units):
        """Set the length (dimension) of the linear slice.

        Parameters
        ----------
        value : float
            The new slice length value.
        units : units.Units
            The desired units for the length value.
        """
        self.set_dimension(value, units)

    def get_midpoint(self, units):
        """Get the midpoint of the linear slice.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned midpoint value.

        Returns
        -------
        core.Point2D
            The slice midpoint in the requested units.
        """
        return super().get_midpoint(units)

    def set_midpoint(self, position, units):
        """Set the midpoint of the linear slice.

        Parameters
        ----------
        position : core.Point2D
            The new slice midpoint value.
        units : units.Units
            The desired unit for the midpoint value.

        Note
        ----
        The endpoints are translated in x and y with respect to the change
        in midpoint.
        """
        super().set_midpoint(position, units)


class RadialSlice(Slice):
    """Represents one Mx radial slice.

    Parameters
    ----------
    control_id : str
        Unique ID of the control containing the slice.
    id_ : str
        The display label of the slice.
    slice_type : RadialSliceType
        The subtype of the radial slice.
    """

    @staticmethod
    def _validate_slice_type(slice_type):
        """Validate input as a valid radial slice type.

        Parameters
        ----------
        slice_type : RadialSliceType or str
            Radial slice type to validate.

        Returns
        -------
        str
            String representation of the specified radial slice type.

        Raises
        ------
        TypeError
            If the input is not a RadialSliceType or str type.
        ValueError
            If the input string is not convertable to a RadialSliceType member.
        """
        if isinstance(slice_type, RadialSliceType):
            return slice_type.name
        if isinstance(slice_type, str):
            for stype in RadialSliceType.__members__:
                if slice_type.lower() == stype.lower():
                    return stype
            raise ValueError('`slice_type` string is not a valid '
                             '`RadialSliceType` member.')
        raise TypeError('`slice_type` must be of type `RadialSliceType` or '
                        'valid string value.')

    def __init__(self, control_id, slice_id, slice_type):
        """Initialize the radial slice.

        Parameters
        ----------
        control_id : str
            Unique ID of the control containing the slice.
        id_ : str
            The display label of the slice.
        slice_type : RadialSliceType
            The subtype of the radial slice.
        """
        super().__init__(control_id, slice_id)
        self._slice_type = RadialSlice._validate_slice_type(slice_type)
        self._category = Slice._validate_slice_category(
            Slice.SliceCategory.radial)

    def get_length(self, units):
        """Get the length (dimension) of the radial slice.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned length value.

        Returns
        -------
        float
            The slice length (dimension) in the requested unit.
        """
        return self.get_dimension(units)

    def set_length(self, value, units):
        """Set the length (dimension) of the radial slice.

        Parameters
        ----------
        value : float
            The new slice length value.
        units : units.Units
            The desired units for the length value.
        """
        self.set_dimension(value, units)

    def get_endpoints(self, units):
        """Get the start and end points of the radial slice.

        Parameters
        ----------
        units : units.Units
            The desired unit for the returned endpoint values.

        Returns
        -------
        tuple of core.Point2D
            The slice endpoints in the requested units.

        See Also
        --------
        get_start, get_end
        """
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'units': _validate_unit(units)}
        endpoints = _get_send_request(_SERVICE, 'GetEndpoints', params)
        return (
            _Point2D(endpoints['m_Item1']['m_Item1'],
                     endpoints['m_Item1']['m_Item2']),
            _Point2D(endpoints['m_Item2']['m_Item1'],
                     endpoints['m_Item2']['m_Item2']))

    def get_start(self, units):
        """Get the start point of the radial slice.

        Parameters
        ----------
        units : units.Units
            The desired unit for the returned start point value.

        Returns
        -------
        core.Point2D
            The slice start point in the requested units.

        Note
        ----
        Equivalent to get_endpoints(units)[0]

        See Also
        --------
        get_end, get_endpoints
        """
        return self.get_endpoints(units)[0]

    def set_start(self, position, units):
        """Set the start point of the radial slice.

        The existing end point remains unchanged.

        Parameters
        ----------
        units : units.Units
            The desired unit for the start point value.
        """
        if not isinstance(position, _Point2D):
            raise TypeError('`position` must be a Point2D value.')
        params = {'controlId': self._control_id,
                  'sliceId': self._id,
                  'sliceCategory': self._category,
                  'sliceType': self._slice_type,
                  'position': {'m_Item1': position.x, 'm_Item2': position.y},
                  'units': _validate_unit(units)}
        _send_request(_SERVICE, 'SetStart', params)

    def get_end(self, units):
        """Get the end point of the radial slice.

        Parameters
        ----------
        units : units.Units
            The desired unit for the returned end point value.

        Returns
        -------
        core.Point2D
            The slice end point in the requested units.

        Note
        ----
        Equivalent to get_endpoints(units)[1]

        See Also
        --------
        get_start, get_endpoints
        """
        return self.get_endpoints(units)[1]


class CircularSlice(Slice):
    """Represents one Mx circular slice.

    Parameters
    ----------
    control_id : str
        Unique ID of the control containing the slice.
    id_ : str
        The display label of the slice.
    slice_type : CircularSliceType
        The subtype of the circular slice.
    """

    @staticmethod
    def _validate_slice_type(slice_type):
        """Validate input as a valid circular slice type.

        Parameters
        ----------
        slice_type : CircularSliceType or str
            Circular slice type to validate.

        Returns
        -------
        str
            String representation of the specified circular slice type.

        Raises
        ------
        TypeError
            If the input is not a CircularSliceType or str type.
        ValueError
            If the input string is not convertable to a CircularSliceType
            member.
        """
        if isinstance(slice_type, CircularSliceType):
            return slice_type.name
        if isinstance(slice_type, str):
            for stype in CircularSliceType.__members__:
                if slice_type.lower() == stype.lower():
                    return stype
            raise ValueError('`slice_type` string is not a valid '
                             '`CircularSliceType` member.')
        raise TypeError('`slice_type` must be of type `CircularSliceType` '
                        'or valid string value.')

    def __init__(self, control_id, slice_id, slice_type):
        """Initialize the circular slice.

        Parameters
        ----------
        control_id : str
            Unique ID of the control containing the slice.
        id_ : str
            The display label of the slice.
        slice_type : CircularSliceType
            The subtype of the circular slice.
        """
        super().__init__(control_id, slice_id)
        self._slice_type = CircularSlice._validate_slice_type(slice_type)
        self._category = Slice._validate_slice_category(
            Slice.SliceCategory.circular)

    def get_radius(self, units):
        """Get the radius (dimension) of the circular slice.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned radius value.

        Returns
        -------
        float
            The slice radius (dimension) in the requested unit.
        """
        return self.get_dimension(units)

    def set_radius(self, value, units):
        """Set the radius (dimension) of the circular slice.

        Parameters
        ----------
        value : float
            The new slice radius value.
        units : units.Units
            The desired units for the radius value.
        """
        return self.set_dimension(value, units)

    def get_center(self, units):
        """Get the center point of the circular slice.

        Parameters
        ----------
        units : units.Units
            Desired unit for the returned center point value.

        Returns
        -------
        core.Point2D
            The slice center point in the requested units.
        """
        return self.get_midpoint(units)

    def set_center(self, position, units):
        """Set the center point of the circular slice.

        Parameters
        ----------
        position : core.Point2D
            The new slice center point value.
        units : units.Units
            The desired unit for the center point value.
        """
        return self.set_midpoint(position, units)

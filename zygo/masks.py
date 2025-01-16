# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx masks functionality.
"""

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.core import Point2D as _Point2D
from zygo.units import _validate_unit


_SERVICE = 'MasksService'
"""str: The service name for the masks module."""


class Mask(object):
    """Represents a single Mx mask.

    Parameters
    ----------
    id_ : str
        The string that uniquely identifies this mask.
    type_ : str
        The type of the mask.
    """

    def __init__(self, id_, type_):
        """Initialize the mask.

        Parameters
        ----------
        id_ : str
            The string that uniquely identifies this mask.
        type_ : str
            The type of the mask.
        """
        self._id = id_
        self._type = type_

    @property
    def center(self):
        """core.Point2D: The masks center (X,Y) coordinate."""
        params = {'maskId': self._id}
        x = _get_send_request(_SERVICE, 'GetCenterX', params)
        y = _get_send_request(_SERVICE, 'GetCenterY', params)
        return _Point2D(x, y)

    @property
    def height(self):
        """float: The height of the mask."""
        params = {'maskId': self._id}
        return _get_send_request(_SERVICE, 'GetHeight', params)

    @property
    def width(self):
        """float: The width of the mask."""
        params = {'maskId': self._id}
        return _get_send_request(_SERVICE, 'GetWidth', params)

    @property
    def type(self):
        """str: The type of the mask."""
        return self._type

    def __str__(self):
        """Return a printable string representation of this mask."""
        return ('type: {self.type}, center: {self.center}, height, width: '
                '{self.height}, {self.width}'.format(self=self))

    def __eq__(self, other):
        """Return True if `other` is equivalent to this object."""
        return (type(self) is type(other) and
                (self._id, self._type) == (other._id, other._type))

    def __ne__(self, other):
        """Return True if `other` is not equivalent to this object."""
        return not self.__eq__(other)

    def move_absolute(self, x, y):
        """Move the center of the mask to the specified absolute (x, y) position.

        Parameters
        ----------
        x : float
            The new mask center x-coordinate.
        y : float
            The new mask center y-coordinate.
        """
        params = {'maskId': self._id, 'x': x, 'y': y}
        _send_request(_SERVICE, 'MoveAbsolute', params)

    def move_relative(self, x, y):
        """Move the center of the mask relative to the current position by the
        specified (x, y) amount.

        Parameters
        ----------
        x : float
            X-offset to move the center.
        y : float
            Y-offset to move the center.
        """
        params = {'maskId': self._id, 'x': x, 'y': y}
        _send_request(_SERVICE, 'MoveRelative', params)

    def resize(self, height, width):
        """Resize the mask to the specified dimensions.

        Parameters
        ----------
        height : float
            The new mask height.
        width : float
            The new mask width.
        """
        params = {'maskId': self._id, 'height': height, 'width': width}
        _send_request(_SERVICE, 'Resize', params)

    def rotate(self, value, unit):
        """Rotate the mask counterclockwise by the specified angle.

        Parameters
        ----------
        value : float
            The mask rotation value.
        unit : units.Units
            Unit for the rotation value.
        """
        unit_str = _validate_unit(unit)
        params = {'maskId': self._id, 'value': value, 'units': unit_str}
        _send_request(_SERVICE, 'Rotate', params)


class Masks(object):
    """Represents a collection of Mx masks."""

    def __init__(self):
        """Initialize the masks collection."""
        self._masks = []
        self._update_masks_list()
        self._pos = 0

    def __iter__(self):
        """The masks collection iterator."""
        self._update_masks_list()
        self._pos = 0
        return self

    def __next__(self):
        """Return the next mask and advance the iterator."""
        if self._pos >= len(self._masks):
            raise StopIteration
        value = self._masks[self._pos]
        self._pos += 1
        return value

    def get_num_masks(self, mask_type=None):
        """Return the number of masks of the specified type.

        Parameters
        ----------
        mask_type : str, optional
            The type of mask; None to query all types.

        Returns
        -------
        int
            The number of masks of the specified type.
        """
        self._update_masks_list()
        if mask_type is None:
            return len(self._masks)
        return len(tuple(
            i for i in self._masks if
            i._type.lower() == mask_type.lower()))

    def save(self, filename):
        """Save the masks to file.

        Parameters
        ----------
        filename : str
            File to save the masks to.
        """
        params = {'fileName': filename}
        _send_request(_SERVICE, 'Save', params)

    def load(self, filename):
        """Load masks from file.

        Parameters
        ----------
        filename : str
            File to load the masks from.
        """
        params = {'fileName': filename}
        _send_request(_SERVICE, 'Load', params)
        self._update_masks_list()

    def delete(self, mask):
        """Remove the specified mask from the collection of Mx masks.

        Parameters
        ----------
        mask : Mask
            The mask to remove.

        Raises
        ------
        RuntimeError
            If the mask could not be found.
        """
        # Find mask in list
        mask_index = next(
            (i for i, m in enumerate(self._masks) if m._id == mask._id), None)
        if mask_index is None:
            raise RuntimeError('Could not find the specified mask.')
        pos = self._pos  # Save iterator position

        # Remove mask, update list
        params = {'maskId': mask._id}
        _send_request(_SERVICE, 'Delete', params)
        self._update_masks_list()

        self._pos = pos  # Restore iterator position
        if mask_index < self._pos:
            self._pos -= 1  # Update to account for removed mask

    def clear(self, mask_type=None):
        """Clear all masks of the specified type.

        Parameters
        ----------
        mask_type : str, optional
            The type of mask to clear, e.g. Acquisition, Surface; None to
            remove all masks.
        """
        if mask_type is None:
            mask_type = ''
        params = {'type': mask_type}
        _send_request(_SERVICE, 'Clear', params)
        self._update_masks_list()

    def get_mask_closest_to(self, x, y, mask_type=None):
        """Get the mask, of the requested type, closest to the specified
        center coordinates.

        Parameters
        ----------
        x : float
            The x-coordinate of the point of interest.
        y : float
            The y-coordinate of the point of interest.
        mask_type : str, optional
            The type of mask to find, e.g. Acquisition, Surface; None to
            search all masks.

        Returns
        -------
        Mask
            The mask closest to the specified point.

        Raises
        ------
        RuntimeError
            If no mask of the requested type is found.
        """
        self._update_masks_list()
        if mask_type is None:
            mask_type = ''
        params = {'x': x, 'y': y, 'type': mask_type}
        mask = _get_send_request(_SERVICE, 'GetMaskClosestTo', params)
        mask = next((m for m in self._masks if mask['m_Item1'] == m._id), None)
        if mask is None:
            raise RuntimeError('Could not find a mask matching the '
                               'specified criteria.')
        return mask

    def _update_masks_list(self):
        """Clear the local masks list and repopulate from Mx."""
        masks_ = _get_send_request(_SERVICE, 'GetMasks', {'type': ''})
        self._masks = [Mask(m['m_Item1'], m['m_Item2']) for m in masks_]
        self._pos = -1

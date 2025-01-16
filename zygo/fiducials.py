# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx fiducials functionality.
"""

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.core import Point2D as _Point2D
from zygo.units import _validate_unit


_SERVICE = 'FiducialsService'
"""str: The service name for the fiducials module."""


class Fiducial(object):
    """Represents one Mx fiducial.

    Parameters
    ----------
    id_ : str
        The string that uniquely identifies this fiducial.
    """

    def __init__(self, id_):
        """Initialize the fiducial.

        Parameters
        ----------
        id_ : str
            The string that uniquely identifies this fiducial.
        """
        self._id = id_

    @property
    def center(self):
        """core.Point2D: The fiducial center (X,Y) coordinate."""
        params = {'fiducialId': self._id}
        x = _get_send_request(_SERVICE, 'GetCenterX', params)
        y = _get_send_request(_SERVICE, 'GetCenterY', params)
        return _Point2D(x, y)

    @property
    def height(self):
        """float: The height of the fiducial."""
        params = {'fiducialId': self._id}
        return _get_send_request(_SERVICE, 'GetHeight', params)

    @property
    def width(self):
        """float: The width of the fiducial."""
        params = {'fiducialId': self._id}
        return _get_send_request(_SERVICE, 'GetWidth', params)

    def __str__(self):
        """Get the printable string representation of this fiducial.

        Returns
        -------
        str
            A printable string representation of this fiducial.
        """
        fmt = 'center: {0.center!s}, height, width: {0.height!s}, {0.width!s}'
        return fmt.format(self)

    def __eq__(self, other):
        """Returns whether or not this fiducial is the same as `other`.

        Returns
        -------
        bool
            True if `other` is the same fiduciual as this fiducial; False
            otherwise.
        """
        return type(self) is type(other) and self._id == other._id

    def __ne__(self, other):
        """Returns whether or not this fiducial is not the same as `other`.

        Returns
        -------
        bool
            True if `other` is not the same fiduciual as this fiducial; False
            otherwise.
        """
        return not self.__eq__(other)

    def move_absolute(self, x, y):
        """Move the center of the fiducial to the specified absolute (x, y)
        position.

        Parameters
        ----------
        x : float
            The new fiducial center x-coordinate.
        y : float
            The new fiducial center y-coordinate.
        """
        params = {'fiducialId': self._id, 'x': x, 'y': y}
        _send_request(_SERVICE, 'MoveAbsolute', params)

    def move_relative(self, x, y):
        """Move the center of the fiducial relative to the current position by
        the specified (x, y) amount.

        Parameters
        ----------
        x : float
            X-offset to move the center.
        y : float
            Y-offset to move the center.
        """
        params = {'fiducialId': self._id, 'x': x, 'y': y}
        _send_request(_SERVICE, 'MoveRelative', params)

    def resize(self, height, width):
        """Resize the fiducial to the specified dimensions.

        Parameters
        ----------
        height : float
            The new fiducial height.
        width : float
            The new fiducial width.
        """
        params = {'fiducialId': self._id, 'height': height, 'width': width}
        _send_request(_SERVICE, 'Resize', params)

    def rotate(self, value, unit):
        """Rotate the fiducial counterclockwise by the specified angle.

        Parameters
        ----------
        value : float
            The fiducial rotation value.
        unit : units.Units
            Unit for the rotation value.
        """
        unit_str = _validate_unit(unit)
        params = {'fiducialId': self._id,
                  'angle': {'m_Item1': value, 'm_Item2': unit_str}}
        _send_request(_SERVICE, 'Rotate', params)


class Fiducials(object):
    """Represents a collection of Mx fiducials."""

    def __init__(self):
        """Initialize the fiducials collection."""
        self._fiducials = []
        self._update_fiducials_list()
        self._pos = 0
        self._working_set = 0

    def __iter__(self):
        """The fiducials collection iterator."""
        self._update_fiducials_list()
        self._pos = 0
        self._working_set = 0
        return self

    def __next__(self):
        """Return the next (working set, fiducial) tuple and advance the
        iterator.
        """
        # Ensure on valid working set
        if self._working_set >= len(self._fiducials):
            raise StopIteration
        # If fiducials exhausted, update working set
        if self._pos >= len(self._fiducials[self._working_set]):
            self._working_set += 1
            self._pos = 0
        # Ensure valid working set, valid fiducials within working set
        if (self._working_set >= len(self._fiducials) or
                self._pos >= len(self._fiducials[self._working_set])):
            raise StopIteration
        value = self._fiducials[self._working_set][self._pos]
        self._pos += 1
        return self._working_set, value

    def get_num_sets(self):
        """Get the number of working sets.

        Returns
        -------
        int
            The number of working sets.
        """
        self._update_fiducials_list()
        return len(self._fiducials)

    def get_num_fiducials(self, working_set=None):
        """Get the number of fiducials in the given working set.

        Parameters
        ----------
        working_set : int or None, optional
            The index of the working set to query; None for all working sets.

        Returns
        -------
        int
            Number of fiducials in the requested working set(s).
        """
        self._update_fiducials_list()
        if working_set is not None:
            return len(self._fiducials[working_set])
        return sum(len(i) for i in self._fiducials)

    # noinspection PyMethodMayBeStatic
    def save(self, filename):
        """Save the fiducials to file.

        Parameters
        ----------
        filename : str
            File to save the fiducials to.
        """
        params = {'fileName': filename}
        _send_request(_SERVICE, 'Save', params)

    def load(self, filename):
        """Load fiducials from file.

        Parameters
        ----------
        filename : str
            File to load fiducials from.
        """
        params = {'fileName': filename}
        _send_request(_SERVICE, 'Load', params)
        self._update_fiducials_list()

    def delete(self, fiducial):
        """Remove the specified fiducial from the collection of Mx fiducials.

        Parameters
        ----------
        fiducial : Fiducial
            The fiducial to remove.
        """
        # Find fiducial in list
        set_index, fid_index = next(
                    ((i, j) for i in range(len(self._fiducials))
                        for j in range(len(self._fiducials[i]))
                        if self._fiducials[i][j]._id == fiducial._id),
                    (None, None))
        if set_index is None or fid_index is None:
            raise RuntimeError('Could not find fiducial.')
        # Save iterator positions
        working_set, pos = self._working_set, self._pos

        # Remove fiducial, update list
        params = {'fiducialId': fiducial._id}
        _send_request(_SERVICE, 'Delete', params)
        self._update_fiducials_list()

        # Restore iterator positions
        self._working_set, self._pos = working_set, pos

        # Adjust iterator positions
        if set_index == self._working_set:
            if fid_index < self._pos:
                self._pos -= 1  # Update to account for removed fiducial

    def clear_set(self, working_set):
        """Clear all fiducials from the specified working set.

        Parameters
        ----------
        working_set : int
            The fiducial working set to clear.
        """
        params = {'workingSet': working_set}
        _send_request(_SERVICE, 'ClearSet', params)
        self._update_fiducials_list()

    def delete_set(self, working_set):
        """Delete the specified working set and all its fiducials.

        Parameters
        ----------
        working_set : int
            The fiducial working set to delete.
        """
        params = {'workingSet': working_set}
        _send_request(_SERVICE, 'DeleteSet', params)
        self._update_fiducials_list()

    def add_set(self):
        """Create a new empty working set."""
        _send_request(_SERVICE, 'AddSet')
        self._update_fiducials_list()

    def get_fiducial_closest_to(self, x, y, working_set=None):
        """Get the working set and fiducial closest to specified center
        coordinate.

        Parameters
        ----------
        x : float
            The x-coordinate of the point of interest.
        y : float
            The y-coordinate of the point of interest.
        working_set : int or None, optional
            The index of the working set to query; None for all working sets.

        Returns
        -------
        tuple of (int, Fiducial)
            The working set and Fiducial closest to the specified point.
        """
        self._update_fiducials_list()
        if working_set is None:
            working_set = -1
        params = {'x': x, 'y': y, 'workingSet': working_set}
        fiducial_ = _get_send_request(_SERVICE, 'GetFiducialClosestTo', params)
        return fiducial_['m_Item1'], Fiducial(fiducial_['m_Item2'])

    def _update_fiducials_list(self):
        """Clear the local fiducials list and repopulate from Mx."""
        params = {'workingSet': -1}
        fiducials_ = _get_send_request(_SERVICE, 'GetFiducials', params)
        self._fiducials = [[Fiducial(id_) for id_ in fiducials_[i]] for
                           i in range(len(fiducials_))]
        self._pos = -1
        self._working_set = -1

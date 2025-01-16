# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************
"""
Provides core functionality for Mx Scripting.
"""


class ZygoError(Exception):
    """Exception generated from Mx or from the connection to Mx."""
    pass


class ZygoTask(object):
    """Represents information pertaining to an asynchronous Mx operation.

    A new ZygoTask object is automatically returned for each asynchronous
    operation. It is not intended for a ZygoTask to be manually created.

    Parameters
    ----------
    task_id
        Unique task identifier.
    done_func
        Function to call for `done` property.
    wait_func
        Function to call for `wait` method.
    """

    def __init__(self, task_id, done_func, wait_func):
        """Initialize task.

        Parameters
        ----------
        task_id
            Unique task identifier.
        done_func
            Function to call for `done` property.
        wait_func
            Function to call for `wait` method.

        """
        self._task_id = task_id
        self._done_func = done_func
        self._wait_func = wait_func
        self._result = None
        self._done = False

    @property
    def done(self):
        """bool: True if the task has completed; False otherwise."""
        # Only set if user waits or gets result successfully; Else ask Mx
        if self._done:
            return True
        return self._done_func(self._task_id)

    def wait(self, timeout=None):
        """Wait for the task to complete.

        Parameters
        ----------
        timeout : int or None, optional
            Maximum time to wait; Defaults to None for infinite wait.
        """
        if not self._done:
            # Expected to wait for result
            self._result = self._wait_func(self._task_id, timeout)
            self._done = True

    def result(self, timeout=None):
        """Return the result of the task after waiting to complete.

        Parameters
        ----------
        timeout : int or None, optional
            Maximum time to wait; Defaults to None for infinite wait.

        Returns
        -------
        object
            The result from the operation, or None for result-less tasks.

        """
        self.wait(timeout)  # Sets self._result
        return self._result


class Point2D(object):
    """Defines a point representing a location in (x, y) coordinate space.

    Parameters
    ----------
    x : int or float
        X-coordinate
    y : int or float
        Y-coordinate
    """

    def __init__(self, x, y):
        """Initialize the 2D point.

        Parameters
        ----------
        x : int or float
            X-coordinate
        y : int or float
            Y-coordinate
        """
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        """Return a printable string representation of this object."""
        return '({0.x!s}, {0.y!s})'.format(self)

    def __repr__(self):
        """Return a string representation of this object."""
        return 'zygo.core.Point2D({0.x!s}, {0.y!s})'.format(self)

    def __eq__(self, other):
        """Return True if `other` is equivalent to this object."""
        return type(self) is type(other) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return True if `other` is not equivalent to this object."""
        return not self.__eq__(other)

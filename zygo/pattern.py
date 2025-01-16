# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx pattern functionality.
"""

from zygo.connectionmanager import send_request as _send_request


_SERVICE = 'PatternService'
"""str: The service name for the pattern module."""


def save(filename):
    """Save the current pattern to file.

    Parameters
    ----------
    filename : str
        File to save the pattern to.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'Save', params)


def load(filename):
    """Load a pattern from file.

    Parameters
    ----------
    filename : str
        File to load the pattern from.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'Load', params)


def load_stitch(filename):
    """Load stitch settings from file.

    Parameters
    ----------
    filename : str
        File to load stitch settings from.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'LoadStitch', params)


def load_and_stitch(folder):
    """Load data from the specified folder and stitch.

    Parameters
    ----------
    folder : str
        Folder name to load data files from.
    """
    params = {'path': str(folder)}
    _send_request(_SERVICE, 'LoadDataAndStitch', params)


def run():
    """Run the current pattern."""
    _send_request(_SERVICE, 'Run')


def prealign():
    """Start pre-alignment on the current pattern."""
    _send_request(_SERVICE, 'PreAlign')


def align():
    """Start alignment on the current pattern."""
    _send_request(_SERVICE, 'Align')

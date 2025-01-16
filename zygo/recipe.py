# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx recipe functionality.
"""

from zygo.connectionmanager import send_request as _send_request


_SERVICE = 'RecipeService'
"""str: The service name for the recipe module."""


def save(filename):
    """Save the current recipe to file.

    Parameters
    ----------
    filename : str
        File to save the recipe to.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'Save', params)


def load(filename):
    """Load a recipe from file.

    Parameters
    ----------
    filename : str
        File to load the recipe from.
    """
    params = {'fileName': filename}
    _send_request(_SERVICE, 'Load', params)


def run():
    """Run the current recipe."""
    _send_request(_SERVICE, 'Run')

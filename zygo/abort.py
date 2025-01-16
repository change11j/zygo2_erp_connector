# -*- coding: utf-8 -*-

# **************************************************************************** 
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# **************************************************************************** 

"""
Supports Mx abort functionality.
"""

from zygo.connectionmanager import send_request as _send_request
import os as _os

_SERVICE = 'AbortService'
"""str: The service name for the abort module."""


def abort():
    """Aborts the current Mx command."""
    pid = _os.getpid()
    _send_request(_SERVICE, 'Abort', {'pid': pid})

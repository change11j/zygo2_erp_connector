# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

import re as _re
from zygo import ui as _ui


# =========================================================================
# ---Constants
# =========================================================================
DEFAULT_BARCODE = ""


# =========================================================================
# ---Custom Exceptions
# =========================================================================
class BarcodeValidationError(Exception):
    """Exception for failed barcode validation."""
    pass


class BarcodeParseError(Exception):
    """Exception for failed barcode string parsing."""
    pass


# =========================================================================
# ---Internal Implementation Methods
# =========================================================================
def _get_regex_pattern():
    """Creates and compiles the regex pattern for simple validation.

    This is a first-order validation that does not capture groups.

    Returns
    -------
    object
        The compiled regular expression object.
    """
    # Unit ID/Barcode: F960G12165321631BSCV6P 7006 CE
    # Supplier Code: F960G
    # Julian Date: 12165
    # Serial No: 321631
    # Part Number: BSCV6P 7006 CE
    re_string = r"""
        [A-Z0-9]{17,}\s[A-Z0-9]+\s[A-Z0-9]+(?:\x1D.+)?
        """
    return _re.compile(re_string, _re.VERBOSE)


def _validate(barcode_string):
    """
    Perform simple barcode validation.

    Parameters
    ----------
    barcode : str
        The scanned barcode string to validate.

    Returns
    -------
    str or None
        The scanned barcode string; None if canceled.

    Raises
    ------
    BarcodeValidationError
        If the barcode string fails validation.
    """
    if barcode_string is not None:
        barcode_match = _regex_pattern.match(barcode_string)
        if not barcode_match:
            raise BarcodeValidationError("Invalid barcode format.")
    return barcode_string


# =========================================================================
# ---Internal Implementation Attributes
# =========================================================================
_regex_pattern = _get_regex_pattern()


# =========================================================================
# ---Public Methods
# =========================================================================
def scan(*, manual_entry=False, validate=True):
    """Prompt the user to scan a barcode.

    Parameters
    ----------
    manual_entry : bool, optional
        True to allow a user to manually enter a barcode string.
    validate : bool, optional
        True to validate barcode prior to returning; False otherwise.

    Returns
    -------
    str or None
        The scanned or typed barcode string; None if canceled.

    Raises
    ------
    BarcodeValidationError
        If the barcode string fails validation.
    """
    barcode_string = None
    if not manual_entry:
        # The prefixKey and suffixKey parameters are string representations
        # of the .Net System.Windows.Forms.Keys enumeration
        params = {
            "text": "Enter:",
            "title": "Scan Barcode",
            "mode": _ui.DialogMode.message_ok_cancel,
            "max_length": 0,
            "prefix_key": "Ctrl+Z",
            "suffix_key": "Ctrl+X"}
        barcode_string = _ui.show_triggered_input_dialog(**params)
    else:
        params = {
            "text": "Enter Barcode:",
            "default_value": DEFAULT_BARCODE,
            "title": "Manual Barcode Entry",
            "mode": _ui.DialogMode.message_ok_cancel,
            "max_length": 0,
            "mask": None}
        barcode_string = _ui.show_masked_input_dialog(**params)
    return _validate(barcode_string)

# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Q-DAS Testplan creation.
"""
# Standard lib imports
import os

# Mx Q-DAS scripting imports
from zygo.qdas import qdas, barcode

# Mx standard scripting imports
from zygo import ui
from zygo import systemcommands as sc
from zygo import mx
from zygo import utils


# =========================================================================
# ---Constants
# =========================================================================
TEST_BARCODE = "F960G16315263059RFHL3P 7006 BC"
barcode.DEFAULT_BARCODE = TEST_BARCODE


# =========================================================================
# ---Private Implementation Methods
# =========================================================================
def _mx_setup():
    """Mx setup and configuration routine for testplan creation.

    Customize this function to automate common Mx setup procedures prior to
    testplan creation.
    """
    mx.clear_script_console()
    mx.reset_data()
    mx.clear_process_stats()

    mx.load_data(r"C:\Users\mlang\Documents\Mx\Data\Samples\Plot3D.datx")


def _get_setup_file_paths():
    """Gets the paths of the new testplan configuration files to create.

    Returns
    -------
    tuple of str
        The TestPlan file path and the Q-DAS parameters file path.
    """
    if qdas.QDAS_SETTINGS.use_default_paths:
        # Create a TestPlan using the default paths
        return (None, None)
    else:
        # Prompt for paths
        ui.show_dialog(
            "Click OK to select the location and name of the new "
            "TestPlan file.",
            ui.DialogMode.message_ok)
        testplan_path = ui.show_file_save_dialog(
            sc.FileTypes.Qdas_TestPlan,
            True,
            qdas.QDAS_SETTINGS.testplan_path,
            True)

        qdas._debug_print("testplan_path: {}".format(testplan_path))

        if utils.is_none_or_whitespace(testplan_path):
            return None

        ui.show_dialog(
            "Click OK to select the location and name of the new "
            "Q-DAS parameters file.",
            ui.DialogMode.message_ok)
        qdas_params_path = ui.show_file_save_dialog(
            sc.FileTypes.Csv,
            True,
            qdas.QDAS_SETTINGS.qdas_params_path,
            True)

        qdas._debug_print("qdas_params_path: {}".format(qdas_params_path))

        if utils.is_none_or_whitespace(qdas_params_path):
            return None

        return (testplan_path, qdas_params_path)


def create_new_testplan(auto_kfields=None):
    # Create a new testplan from the Mx proc stats configuration.
    # ***NOTE: The .TestPlan file path must match the setting file's
    # SpcTestPlan entry, e.g.:
    # "SpcTestPlan": "C:\\ProgramData\\Zygo\\Mx\\qdas\\testplans\\20.testplan"
    try:
        file_paths = _get_setup_file_paths()
        if file_paths is None:
            msg = "Testplan creation aborted."
            qdas._debug_print(msg)
            mx.log_info(msg)
            return None

        # If we get here, and the testplan file exists, the user has already
        # agreed to overwrite the file. This file cannot exist when we call
        # Talyseries SPC to create the testplan, so we'll get rid of it now.
        if os.path.isfile(file_paths[0]):
            os.remove(file_paths[0])

        # Create a TestPlan using the specified paths
        testplan_path = qdas.create_qdas_testplan(
                *file_paths,
                auto_kfields=auto_kfields)
        qdas._debug_print("testplan_path: {}".format(testplan_path))

        return testplan_path
    except Exception as ex:
        msg = "Error creating testplan.\n{}".format(ex)
        qdas._debug_print(msg)
        mx.log_error(msg)
        return None


# =========================================================================
# ---Main Test Method
# =========================================================================
def main():
    """The main function."""

    # Setup Mx with mock data and create a new testplan.
    # If Mx has been manually configured, this call may be commented-out.
    _mx_setup()

    auto_kfields = None
    try:
        auto_kfields = qdas.QDAS_SETTINGS.auto_kfields
    except NameError:
        # Ignore if not defined
        pass

    if create_new_testplan(auto_kfields) is None:
        msg = "Testplan creation aborted."
        qdas._debug_print(msg)
        mx.log_info(msg)
        return None

    qdas._debug_print("Testplan creation completed successfully.")


if __name__ == "__main__":
    mx.clear_script_console()
    main()

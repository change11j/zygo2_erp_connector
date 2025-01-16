# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

import configparser
import os.path
from ast import literal_eval
from collections import OrderedDict, namedtuple

from zygo import mx as _mx

# =========================================================================
# ---Constants
# =========================================================================
CONFIG_PATH = r"C:\ProgramData\Zygo\Mx\Utilities\Q-DAS\qdas_config.ini"
# Configuration sections
GLOBAL_SETTINGS = "Global Settings"
QDAS_SETTINGS = "Q-DAS Settings"
AUTO_KFIELDS = "Auto K-Fields"
STUDY_SETTINGS = "Q-DAS Study Settings"
QLSCM_SETTINGS = "QLS-CM Settings"

# =========================================================================
# ---Named Tuples
# =========================================================================
MxTestPlanSettings = namedtuple('MxTestPlanSettings',
                                ['Name',
                                 'MxApplication',
                                 'MxSettings',
                                 'MxRecipe',
                                 'MxScript',
                                 'SpcTestPlan'])


class QdasConfiguration(object):
    # =========================================================================
    # ---Internal Implementation Methods
    # =========================================================================
    def _read_configuration(self):
        config = configparser.ConfigParser()
        try:
            config.read(["qdas_config.ini",
                         CONFIG_PATH,
                         os.path.expanduser(
                                 r"~\Documents\Mx\Settings\qdas_config.ini")])
            if (config is None or
                    (len(config.sections()) == 0 and
                     len(config.defaults()) == 0)):
                raise Exception("No configuration found.")
            return config
        except Exception as ex:
            msg = "Unable to read configuration file '{}'.\n{}".format(
                    CONFIG_PATH, ex)
            _mx.log_warn(msg)
            return None

    # =========================================================================
    # ---Initialization
    # =========================================================================
    def __init__(self):
        self._config = self._read_configuration()

    # =========================================================================
    # ---Public Properties
    # =========================================================================
    @property
    def configuration(self):
        """configparser.ConfigParser: The raw configuration data."""
        return self._config

    # =========================================================================
    # ---Global Settings
    # =========================================================================
    @property
    def spc_exe_path(self):
        """str: Path to the TalyseriesSPC executable."""
        ret = None
        if self._config is not None:
            ret = self._config.get(GLOBAL_SETTINGS,
                                   "spc_exe_path",
                                   fallback=None)
        return ret

    @property
    def qdas_params_path(self):
        """str: Default Q-DAS parameters (.csv) file path for testplan
        creation.
        """
        ret = None
        if self._config is not None:
            ret = self._config.get(GLOBAL_SETTINGS,
                                   "qdas_params_path",
                                   fallback=None)
        return ret

    @property
    def testplan_path(self):
        """str: Default Talyseries SPC test plan (.TestPlan) file path."""
        ret = None
        if self._config is not None:
            ret = self._config.get(GLOBAL_SETTINGS,
                                   "testplan_path",
                                   fallback=None)
        return ret

    @property
    def qdas_results_path(self):
        """str: Default process statistics Q-DAS results (.csv) file path."""
        ret = None
        if self._config is not None:
            ret = self._config.get(GLOBAL_SETTINGS,
                                   "qdas_results_path",
                                   fallback=None)
        return ret

    @property
    def ps_grid_path(self):
        """tuple of str: Mx identify path for the Q-DAS-configured proc stats
        grid.
        """
        ret = None
        if self._config is not None:
            ret = self._config.get(GLOBAL_SETTINGS,
                                   "ps_grid_path",
                                   fallback=None)
            try:
                return literal_eval(ret)
            except Exception:
                return None
        return ret

    @property
    def use_default_paths(self):
        """bool: Whether or not to use the default file paths."""
        ret = None
        if self._config is not None:
            ret = self._config.getboolean(GLOBAL_SETTINGS,
                                          "use_default_paths",
                                          fallback=False)
        return ret

    @property
    def backup_files(self):
        """bool: Whether or not to backup proc stats outputs before processing.
        """
        ret = None
        if self._config is not None:
            ret = self._config.getboolean(GLOBAL_SETTINGS,
                                          "backup_files",
                                          fallback=True)
        return ret

    @property
    def debug(self):
        """bool: True to enable debug output."""
        ret = None
        if self._config is not None:
            ret = self._config.getboolean(GLOBAL_SETTINGS,
                                          "debug",
                                          fallback=False)
        return ret

    @property
    def spc_prompt(self):
        """bool: True to instruct Talyseries SPC to prompt for input after
        measure.
        """
        ret = None
        if self._config is not None:
            ret = self._config.getboolean(GLOBAL_SETTINGS,
                                          "spc_prompt",
                                          fallback=False)
        return ret

    # =========================================================================
    # ---Q-DAS Study Settings
    # =========================================================================
    @property
    def type1_references(self):
        """int: Number of reference measurements for Type 1 studies."""
        ret = None
        if self._config is not None:
            ret = self._config.getint(STUDY_SETTINGS,
                                      "type1_references",
                                      fallback=50)
        return ret

    @property
    def type2_parts(self):
        """int: Number of parts for Type 2 studies."""
        ret = None
        if self._config is not None:
            ret = self._config.getint(STUDY_SETTINGS,
                                      "type2_parts",
                                      fallback=5)
        return ret

    @property
    def type2_operators(self):
        """int: Number of operators for Type 2 studies."""
        ret = None
        if self._config is not None:
            ret = self._config.getint(STUDY_SETTINGS,
                                      "type2_operators",
                                      fallback=2)
        return ret

    @property
    def type2_trials(self):
        """int: Number of trials for Type 2 studies."""
        ret = None
        if self._config is not None:
            ret = self._config.getint(STUDY_SETTINGS,
                                      "type2_trials",
                                      fallback=3)
        return ret

    @property
    def type3_parts(self):
        """int: Number of parts for Type 3 studies."""
        ret = None
        if self._config is not None:
            ret = self._config.getint(STUDY_SETTINGS,
                                      "type3_parts",
                                      fallback=5)
        return ret

    @property
    def type3_trials(self):
        """int: Number of trials for Type 3 studies."""
        ret = None
        if self._config is not None:
            ret = self._config.getint(STUDY_SETTINGS,
                                      "type3_trials",
                                      fallback=3)
        return ret

    # =========================================================================
    # ---QLS-CM Settings
    # =========================================================================
    @property
    def birth_history_catalog(self):
        """str: Path to the Ford birth history/barcode catalog."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QLSCM_SETTINGS,
                                   "birth_history_catalog",
                                   fallback=None)
        return ret

    @property
    def operation_id(self):
        """str: Operation ID(s) to query."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QLSCM_SETTINGS,
                                   "operation_id",
                                   fallback="ALL")
        return ret

    @property
    def station_id(self):
        """str: Station ID(s) to query."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QLSCM_SETTINGS,
                                   "station_id",
                                   fallback="ALL")
        return ret

    @property
    def data_id(self):
        """str: Data ID(s) to query."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QLSCM_SETTINGS,
                                   "data_id",
                                   fallback="")
        return ret

    @property
    def accept_result_code(self):
        """str: The QLS-CM result code for Accept."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QLSCM_SETTINGS,
                                   "accept_result_code",
                                   fallback="")
        return ret

    @property
    def reject_result_code(self):
        """str: The QLS-CM result code for Reject."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QLSCM_SETTINGS,
                                   "reject_result_code",
                                   fallback="")
        return ret

    # =========================================================================
    # ---Q-DAS Settings
    # =========================================================================
    @property
    def serial_number_field(self):
        """str: The K-Field representing the part serial number."""
        ret = None
        if self._config is not None:
            ret = self._config.get(QDAS_SETTINGS,
                                   "serial_number_field",
                                   fallback="K0006")
        return ret

    # =========================================================================
    # ---Auto K-Fields
    # =========================================================================
    @property
    def auto_kfields(self):
        """collections.OrderedDict: K-Fields, with their default values, which
        will be automatically populated during test plan creation and
        execution.
        """
        if self._config is not None and self._config.has_section(AUTO_KFIELDS):
            try:
                return OrderedDict(self._config.items(AUTO_KFIELDS))
            except Exception:
                return None
        return None

    # =========================================================================
    # ---Mx Test Plans
    # =========================================================================
    @property
    def mx_test_plans(self):
        """list of `MxTestPlanSettings`: List of configured test plan settings.
        """
        if self._config is None:
            return None
        sections = [GLOBAL_SETTINGS,
                    AUTO_KFIELDS,
                    STUDY_SETTINGS,
                    QLSCM_SETTINGS]
        plan_names = [s for s in self._config.sections() if s not in sections]
        testplans = []
        for p in plan_names:
            mx_application = self._config.get(p,
                                              "mx_application",
                                              fallback=None)
            mx_settings = self._config.get(p,
                                           "mx_settings",
                                           fallback=None)
            mx_recipe = self._config.get(p,
                                         "mx_recipe",
                                         fallback=None)
            mx_script = self._config.get(p,
                                         "mx_script",
                                         fallback=None)
            spc_test_plan = self._config.get(p,
                                             "spc_test_plan",
                                             fallback=None)
            testplans.append(MxTestPlanSettings(
                    p,
                    mx_application,
                    mx_settings,
                    mx_recipe,
                    mx_script,
                    spc_test_plan))
        return testplans

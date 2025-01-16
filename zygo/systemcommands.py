# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports basic system commands on the Mx host.
"""
from enum import Enum

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request


_SERVICE = 'SystemCommandsService'
"""str: The service name for this module."""


# =============================================================================
# ---Enumerations
# =============================================================================
class _AutoNumber(Enum):
    """Helper class to allow creating enums without explicit numbering."""
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class FileTypes(_AutoNumber):
    """Mx-supported file types.

    Notes
    -----
    These file types are the available types in DirectoryMapConfig.xml.
    """
    All = ()
    UI_Application = ()
    Script = ()
    Csv = ()
    Swli = ()
    AFC_Measurement = ()
    ShortTerm = ()
    DeltaPsi = ()
    Bin = ()
    Xml = ()
    Setting = ()
    Application = ()
    Data = ()
    Signal_Data = ()
    Programming = ()
    Application_Reference = ()
    VisionPro_Persistance = ()
    Image = ()
    Recipe = ()
    Result = ()
    Text = ()
    Mask = ()
    Fiducial = ()
    Zernike = ()
    Average = ()
    Proc_Stats = ()
    Logging = ()
    Slice = ()
    Region = ()
    Region_Stats = ()
    Cal_Data = ()
    Cal_Data_Archive = ()
    Pattern = ()
    Stitch = ()
    Qdas_TestPlan = ()


def _get_file_types_dict():
    """Gets the mapping of FileType members to Mx file type strings.

    Mx file types may have spaces in them, but Enum values cannot. This
    function return a dictionary which maps FileTypes containing spaces to the
    correct Mx string representation.

    Returns
    -------
    dict
        The mapping of FileType members to Mx file type string.
    """
    return {
        FileTypes.UI_Application: "UI Application",
        FileTypes.AFC_Measurement: "AFC Measurement",
        FileTypes.Signal_Data: "Signal Data",
        FileTypes.Application_Reference: "Application Reference",
        FileTypes.VisionPro_Persistance: "VisionPro Persistance",
        FileTypes.Proc_Stats: "Proc Stats",
        FileTypes.Region_Stats: "Region Stats",
        FileTypes.Cal_Data: "Cal Data",
        FileTypes.Cal_Data_Archive: "Cal Data Archive",
        FileTypes.Qdas_TestPlan: "Qdas TestPlan"}


def _validate_file_type(file_type):
    """Validate input as a valid file type value.

    Parameters
    ----------
    file_type : FileTypes or str
        File type to validate.

    Returns
    -------
    str
        String representation of the specified file type.

    Raises
    ------
    TypeError
        If the input is not a FileTypes or str type.
    ValueError
        If the input string is not convertable to a FileTypes member.
    """
    if isinstance(file_type, FileTypes):
        return _get_file_types_dict().get(file_type, file_type.name)
    if isinstance(file_type, str):
        # First check if the supplied string matches a FileTypes member name
        for ftype in FileTypes.__members__:
            if file_type.lower() == ftype.lower():
                return _validate_file_type(FileTypes[ftype])
        # No luck -- now check if the supplied string is in the dictionary
        for k, v in _get_file_types_dict().items():
            if file_type.lower() == v.lower():
                return _validate_file_type(k)
        raise ValueError(
            '`file_type` string is not a valid `FileTypes` member.')
    raise TypeError(
        '`file_type` must be of type `FileTypes` or valid string value.')


# =============================================================================
# ---Directories Information
# =============================================================================
def get_bin_dir():
    """Gets the directory path containing the Mx executable.

    Returns
    -------
    str
        The absolute path to the Mx bin directory.
    """
    return _get_send_request(_SERVICE, 'GetBinDir')


def get_working_dir():
    """Gets the current working directory of the host Mx process.

    Returns
    -------
    str
        The absolute path to the Mx working directory.
    """
    return _get_send_request(_SERVICE, 'GetWorkingDir')


def get_open_dir(file_type):
    """Gets the directory path for the given file type that Mx uses for
    opening a file.

    Parameters
    ----------
    file_type : FileTypes
        The file type to query.

    Returns
    -------
    str
        The absolute path to the open directory for the specified file type.
    """
    file_type_str = _validate_file_type(file_type)
    params = {'fileType': file_type_str}
    return _get_send_request(_SERVICE, 'GetOpenDir', params)


def get_save_dir(file_type):
    """Gets the directory path for the given file type that Mx uses for
    saving a file.

    Parameters
    ----------
    file_type : FileTypes
        The file type to query.

    Returns
    -------
    str
        The absolute path to the save directory for the specified file type.
    """
    file_type_str = _validate_file_type(file_type)
    params = {'fileType': file_type_str}
    return _get_send_request(_SERVICE, 'GetSaveDir', params)


def set_open_dir(file_type, path):
    """Sets the directory path for the given file type that Mx uses for
    opening a file.

    Parameters
    ----------
    file_type : FileTypes
        The file type to set.
    path : str
        The absolute path to the open directory to set for the specified
        file type.
    """
    file_type_str = _validate_file_type(file_type)
    params = {'fileType': file_type_str, 'path': path}
    _send_request(_SERVICE, 'SetOpenDir', params)


def set_save_dir(file_type, path):
    """Set the directory path for the given file type that Mx uses for
    saving a file.

    Parameters
    ----------
    file_type : FileTypes
        The file type to set.
    path : str
        The absolute path to the save directory to set for the specified
        file type.
    """
    file_type_str = _validate_file_type(file_type)
    params = {'fileType': file_type_str, 'path': path}
    _send_request(_SERVICE, 'SetSaveDir', params)


def list_files_in_open_dir(file_type):
    """Returns a list of all the files of the specified type in the type's
    current open directory.

    Parameters
    ----------
    file_type : FileTypes
        The file type to query.

    Returns
    -------
    list of str
        A list of absolute file paths of the requested type in the
        corresponding open directory.
    """
    file_type_str = _validate_file_type(file_type)
    params = {'fileType': file_type_str}
    return _get_send_request(_SERVICE, 'ListFilesInOpenDir', params)


def list_files_in_dir(directory, extensions, recursive=False):
    """Gets a list of all files in the specified directory that match the
    given list of extensions.

    Parameters
    ----------
    directory : str
        The directory to search.
    extensions : list of str
        A list of extensions to match.
    recursive : bool
        True to search the directory and all subdirectories; False otherwise.

    Returns
    -------
    list of str
        A list of absolute file paths in the specified directory.
    """
    params = {'directory': directory,
              'extensions': extensions,
              'recursive': recursive}
    return _get_send_request(_SERVICE, 'ListFilesInDir', params)


# =============================================================================
# ---Host Information
# =============================================================================
def get_ram_size():
    """Gets the amount of private memory allocated for Mx, in bytes, that
    cannot be shared with other processes.

    Returns
    -------
    int
        The amount of private memory, in bytes, allocated for Mx.
    """
    return _get_send_request(_SERVICE, 'GetRamSize')


def get_os_name():
    """Gets the operating system name of the Mx host computer.

    Returns
    -------
    str
        The host operating system name.
    """
    return _get_send_request(_SERVICE, 'GetOSName')


def get_computer_name():
    """Gets the computer name of the Mx host computer.

    Returns
    -------
    str
        The host computer name.
    """
    return _get_send_request(_SERVICE, 'GetComputerName')


# =============================================================================
# ---Internal Support Methods
# =============================================================================
def _execute_command(service, command, args):
    """Execute a public non-API method.

    This method is for internal use, and is not intended to be called by
    end-user scripts.
    """
    params = {'service': service, 'method': command, 'args': args}
    return _get_send_request(_SERVICE, 'ExecuteCommand', params)


def _exec_command(service, command, params, decode=True):
    """Execute a public API method.

    This method is for internal use, and is not intended to be called by
    end-user scripts.
    """
    return _send_request(service, command, params, decode=decode)


def _noop():
    _send_request(_SERVICE, 'NoOp')

# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports Mx user interface functionality.
"""
from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from enum import IntEnum as _IntEnum
from datetime import datetime as _datetime
import warnings as _warnings

from zygo.connectionmanager import send_request as _send_request
from zygo.connectionmanager import get_send_request as _get_send_request
from zygo.systemcommands import _validate_file_type
from zygo.units import _validate_unit, Units as _Units
from zygo import _charts as charts


_SERVICE = 'UserInterfaceService'
"""str: The service name for the ui module."""


# =============================================================================
# ---Modal Dialogs
# =============================================================================
class DialogMode(_IntEnum):
    """Dialog window modes. Defines which buttons and icons to be displayed in
    the dialog.
    """
    message_ok = 1
    error_ok = 2
    warning_ok = 3
    confirm_yes_no = 4
    error_ok_cancel = 5
    warning_yes_no = 6
    message_ok_cancel = 7


def _validate_dialog_mode(dialog_mode):
    """Validate input as a valid dialog mode value.

    Parameters
    ----------
    dialog_mode : DialogMode or str
        Dialog mode to validate.

    Returns
    -------
    str
        String representation of the specified dialog mode.

    Raises
    ------
    TypeError
        If the input is not a DialogMode or str type.
    ValueError
        If the input string is not convertable to a DialogMode member.

    """
    if isinstance(dialog_mode, DialogMode):
        return dialog_mode.name
    if isinstance(dialog_mode, str):
        for dmode in DialogMode.__members__:
            if dialog_mode.lower() == dmode.lower():
                return dmode
        raise ValueError(
            '`dialog_mode` string is not a valid `DialogMode` member.')
    raise TypeError(
        '`dialog_mode` must be of type `DialogMode` '
        'or valid string value.')


class Font(object):
    """Defines a Font to be used in various operations.

    Parameters
    ----------
    font_family : str
        The name of the font, e.g., "Tahoma", "Comic Sans MS".
    font_size : int or float
        The em size of the font.
    font_style : FontStyle
        The style of the font.
    """

    class FontStyle(_IntEnum):
        """Valid font styles."""
        bold = 1
        italic = 2
        regular = 3
        strikeout = 4
        underline = 5

    @staticmethod
    def _validate_font_style(font_style):
        """Validate input as a valid font style value.

        Parameters
        ----------
        font_style : Font.FontStyle or str
            Font style to validate.

        Returns
        -------
        str
            String representation of the specified font style.

        Raises
        ------
        TypeError
            If the input is not a Font.FontStyle or str type.
        ValueError
            If the input string is not convertable to a Font.FontStyle member.

        """
        if isinstance(font_style, Font.FontStyle):
            return font_style.name
        if isinstance(font_style, str):
            for fstyle in Font.FontStyle.__members__:
                if font_style.lower() == fstyle.lower():
                    return fstyle
            raise ValueError(
                '`font_style` string is not a valid `Font.FontStyle` member.')
        raise TypeError(
            '`font_style` must be of type `Font.FontStyle` '
            'or valid string value.')

    def __init__(self, font_family, font_size, font_style):
        """Initialize the font.

        Parameters
        ----------
        font_family : str
            The name of the font, e.g., "Tahoma", "Comic Sans MS".
        font_size : int or float
            The em size of the font.
        font_style : FontStyle
            The style of the font.
        """
        self.font_family = font_family
        self.font_size = float(font_size)
        self.font_style = Font._validate_font_style(font_style)

    def to_dict(self):
        """Create a serializable dictionary containing this Font's properties.
        """
        return {'FontFamily': self.font_family,
                'FontSize': self.font_size,
                'FontStyle': self.font_style}


def show_dialog(text, mode, seconds=None, *,
                title=None, message_font=None, button_font=None):
    """Show a dialog with specified text and mode.

    Specify a duration to display a timed dialog. Timed dialogs have no
    buttons, and automatically close after the time has elapsed.

    Parameters
    ----------
    text : str
        Message text to display in the dialog.
    mode : DialogMode
        The desired dialog mode.
    seconds : int, optional
        The number of seconds to show for timed dialogs. Defaults to None to
        wait for user acknowledgement.
    title : str, optional
        Text to display as the dialog title. Use None for the Mx default value.
    message_font : Font, optional
        The font family, size, and style to use for the displayed text.
    button_font : Font, optional
        The font family, size, and style to use for the displayed buttons.

    Returns
    -------
    bool
        The result of the dialog interaction. Timed dialogs do not return
        a value.

        Yes and OK buttons result in a True value; No and Cancel buttons
        return False.
    """
    mode_val = DialogMode[_validate_dialog_mode(mode)].value
    params = {'text': text, 'mode': mode_val}
    if seconds is None:
        if not (message_font or button_font):
            return _get_send_request(_SERVICE, 'ShowDialog', params)
        else:
            if not message_font:
                message_font = Font("Microsoft Sans Serif",
                                    8.25,
                                    Font.FontStyle.regular)
            if not button_font:
                button_font = Font("Microsoft Sans Serif",
                                   8.25,
                                   Font.FontStyle.regular)
            params.update({'title': title,
                           'messageFont': message_font.to_dict(),
                           'buttonFont': button_font.to_dict()})

            return _get_send_request(_SERVICE, 'ShowFormattedDialog', params)
    else:
        params['seconds'] = seconds
        _send_request(_SERVICE, 'ShowTimedDialog', params)


def show_input_dialog(text, default_value, mode, max_length=0, *,
                      title=None, message_font=None, button_font=None,
                      input_font=None):
    """Show a dialog requesting user input.

    Parameters
    ----------
    text : str
        Message text to display in the dialog.
    default_value : str
        Default value to show in the user input field.
    mode : DialogMode
        The desired dialog mode.
    max_length : int, optional
        Maximum length for the user input field. Defaults to 0 for no limit.
    title : str, optional
        Text to display as the dialog title. Use None for the Mx default value.
    message_font : Font, optional
        The font family, size, and style to use for the displayed text.
    button_font : Font, optional
        The font family, size, and style to use for the displayed buttons.
    input_font : Font, optional
        The font family, size, and style to use for the text input box.

    Returns
    -------
    str
        The user input value. Dismissed/canceled dialogs return None.
    """
    mode_val = DialogMode[_validate_dialog_mode(mode)].value
    params = {'text': text,
              'defaultValue': default_value,
              'mode': mode_val,
              'maxLength': max_length}

    # set defaults
    if not message_font:
        message_font = Font("Microsoft Sans Serif",
                            8.25,
                            Font.FontStyle.regular)
    if not button_font:
        button_font = Font("Microsoft Sans Serif",
                           8.25,
                           Font.FontStyle.regular)

    if not input_font:
        input_font = Font("Microsoft Sans Serif",
                          8.25,
                          Font.FontStyle.regular)

    params.update({'title': title,
                   'messageFont': message_font.to_dict(),
                   'buttonFont': button_font.to_dict(),
                   'inputFont': input_font.to_dict()})

    return _get_send_request(_SERVICE, 'ShowFormattedInputDialog', params)


def show_masked_input_dialog(text,
                             default_value,
                             title,
                             mode,
                             max_length,
                             mask,
                             use_regex=False):
    r"""Show a dialog requesting user input using the specified input mask.

    Parameters
    ----------
    text : str
        Message text to display in the dialog.
    default_value : str
        Default value to show in the user input field.
    title : str
        Text to display as the dialog title. Use None for the Mx default value.
    mode : DialogMode
        The desired dialog mode.
    max_length : int
        Maximum length for the user input field. Set to 0 for no limit.
    mask : str
        The mask to be applied to the input box.
    use_regex : bool
        True to use regular expressions in the mask.

    Returns
    -------
    str
        The user input value. Dismissed/canceled dialogs return None.

    Notes
    -----
    Input mask strings can either be regular expressions (when use_regex is
    True), or simple masks. Simple masks consist of metacharacters, special
    characters, and literal characters.

    Metacharacters:
        L   An L character requires an alphabetic character in this position.
            For the U.S. this is A-Z, a-z.
        l	  An l character permits only an alphabetic character in this
            position, but doesn't require it.
        A	  An A character requires an alphanumeric character in this position.
            For the U.S. this is A-Z, a-z, 0-9.
        a	  An a character permits only an alphanumeric character in this
            position, but doesn't require it.
        C	  A C character requires an arbitrary character in this position.
        c	  A c character permits an arbitrary character in this position, but
            doesn't require it.
        0	  A 0 character requires a numeric character in this position.
        9	  A 9 character permits only a numeric character in this position,
            but doesn't require it.
        #	  A # character permits only a numeric character or a plus or minus
            sign in this position, but doesn't require it.

    Special characters:
        >	  If a > character appears in the mask, all the characters that
            follow  it are converted to uppercase until the end of the mask or
            until a < character is encountered.
        <	  If a < character appears in the mask, all the characters that
            follow it are converted to lowercase until the end of the mask or
            until a > character is encountered.
        <>	  If these two characters appear together in a mask, no case
            checking is performed and the data is formatted with the case used
            by the end-user during data entry.
        /	  A / character is used to separate the months, days, and years in
            dates. If the character that separates the months, days, and years
            is different in the regional settings of the system that the
            application runs on that character will be used instead.
        :	  A : character is used to separate the hours, minutes, and seconds
            in time values. If the character that separates the hours, minutes,
            and seconds is different in the regional settings of the system
            that the application runs on that character will be used instead.
        $	  A $ character is used to designate currency values. If the
            character that designates the currency values is different in the
            regional settings of the system that the application runs on that
            character is used instead.

    Literal characters:
        A character that is neither a metacharacter nor a special character is
        called a literal. Literals are inserted automatically as is into the
        edit box in their positions defined by the mask. An end-user has no
        need to enter literal characters. The cursor skips over them during
        editing.

        The metacharacters and special characters can also appear as literal
        characters if they are preceded by a backslash (\).
    """
    mode_val = DialogMode[_validate_dialog_mode(mode)].value
    params = {'text': text,
              'defaultValue': default_value,
              'title': title,
              'mode': mode_val,
              'maxLength': max_length,
              'mask': mask,
              'useRegEx': use_regex}
    return _get_send_request(_SERVICE, 'ShowMaskedInputDialog', params)


def show_triggered_input_dialog(text,
                                title,
                                mode,
                                max_length,
                                prefix_key,
                                suffix_key):
    """Show a dialog requesting user input.

    Parameters
    ----------
    text : str
        Message text to display in the dialog.
    title : str
        Text to display as the dialog title. Use None for the Mx default value.
    mode : DialogMode
        The desired dialog mode.
    max_length : int
        Maximum length for the user input field. Set to 0 for no limit.
    prefix_key : str
        The key required to enable dialog input. Must be the string
        representation of a valid .Net System.Windows.Forms.Keys enumeration
        member.
    suffix_key :
        The key required to automatically accept the dialog. Must be the string
        representation of a valid .Net System.Windows.Forms.Keys enumeration
        member.

    Returns
    -------
    str
        The user input value. Dismissed/canceled dialogs return None.

    Note
    ----
    This dialog type is designed to be used with keyboard wedge devices, e.g.,
    barcode scanners.
    """
    params = {
        "text": text,
        "title": title,
        "mode": DialogMode[_validate_dialog_mode(mode)].value,
        "maxLength": max_length,
        "prefixKey": prefix_key,
        "suffixKey": suffix_key}
    return _get_send_request(_SERVICE, "ShowTriggeredInputDialog", params)


def show_dropdown_dialog(text, selection_values, mode, *,
                         title=None, message_font=None, button_font=None,
                         selection_font=None):
    """Show a dialog requesting user selection from a dropdown control.

    Parameters
    ----------
    text : str
        Message text to display in the dialog.
    selection_values : list of str
        List of values to add to the dropdown control, in display order.
    mode : DialogMode
        The desired dialog mode.
    title : str, optional
        Text to display as the dialog title. Use None for the Mx default value.
    message_font : Font, optional
        The font family, size, and style to use for the displayed text.
    button_font : Font, optional
        The font family, size, and style to use for the displayed buttons.
    selection_font : Font, optional
        The font family, size, and style to use for the dropdown box.

    Returns
    -------
    int
        The zero-based index of the selected item. Dismissed/canceled dialogs
        return -1.
    """
    mode_val = DialogMode[_validate_dialog_mode(mode)].value
    params = {'text': text,
              'selectionValues': selection_values,
              'mode': mode_val}

    # set defaults
    if not message_font:
        message_font = Font("Microsoft Sans Serif",
                            8.25,
                            Font.FontStyle.regular)
    if not button_font:
        button_font = Font("Microsoft Sans Serif",
                           8.25,
                           Font.FontStyle.regular)

    if not selection_font:
        selection_font = Font("Microsoft Sans Serif",
                              8.25,
                              Font.FontStyle.regular)

    params.update({'title': title,
                   'messageFont': message_font.to_dict(),
                   'buttonFont': button_font.to_dict(),
                   'selectionFont': selection_font.to_dict()})

    return _get_send_request(_SERVICE, 'ShowFormattedDropdownDialog', params)


def show_file_open_dialog(filetype,
                          make_dir_primary=False,
                          allow_multiselect=False):
    """Display an Mx file open dialog for the specified type.

    Parameters
    ----------
    filetype : systemcommands.FileTypes
        The file type to use for the dialog.
    make_dir_primary : bool, optional
        True to set the selected directory as the default open directory for
        the type.
    allow_multiselect : bool, optional
        True to allow multiple file selections in the dialog. Default to False
        to allow a single selection.

    Returns
    -------
    list of str
        List of selected file paths. Dismissed/canceled dialogs return None.
    """
    type_string = _validate_file_type(filetype)
    params = {'type': type_string,
              'makeDirPrimary': make_dir_primary,
              'allowMultiselect': allow_multiselect}
    return _get_send_request(_SERVICE, 'ShowFileOpenDialog', params)


def show_file_save_dialog(filetype,
                          make_dir_primary=False,
                          default_file='',
                          overwrite_prompt=True):
    """Display an Mx file save dialog for the selected type.

    Parameters
    ----------
    filetype : systemcommands.FileTypes
        The file type to use for the dialog.
    make_dir_primary : bool, optional
        True to set the selected directory as the default save directory for
        the type.
    default_file : str, optional
        The default filename to use in the save file dialog; use the empty
        string for no default filename.
    overwrite_prompt : bool
        True to display a warning if the selected file already exists; False
        otherwise.

    Returns
    -------
    str
        The selected file path. Dismissed/canceled dialogs return None.
    """
    type_string = _validate_file_type(filetype)
    params = {'type': type_string,
              'makeDirPrimary': make_dir_primary,
              'defaultFile': default_file,
              'overwritePrompt': overwrite_prompt}
    return _get_send_request(_SERVICE, 'ShowFileSaveDialog', params)


# =============================================================================
# ---Window Access Methods
# =============================================================================
def show_mask_editor():
    """Display the main Mx mask editor.

    Returns
    -------
    Window
        A `Window` object representing the mask editor.
    """
    _send_request(_SERVICE, 'ShowMaskEditor')
    return Window('Mask Editor')


def show_fiducial_editor():
    """Display the Mx fiducial editor.

    Returns
    -------
    Window
        A `Window` object representing the fiducial editor.
    """
    _send_request(_SERVICE, 'ShowFiducialEditor')
    return Window('Fiducial Editor')


def _get_supported_windows():
    """Get the names of the Mx windows supported by scripting.

    Returns
    -------
    tuple of str
        The names of the supported windows.
    """
    return tuple(_get_send_request(_SERVICE, 'GetSupportedWindows'))


# =============================================================================
# ---Toolbar Methods
# =============================================================================
def click_toolbar_item(path):
    """Click a top-level Mx toolbar item.

    Parameters
    ----------
    path : tuple of str
        The path to the toolbar item.
    """
    params = {'buttonPath': path}
    _send_request(_SERVICE, 'ClickToolbarButton', params)


# =============================================================================
# ---Image Grid Methods
# =============================================================================
def set_image_grid(control, image_path):
    """Specify the image to show in the image grid.

    Parameters
    ----------
    control : Control
        The image grid control to set.
    image_path : str
        The full path of the image file.
    """
    params = {'controlId': control._id, 'imagePath': image_path}
    _send_request(_SERVICE, 'SetImageGrid', params)


# =============================================================================
# ---Plot Palette Methods
# =============================================================================
class Palette(_IntEnum):
    """Available plot palette selections."""
    Spectrum = 0
    RWB = 1
    Grey = 2
    CMYK = 3
    IcyCool = 4
    Neon = 5
    RedHot = 6
    Bands = 7
    Gold = 8
    Red = 9
    Binary = 10


def _validate_palette(palette):
    """Validate input as a valid palette value.

    Parameters
    ----------
    palette : Palette or str
        Palette type to validate.

    Returns
    -------
    str
        String representation of the specified palette type.

    Raises
    ------
    TypeError
        If the input is not a Palette or str type.
    ValueError
        If the input string is not convertable to a Palette member.
    """
    if isinstance(palette, Palette):
        return palette.name
    if isinstance(palette, str):
        for pal in Palette.__members__:
            if palette.lower() == pal.lower():
                return pal
        raise ValueError('`palette` string is not a valid `Palette` member.')
    raise TypeError(
        '`palette` must be of type `Palette` or valid string value.')


def set_plot_palette(control, palette_name=Palette.Spectrum):
    """Set the palette of the specified plot.

    Parameters
    ----------
    control : Control
        The plot control to set.
    palette_name : Palette, optional
        The palette to use in the plot.
    """
    params = {'controlId': control._id,
              'paletteName': _validate_palette(palette_name)}
    _send_request(_SERVICE, 'SetPlotPalette', params)


class PaletteScaleMode(_IntEnum):
    """Available plot palette modes."""
    PV = 0
    Auto = 1
    ThreeSigma = 2
    Fixed = 3


def _validate_palette_scaling_mode(scaling_mode):
    """Validate input as a valid palette scaling mode value.

    Parameters
    ----------
    scaling_mode : PaletteScaleMode or str
        Palette scaling mode to validate.

    Returns
    -------
    str
        String representation of the specified palette scaling mode value.

    Raises
    ------
    TypeError
        If the input is not a PaletteScaleMode or str type.
    ValueError
        If the input string is not convertable to a PaletteScaleMode member.
    """
    if isinstance(scaling_mode, PaletteScaleMode):
        return scaling_mode.name
    if isinstance(scaling_mode, str):
        for pmode in PaletteScaleMode.__members__:
            if scaling_mode.lower() == pmode.lower():
                return pmode
        raise ValueError(
            '`scaling_mode` string is not a valid `PaletteScaleMode` member.')
    raise TypeError(
        '`scaling_mode` must be of type `PaletteScaleMode` '
        'or valid string value.')


def set_plot_palette_scale(control,
                           scale_mode=PaletteScaleMode.Auto,
                           peak=10.0,
                           valley=0.0,
                           unit=_Units.MicroMeters):
    """Set the palette scaling mode for the specified plot.

    Parameters
    ----------
    control : Control
        The plot control to set.
    scale_mode : PaletteScaleMode
        The desired palette scaling mode.
    peak : float, optional
        The Fixed mode peak value. Only used with PaletteScaleMode.Fixed.
    valley : float, optional
        The Fixed mode valley value. Only used with PaletteScaleMode.Fixed.
    units : units.Units, optional
        The units for the peak and valley values. Only used with
        PaletteScaleMode.Fixed.
    """
    params = {'controlId': control._id,
              'scaleMode': _validate_palette_scaling_mode(scale_mode),
              'peak': peak,
              'valley': valley,
              'unit': _validate_unit(unit)}
    _send_request(_SERVICE, 'SetPlotPaletteScale', params)


# =============================================================================
# ---Global Tab Methods
# =============================================================================
def get_tab(name):
    """Get the requested Mx tab by its display name.

    Parameters
    ----------
    name : str
        The display name of the requested tab.

    Returns
    -------
    Tab
        The Tab object representing the Mx tab.
    """
    lower_name = name.lower()
    for tab in get_tabs():
        if tab.name.lower() == lower_name:
            return tab
    raise RuntimeError('Could not find tab "{0}"'.format(name))


def get_tabs():
    """Get all available Mx tabs.

    Returns
    -------
    tuple of Tab
        A tuple of Tab objects for all available Mx tabs.
    """
    tabs = _get_send_request(_SERVICE, 'GetTabs')
    return tuple(Tab(tab['m_Item1'], tab['m_Item2']) for tab in tabs)


def get_home_tab():
    """Gets the Mx home tab.

    Returns
    -------
    Tab
        The tab configured as the startup tab, or the first available tab if
        no startup tab is configured.
    """
    tab = _get_send_request(_SERVICE, 'GetHomeTab')
    return Tab(tab['m_Item1'], tab['m_Item2'])


# =============================================================================
# ---Global Container Methods
# =============================================================================
def get_home_container():
    """Gets the Mx home container.

    Returns
    -------
    Container or ContainerWindow
        The container configured as the startup container in the home tab, or
        the first available container in the home tab if no startup container
        is defined.
    """
    container = _get_send_request(_SERVICE, 'GetHomeContainer')
    name, uid, cont_type = (container['m_Item1'],
                            container['m_Item2'],
                            container['m_Item3'])
    if cont_type == 'Modal Dialog':
        return ContainerWindow(name, uid, True)
    elif cont_type == 'Non-Modal Dialog':
        return ContainerWindow(name, uid, False)
    return Container(name, uid)


# =============================================================================
# ---Global Control Methods
# =============================================================================
def get_default_plot_control_path():
    """Gets the path of the default Mx plot control.

    Returns
    -------
    tuple of str
        The path to the currently-defined default plot in Mx.
    """

    path = _get_send_request(_SERVICE, 'GetDefaultPlotControlPath')
    return tuple(path)


def get_control(path):
    """Get the control identified by the given path.

    Parameters
    ----------
    path : tuple of str
        Path to the control.

    Returns
    -------
    Control
        A control object representing the Mx GUI control.
    """
    params = {'path': path}
    control = _get_send_request(_SERVICE, 'GetControlByPath', params)
    return Control(control['Name'], control['Id'], control['Path'])


# =============================================================================
# ---Control Class
# =============================================================================
class Control(object):
    """Represents an Mx GUI control.

    Parameters
    ----------
    name : str
        The name of the control.
    uid : str
        The string that uniquely identifies this control.

        Note that this value is not guaranteed to be unique across Mx
        sessions or application loads.
    path : tuple of str
        Path to the control.
    """

    def __init__(self, name, uid, path):
        """Initialize the control.

        Parameters
        ----------
        name : str
            The name of the control.
        uid : str
            The string that uniquely identifies this control.

            Note that this value is not guaranteed to be unique across Mx
            sessions or application loads.
        path : tuple of str
            Path to the control.
        """
        self.name = name
        self._id = uid
        self.path = None if path is None else tuple(path)

    @property
    def controls(self):
        """tuple of Control: Child controls contained within this control."""
        params = {'controlId': self._id}
        children = _get_send_request(_SERVICE, 'GetControls', params)
        return tuple(
            Control(control['Name'], control['Id'], control['Path'])
            for control in children)

    class IOptionalParams(metaclass=_ABCMeta):
        """Interface for optional save data parameters."""
        @property
        @_abstractmethod
        def _request_format(self):
            """list of dict: Gets this object's properties in the format
            suitable for sending to Mx."""
            pass

    class ProcStatsParams(IOptionalParams):
        """Process statistics save data parameters.

        Parameters
        ----------
        simple_mode : bool, optional
            True to use export button formats, False to use autolog
            formats.
        standard_format : bool, optional
            Corresponds to the Standard Format button in the proc stats
            control.
        """

        def __init__(self, simple_mode=False, standard_format=False):
            """Initializes the process stats parameters.

            Parameters
            ----------
            simple_mode : bool, optional
                True to use export button formats, False to use autolog
                formats.
            standard_format : bool, optional
                Corresponds to the Standard Format button in the proc stats
                control.
            """
            self._simple_mode = simple_mode
            self._standard_format = standard_format
            self._qdas_parameters = False
            self._qdas_results = False
            self._append = False
            self._log_all = True

        @property
        def simple_mode(self):
            """bool: Determines the process statistics save mode.

            If True, the data will be saved in the format corresponding to one
            of the export buttons in the Process Stats control. If False, the
            data will be saved in one of the autolog formats.
            """
            return self._simple_mode

        @simple_mode.setter
        def simple_mode(self, value):
            self._simple_mode = value

        @property
        def standard_format(self):
            """bool: Determines the process statistics save format,

            This value corresponds to the AutoLog>Standard Format button in
            the Process Stats control.
            """
            return self._standard_format

        @standard_format.setter
        def standard_format(self, value):
            self._standard_format = value

        @property
        def qdas_parameters(self):
            """bool: True to export Q-DAS parameters.

            Cannot be combined with any other property.
            """
            return self._qdas_parameters

        @qdas_parameters.setter
        def qdas_parameters(self, value):
            self._qdas_parameters = value

        @property
        def qdas_results(self):
            """bool: True to export Q-DAS results.

            Cannot be combined with any other property.
            """
            return self._qdas_results

        @qdas_results.setter
        def qdas_results(self, value):
            self._qdas_results = value

        @property
        def append(self):
            """bool: True to append data to the file; False to overwrite the
            file. If the specified file does not exist, this parameter has no
            effect and a new file will be created.

            This currently only applies to Q-DAS results export.
            """
            return self._append

        @append.setter
        def append(self, value):
            self._append = value

        @property
        def log_all(self):
            """bool: True to output all results; False to output only the last
            (most-recent) row.
            """
            return self._log_all

        @log_all.setter
        def log_all(self, value):
            self._log_all = value

        @property
        def _request_format(self):
            """list of dict: Gets the save data properties in the format
            suitable for sending to Mx."""
            return [{'m_Item1': 'simple',
                     'm_Item2': self.simple_mode},
                    {'m_Item1': 'standard',
                     'm_Item2': self.standard_format},
                    {'m_Item1': 'qdasParameters',
                     'm_Item2': self.qdas_parameters},
                    {'m_Item1': 'qdasResults',
                     'm_Item2': self.qdas_results},
                    {'m_Item1': 'append',
                     'm_Item2': self.append},
                    {'m_Item1': 'logAll',
                     'm_Item2': self.log_all}]

    class CodeVParams(IOptionalParams):
        """CodeV file export parameters.

        Parameters
        ----------
        title : str, optional
            The CodeV Title export field.
        data_type : DataType, optional
            The CodeV Type export field.
        comment : str, optional
            The CodeV Comment export field.
        """

        class DataType(_IntEnum):
            """CodeV data types."""
            Wavefront = 1
            Surface = 2
            Filter = 3

        def _validate_data_type(self, data_type):
            """Validate input as a valid data type value.

            Parameters
            ----------
            data_type : DataType or str
                Data type to validate.

            Returns
            -------
            str
                String representation of the specified data type.

            Raises
            ------
            TypeError
                If the input is not a DataType or str type.
            ValueError
                If the input string is not convertable to a DataType member.
            """
            if isinstance(data_type, self.DataType):
                return data_type.name
            if isinstance(data_type, str):
                for dtype in self.DataType.__members__:
                    if data_type.lower() == dtype.lower():
                        return dtype
                raise ValueError(
                    '`data_type` string is not a valid `DataType` member.')
            raise TypeError(
                '`data_type` must be of type `DataType` '
                'or valid string value.')

        def __init__(self, title='Mx',
                     data_type=DataType.Surface,
                     comment=''):
            """Initializes the CodeV parameters.

            Parameters
            ----------
            title : str, optional
                The CodeV Title export field.
            data_type : DataType, optional
                The CodeV Type export field.
            comment : str, optional
                The CodeV Comment export field.
            """
            self._title = title
            self._type = self._validate_data_type(data_type)
            self._comment = comment

        @property
        def title(self):
            """str: The CodeV Title export field."""
            return self._title

        @title.setter
        def title(self, value):
            self._title = value

        @property
        def data_type(self):
            """DataType: The CodeV Type export field."""
            return self._type

        @data_type.setter
        def data_type(self, value):
            self._type = self._validate_data_type(value)

        @property
        def comment(self):
            """str: The CodeV Comment export field."""
            return self._comment

        @comment.setter
        def comment(self, value):
            self._comment = value

        @property
        def _request_format(self):
            """list of dict: Gets the CodeV export properties in the format
            suitable for sending to Mx."""
            return [{'m_Item1': 'CodeVTitle',
                     'm_Item2': self.title},
                    {'m_Item1': 'CodeVType',
                     'm_Item2': self.data_type},
                    {'m_Item1': 'CodeVComment',
                     'm_Item2': self.comment}]

    class SdfParams(IOptionalParams):
        """Sdf file export parameters.

        Parameters
        ----------
        manufacturer : str, optional
            The Sdf Manufacturer export field.
        create_date : datetime.datetime, optional
            The Sdf CreateDate export field.
        modification_date : datetime.datetime, optional
            The Sdf ModificationDate export field.
        wavelength : double, optional
            The Sdf Wavelength export field.
        data_type : DataType, optional
            The Sdf DataType export field.
        """

        class DataType(_IntEnum):
            """Sdf data types."""
            Double = 1
            Integer = 2

        def _validate_data_type(self, data_type):
            """Validate input as a valid data type value.

            Parameters
            ----------
            data_type : DataType or str
                Data type to validate.

            Returns
            -------
            str
                String representation of the specified data type.

            Raises
            ------
            TypeError
                If the input is not a DataType or str type.
            ValueError
                If the input string is not convertable to a DataType member.
            """
            if isinstance(data_type, self.DataType):
                return data_type.name
            if isinstance(data_type, str):
                for dtype in self.DataType.__members__:
                    if data_type.lower() == dtype.lower():
                        return dtype
                raise ValueError(
                    '`data_type` string is not a valid `DataType` member.')
            raise TypeError(
                '`data_type` must be of type `DataType` '
                'or valid string value.')

        def __init__(self,
                     manufacturer='',
                     create_date=_datetime.now(),
                     modification_date=_datetime.now(),
                     wavelength=632.8,
                     data_type=DataType.Double):
            """Initializes the Sdf parameters.

            Parameters
            ----------
            manufacturer : str, optional
                The Sdf Manufacturer export field.
            create_date : datetime.datetime, optional
                The Sdf CreateDate export field.
            modification_date : datetime.datetime, optional
                The Sdf ModificationDate export field.
            wavelength : double, optional
                The Sdf Wavelength export field.
            data_type : DataType, optional
                The Sdf DataType export field.
            """
            self._manufacturer = manufacturer
            self._create_date = str(create_date)
            self._modification_date = str(modification_date)
            self._wavelength = wavelength
            self._data_type = self._validate_data_type(data_type)

        @property
        def manufacturer(self):
            """str: The Sdf Manufacturer export field."""
            return self._manufacturer

        @manufacturer.setter
        def manufacturer(self, value):
            self._manufacturer = value

        @property
        def create_date(self):
            """The Sdf CreateDate export field."""
            return self._create_date

        @create_date.setter
        def create_date(self, value):
            self._create_date = str(value)

        @property
        def modification_date(self):
            """The Sdf ModificationDate export field."""
            return self._modification_date

        @modification_date.setter
        def modification_date(self, value):
            self._modification_date = str(value)

        @property
        def wavelength(self):
            """The Sdf Wavelength export field."""
            return self._wavelength

        @wavelength.setter
        def wavelength(self, value):
            self._wavelength = value

        @property
        def data_type(self):
            """The Sdf DataType export field."""
            return self._data_type

        @data_type.setter
        def data_type(self, value):
            self._data_type = self._validate_data_type(value)

        @property
        def _request_format(self):
            """list of dict: Gets the Sdf export properties in the format
            suitable for sending to Mx."""
            return [{'m_Item1': 'SdfManufacturer',
                     'm_Item2': self.manufacturer},
                    {'m_Item1': 'SdfCreateDate',
                     'm_Item2': self.create_date},
                    {'m_Item1': 'SdfModificationDate',
                     'm_Item2': self.modification_date},
                    {'m_Item1': 'SdfWavelength',
                     'm_Item2': self.wavelength},
                    {'m_Item1': 'SdfDataType',
                     'm_Item2': self.data_type}]

    def save_data(self, file_path, optional_params=None):
        """Save the control's data to file.

        Parameters
        ----------
        file_path : str
            Target file path to save data to. The file extension is used to
            determine the file type.
        optional_params : IOptionalParams, optional
            The optional process stats, CodeV, or Sdf parameters used for
            saving data.

        Raises
        ------
        TypeError
            If `optional_params` is not an IOptionalParams type or None.
        """
        opt_args = []
        if optional_params is not None:
            if isinstance(optional_params, Control.IOptionalParams):
                opt_args = optional_params._request_format
            else:
                raise TypeError(
                    '`optional_params` must be of type `IOptionalParams`.')

        params = {'controlId': self._id,
                  'filePath': file_path,
                  'optArgs': opt_args}
        _send_request(_SERVICE, 'SaveData', params)

    def save_data_to_stream(self, file_extension, optional_params=None):
        """Get the control's data as a binary sequence.

        Parameters
        ----------
        file_extension : str
            The file type of the data to save (as an extension, e.g., '.datx'
            or '.csv').
        optional_params : IOptionalParams, optional
            The optional process stats, CodeV, or Sdf parameters used for
            saving data.

        Raises
        ------
        TypeError
            If `optional_params` is not an IOptionalParams type or None.

        Returns
        -------
        bytes
            The control's data, of the requested type, as a bytes object.
        """
        opt_args = []
        if optional_params is not None:
            if isinstance(optional_params, Control.IOptionalParams):
                opt_args = optional_params._request_format
            else:
                raise TypeError(
                    '`optional_params` must be of type `IOptionalParams`.')

        params = {'controlId': self._id,
                  'fileExtension': file_extension,
                  'optArgs': opt_args}
        return _send_request(_SERVICE,
                             'SaveDataToStream',
                             params,
                             decode=False)

    def save_image(self, file_path):
        """Save the control's image to file.

        Parameters
        ----------
        file_path : str
            Target file path to save the image to. The file extension is used
            to determine the file type.
        """
        params = {'controlId': self._id, 'filePath': file_path}
        _send_request(_SERVICE, 'SaveImage', params)

    def print_data(self):
        """Send the control's data to the default printer."""
        _warnings.warn(
            "`print_data` is deprecated. It will be replaced or removed in " +
            "a future version of Mx scripting.", DeprecationWarning)
        params = {'controlId': self._id}
        _send_request(_SERVICE, 'PrintData', params)

    def click_toolbar_item(self, path):
        """Click a toolbar item in this control.

        Parameters
        ----------
        path : tuple of str
            The path to the toolbar item.
        """
        params = {'controlId': self._id, 'path': path}
        _send_request(_SERVICE, 'ClickControlToolbarButton', params)


# =============================================================================
# ---Container Class
# =============================================================================
class Container(object):
    """Represents an Mx GUI container.

    Parameters
    ----------
    name : str
        The display name of the container.
    uid : str
        The string that uniquely identifies this container.

        Note that this value is not guaranteed to be unique across Mx
        sessions or application loads.

    Note
    ----
    Mx containers are referred to elsewhere as screens or views.
    """

    def __init__(self, name, uid):
        """Initialize the container.

        Parameters
        ----------
        name : str
            The display name of the container.
        uid : str
            The string that uniquely identifies this container.

            Note that this value is not guaranteed to be unique across Mx
            sessions or application loads.
        """
        self.name = name
        self._id = uid

    @property
    def controls(self):
        """tuple of Control: Child controls contained within this container."""
        params = {'containerId': self._id}
        children = _get_send_request(_SERVICE,
                                     'GetControlsFromContainer',
                                     params)
        return tuple(
            Control(control['Name'], control['Id'], control['Path'])
            for control in children)

    @property
    def plots(self):
        """tuple of Control: Plot controls contained within this container."""
        params = {'containerId': self._id}
        children = _get_send_request(_SERVICE,
                                     'GetPlotsFromContainer',
                                     params)
        return tuple(
            Control(control['Name'], control['Id'], control['Path'])
            for control in children)

    def show(self):
        """Show the container."""
        params = {'containerId': self._id}
        _send_request(_SERVICE, 'ShowContainer', params)

    def _navigatortoolvisibility(self):
        """Get the container's navigator tool visibility mode.

        Returns
        -------
        str
            The container's navigator tool visibility mode.
        """
        params = {'containerId': self._id}
        return _get_send_request(_SERVICE, 'NavigatorToolVisibility', params)


# =============================================================================
# ---ContainerWindow Class
# =============================================================================
class ContainerWindow(object):
    """Represents an Mx GUI container window.

    Parameters
    ----------
    name : str
        The display name of the container window.
    uid : str
        The string that uniquely identifies this container window.
        Note that this value is not guaranteed to be unique across Mx
        sessions or application loads.
    is_modal : bool
        True if this container window is modal, False if it is modeless.

    Note
    ----
    Mx container windows are containers which appear as popup dialogs.
    """
    def __init__(self, name, uid, is_modal):
        """Initialize the container window.

        Parameters
        ----------
        name : str
            The display name of the container window.
        uid : str
            The string that uniquely identifies this container window.
            Note that this value is not guaranteed to be unique across Mx
            sessions or application loads.
        is_modal : bool
            True if this container window is modal, False if it is modeless.
        """
        self.name = name
        self._id = uid
        self._is_modal = is_modal

    @property
    def controls(self):
        """tuple of Control: Child controls contained within this container
        window."""
        params = {'containerId': self._id}
        children = _get_send_request(_SERVICE,
                                     'GetControlsFromContainer',
                                     params)
        return tuple(
            Control(control['Name'], control['Id'], control['Path'])
            for control in children)

    @property
    def plots(self):
        """tuple of Control: Plot controls contained within this container
        window."""
        params = {'containerId': self._id}
        children = _get_send_request(_SERVICE,
                                     'GetPlotsFromContainer',
                                     params)
        return tuple(
            Control(control['Name'], control['Id'], control['Path'])
            for control in children)

    @property
    def is_modal(self):
        """bool: True if the container window is modal; False otherwise.
        """
        return self._is_modal

    @property
    def open(self):
        """bool: True if the container window is currently open; False
        otherwise."""
        params = {'windowName': self.name}
        return _get_send_request(_SERVICE, 'IsWindowOpen', params)

    def show(self):
        """Show the container window."""
        params = {'containerId': self._id}
        _send_request(_SERVICE, 'ShowContainer', params)

    def close(self):
        """Close the container window."""
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'CloseWindow', params)

    def print(self):
        """Send the container window image to the default printer."""
        _warnings.warn(
            "`print` is deprecated. It will be replaced or removed in a " +
            "future version of Mx scripting.", DeprecationWarning)
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'PrintWindow', params)

    def to_front(self):
        """Bring the container window to the front."""
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'BringWindowToFront', params)

    def to_back(self):
        """Send the container window to the back."""
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'SendWindowToBack', params)

    def _navigatortoolvisibility(self):
        """Get the container window's navigator tool visibility mode.

        Returns
        -------
        str
            The container window's navigator tool visibility mode.
        """
        params = {'containerId': self._id}
        return _get_send_request(_SERVICE, 'NavigatorToolVisibility', params)


# =============================================================================
# ---Window Class
# =============================================================================
class Window(object):
    """Represents an Mx GUI window.

    These are non-container windows, e.g., Mask Editor, Fiducial Editor, etc.

    Parameters
    ----------
    name : str
        Uniquely-identifying window name in Mx.
    """

    def __init__(self, name):
        """Initialize the window.

        Parameters
        ----------
        name : str
            Uniquely-identifying window name in Mx.
        """
        self.name = name

    @property
    def controls(self):
        """tuple of Control: Child controls contained within this window."""
        params = {'windowName': self.name}
        children = _get_send_request(_SERVICE,
                                     'GetControlsFromWindow',
                                     params)
        return tuple(
            Control(control['Name'], control['Id'], control['Path'])
            for control in children)

    @property
    def open(self):
        """bool: True if the window is currently open; False otherwise."""
        params = {'windowName': self.name}
        return _get_send_request(_SERVICE, 'IsWindowOpen', params)

    def close(self):
        """Close the window."""
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'CloseWindow', params)

    def save_data(self, file_path):
        """Save the window's data to file.

        Parameters
        ----------
        file_path : str
            Target file path to save data to. The file extension is used to
            determine the file type.
        """
        params = {'windowName': self.name, 'filePath': file_path}
        _send_request(_SERVICE, 'SaveDataForWindow', params)

    def save_image(self, file_path):
        """Save the window's image to file.

        Parameters
        ----------
        file_path : str
            Target file path to save the image to. The file extension is used
            to determine the file type.
        """
        params = {'windowName': self.name, 'filePath': file_path}
        _send_request(_SERVICE, 'SaveImageForWindow', params)

    def print(self):
        """Send the window image to the default printer."""
        _warnings.warn(
            "`print` is deprecated. It will be replaced or removed in a " +
            "future version of Mx scripting.", DeprecationWarning)
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'PrintWindow', params)

    def to_front(self):
        """Bring the window to the front."""
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'BringWindowToFront', params)

    def to_back(self):
        """Send the window to the back."""
        params = {'windowName': self.name}
        _send_request(_SERVICE, 'SendWindowToBack', params)


# =============================================================================
# ---Navigator Class
# =============================================================================
class Navigator(object):
    """Represents the Mx navigator.

    Parameters
    ----------
    tab_id : str
        The unique ID of the Mx GUI tab.
    """

    def __init__(self, tab_id):
        """Initialize the navigator for the given tab.

        Parameters
        ----------
        tab_id : str
            The unique ID of the Mx GUI tab.
        """
        self._tab_id = tab_id

    def pin(self, do_pin):
        """Pin/Unpin the navigator.

        Parameters
        ----------
        do_pin : bool
            True to pin; False to unpin.
        """
        params = {'tabId': self._tab_id, 'pinNavigator': do_pin}
        _send_request(_SERVICE, 'PinUnpinNavigator', params)


# =============================================================================
# ---DockPanel Class
# =============================================================================
class DockPanel(object):
    """Represents an Mx dock panel.

    Parameters
    ----------
    name : str
        The display name of the dock panel.
    uid :  str
        The string that uniquely identifies this dock panel.

        Note that this value is not guaranteed to be unique across Mx
        sessions or application loads.
    """

    def __init__(self, name, uid):
        """Initialize the dock panel.

        Parameters
        ----------
        name : str
            The display name of the dock panel.
        uid :  str
            The string that uniquely identifies this dock panel.

            Note that this value is not guaranteed to be unique across Mx
            sessions or application loads.
        """
        self.name = name
        self._id = uid

    def pin(self, do_pin):
        """Pin/Unpin the dock panel.

        Parameters
        ----------
        do_pin : bool
            True to pin; False to unpin.
        """
        params = {'panelId': self._id, 'pinDockPanel': do_pin}
        _send_request(_SERVICE, 'PinUnpinDockPanel', params)


# =============================================================================
# ---Tab Class
# =============================================================================
class Tab(object):
    """Represents an Mx GUI tab.

    Parameters
    ----------
    name : str
        The display name of the tab.
    uid :  str
        The string that uniquely identifies this tab.

        Note that this value is not guaranteed to be unique across Mx
        sessions or application loads.
    """

    def __init__(self, name, uid):
        """Initialize the tab.

        Parameters
        ----------
        name : str
            The display name of the tab.
        uid :  str
            The string that uniquely identifies this tab.

            Note that this value is not guaranteed to be unique across Mx
            sessions or application loads.
        """
        self.name = name
        self._id = uid
        self.navigator = Navigator(uid)

    def show(self):
        """Show the tab."""
        params = {'id': self._id}
        _send_request(_SERVICE, 'ShowTab', params)

    @property
    def groups(self):
        """tuple of Group: Groups contained within this tab."""
        params = {'tabId': self._id}
        groups_ = _get_send_request(_SERVICE, 'GetGroupings', params)
        return tuple(Group(group['m_Item1'], group['m_Item2'])
                     for group in groups_)

    def get_group(self, group_name):
        """Get the requested group in this tab's navigator.

        Parameters
        ----------
        group_name : str
            The display name of the requested group.

        Returns
        -------
        Group
            The Group object representing the Mx group.
        """
        lower_name = group_name.lower()
        for group in self.groups:
            if group.name.lower() == lower_name:
                return group
        raise RuntimeError('Could not find Group "{}"'.format(group_name))

    @property
    def dock_panels(self):
        """tuple of DockPanel: Dock panels contained within this tab."""
        params = {'tabId': self._id}
        panels = _get_send_request(_SERVICE, 'GetDockPanels', params)
        return tuple(DockPanel(panel['m_Item1'], panel['m_Item2'])
                     for panel in panels)

    def get_dock_panel(self, panel_name):
        """Get the requested dock panel in this tab.

        Parameters
        ----------
        panel_name : str
            The display name of the requested dock panel.

        Returns
        -------
        DockPanel
            The DockPanel object representing the Mx dock panel.
        """
        lower_name = panel_name.lower()
        for panel in self.dock_panels:
            if panel.name.lower() == lower_name:
                return panel
        raise RuntimeError('Could not find dock panel "{}"'.format(panel_name))


# =============================================================================
# ---Group Class
# =============================================================================
class Group(object):
    """Represents an Mx navigator group of containers.
    Parameters
    ----------
    name : str
        The display name of the group.
    uid : str
        The string that uniquely identifies this group.
    """

    def __init__(self, name, uid):
        """Initialize the group.

        Parameters
        ----------
        name : str
            The display name of the group.
        uid : str
            The string that uniquely identifies this group.
        """
        self.name = name
        self._id = uid

    @property
    def containers(self):
        """tuple: Containers and ContainerWindows contained within this
        group."""
        params = {'groupingId': self._id}
        containers_ = _get_send_request(_SERVICE, 'GetContainers', params)
        res = []
        for cont in containers_:
            name, uid, cont_type = (cont['m_Item1'],
                                    cont['m_Item2'],
                                    cont['m_Item3'])
            if cont_type == 'Modal Dialog':
                res.append(ContainerWindow(name, uid, True))
            elif cont_type == 'Non-Modal Dialog':
                res.append(ContainerWindow(name, uid, False))
            else:
                res.append(Container(name, uid))

        return res

    def get_container(self, container_name):
        """Get the requested container or container window in this group.

        Parameters
        ----------
        container_name : str
            The display name of the container or container window.

        Returns
        -------
        Container or ContainerWindow
            The Container or ContainerWindow object representing the requested
            container or container window.
        """
        lower_name = container_name.lower()
        for cont in self.containers:
            if cont.name.lower() == lower_name:
                return cont
        raise RuntimeError('Could not find Container "{}"'.
                           format(container_name))


# =============================================================================
# ---Deprecated Methods
# =============================================================================
def show_file_dialog(filetype,
                     make_dir_primary=False,
                     allow_multiselect=False):
    """Display an Mx file open dialog.

    Parameters
    ----------
    filetype : systemcommands.FileTypes
        The specified systemcommands.FileTypes type for the dialog.
    make_dir_primary : bool
        Whether or not to save the selected directory as the default for the
        type.
    allow_multiselect : bool
        Whether or not to allow multiple file selections in the dialog.

    Returns
    -------
    list of str
        List of selected files, None for canceled dialog.
    """
    _warnings.warn(
        "show_file_dialog is deprecated, please use " +
        "show_file_open_dialog instead.", DeprecationWarning)
    type_string = _validate_file_type(filetype)
    params = {'type': type_string,
              'makeDirPrimary': make_dir_primary,
              'allowMultiselect': allow_multiselect}
    return _get_send_request(_SERVICE, 'ShowFileDialog', params)


def set_sequence_step_state(sequence_id, sequence_step_description, is_on):
    """Set a sequence step on/off state.

    Parameters
    ----------
    sequence_id : str
        The sequence id from using Show Id.
    sequence_step_description : str
        The sequence step description from the Step Properties.
    is_on : bool
        The True (on) or False (off) state of the step.
    """
    _warnings.warn(
        "set_sequence_step_state is deprecated, please use " +
        "mx.set_sequence_step_status instead.", DeprecationWarning)
    params = {'sequenceId': sequence_id,
              'sequenceStepDesc': sequence_step_description,
              'onOff': is_on}
    _send_request(_SERVICE, 'SetSequenceStepState', params)

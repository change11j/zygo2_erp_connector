# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Supports connection to Mx.

This module is intended for internal use by other modules in the zygo scripting
package, and should not be called directly from end-user scripts.
"""
from enum import IntEnum as _IntEnum
from urllib import request as _request, error as _error
import json as _json

from zygo.core import ZygoError as _ZygoError

# =========================================================================
# ---Constants
# =========================================================================
_SERVICE = 'ConnectionManagerService'
"""str: The service name for the connectionmanager module."""
_CLIENT_TYPE = 0
"""int: The Mx WebServices client type for the scripting client."""
_STATUS_OK = 200
"""int: The HTTP OK status code."""


# =========================================================================
# ---Global variables
# =========================================================================
_base_url = ''
"""str: The base url of the Mx host."""
_uid = ''
"""str: The uniquely identifying string for the active connection."""
_connected = False
"""bool: True if a connection with Mx has been established; False otherwise."""


# =========================================================================
# ---Enumerations
# =========================================================================
class WebServiceState(_IntEnum):
    """Represents the Mx service state."""
    none = 0
    idle = 1
    active = 2


# =========================================================================
# ---Connection methods
# =========================================================================
def connect(force_if_active=False, host='localhost', port=8733, uid=''):
    """Establish a connection to Mx.

    Parameters
    ----------
    force_if_active : bool
        True to connect even if current service state is Active.
    host : str
        Host name (Default='localhost') or ip address.
    port : int
        Port number (Default=8733).
    uid : str
        The string that uniquely identifies this connection.

    Returns
    -------
    str
        The uniquely-identifying string (uid) for this connection.
    """
    global _base_url
    global _uid
    global _connected

    if _connected:
        terminate()
    try:
        _base_url = 'http://{0}:{1}'.format(host, port)
        params = {'forceIfActive': force_if_active,
                  'clientType': _CLIENT_TYPE,
                  'uid': uid}
        _connected = True
        _uid = get_send_request(_SERVICE, 'Connect', params)

        return _uid
    except _ZygoError as ze:
        _base_url = ''
        _connected = False
        raise ze
    except Exception as e:
        _base_url = ''
        _connected = False
        raise _ZygoError(e)


def terminate():
    """Close connection to Mx."""
    try:
        params = {'uid': _uid}
        send_request(_SERVICE, 'Terminate', params)
    except _ZygoError as ze:
        raise ze
    except Exception as e:
        raise _ZygoError(e)
    finally:
        global _base_url
        global _connected

        _base_url = ''
        _connected = False


def get_service_state():
    """Get the current service state.


    Returns
    -------
    WebServiceState
        The current service state.
    """
    return WebServiceState(get_send_request(_SERVICE, 'GetServiceState'))


def set_is_sequence_step(is_sequence_step):
    """Sets whether this script is being run from a sequence step.

    Parameters
    ----------
    is_sequence_step : bool
        Whether this script is being run from a sequence step.
    """
    if is_sequence_step:
        params = {'uid': _uid}
        send_request(_SERVICE, 'SetIsSequenceStep', params)


def get_uid():
    """Gets the unique identifier for this connection.

    Returns
    -------
    str
        The unique identifier (uid) for this connection.
    """
    return _uid


def get_is_remote_access_connected():
    """Gets whether a remote access client is connected.

    Returns
    -------
    bool
        True if a remote access connection is active; False otherwise.
    """
    return get_send_request(_SERVICE, 'GetIsRemoteAccessConnected')


def send_request(service,
                 method,
                 params=None,
                 *,
                 decode=True):
    """Send HTTP request to the service and wait for the response.

    Parameters
    ----------
    service : str
        Service name.
    method : str
        Method name to invoke.
    params : dict, optional
        Dictionary of input parameters (Default=None).
    decode : bool, optional
        True to decode and unpack JSON byte string, False to return
        response unmodified.

    Returns
    -------
    dict or str
        The decoded response from Mx as a dict, or the raw undecoded response
        as a string.

    Notes
    -----
    When decode is True, this method will return the response from Mx as a
    dictionary containing a single key-value pair, where the key is the
    concatenation of the method name and the string "Result", e.g.,
    "ConnectResult", and the value is the return value of the invoked method.
    """
    try:
        if not _connected:
            raise _ZygoError('No valid connection to Mx.')

        # Prepare input data, headers
        data = bytes() if params is None else \
            _json.dumps(params, skipkeys=True).encode('utf-8')
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Content-Length': len(data)}
        # Send request, get response
        url = '/'.join((_base_url, service, method))

        req = _request.Request(url, data, headers)
        with _request.urlopen(req) as resp:
            try:
                read_resp = resp.read()
                # Interpret JSON byte string as Python object if requested
                value = _json.loads(read_resp.decode('utf-8')) \
                    if decode else read_resp
            except Exception:
                raise _ZygoError(resp.reason)
            # check HTTP status code; 200 == OK
            if resp.status != _STATUS_OK:
                value = (_json.loads(value.decode('utf-8')) if not decode
                         else value)
                if ('DetailedInformation' in value and
                        value['DetailedInformation']):
                    raise _ZygoError(value['Reason'],
                                     value['DetailedInformation'])
                else:
                    raise _ZygoError(value['Reason'])
            return value
    except _error.HTTPError as e:
        e_resp = e.read()
        value = _json.loads(e_resp.decode('utf-8')) if decode else e_resp
        if ('DetailedInformation' in value and
                value['DetailedInformation']):
            raise _ZygoError(value['Reason'],
                             value['DetailedInformation'])
        else:
            raise _ZygoError(value['Reason'])
    except _ZygoError as ze:
        raise ze
    except Exception as e:
        raise _ZygoError(e)


def get_send_request(service,
                     method,
                     params=None,
                     *,
                     decode=True):
    """Send HTTP request to the service and wait for the response.

    Parameters
    ----------
    service : str
        Service name.
    method : str
        Method name to invoke.
    params : dict, optional
        Dictionary of input parameters (Default=None).
    decode : bool, optional
        True to decode and unpack JSON byte string, False to return
        response unmodified.

    Returns
    -------
    object or str
        The decoded response from Mx as a dict, or the raw undecoded response
        as a string.

    Notes
    -----
    When decode is True, this method will return the return value of the
    invoked method already extracted from the outer dictionary.
    """
    result_key = method + "Result"
    result = send_request(service, method, params, decode=decode)
    return result[result_key]

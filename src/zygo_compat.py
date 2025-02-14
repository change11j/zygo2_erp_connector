# zygo_compat.py
import sys
import importlib

def get_zygo_module():
    """
    嘗試導入zygo模組，如果不存在則返回None
    """
    try:
        return importlib.import_module('zygo')
    except ImportError:
        return None

def is_zygo_available():
    """
    檢查是否能使用zygo模組
    """
    return get_zygo_module() is not None

def get_python_version():
    """
    獲取當前Python版本
    """
    return sys.version_info[:2]
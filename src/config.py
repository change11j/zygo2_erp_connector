# config.py
class ERPConfig:
    # ERP API 配置
    API_URL = "http://192.168.22.95:8080/ADInterface/services/rest/composite_service/composite_operation/"

    # 登錄信息
    LOGIN_INFO = {
        "user": "WebService",
        "pass": "WebService",
        "lang": "en_US",
        "ClientID": "1000000",
        "RoleID": "1000087",
        "OrgID": "1000000",
        "WarehouseID": "1000001",
        "stage": "9"
    }

    # 測量數據配置
    DEFAULT_DEVICE_NAME = "ZYGO"
import zygo.mx as mx
import zygo.core as zc
from zygo.connectionmanager import connect, terminate
import logging

# 設置日誌級別以便調試
logging.basicConfig(level=logging.DEBUG)
print("Starting connection attempt...")

try:
    # 建立連接
    uid = connect(force_if_active=True, host='localhost', port=8733)
    print('Connected successfully. UID: {0}'.format(uid))

    # 原本的代碼
    print('Is application open? {0}'.format(mx.is_application_open()))
    print('Application version: {0}'.format(mx.get_application_version()))

except zc.ZygoError as e:
    print('連接錯誤: {0}'.format(str(e)))
except Exception as e:
    print('其他錯誤: {0}'.format(str(e)))
finally:
    # 確保在結束時關閉連接
    try:
        terminate()
        print('Connection terminated')
    except:
        pass
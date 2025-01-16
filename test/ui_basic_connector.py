import zygo.mx as mx
import zygo.core as zc
import zygo.ui as ui
from zygo.connectionmanager import connect, terminate
import logging
import time

# 設置日誌級別
logging.basicConfig(level=logging.DEBUG)
print("Starting UI connection attempt...")

try:
    # 建立連接
    uid = connect(force_if_active=True, host='localhost', port=8733)
    print('Connected successfully. UID: {0}'.format(uid))

    # 檢查應用程序狀態
    print('Is application open? {0}'.format(mx.is_application_open()))

    # UI 相關操作
    print('Getting active window title...')
    title = ui.get_active_window_title()
    print('Active window title: {0}'.format(title))

    # 獲取所有可見窗口
    print('\nGetting visible windows...')
    windows = ui.get_visible_windows()
    print('Visible windows:')
    for window in windows:
        print('- {0}'.format(window))

    # 嘗試獲取和設置一些UI元素
    try:
        # 獲取當前活動窗口中的控件
        controls = ui.get_window_controls(title)
        print('\nControls in active window:')
        for control in controls:
            print('- {0}'.format(control))

        # 等待一下以確保UI操作完成
        time.sleep(1)

    except zc.ZygoError as e:
        print('UI control operation error: {0}'.format(str(e)))

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
from __future__ import print_function
import sys
print("Python version:", sys.version)
print("Python path:", sys.path)

# 添加zygo模組路徑
zygo_path = 'C:\\projects\\zygo2_erp_connector'  # 調整為實際路徑
if zygo_path not in sys.path:
    sys.path.append(zygo_path)

# 然後再導入zygo
from zygo.core import *
from zygo import ui, mx, connectionmanager
from zygo.ui import show_dialog, DialogMode
from zygo.ui import get_tab

# 顯示不會阻塞的提示信息
# show_dialog("處理中...", DialogMode.message_ok, seconds=3)

from zygo import mx, ui
import time


def create_status_container():
    # 先確保應用程序已打開
    if not mx.is_application_open():
        mx.open_application("path/to/your/app.mx")  # 替換成你的應用程序路徑
        time.sleep(1)  # 給應用程序加載的時間

    # 獲取所有可用的頁籤
    tabs = ui.get_tabs()

    # 找到一個合適的頁籤（這裡我們查看所有可用的頁籤）
    print("Available tabs:")
    for tab in tabs:
        print(f"- {tab}")
        # 打印該頁籤下的所有組
        for group in tab.groups:
            print(f"  Group: {group}")
            # 打印該組下的所有容器
            for container in group.containers:
                print(f"    Container: {container}")

    # 選擇第一個可用的頁籤
    first_tab = tabs[0]
    first_tab.show()

    # 在第一個組創建或獲取一個容器
    if first_tab.groups:
        first_group = first_tab.groups[0]
        if first_group.containers:
            status_container = first_group.containers[0]
            status_container.show()
            return status_container

    return None


try:
    # 創建狀態容器
    status_container = create_status_container()

    if status_container:
        print(f"Successfully created status container in {status_container}")
        # 使用這個容器進行後續操作...
    else:
        print("Failed to create status container")

except Exception as e:
    print(f"Error: {str(e)}")
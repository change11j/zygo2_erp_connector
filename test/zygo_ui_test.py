from __future__ import print_function  # Python 3.4.3 compatibility
from zygo import ui, mx, connectionmanager
from zygo.units import Units
import time

def test_basic_dialogs():
    """測試基本對話框"""
    print("\nTesting basic dialogs...")

    # 測試不同模式的對話框
    modes = [
        ("message_ok", ui.DialogMode.message_ok),
        ("error_ok", ui.DialogMode.error_ok),
        ("warning_ok", ui.DialogMode.warning_ok),
        ("confirm_yes_no", ui.DialogMode.confirm_yes_no),
        ("error_ok_cancel", ui.DialogMode.error_ok_cancel),
        ("warning_yes_no", ui.DialogMode.warning_yes_no),
        ("message_ok_cancel", ui.DialogMode.message_ok_cancel)
    ]
    
    for mode_name, mode in modes:
        print("\nTesting {0} dialog...".format(mode_name))
        result = ui.show_dialog(
            "This is a test of {0} dialog".format(mode_name),
            mode,
            seconds=2  # 自動關閉
        )
        print("Dialog result: {0}".format(result))

def test_input_dialogs():
    """測試輸入對話框"""
    print("\nTesting input dialogs...")
    
    # 基本輸入對話框
    print("\nTesting basic input dialog...")
    result = ui.show_input_dialog(
        "Please enter some text:",
        "Default value",
        ui.DialogMode.message_ok_cancel,
        50
    )
    print("Input result: {0}".format(result))
    
    # 下拉選單對話框
    print("\nTesting dropdown dialog...")
    items = ["Option 1", "Option 2", "Option 3"]
    result = ui.show_dropdown_dialog(
        "Please select an option:",
        items,
        ui.DialogMode.message_ok_cancel
    )
    print("Selected index: {0}".format(result))

def test_tab_access():
    """測試Tab訪問"""
    print("\nTesting tab access...")
    
    # 獲取所有tabs
    print("\nGetting all tabs...")
    tabs = ui.get_tabs()
    print("Found {0} tabs:".format(len(tabs) if tabs else 0))
    for tab in tabs:
        print("Tab found")  # 由於不確定tab物件的屬性，先簡單打印
        
    # 嘗試獲取特定tab
    print("\nTrying to get specific tabs...")
    tabs_to_try = ["Measure", "Analyze", "Automation"]
    for tab_name in tabs_to_try:
        tab = ui.get_tab(tab_name)
        if tab:
            print("Found tab: {0}".format(tab_name))
            try:
                tab.show()
                print("Successfully showed tab: {0}".format(tab_name))
            except Exception as e:
                print("Error showing tab {0}: {1}".format(tab_name, str(e)))
        else:
            print("Tab not found: {0}".format(tab_name))

def test_container_access():
    """測試Container訪問"""
    print("\nTesting container access...")
    
    try:
        # 嘗試獲取Analyze tab
        analyze_tab = ui.get_tab("Analyze")
        if analyze_tab:
            print("Found Analyze tab")
            
            # 獲取groups
            groups = analyze_tab.groups
            print("Found {0} groups".format(len(groups) if groups else 0))
            
            # 嘗試訪問每個group中的container
            for group in groups:
                print("\nAccessing group containers...")
                containers = group.containers()
                if containers:
                    for container in containers:
                        try:
                            container.show()
                            print("Successfully showed a container")
                            time.sleep(1)  # 暫停以便觀察
                        except Exception as e:
                            print("Error showing container: {0}".format(str(e)))
    except Exception as e:
        print("Error in container access test: {0}".format(str(e)))

def test_dock_panels():
    """測試DockPanel訪問"""
    print("\nTesting dock panels...")
    
    try:
        # 嘗試獲取各個tab的dock panels
        tabs = ui.get_tabs()
        if tabs:
            for tab in tabs:
                try:
                    dock_panels = tab.dock_panels
                    print("Found {0} dock panels".format(len(dock_panels) if dock_panels else 0))
                    
                    # 嘗試操作每個dock panel
                    for panel in dock_panels:
                        try:
                            # 嘗試pin/unpin操作
                            panel.pin(True)
                            time.sleep(1)
                            panel.pin(False)
                            time.sleep(1)
                            print("Successfully manipulated a dock panel")
                        except Exception as e:
                            print("Error manipulating dock panel: {0}".format(str(e)))
                except Exception as e:
                    print("Error accessing dock panels: {0}".format(str(e)))
    except Exception as e:
        print("Error in dock panel test: {0}".format(str(e)))

def test_window_operations():
    """測試Window操作"""
    print("\nTesting window operations...")
    
    try:
        # 測試顯示遮罩編輯器
        print("\nTesting mask editor...")
        mask_window = ui.show_mask_editor()
        if mask_window:
            print("Mask editor window opened")
            time.sleep(2)
            mask_window.close()
            print("Mask editor window closed")
            
        # 測試顯示基準點編輯器
        print("\nTesting fiducial editor...")
        fiducial_window = ui.show_fiducial_editor()
        if fiducial_window:
            print("Fiducial editor window opened")
            time.sleep(2)
            fiducial_window.close()
            print("Fiducial editor window closed")
            
    except Exception as e:
        print("Error in window operations test: {0}".format(str(e)))

def main():
    try:
        print("Starting UI tests...")
        print("-" * 50)
        
        # 連接到Zygo
        print("Connecting to Zygo...")
        uid = connectionmanager.connect(host='localhost', port=8733)
        print("Connected to Zygo (UID: {0})".format(uid))
        
        # 執行所有測試
        test_basic_dialogs()
        test_input_dialogs()
        test_tab_access()
        test_container_access()
        test_dock_panels()
        test_window_operations()
        
    except Exception as e:
        print("Fatal error: {0}".format(str(e)))
    finally:
        # 斷開連接
        connectionmanager.terminate()
        print("\nDisconnected from Zygo")
        print("Test completed!")

if __name__ == "__main__":
    main()

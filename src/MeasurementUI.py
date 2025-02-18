import logging
import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime


class MeasurementUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Data Monitor")

        # 主框架配置
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # 基础信息区域
        self.base_frame = ttk.LabelFrame(self.main_frame, text="基本資訊")
        self.base_frame.pack(fill="x", padx=5, pady=5)

        # 基础信息标签
        self.base_info_labels = {}
        # 添加 SOP 参数区域
        self.sop_frame = ttk.LabelFrame(self.main_frame, text="製程參數")
        self.sop_frame.pack(fill="x", padx=5, pady=5)

        # 用于存储 SOP 参数标签的字典
        self.sop_labels = {}

        # 测量数据表格
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 创建带滚动条的表格
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.tree_frame, show='headings')
        self.tree.pack(fill="both", expand=True)

        # 配置滚动条
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.configure(command=self.tree.yview)

        # 自定义样式
        self.style = ttk.Style()
        self.style.configure("Error.Treeview.Item", foreground="red")

        # 存储上一次的base_info
        self.last_base_info = None
        self.new_data_available = False  # 添加标志位
        self.upload_error = False  # 添加上传错误标志

    def update_display(self, data,is_error=False):
        """
        更新显示界面
        data格式:
        {
            'base_info': {
                'operator': '...',
                'groupName': '...',
                'attributeName1': '...',
                ...
            },
            'measurement': {
                'positionName': '...',
                'dataname1': 'value1',
                'dataname2': 'value2',
                ...
            },
            'timestamp': '...'
        }
        """
        # 检查base_info是否发生变化（除了update字段）
        current_base_info = {k: v for k, v in data['base_info'].items() if k != 'Updata'}
        if self.last_base_info and current_base_info != self.last_base_info:
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)

        self.last_base_info = current_base_info


        # 更新基础信息
        for i, (key, value) in enumerate(data['base_info'].items()):
            if key != 'Updata' and key in 'operator' 'groupName' "slide_id" "sample_number" :  # 跳过Updata字段
                if key not in self.base_info_labels:
                    ttk.Label(self.base_frame, text=str.format("%s:",key)).grid(row=i // 3, column=(i % 3) * 2, sticky="e", padx=5)
                    self.base_info_labels[key] = ttk.Label(self.base_frame, text=value)
                    self.base_info_labels[key].grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w")
                else:
                    self.base_info_labels[key].configure(text=value)

        # 更新表格列 (确保包含时间戳列)
        if 'measurement' in data:
            headers = ['timestamp', 'positionName'] + list(data['measurement'].keys())
            headers.remove('positionName')  # 移除重复的positionName

            if self.tree["columns"] != headers:
                self.tree["columns"] = headers
                for header in headers:
                    self.tree.heading(header, text=header)
                    self.tree.column(header, width=100)

            # 更新 SOP 参数显示
            excluded_fields = [
                'sample_name', 'groupName', 'position_name',
                'operator', 'measurement_fields', 'timestamp',
                'slide_id', 'sample_number'
            ]

            # 获取 SOP 参数
            sop_params = {k: v for k, v in data['base_info'].items()
                          if k not in excluded_fields}

            # 清理旧的 SOP 参数标签
            for widget in self.sop_frame.winfo_children():
                widget.destroy()

            # 添加新的 SOP 参数标签
            for i, (key, value) in enumerate(sop_params.items()):
                label_frame = ttk.Frame(self.sop_frame)
                label_frame.pack(fill="x", padx=5, pady=2)

                ttk.Label(label_frame, text=str.format("%s :",key),
                          width=20, anchor="e").pack(side="left", padx=(5, 2))
                ttk.Label(label_frame, text=str(value),
                          anchor="w").pack(side="left", fill="x", expand=True)

            # 添加新的测量数据
            if 'measurement' in data:
                # 准备行数据
                measurement = data['measurement']
                row_data = [
                               data['timestamp'],
                               measurement['positionName']
                           ] + [measurement[key] for key in headers[2:]]

                # 插入新行
                item = self.tree.insert('', 0, values=row_data)

                # 如果有错误，使用错误标记
                if is_error:
                    self.tree.item(item, tags=('error',))

    def show_error_message(self, message):
        """顯示錯誤訊息對話框"""
        messagebox.showerror("錯誤", message)
def start_ui(monitor):
    try:
        root = tk.Tk()
        root.geometry("1200x800")
        ui = MeasurementUI(root)

        def update():
            try:
                # 获取数据时才需要锁
                settings = None
                last_data = None
                upload_error = False
                new_data = False

                new_data = monitor.new_data_available
                if new_data:
                    settings = monitor.settings_manager.load_current_settings()
                    last_data = monitor.last_data
                    upload_error = monitor.last_upload_error
                    monitor.new_data_available = False

                # 有新数据时才更新UI
                if new_data and settings:
                    base_info = {
                        'operator': settings['operator'],
                        'groupName': settings['group_name'],
                        'slide_id': settings['slide_id']
                    }
                    # 添加 SOP 参数
                    for k, v in settings.items():
                        if k not in ['operator', 'group_name', 'slide_id',
                                     'sample_name', 'position_name',
                                     'measurement_fields', 'timestamp']:
                            base_info[k] = v

                    measurement = {
                        'positionName': settings['position_name']
                    }
                    if last_data:
                        for k, v in last_data.items():
                            measurement[k] = v

                    ui_data = {
                        'base_info': base_info,
                        'measurement': measurement,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if upload_error:
                        ui_data['timestamp'] = "* " + ui_data['timestamp']
                        ui.show_error_message("上傳數據失敗，請檢查網路連接或聯繫管理員")

                    ui.update_display(ui_data, upload_error)

                root.after(1000, update)
            except tk.TclError:
                # UI已关闭，不继续更新
                return
            except Exception as e:
                logging.error("Error in UI update: {0}".format(str(e)))
                root.after(1000, update)

        update()
        root.mainloop()
    except Exception as e:
        logging.error("Error in start_ui: {0}".format(str(e)))
def main():
    root = tk.Tk()
    root.geometry("1200x800")
    ui = MeasurementUI(root)

    def generate_test_data():
        """生成测试数据"""
        test_data = {
            'base_info': {
                'operator': 'Tom',
                'groupName': 'IT',
                'slide_id': 'TG-Test-1',
                'attributeName1': 'attributeValue1',
                'attributeName2': 'attributeValue2'
            },
            'measurement': {
                'positionName': 1,
                'dataname1': '1.399',
                'dataname2': '1.435',
                'dataname3': '1.425',
                'dataname4': '9.380',
                'dataname5': '9.369',
                'dataname6': '9.372'

            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return test_data

    def update():
        test_data = generate_test_data()
        # 检查网络状态
        network_status = ui.check_network()

        if not network_status:
            ui.show_network_error()
            test_data['timestamp'] = "* " + test_data['timestamp']

        ui.update_display(test_data)
        root.after(2000, update)

    update()
    root.mainloop()


if __name__ == "__main__":
    main()
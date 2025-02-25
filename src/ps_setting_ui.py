# ps_settings_ui.py
import os

from settings_ui import SettingsUI
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, dialog
import json


class PSSettingsUI(SettingsUI):
    def __init__(self):
        # 初始化状态变量
        self.current_ht_index = 0
        self.current_dom_index = 0
        self.repeat_patterns = {
            'HT': [],
            'DOM': {}
        }
        self.repeat_tree = None
        self.ht_value_entry = None  # 确保这些属性存在
        self.dom_value_entry = None  # 确保这些属性存在

        # 调用父类初始化
        super().__init__()
        # 调整行权重
        self.main_frame.grid_rowconfigure(0, weight=1)  # 基本信息
        self.main_frame.grid_rowconfigure(1, weight=1)  # 量测欄位
        self.main_frame.grid_rowconfigure(2, weight=1)  # 重复模式设置
        self.main_frame.grid_rowconfigure(3, weight=2)  # SOP参数
        self.main_frame.grid_rowconfigure(4, weight=0)  # 按钮
        # 设置标题
        self.root.title("PS 測量設置")

        # 添加HT/DOM起点设置区域
        self.add_start_index_fields()

        # 设置PS特有的UI
        self.setup_ps_ui()

        # 直接加载PS设置数据
        self.load_ps_patterns()

    def add_start_index_fields(self):
        """添加HT/DOM起点设置字段"""
        # 查找基本信息框架
        info_frame = None
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.cget("text") == "基本信息":
                info_frame = widget
                break

        if not info_frame:
            print("Error: Basic info frame not found")
            return

        # 获取最后一行的行号
        last_row = 0
        for child in info_frame.winfo_children():
            info = child.grid_info()
            if 'row' in info:
                last_row = max(last_row, int(info['row']))

        # 创建包含HT和DOM的行
        next_row = last_row + 1

        # 左侧HT标签和输入框
        ttk.Label(info_frame, text="目前HT:").grid(row=next_row, column=0, sticky=tk.W, padx=5)
        self.ht_value_entry = ttk.Entry(info_frame, width=10)
        self.ht_value_entry.grid(row=next_row, column=1, sticky=tk.W, padx=5)

        # 右侧DOM标签和输入框
        ttk.Label(info_frame, text="目前DOM:").grid(row=next_row, column=2, sticky=tk.W, padx=5)
        self.dom_value_entry = ttk.Entry(info_frame, width=10)
        self.dom_value_entry.grid(row=next_row, column=3, sticky=tk.W, padx=5)

        # 初始化显示值
        self.update_current_value_display()

    def load_ps_patterns(self):
        """单独加载PS相关设置"""
        print("Starting load_ps_patterns...")

        if not hasattr(self, 'repeat_tree') or not self.repeat_tree:
            print("Error: Repeat tree not available")
            return

        measure_id = self.settings_manager.get_latest_measure_id()
        print(f"Loading patterns for measure_id: {measure_id}")

        if measure_id:
            patterns = self.settings_manager.get_ps_patterns(measure_id)
            print(f"Loaded patterns from database: {patterns}")

            if patterns and 'repeat_patterns' in patterns:
                self.repeat_patterns = patterns['repeat_patterns']
                self.current_ht_index = patterns.get('current_ht_index', 0)
                self.current_dom_index = patterns.get('current_dom_index', 0)

                # 更新显示值
                self.update_current_value_display()

                print("Calling update_repeat_patterns_display...")
                self.update_repeat_patterns_display()
                print("Update complete")

    def setup_ps_ui(self):
        """设置PS特有的UI组件"""
        print("Starting setup_ps_ui...")
        # 查找量测字段框架
        self.field_frame = None
        for widget in self.main_frame.winfo_children():
            print(f"Widget: {widget}, type: {type(widget)}")
            if isinstance(widget, ttk.LabelFrame):
                print(f"LabelFrame text: '{widget.cget('text')}'")
                if widget.cget("text") == "量測欄位":
                    self.field_frame = widget
                    print("Found field frame!")
                    break

        if self.field_frame:
            print("Field frame found, creating repeat pattern frame...")
            self.insert_repeat_pattern_frame()
        else:
            print("Error: Field frame not found! Looking for '量測欄位'")
            # 打印出所有找到的LabelFrame的text属性
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, ttk.LabelFrame):
                    print(f"Available LabelFrame: '{widget.cget('text')}'")

    def insert_repeat_pattern_frame(self):
        """创建重复模式框架"""
        field_info = self.field_frame.grid_info()
        print(f"Field frame grid info: {field_info}")
        row = field_info['row']

        # 将已有元素向下移动一行
        for widget in self.main_frame.grid_slaves():
            info = widget.grid_info()
            if int(info.get('row', 0)) > row:
                widget.grid_configure(row=int(info['row']) + 1)

        # 创建重复模式框架
        pattern_frame = ttk.LabelFrame(self.main_frame, text="重複模式設置", padding="5")
        pattern_frame.grid(row=row + 1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 创建左右分栏
        left_frame = ttk.Frame(pattern_frame)
        right_frame = ttk.Frame(pattern_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        pattern_frame.grid_columnconfigure(0, weight=1)  # 左侧分配更多空间
        pattern_frame.grid_columnconfigure(1, weight=1)  # 右侧分配更多空间

        # 创建树状结构 (放在左侧)
        self.repeat_tree = ttk.Treeview(left_frame, columns=("value",), height=4)  # 减小高度
        self.repeat_tree.heading("#0", text="參數")
        self.repeat_tree.heading("value", text="數值")
        self.repeat_tree.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 绑定双击事件
        self.repeat_tree.bind("<Double-1>", self.on_tree_double_click)

        # 按钮区域 (放在右侧)
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), pady=5)

        # 垂直排列按钮
        ttk.Button(btn_frame, text="添加HT%", command=self.add_ht).pack(side=tk.TOP, pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="添加DOM", command=self.add_dom).pack(side=tk.TOP, pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="删除", command=self.delete_pattern).pack(side=tk.TOP, pady=2, fill=tk.X)

        print("Repeat tree created")

    def update_current_value_display(self):
        """更新当前HT/DOM值的显示"""
        # 确保UI组件已创建
        if not hasattr(self, 'ht_value_entry') or not self.ht_value_entry:
            print("Warning: ht_value_entry not available yet")
            return

        if not hasattr(self, 'dom_value_entry') or not self.dom_value_entry:
            print("Warning: dom_value_entry not available yet")
            return

        # 清空现有值
        self.ht_value_entry.delete(0, tk.END)
        self.dom_value_entry.delete(0, tk.END)

        # 检查是否有HT值
        if self.repeat_patterns['HT'] and 0 <= self.current_ht_index < len(self.repeat_patterns['HT']):
            ht_value = self.repeat_patterns['HT'][self.current_ht_index]
            self.ht_value_entry.insert(0, str(ht_value))  # 不添加百分比符号

            # 检查是否有DOM值
            ht_key = str(ht_value)
            if (ht_key in self.repeat_patterns['DOM'] and
                    self.repeat_patterns['DOM'][ht_key] and
                    0 <= self.current_dom_index < len(self.repeat_patterns['DOM'][ht_key])):
                dom_value = self.repeat_patterns['DOM'][ht_key][self.current_dom_index]
                self.dom_value_entry.insert(0, str(dom_value))

    def on_tree_double_click(self, event):
        """处理树状图双击事件"""
        item = self.repeat_tree.selection()[0] if self.repeat_tree.selection() else None
        if not item:
            return

        # 检查是否为DOM项（有父项）
        parent = self.repeat_tree.parent(item)
        if not parent:  # 如果是HT项
            # 获取HT值并更新HT索引
            try:
                ht_value = float(self.repeat_tree.item(item)["values"][0].strip("%"))
                ht_index = self.repeat_patterns['HT'].index(ht_value)
                self.current_ht_index = ht_index
                self.current_dom_index = 0  # DOM索引重置为0
                self.update_current_value_display()
            except (ValueError, IndexError) as e:
                print(f"Error setting HT index: {e}")
        else:  # 如果是DOM项
            try:
                # 获取父项（HT值）
                ht_value = float(self.repeat_tree.item(parent)["values"][0].strip("%"))
                ht_index = self.repeat_patterns['HT'].index(ht_value)

                # 获取DOM值
                dom_value = float(self.repeat_tree.item(item)["values"][0])
                ht_key = str(ht_value)
                if ht_key in self.repeat_patterns['DOM']:
                    dom_index = self.repeat_patterns['DOM'][ht_key].index(dom_value)

                    # 更新索引值
                    self.current_ht_index = ht_index
                    self.current_dom_index = dom_index

                    # 更新显示
                    self.update_current_value_display()
                    print(f"Set HT index to {ht_index}, DOM index to {dom_index}")
            except (ValueError, IndexError) as e:
                print(f"Error setting indices: {e}")

    def add_ht(self):
        """添加HT%值"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加HT%")
        dialog.transient(self.root)

        # 根据主窗口位置设置对话框位置
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()  # 模态对话框

        input_frame = ttk.Frame(dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, text="HT值 (%):").pack(side=tk.LEFT, padx=5)
        ht_entry = ttk.Entry(input_frame, width=10)
        ht_entry.pack(side=tk.LEFT, padx=5)

        def save():
            try:
                ht_value = float(ht_entry.get().strip())
                if 0 <= ht_value <= 100:
                    ht_id = self.repeat_tree.insert("", tk.END, text="HT%", values=(f"{ht_value}%",))
                    self.repeat_patterns['HT'].append(ht_value)
                    self.repeat_patterns['DOM'][str(ht_value)] = []  # 使用字符串键
                    dialog.destroy()
                else:
                    messagebox.showerror("錯誤", "HT值必須在0-100之間")
            except ValueError:
                messagebox.showerror("錯誤", "請輸入有效數字")

        def on_enter(event):
            save()

        ht_entry.bind('<Return>', on_enter)

        btn_frame = ttk.Frame(dialog, padding="5")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="確定", command=save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

        # 设置初始焦点
        ht_entry.focus_set()

    def add_dom(self):
        """添加DOM值"""
        selected = self.repeat_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "請先選擇一個HT%項")
            return

        parent = self.repeat_tree.parent(selected[0])
        if parent:  # 如果选中的是DOM项
            selected = parent

        dialog = tk.Toplevel(self.root)
        dialog.title("添加DOM")
        dialog.transient(self.root)

        # 根据主窗口位置设置对话框位置
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()  # 模态对话框

        input_frame = ttk.Frame(dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, text="DOM值:").pack(side=tk.LEFT, padx=5)
        dom_entry = ttk.Entry(input_frame, width=10)
        dom_entry.pack(side=tk.LEFT, padx=5)

        def save():
            try:
                dom_value = float(dom_entry.get().strip())
                if dom_value > 0:
                    ht_value = float(self.repeat_tree.item(selected[0])["values"][0].strip("%"))
                    self.repeat_tree.insert(selected[0], tk.END, text="DOM", values=(dom_value,))

                    ht_key = str(ht_value)  # 使用字符串键
                    if ht_key not in self.repeat_patterns['DOM']:
                        self.repeat_patterns['DOM'][ht_key] = []
                    self.repeat_patterns['DOM'][ht_key].append(dom_value)

                    dialog.destroy()
                else:
                    messagebox.showerror("錯誤", "DOM值必須大於0")
            except ValueError:
                messagebox.showerror("錯誤", "請輸入有效數字")

        def on_enter(event):
            save()

        dom_entry.bind('<Return>', on_enter)

        btn_frame = ttk.Frame(dialog, padding="5")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="確定", command=save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

        # 设置初始焦点
        dom_entry.focus_set()

    def delete_pattern(self):
        """删除选中的重复模式项"""
        selected = self.repeat_tree.selection()
        if not selected:
            return

        if messagebox.askyesno("确认", "确定要删除选中项吗?"):
            for item in selected:
                parent = self.repeat_tree.parent(item)
                if not parent:  # 删除HT项
                    ht_value = float(self.repeat_tree.item(item)["values"][0].strip("%"))
                    # 从HT列表中删除
                    self.repeat_patterns['HT'].remove(ht_value)
                    # 从DOM字典中删除，使用字符串键
                    if str(ht_value) in self.repeat_patterns['DOM']:
                        del self.repeat_patterns['DOM'][str(ht_value)]
                else:  # 删除DOM项
                    ht_value = float(self.repeat_tree.item(parent)["values"][0].strip("%"))
                    dom_value = float(self.repeat_tree.item(item)["values"][0])
                    # 从DOM列表中删除指定值，使用字符串键
                    ht_key = str(ht_value)
                    if ht_key in self.repeat_patterns['DOM']:
                        if dom_value in self.repeat_patterns['DOM'][ht_key]:
                            self.repeat_patterns['DOM'][ht_key].remove(dom_value)
                self.repeat_tree.delete(item)

    def save_settings(self):
        """重写保存设置方法"""
        # 获取当前的HT和DOM值
        current_ht = None
        current_dom = None

        # 获取所有参数（不包括HT和DOM，因为已被过滤）
        params = self.get_current_params()

        # 从UI直接获取当前显示的值
        try:
            current_ht = float(self.ht_value_entry.get().strip())
            current_dom = float(self.dom_value_entry.get().strip())

            # 添加HT和DOM值到SOP参数
            params["HT"] = str(current_ht)
            params["DOM"] = str(current_dom)

            # 验证indices是否正确，以备保存ps_patterns
            if self.repeat_patterns['HT']:
                try:
                    self.current_ht_index = self.repeat_patterns['HT'].index(current_ht)
                    ht_key = str(current_ht)
                    if ht_key in self.repeat_patterns['DOM'] and self.repeat_patterns['DOM'][ht_key]:
                        self.current_dom_index = self.repeat_patterns['DOM'][ht_key].index(current_dom)
                except ValueError:
                    # 如果值不在序列中，保持当前索引不变
                    print(f"Warning: Current values not found in patterns, keeping indices unchanged")
        except (ValueError, AttributeError) as e:
            print(f"Warning: Using values from indices instead: {e}")
            # 如果UI获取失败，使用索引获取值
            if self.repeat_patterns['HT'] and 0 <= self.current_ht_index < len(self.repeat_patterns['HT']):
                current_ht = self.repeat_patterns['HT'][self.current_ht_index]
                params["HT"] = str(current_ht)

                ht_key = str(current_ht)
                if (ht_key in self.repeat_patterns['DOM'] and
                        self.repeat_patterns['DOM'][ht_key] and
                        0 <= self.current_dom_index < len(self.repeat_patterns['DOM'][ht_key])):
                    current_dom = self.repeat_patterns['DOM'][ht_key][self.current_dom_index]
                    params["DOM"] = str(current_dom)

        # 调用父类的保存方法
        sample_name = self.sample_name.get().strip()
        group_name = self.group_name.get().strip()
        position_name = self.position.get().strip()
        operator = self.operator.get().strip()
        sample_number = self.sample_number.get().strip()

        # 生成试片ID
        import time
        today = time.strftime("%Y%m%d")
        slide_id = "{0}-{1}-{2}".format(
            sample_name,
            today,
            sample_number
        ) if sample_name and sample_number else ""

        # 获取量测欄位
        measurement_fields = []
        for item in self.field_tree.get_children():
            values = self.field_tree.item(item)["values"]
            measurement_fields.append({
                "name": values[0],
                "path": values[1]
            })

        # 添加量测欄位到参数
        params["measurement_fields"] = measurement_fields
        if not measurement_fields:
            params["measurement_fields"] = [{
                "name": "default",
                "path": ""
            }]

        try:
            # 调用settings_manager保存设置
            success = self.settings_manager.save_settings(
                sample_name,
                position_name,
                group_name,
                operator,
                "Unknown.appx",  # 或从mx获取
                slide_id,
                sample_number,
                params
            )

            if success:
                # 获取最新的measure_id
                measure_id = self.settings_manager.get_latest_measure_id()
                if measure_id:
                    # 保存重复模式
                    patterns = {
                        'repeat_patterns': self.repeat_patterns,
                        'current_ht_index': self.current_ht_index,
                        'current_dom_index': self.current_dom_index
                    }
                    return self.settings_manager.save_ps_patterns(measure_id, patterns)
            return success
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def export_settings(self):
        """重写导出设置方法"""
        try:
            self.current_ht_index = int(self.ht_start_entry.get().strip())
            self.current_dom_index = int(self.dom_start_entry.get().strip())
        except (ValueError, AttributeError) as e:
            print(f"Warning: Failed to update indices from UI: {e}")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="ps_settings.json"
        )

        if file_path:
            # 获取基本设置
            settings = {
                "sample_name": self.sample_name.get().strip(),
                "group_name": self.group_name.get().strip(),
                "position_name": self.position.get().strip(),
                "operator": self.operator.get().strip(),
                "sample_number": self.sample_number.get().strip(),
                "measurement_fields": []
            }

            # 生成完整ID
            import time
            today = time.strftime("%Y%m%d")
            settings["slide_id"] = "{0}-{1}-{2}".format(
                settings["sample_name"],
                today,
                settings["sample_number"]
            )

            # 添加量测字段
            for item in self.field_tree.get_children():
                values = self.field_tree.item(item)["values"]
                settings["measurement_fields"].append({
                    "name": values[0],
                    "path": values[1]
                })

            # 添加SOP参数
            params = self.get_current_params()
            for name, value in params.items():
                settings[name] = value

            # 添加PS重复模式设置
            settings["ps_patterns"] = {
                "repeat_patterns": self.repeat_patterns,
                "current_ht_index": self.current_ht_index,
                "current_dom_index": self.current_dom_index
            }

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("成功", "設置已導出")
            except Exception as e:
                messagebox.showerror("錯誤", "導出失敗: {}".format(e))

    def import_settings(self):
        """重写导入设置方法"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # 导入PS重复模式设置
                ps_patterns = settings.pop("ps_patterns", {})
                self.repeat_patterns = ps_patterns.get("repeat_patterns", {"HT": [], "DOM": {}})
                self.current_ht_index = ps_patterns.get("current_ht_index", 0)
                self.current_dom_index = ps_patterns.get("current_dom_index", 0)

                # 更新界面显示
                self.update_current_value_display()
                self.update_repeat_patterns_display()

                # 移除HT和DOM参数，避免它们进入SOP参数
                settings.pop("HT", None)
                settings.pop("DOM", None)

                # 调用父类的导入设置方法处理其他设置
                if self.settings_manager.import_settings(file_path):
                    self.load_latest_settings()
                    messagebox.showinfo("成功", "設置已導入")
                else:
                    messagebox.showerror("錯誤", "設置導入失敗")

            except Exception as e:
                messagebox.showerror("錯誤", "導入失敗: {}".format(e))

    def load_latest_settings(self):
        """完全重写加载设置方法，不调用父类方法"""
        print("begin ps_setting_ui.load_latest_settings()")

        # 手动加载设置
        settings = self.settings_manager.load_current_settings()
        if settings:
            # 載入基本資訊欄位，但跳过HT和DOM
            self.sample_name.delete(0, tk.END)
            self.sample_name.insert(0, settings.get("sample_name", ""))

            self.group_name.delete(0, tk.END)
            self.group_name.insert(0, settings.get("group_name", ""))

            self.position.delete(0, tk.END)
            self.position.insert(0, settings.get("position_name", ""))

            self.operator.delete(0, tk.END)
            self.operator.insert(0, settings.get("operator", ""))

            # 載入試片編號
            self.sample_number.delete(0, tk.END)
            self.sample_number.insert(0, settings.get("sample_number", ""))

            # 清除現有參數並載入
            self.param_entries.clear()
            for widget in self.params_frame.winfo_children():
                widget.destroy()

            # 只載入非系統欄位作為參數，排除HT和DOM
            excluded_fields = ["sample_name", "position_name", "group_name",
                               "operator", "measurement_fields", "slide_id",
                               "sample_number", "HT", "DOM"]  # 添加HT和DOM到排除列表

            for name, value in settings.items():
                if name not in excluded_fields:
                    self.add_param_entry(name, value)

            # 載入量測欄位
            for item in self.field_tree.get_children():
                self.field_tree.delete(item)
            for field in settings.get("measurement_fields", []):
                self.field_tree.insert("", tk.END, values=(field["name"], field["path"]))

        # 不要在这里更新UI，因为此时UI组件可能还没创建

    def update_repeat_patterns_display(self):
        """更新重复模式的界面显示"""
        if not hasattr(self, 'repeat_tree') or not self.repeat_tree:
            print("Repeat tree not found and return")
            return

        print("Updating display with patterns:", self.repeat_patterns)

        # 清除现有显示
        for item in self.repeat_tree.get_children():
            self.repeat_tree.delete(item)

        # 更新树状显示
        for ht_value in self.repeat_patterns['HT']:
            print(f"Adding HT value: {ht_value}")
            ht_id = self.repeat_tree.insert("", tk.END, text="HT%", values=(f"{ht_value}%",))

            # 检查并添加对应的DOM值
            ht_key = str(ht_value)  # 转换为字符串键
            if isinstance(self.repeat_patterns['DOM'], dict) and ht_key in self.repeat_patterns['DOM']:
                dom_values = self.repeat_patterns['DOM'][ht_key]
                print(f"Found DOM values for HT {ht_value}: {dom_values}")

                # 确保dom_values是列表
                if isinstance(dom_values, list):
                    for dom_value in dom_values:
                        print(f"Adding DOM value: {dom_value}")
                        self.repeat_tree.insert(ht_id, tk.END, text="DOM", values=(dom_value,))
                else:
                    print(f"Warning: DOM values for HT {ht_value} is not a list: {dom_values}")
            else:
                print(f"No DOM values found for HT {ht_value}")

    def add_param_entry(self, name="", value=""):
        try:
            row_frame = ttk.Frame(self.params_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=1)  # 减小上下边距

            name_entry = ttk.Entry(row_frame, width=15)  # 减小名称宽度
            name_entry.insert(0, name)
            name_entry.pack(side=tk.LEFT, padx=(0, 2))  # 减小左右边距

            value_entry = ttk.Entry(row_frame)
            value_entry.insert(0, value)
            value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)  # 减小左右边距

            def remove_entry():
                del self.param_entries[name_entry]
                row_frame.destroy()

            ttk.Button(row_frame, text="×", width=2, command=remove_entry).pack(side=tk.RIGHT)  # 使用更紧凑的移除按钮
            self.param_entries[name_entry] = value_entry

        except Exception as e:
            print("Error adding param entry: {}".format(str(e)))

    def get_current_params(self):
        """重写获取当前参数的方法，过滤掉 HT 和 DOM"""
        # 获取所有参数
        all_params = {}
        try:
            for name_entry, value_entry in self.param_entries.items():
                name = name_entry.get().strip()
                value = value_entry.get().strip()
                if name and value and name not in ['HT', 'DOM']:  # 直接在这里过滤掉HT和DOM
                    all_params[name] = value
        except Exception as e:
            print(f"Error getting params: {e}")
        return all_params

    def run(self):
        """运行程序"""
        # 设置窗口大小和位置
        self.root.geometry("900x700")  # 增加窗口初始大小
        self.root.update_idletasks()

        # 居中显示
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry("+{0}+{1}".format(x, y))

        # 设置图标（可选）
        try:
            self.root.iconbitmap("icon.ico")  # 如果有图标文件的话
        except:
            pass

        self.root.mainloop()

def main():
    try:
        app = PSSettingsUI()
        print("UI initialized, starting mainloop...")
        app.run()
    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        raise

if __name__ == "__main__":
    main()
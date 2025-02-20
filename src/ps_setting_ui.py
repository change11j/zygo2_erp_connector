# ps_settings_ui.py
import os

from settings_ui import SettingsUI
import tkinter as tk
from tkinter import ttk, messagebox
import json


class PSSettingsUI(SettingsUI):
    def __init__(self):
        # 初始化循环索引
        self.current_ht_index = 0
        self.current_dom_index = 0

        # 初始化重复模式
        self.repeat_patterns = {
            'HT': [],
            'DOM': {}
        }
        self.repeat_tree = None
        self.field_frame = None

        # 调用父类初始化
        super().__init__()

        # 设置标题
        self.root.title("PS 測量設置")

        # 设置重复模式框架
        self.setup_ps_ui()

    def setup_ps_ui(self):
        """设置PS特有的UI组件"""
        # 查找量测字段框架
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                if widget.cget("text") == "SOP參數":
                    widget.grid_configure(height=10)  # 设置固定高度
                if widget.cget("text") in ["量測欄位", "量测字段"]:
                    self.field_frame = widget
                    break

        if self.field_frame:
            self.insert_repeat_pattern_frame()

    def insert_repeat_pattern_frame(self):
        # 获取field_frame的网格信息
        field_info = self.field_frame.grid_info()
        print("Field frame grid info:", field_info)
        row = field_info['row']

        # 将后面的widgets向下移动
        for widget in self.main_frame.grid_slaves():
            cur_row = int(widget.grid_info()['row'])
            if cur_row >= row:
                print(f"Moving widget from row {cur_row} to {cur_row + 1}")
                widget.grid(row=cur_row + 1)

        # 创建重复模式框架
        pattern_frame = ttk.LabelFrame(self.main_frame, text="重複模式設置", padding="5")
        pattern_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 创建树状结构
        self.repeat_tree = ttk.Treeview(pattern_frame, columns=("value",), height=5)
        self.repeat_tree.heading("#0", text="參數")
        self.repeat_tree.heading("value", text="數值")
        self.repeat_tree.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 按钮区域
        btn_frame = ttk.Frame(pattern_frame)
        btn_frame.grid(row=1, column=0, pady=5)

        ttk.Button(btn_frame, text="添加HT%", command=self.add_ht).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="添加DOM", command=self.add_dom).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self.delete_pattern).pack(side=tk.LEFT, padx=5)

        print("Pattern frame inserted")

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
                    self.repeat_patterns['DOM'][ht_value] = []
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

                    if ht_value not in self.repeat_patterns['DOM']:
                        self.repeat_patterns['DOM'][ht_value] = []
                    self.repeat_patterns['DOM'][ht_value].append(dom_value)

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
                    self.repeat_patterns['HT'].remove(ht_value)
                    del self.repeat_patterns['DOM'][ht_value]
                else:  # 删除DOM项
                    ht_value = float(self.repeat_tree.item(parent)["values"][0].strip("%"))
                    dom_value = float(self.repeat_tree.item(item)["values"][0])
                    self.repeat_patterns['DOM'][ht_value].remove(dom_value)
                self.repeat_tree.delete(item)

    def save_settings(self):
        """重写保存设置方法"""
        # 获取基本参数
        params = self.get_current_params()

        # 获取量测字段
        measurement_fields = []
        for item in self.field_tree.get_children():
            values = self.field_tree.item(item)["values"]
            measurement_fields.append({
                "name": values[0],
                "path": values[1]
            })
        params["measurement_fields"] = measurement_fields

        # 将当前的 HT/DOM 作为普通参数
        if self.repeat_patterns['HT']:
            ht_value = self.repeat_patterns['HT'][self.current_ht_index]
            params['HT%'] = str(ht_value)

            if ht_value in self.repeat_patterns['DOM'] and self.repeat_patterns['DOM'][ht_value]:
                dom_values = self.repeat_patterns['DOM'][ht_value]
                params['DOM'] = str(dom_values[self.current_dom_index])

                # 更新索引，为下一次准备
                self.current_dom_index = (self.current_dom_index + 1) % len(dom_values)
                if self.current_dom_index == 0:  # 如果 DOM 循环完成，换下一个 HT
                    self.current_ht_index = (self.current_ht_index + 1) % len(self.repeat_patterns['HT'])

        # 调用父类的 save_settings 来保存
        if super().save_settings():
            # 保存重复模式数据到本地文件
            try:
                repeat_settings = {
                    "repeat_patterns": self.repeat_patterns,
                    "current_ht_index": self.current_ht_index,
                    "current_dom_index": self.current_dom_index
                }
                with open('ps_settings.json', 'w', encoding='utf-8') as f:
                    json.dump(repeat_settings, f, indent=4)
                return True
            except Exception as e:
                print(f"Error saving repeat patterns: {e}")
        return False
    
    def export_ps_settings(self):
        """导出PS特有的设置到JSON文件"""
        try:
            settings = {
                "repeat_patterns": self.repeat_patterns,
                "current_ht_index": self.current_ht_index,
                "current_dom_index": self.current_dom_index
            }
            with open('ps_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error exporting PS settings: {str(e)}")
            return False

    def load_latest_settings(self):
        """重写加载设置方法"""
        # 先调用父类加载基本设置
        super().load_latest_settings()

        if not hasattr(self, 'repeat_tree') or not self.repeat_tree:
            return

        # 清除现有重复模式
        for item in self.repeat_tree.get_children():
            self.repeat_tree.delete(item)

        # 从父类加载的设置中获取PS特有的设置
        settings = self.settings_manager.load_current_settings()
        if settings and "_ps_settings" in settings:
            ps_settings = settings["_ps_settings"]
            self.repeat_patterns = ps_settings.get("repeat_patterns", {"HT": [], "DOM": {}})
            self.current_ht_index = ps_settings.get("current_ht_index", 0)
            self.current_dom_index = ps_settings.get("current_dom_index", 0)

            # 重建树状显示
            for ht_value in self.repeat_patterns['HT']:
                ht_id = self.repeat_tree.insert("", tk.END, text="HT%", values=(f"{ht_value}%",))
                for dom_value in self.repeat_patterns['DOM'].get(str(ht_value), []):
                    self.repeat_tree.insert(ht_id, tk.END, text="DOM", values=(dom_value,))
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
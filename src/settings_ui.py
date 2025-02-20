# settings_ui.py
from __future__ import print_function
import json


try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox

from settings_manager import SettingsManager


class SettingsUI(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zygo 參數設置管理")
        self.root.minsize(400, 300)
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置grid权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.settings_manager = SettingsManager()
        self.param_entries = {}  # 初始化放在這裡
        self.setup_ui()
        self.load_latest_settings()

        # 添加視窗關閉處理

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """視窗關閉時的清理工作"""
        try:
            self.save_settings()
            self.param_entries.clear()
            self.settings_manager.close()
        finally:
            self.root.destroy()
    def setup_ui(self):


        # 樣品信息區域
        info_frame = ttk.LabelFrame(self.main_frame, text="基本信息", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 樣品名稱
        ttk.Label(info_frame, text="樣品名稱:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.sample_name = ttk.Entry(info_frame)
        self.sample_name.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)



        # 組別
        ttk.Label(info_frame, text="組別:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.group_name = ttk.Entry(info_frame)
        self.group_name.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)

        # 點位
        ttk.Label(info_frame, text="點位:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.position = ttk.Entry(info_frame)
        self.position.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)

        # 操作人員
        ttk.Label(info_frame, text="操作人員:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.operator = ttk.Entry(info_frame)
        self.operator.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        # 試片編號
        ttk.Label(info_frame, text="試片編號:").grid(row=4, column=0, sticky=tk.W, padx=5)
        self.sample_number = ttk.Entry(info_frame)  # 改名為 sample_number
        self.sample_number.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5)

        # 量測欄位區域
        field_frame = ttk.LabelFrame(self.main_frame, text="量測欄位", padding="5")
        field_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 建立表格
        self.field_tree = ttk.Treeview(field_frame, columns=("name", "path"), show="headings", height=6)
        self.field_tree.heading("name", text="欄位名稱")
        self.field_tree.heading("path", text="Identity Path")
        self.field_tree.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 欄位按鈕
        btn_frame = ttk.Frame(field_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="新增欄位", command=self.add_field).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刪除欄位", command=self.delete_field).pack(side=tk.LEFT, padx=5)

        # 參數區域
        param_frame = ttk.LabelFrame(self.main_frame, text="SOP參數", padding="5")
        param_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.main_frame.grid_rowconfigure(2, weight=1)

        # 參數列表框架（使用Canvas實現滾動）
        canvas_frame = ttk.Frame(param_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        param_frame.grid_columnconfigure(0, weight=1)
        param_frame.grid_rowconfigure(0, weight=1)

        # 創建Canvas和Scrollbar
        self.canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.params_frame = ttk.Frame(self.canvas)

        # 配置Canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 放置Canvas和Scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 創建canvas窗口
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.params_frame, anchor=tk.NW)

        # 綁定事件
        self.params_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # 按鈕區域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 左側按鈕
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        ttk.Button(left_buttons, text="新增參數", command=self.add_param).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="保存設置", command=self.save_settings).pack(side=tk.LEFT, padx=5)

        # 右側按鈕
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        ttk.Button(right_buttons, text="導出設置", command=self.export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_buttons, text="導入設置", command=self.import_settings).pack(side=tk.LEFT, padx=5)

        # 初始化參數列表
        self.param_entries = {}

    def add_field(self):
        """新增量測欄位對話框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("新增量測欄位")
        dialog.transient(self.root)
        # 讓視窗跟隨主視窗移動
        dialog.geometry("+%d+%d" % (
            self.root.winfo_x() + 50,
            self.root.winfo_y() + 50
        ))

        # 保持在最上層
        dialog.grab_set()

        # 禁止改變大小
        dialog.resizable(True, False)

        ttk.Label(dialog, text="欄位名稱:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Identity Path:").grid(row=1, column=0, padx=5, pady=5)
        path_entry = ttk.Entry(dialog)
        path_entry.grid(row=1, column=1, padx=5, pady=5)

        def save():
            name = name_entry.get().strip()
            path = path_entry.get().strip()

            if name and path:
                self.field_tree.insert("", tk.END, values=(name, path))
                dialog.destroy()

        ttk.Button(dialog, text="確定", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def delete_field(self):
        """刪除選中的量測欄位"""
        selected_items = self.field_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇要刪除的欄位")
            return

        if messagebox.askyesno("確認", "確定要刪除選中的欄位嗎?"):
            for item in selected_items:
                self.field_tree.delete(item)

    def on_frame_configure(self, event=None):
        """更新Canvas的滾動區域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event=None):
        """當Canvas調整大小時，更新內部frame的寬度"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    def add_param_entry(self, name="", value=""):
        try:
            row_frame = ttk.Frame(self.params_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)

            name_entry = ttk.Entry(row_frame, width=20)
            name_entry.insert(0, name)
            name_entry.pack(side=tk.LEFT, padx=(0, 5))

            value_entry = ttk.Entry(row_frame)
            value_entry.insert(0, value)
            value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            def remove_entry():
                del self.param_entries[name_entry]
                row_frame.destroy()

            ttk.Button(row_frame, text="移除", command=remove_entry).pack(side=tk.RIGHT)
            self.param_entries[name_entry] = value_entry

        except Exception as e:
            print("Error adding param entry: {}".format(str(e)))

    def add_param(self):
        """添加新參數"""
        self.add_param_entry()

    def get_current_params(self):
        params = {}
        try:
            for name_entry, value_entry in self.param_entries.items():
                name = name_entry.get().strip()
                value = value_entry.get().strip()
                if name and value:
                    params[name] = value
        except Exception as e:
            print("Error getting params: {}".format(str(e)))
        return params

    def load_latest_settings(self):
        settings = self.settings_manager.load_current_settings()
        if settings:
            # 載入基本資訊欄位
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

            # 只載入非系統欄位作為參數
            excluded_fields = ["sample_name", "position_name", "group_name",
                               "operator", "measurement_fields", "slide_id",
                               "sample_number"]

            for name, value in settings.items():
                if name not in excluded_fields:
                    self.add_param_entry(name, value)

            # 載入量測欄位
            for item in self.field_tree.get_children():
                self.field_tree.delete(item)
            for field in settings.get("measurement_fields", []):
                self.field_tree.insert("", tk.END, values=(field["name"], field["path"]))

    # settings_ui.py
    def save_settings(self):
        # 獲取基本信息
        sample_name = self.sample_name.get().strip()
        group_name = self.group_name.get().strip()
        position_name = self.position.get().strip()
        operator = self.operator.get().strip()
        sample_number = self.sample_number.get().strip()

        # 生成試片ID
        import time
        today = time.strftime("%Y%m%d")
        slide_id = "{0}-{1}-{2}".format(
            sample_name,
            today,
            sample_number
        ) if sample_name and sample_number else ""

        # 獲取量測欄位
        measurement_fields = []
        for item in self.field_tree.get_children():
            values = self.field_tree.item(item)["values"]
            measurement_fields.append({
                "name": values[0],
                "path": values[1]
            })

        # 只獲取 SOP 參數
        params = self.get_current_params()
        params["measurement_fields"] = measurement_fields

        try:
            return self.settings_manager.save_settings(
                sample_name,
                position_name,
                group_name,
                operator,
                "Unknown.appx",  # 或從mx獲取
                slide_id,
                sample_number,
                params
            )
        except Exception as e:
            print("Error saving settings: {}".format(e))
            return False

    def export_settings(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="settings.json"
        )
        if file_path:
            settings = {
                "sample_name": self.sample_name.get().strip(),
                "group_name": self.group_name.get().strip(),
                "position_name": self.position.get().strip(),
                "operator": self.operator.get().strip(),
                "sample_number": self.sample_number.get().strip(),  # 添加試片編號
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

            for item in self.field_tree.get_children():
                values = self.field_tree.item(item)["values"]
                settings["measurement_fields"].append({
                    "name": values[0],
                    "path": values[1]
                })

            params = self.get_current_params()
            for name, value in params.items():
                settings[name] = value

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("成功", "設置已導出")
            except Exception as e:
                messagebox.showerror("錯誤", "導出失敗: {}".format(e))

    def import_settings(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            if self.settings_manager.import_settings(file_path):
                self.load_latest_settings()
                messagebox.showinfo("成功", "設置已導入")
            else:
                messagebox.showerror("錯誤", "設置導入失敗")

    def run(self):
        """運行程序"""
        # 設置窗口大小和位置
        self.root.geometry("800x600")
        self.root.update_idletasks()

        # 居中顯示
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry("+{0}+{1}".format(x, y))

        # 設置圖標（可選）
        try:
            self.root.iconbitmap("icon.ico")  # 如果有圖標文件的話
        except:
            pass

        self.root.mainloop()

    def __del__(self):
        try:
            self.param_entries.clear()  # 清理參數入口
            if hasattr(self, 'settings_manager'):
                self.settings_manager.close()
        except:
            pass

def main():
    """主函數"""
    try:
        app = SettingsUI()
        app.run()
    except Exception as e:
        print("Error: {0}".format(str(e)))
        try:
            messagebox.showerror("錯誤", "程式錯誤：{0}".format(str(e)))
        except:
            print("Critical error: {0}".format(str(e)))

if __name__ == "__main__":
    main()
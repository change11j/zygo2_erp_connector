import tkinter as tk
from tkinter import ttk
import time
from collections import defaultdict


class MeasurementUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Data Monitor")

        # 创建主滚动框架
        self.main_canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局主组件
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 存储所有slide块的引用
        self.slide_frames = {}

    def update_display(self, data_dict):
        # 清理不再存在的slide块
        current_slides = set(data_dict.keys())
        existing_slides = set(self.slide_frames.keys())

        for slide_id in existing_slides - current_slides:
            self.slide_frames[slide_id].destroy()
            del self.slide_frames[slide_id]

        # 更新或创建slide块
        for slide_id, slide_data in data_dict.items():
            if slide_id not in self.slide_frames:
                # 创建新的slide块
                frame = ttk.LabelFrame(self.scrollable_frame, text=slide_id)
                frame.pack(fill="x", padx=5, pady=5)

                # 基础信息区域
                base_info_frame = ttk.Frame(frame)
                base_info_frame.pack(fill="x", padx=5, pady=5)

                # 创建基础信息标签
                base_info_labels = {}
                for i, (key, value) in enumerate(slide_data['base_info'].items()):
                    ttk.Label(base_info_frame, text=f"{key}:").grid(row=i // 3, column=(i % 3) * 2, sticky="e", padx=5)
                    base_info_labels[key] = ttk.Label(base_info_frame, text=value)
                    base_info_labels[key].grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w")

                # 测量数据表格
                headers = ['positionName'] + list(next(iter(slide_data['positions'].values())).keys())
                tree = ttk.Treeview(frame, columns=headers, show='headings')
                for header in headers:
                    tree.heading(header, text=header)
                    tree.column(header, width=100)  # 设置列宽

                tree.pack(fill="x", padx=5, pady=5)

                self.slide_frames[slide_id] = {
                    'frame': frame,
                    'base_info_labels': base_info_labels,
                    'tree': tree
                }

            # 更新基础信息
            frame_data = self.slide_frames[slide_id]
            for key, value in slide_data['base_info'].items():
                if key in frame_data['base_info_labels']:
                    frame_data['base_info_labels'][key].configure(text=value)

            # 更新测量数据
            tree = frame_data['tree']
            for item in tree.get_children():
                tree.delete(item)

            for position, values in slide_data['positions'].items():
                row_data = [position] + list(values.values())
                tree.insert('', 'end', values=row_data)


def main():
    root = tk.Tk()
    root.geometry("1000x800")  # 设置窗口大小
    ui = MeasurementUI(root)

    def generate_test_data():
        """生成测试数据"""
        test_data = {
            'TG-Test-1': {
                'base_info': {
                    'operator': 'Tom',
                    'groupName': 'IT',
                    'Updata': 'm.updated',
                    'attributeName1': 'attributeValue1',
                    'attributeName2': 'attributeValue2'
                },
                'positions': {
                    'positionName1': {
                        'dataname1': '1.399',
                        'dataname2': '1.435',
                        'dataname3': '1.425',
                        'dataname4': '9.380',
                        'dataname5': '9.369',
                        'dataname6': '9.372'
                    },
                    'positionName2': {
                        'dataname1': '1.398',
                        'dataname2': '1.434',
                        'dataname3': '1.424',
                        'dataname4': '9.379',
                        'dataname5': '9.368',
                        'dataname6': '9.371'
                    }
                }
            },
            'TG-Test-2': {
                'base_info': {
                    'operator': 'Tom',
                    'groupName': 'IT',
                    'Updata': 'm.updated',
                    'attributeName1': 'attributeValue1',
                    'attributeName2': 'attributeValue2'
                },
                'positions': {
                    'positionName1': {
                        'dataname1': '1.399',
                        'dataname2': '1.435',
                        'dataname3': '1.425',
                        'dataname4': '9.380',
                        'dataname5': '9.369',
                        'dataname6': '9.372'
                    }
                }
            }
        }
        return test_data

    def update():
        # 更新测试数据
        test_data = generate_test_data()
        ui.update_display(test_data)
        root.after(1000, update)  # 每秒更新一次

    update()
    root.mainloop()


if __name__ == "__main__":
    main()
"""
OCR Handler for Python 3.4.3
Compatible with Python 3.4.3 syntax requirements
"""
import os
import sqlite3

from PIL import ImageGrab
import pytesseract
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
from erp_util import ERPAPIUtil
from settings_manager import SettingsManager
import threading
import logging
import json
import time

class RemoteOCR(object):
    def __init__(self):
        self.tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        logging.info("Tesseract version: {0}".format(
            pytesseract.get_tesseract_version()))

    def capture_region(self):
        """捕獲指定區域"""
        try:
            screenshot = ImageGrab.grab(bbox=(1060, 760, 1200, 780))
            logging.debug("Screenshot size: {0}, mode: {1}".format(
                screenshot.size, screenshot.mode))
            return screenshot
        except Exception as e:
            logging.error("Screenshot error: {0}".format(e))
            return None

    def preprocess_image(self, image):
        """預處理圖像以提高OCR準確性"""
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            scale_factor = 2
            width = int(gray.shape[1] * scale_factor)
            height = int(gray.shape[0] * scale_factor)
            enlarged = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

            enhanced = cv2.convertScaleAbs(enlarged, alpha=1.5, beta=0)

            binary = cv2.adaptiveThreshold(
                enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            bordered = cv2.copyMakeBorder(
                binary,
                10, 10, 10, 10,
                cv2.BORDER_CONSTANT,
                value=[255, 255, 255]
            )

            logging.debug("Processed image size: {0}".format(bordered.shape))
            return bordered

        except Exception as e:
            logging.error("Image processing error: {0}".format(e))
            return None

    def extract_text(self, image):
        """執行OCR識別"""
        try:
            psm_modes = [6, 7, 8, 13]
            results = []

            for psm in psm_modes:
                custom_config = '--oem 3 --psm {0}'.format(psm)
                text = pytesseract.image_to_string(
                    image,
                    config=custom_config,
                    lang='eng'
                )
                text = text.strip()
                if text:
                    results.append(text)
                logging.debug("PSM {0} result: '{1}'".format(psm, text))

            return results[0] if results else None

        except Exception as e:
            logging.error("OCR error: {0}".format(e))
            return None

    def extract_number(self, text):
        """從OCR文本中提取數字，保留小數點前的零"""
        try:
            if not text:
                return None

            # 清理並標準化文本
            text = text.strip()

            # 檢查是否包含多個小數點或逗號
            dots = text.count('.') + text.count(',')
            if dots > 1:
                logging.error(f"Multiple decimal separators found in text: {text}")
                return None

            # 替換逗號為小數點
            text = text.replace(',', '.')

            # 只保留數字、小數點和負號
            number_text = ''.join(c for c in text if c.isdigit() or c in '.-')

            # 檢查格式
            if not number_text:
                return None

            try:
                value = float(number_text)

                # 保持前導零的格式
                if text.startswith("0"):
                    # 使用格式化字符串保持前導零
                    return float(f"{value:.{len(text.split('.')[1]) if '.' in text else 0}f}")
                return value

            except ValueError as e:
                logging.error(f"Value error converting '{text}' to float: {e}")
                return None
            except IndexError as e:
                logging.error(f"Index error processing '{text}': {e}")
                return None

        except Exception as e:
            logging.error(f"General error in extract_number: {e}")
            return None


class SliceDataManager(object):
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.slice_data_lock = threading.Lock()
        self.settings_manager = SettingsManager()
        self.last_data_name = self.load_last_data_name()

    def load_last_data_name(self):
        """從配置文件加載上次使用的data_name"""
        try:
            if os.path.exists('slice_settings.json'):
                with open('slice_settings.json', 'r') as f:
                    settings = json.load(f)
                    return settings.get('last_data_name', 'FT')
        except Exception as e:
            logging.error("Error loading last data name: {0}".format(e))
        return 'FT'

    def save_last_data_name(self, data_name):
        """保存data_name到配置文件"""
        try:
            settings = {'last_data_name': data_name}
            with open('slice_settings.json', 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            logging.error("Error saving last data name: {0}".format(e))

    def save_and_upload_slice_data(self, data_name, data_value):
        """保存並上傳切片數據"""
        try:
            settings = self.settings_manager.load_current_settings()
            if not settings:
                logging.error("No settings found")
                return False

            # 獲取 SOP 參數
            sop_params = {}
            exclude_keys = {'sample_name', 'position_name', 'group_name',
                            'operator', 'measurement_fields', 'slide_id',
                            'sample_number', 'appx_filename'}

            for key, value in settings.items():
                if key not in exclude_keys:
                    sop_params[key] = value

            with self.slice_data_lock:
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    c = conn.cursor()

                    # 1. 插入 measures 表記錄
                    c.execute("""
                        INSERT INTO measures 
                        (sample_name, position_name, group_name, operator, appx_filename, 
                         slide_id, sample_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        settings.get('sample_name', ''),
                        settings.get('position_name', ''),
                        settings.get('group_name', ''),
                        settings.get('operator', 'Unknown'),
                        settings.get('appx_filename', 'Unknown.appx'),
                        settings.get('slide_id', ''),
                        settings.get('sample_number', '')
                    ))

                    measure_id = c.lastrowid

                    # 2. 插入 measured_data 表記錄
                    c.execute("""
                        INSERT INTO measured_data 
                        (measure_id, data_name, data_value, identity_path)
                        VALUES (?, ?, ?, ?)
                    """, (
                        measure_id,
                        data_name,
                        float(data_value),
                        "OCR_GENERATED"
                    ))

                    measured_data_id = c.lastrowid

                    # 3. 插入 SOP 參數到 measure_attributes 表
                    for param_name, param_value in sop_params.items():
                        c.execute("""
                            INSERT INTO measure_attributes
                            (measured_data_id, attribute_name, attribute_value)
                            VALUES (?, ?, ?)
                        """, (measured_data_id, param_name, str(param_value)))

                    conn.commit()

                # 構建用於 ERP 上傳的數據結構
                measured_data = {
                    'field_name': data_name,
                    'value': float(data_value),
                    'attributes': sop_params,  # 加入 SOP 參數
                    'operator': settings.get('operator', 'Unknown')
                }

                # 上傳到 ERP
                success, error = ERPAPIUtil.upload_measurement(
                    settings.get('sample_name', ''),
                    settings.get('position_name', ''),
                    settings.get('group_name', ''),
                    settings.get('operator', 'Unknown'),
                    settings.get('appx_filename', 'Unknown.appx'),
                    settings.get('slide_id', ''),
                    settings.get('sample_number', ''),
                    [measured_data]
                )

                if not success:
                    logging.error("Failed to upload slice data to ERP: {0}".format(error))
                    return False

                self.save_last_data_name(data_name)
                return True

        except Exception as e:
            logging.error("Error in save_and_upload_slice_data: {0}".format(e))
            return False


class DataCheckUI:
    def __init__(self, data_value, raw_text=""):
        self.root = tk.Tk()
        self.root.title("數據確認")
        self.data_manager = SliceDataManager()
        self.result = None

        # 載入當前設置
        self.settings = self.data_manager.settings_manager.load_current_settings()

        # 設置窗口大小和位置
        window_width = 600  # 加寬以容納更多內容
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 創建滾動視窗
        self.create_scrollable_frame()
        self.create_widgets(data_value, raw_text)

    def create_scrollable_frame(self):
        # 創建主滾動視窗
        self.main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack 到主窗口
        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_widgets(self, data_value, raw_text):
        # OCR結果區域
        ocr_frame = ttk.LabelFrame(self.scrollable_frame, text="OCR 結果", padding="5")
        ocr_frame.pack(fill="x", padx=5, pady=5)

        if raw_text:
            ttk.Label(ocr_frame, text="原始文本:").pack(side="left")
            ttk.Label(ocr_frame, text=raw_text).pack(side="left", padx=5)

        # 測量數據區域
        measure_frame = ttk.LabelFrame(self.scrollable_frame, text="測量數據", padding="5")
        measure_frame.pack(fill="x", padx=5, pady=5)

        # Data Name
        name_frame = ttk.Frame(measure_frame)
        name_frame.pack(fill="x", pady=2)
        ttk.Label(name_frame, text="Data Name:").pack(side="left")
        self.name_var = tk.StringVar(value=self.data_manager.last_data_name)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        self.name_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Data Value
        value_frame = ttk.Frame(measure_frame)
        value_frame.pack(fill="x", pady=2)
        ttk.Label(value_frame, text="Data Value:").pack(side="left")
        self.value_var = tk.StringVar(value=str(data_value))
        self.value_entry = ttk.Entry(value_frame, textvariable=self.value_var)
        self.value_entry.pack(side="left", padx=5, fill="x", expand=True)

        # SOP參數區域
        sop_frame = ttk.LabelFrame(self.scrollable_frame, text="SOP 參數", padding="5")
        sop_frame.pack(fill="x", padx=5, pady=5)

        # 創建SOP參數輸入欄位
        self.sop_entries = {}
        exclude_keys = ['sample_name', 'position_name', 'group_name',
                        'operator', 'measurement_fields', 'slide_id',
                        'sample_number', 'appx_filename']

        for key, value in self.settings.items():
            if key not in exclude_keys:
                param_frame = ttk.Frame(sop_frame)
                param_frame.pack(fill="x", pady=2)
                ttk.Label(param_frame, text=f"{key}:").pack(side="left")
                value_var = tk.StringVar(value=str(value))
                entry = ttk.Entry(param_frame, textvariable=value_var)
                entry.pack(side="left", padx=5, fill="x", expand=True)
                self.sop_entries[key] = value_var

        # 基本資訊區域（改為可編輯）
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="基本資訊", padding="5")
        info_frame.pack(fill="x", padx=5, pady=5)

        # 創建基本資訊輸入欄位
        self.base_info_entries = {}

        # 基本資訊欄位定義
        base_info_fields = [
            ("sample_name", "Sample Name", self.settings.get('sample_name', '')),
            ("position_name", "Position Name", self.settings.get('position_name', '')),
            ("group_name", "Group Name", self.settings.get('group_name', '')),
            ("operator", "Operator", self.settings.get('operator', '')),
            ("sample_number", "Sample Number", self.settings.get('sample_number', ''))
        ]

        # 創建每個基本資訊的輸入欄位
        for key, label, value in base_info_fields:
            info_row = ttk.Frame(info_frame)
            info_row.pack(fill="x", pady=2)

            # 標籤
            ttk.Label(info_row, text=f"{label}:", width=15).pack(side="left")

            # 輸入框
            value_var = tk.StringVar(value=value)
            entry = ttk.Entry(info_row)
            entry.insert(0, value)
            entry.pack(side="left", padx=5, fill="x", expand=True)

            # 保存到字典中以便後續使用
            self.base_info_entries[key] = entry

        # 按鈕區域
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="確認", command=self.confirm).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side="left", padx=5)

    def confirm(self):
        try:
            # 驗證輸入
            data_name = self.name_var.get().strip()
            data_value = float(self.value_var.get().strip())

            if not data_name:
                raise ValueError("Data name cannot be empty")

            # 更新基本資訊
            for key, entry in self.base_info_entries.items():
                value = entry.get().strip()
                if not value and key in ['sample_name', 'position_name', 'group_name']:
                    raise ValueError(f"{key} cannot be empty")
                self.settings[key] = value

            # 更新 SOP 參數
            for key, var in self.sop_entries.items():
                self.settings[key] = var.get().strip()

            # 更新 slide_id
            import time
            today = time.strftime("%Y%m%d")
            self.settings['slide_id'] = "{0}-{1}-{2}".format(
                self.settings['sample_name'],
                today,
                self.settings['sample_number']
            )

            # 保存設置
            success = self.data_manager.settings_manager.save_settings(
                self.settings['sample_name'],
                self.settings['position_name'],
                self.settings['group_name'],
                self.settings['operator'],
                self.settings.get('appx_filename', 'Unknown.appx'),
                self.settings['slide_id'],
                self.settings['sample_number'],
                self.settings
            )

            if not success:
                raise ValueError("Failed to save settings")

            # 設置結果
            self.result = {
                'data_name': data_name,
                'data_value': data_value,
                'settings': self.settings
            }

            self.root.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def cancel(self):
        self.result = None
        self.root.destroy()

    def get_result(self):
        self.root.mainloop()
        return self.result

def process_slice_data():
    """處理切片數據的主函數"""
    try:
        # 初始化OCR處理器
        ocr = RemoteOCR()

        # 捕獲屏幕區域
        image = ocr.capture_region()
        if image is None:
            logging.error("Failed to capture screen region")
            return False

        # 保存原始截圖（用於調試）
        image.save("debug_screenshot.png")

        # 處理圖像
        processed_image = ocr.preprocess_image(image)
        if processed_image is None:
            logging.error("Failed to process image")
            return False

        # 保存處理後的圖像（用於調試）
        cv2.imwrite("debug_processed.png", processed_image)

        # 執行OCR識別
        raw_text = ocr.extract_text(processed_image)
        if not raw_text:
            logging.error("No text recognized")
            return False

        # 提取數字
        data_value = ocr.extract_number(raw_text)
        if data_value is None:
            logging.error("Failed to extract number from text")
            return False

        # 創建並顯示確認UI
        ui = DataCheckUI(data_value, raw_text)
        result = ui.get_result()

        if result is None:
            logging.info("User cancelled the operation")
            return False

        # 保存並上傳數據
        slice_manager = SliceDataManager()
        success = slice_manager.save_and_upload_slice_data(
            data_name=result['data_name'],
            data_value=result['data_value']
        )

        if success:
            logging.info("Successfully processed slice data")
            return True
        else:
            logging.error("Failed to process slice data")
            ui.show_error_message("無法上傳到erp,請檢查網路或是本地資料庫")

            return False

    except Exception as e:
        logging.error("Error processing slice data: {0}".format(e))
        return False

if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 運行主程序
    success = process_slice_data()
    print("Process completed successfully" if success else "Process failed")
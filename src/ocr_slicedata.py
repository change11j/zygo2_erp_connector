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
        """從OCR文本中提取數字"""
        try:
            if not text:
                return None

            # 移除所有非數字字符(保留小數點和負號)
            number_text = ''.join(c for c in text if c.isdigit() or c in '.-')

            # 嘗試轉換為浮點數
            try:
                return float(number_text)
            except ValueError:
                logging.error("Could not convert '{0}' to float".format(number_text))
                return None

        except Exception as e:
            logging.error("Number extraction error: {0}".format(e))
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
                logging.error("No settings found for slice data upload")
                return False

            with self.slice_data_lock:
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    c = conn.cursor()

                    # 1. 首先插入measures表記錄
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

                    # 獲取新插入的measure_id
                    measure_id = c.lastrowid

                    # 2. 插入measured_data表記錄
                    c.execute("""
                        INSERT INTO measured_data 
                        (measure_id, data_name, data_value, identity_path)
                        VALUES (?, ?, ?, ?)
                    """, (
                        measure_id,
                        data_name,
                        float(data_value),
                        "OCR_GENERATED"  # 因為是OCR生成的數據,使用固定標識
                    ))

                    conn.commit()

                # 構建用於ERP上傳的數據結構
                measured_data = {
                    'field_name': data_name,
                    'value': float(data_value),
                    'attributes': {},
                    'operator': settings.get('operator', 'Unknown')
                }

                # 上傳到ERP
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

class DataCheckUI(object):
    def __init__(self, data_value, raw_text=""):
        self.root = tk.Tk()
        self.root.title("數據確認")
        self.data_manager = SliceDataManager()
        self.result = None

        # 設置窗口大小和位置
        window_width = 400
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry("{0}x{1}+{2}+{3}".format(
            window_width, window_height, x, y))

        self.create_widgets(data_value, raw_text)

    def create_widgets(self, data_value, raw_text):
        # OCR原始文本顯示
        if raw_text:
            raw_frame = ttk.Frame(self.root)
            raw_frame.pack(pady=5, padx=20, fill='x')
            ttk.Label(raw_frame, text="OCR原始文本:").pack(side='left')
            ttk.Label(raw_frame, text=raw_text).pack(side='left', padx=(5, 0))

        # Data Name 輸入框
        name_frame = ttk.Frame(self.root)
        name_frame.pack(pady=10, padx=20, fill='x')

        ttk.Label(name_frame, text="Data Name:").pack(side='left')
        self.name_var = tk.StringVar(value=self.data_manager.last_data_name)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        self.name_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))

        # Data Value 輸入框
        value_frame = ttk.Frame(self.root)
        value_frame.pack(pady=10, padx=20, fill='x')

        ttk.Label(value_frame, text="Data Value:").pack(side='left')
        self.value_var = tk.StringVar(value=str(data_value))
        self.value_entry = ttk.Entry(value_frame, textvariable=self.value_var)
        self.value_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))

        # 按鈕框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="確認", command=self.confirm).pack(side='left', padx=10)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side='left', padx=10)

    def confirm(self):
        try:
            data_name = self.name_var.get().strip()
            data_value = float(self.value_var.get().strip())

            if not data_name:
                raise ValueError("Data name cannot be empty")

            self.result = {
                'data_name': data_name,
                'data_value': data_value
            }
            self.root.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

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
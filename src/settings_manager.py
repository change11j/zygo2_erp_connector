# settings_manager.py
from __future__ import print_function
import os
import json
import sqlite3
import sys
from datetime import datetime
from logging import fatal
from tkinter import messagebox

# zygo_path = 'C:\\projects\\zygo2_erp_connector'
zygo_path = '/Users/mac/Desktop/topgiga/projects/zygo2_erp_connector/zygo2_erp_connector'
if zygo_path not in sys.path:
    sys.path.append(zygo_path)
from zygo import mx


class SettingsManager(object):
    def __init__(self, db_path="measurements.db"):
        self.db_path = db_path
        self.initialize_database()
        self.load_current_settings()

    def initialize_database(self):
        """初始化資料庫"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # 创建 Measure 表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS measures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_name TEXT NOT NULL,
                    position_name TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    appx_filename TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建 MeasuredData 表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS measured_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measure_id INTEGER,
                    data_name TEXT NOT NULL,
                    data_value REAL NOT NULL,
                    identity_path TEXT NOT NULL,
                    FOREIGN KEY (measure_id) REFERENCES measures(id)
                )
            """)
            # 檢查並添加新列
            try:
                self.cursor.execute("ALTER TABLE measures ADD COLUMN slide_id TEXT")
            except:
                pass  # 列已存在

            try:
                self.cursor.execute("ALTER TABLE measures ADD COLUMN sample_number TEXT")
            except:
                pass  # 列已存在

            # 创建 MeasureAttribute 表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS measure_attributes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measured_data_id INTEGER,
                    attribute_name TEXT NOT NULL,
                    attribute_value TEXT NOT NULL,
                    FOREIGN KEY (measured_data_id) REFERENCES measured_data(id)
                )
            """)
            # 添加 PS 重复模式表
            self.cursor.execute("""
                   CREATE TABLE IF NOT EXISTS ps_patterns (
                        measure_id INTEGER PRIMARY KEY,
                        ht_values TEXT,  -- JSON array of HT values
                        dom_values TEXT, -- JSON object mapping HT to DOM values
                        current_ht_index INTEGER,
                        current_dom_index INTEGER,
                        FOREIGN KEY (measure_id) REFERENCES measures(id)
                    )
               """)

            self.conn.commit()
            print("Database initialized successfully")



        except Exception as e:
            print("Database initialization error: {0}".format(str(e)))
            raise


    def save_measurement_field(self, field_name, field_unit, identity_path, group_name):
        """保存量測欄位設置"""
        try:
            self.cursor.execute("""
                INSERT INTO measurement_fields 
                (field_name, field_unit, identity_path, group_name)
                VALUES (?, ?, ?, ?)
            """, (field_name, field_unit, identity_path, group_name))
            self.conn.commit()
            return True
        except Exception as e:
            print("Error saving measurement field: {0}".format(str(e)))
            return False

    def get_measurement_fields(self):
        """獲取所有量測欄位設置"""
        try:
            self.cursor.execute("""
                SELECT field_name, field_unit, identity_path, group_name
                FROM measurement_fields
                ORDER BY id DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print("Error getting measurement fields: {0}".format(str(e)))
            return []

    def save_operator(self, operator_id, operator_name):
        """保存操作人員"""
        try:
            self.cursor.execute("""
                INSERT INTO operators (operator_id, operator_name)
                VALUES (?, ?)
            """, (operator_id, operator_name))
            self.conn.commit()
            return True
        except Exception as e:
            print("Error saving operator: {0}".format(str(e)))
            return False

    def get_operators(self):
        """獲取所有操作人員"""
        try:
            self.cursor.execute("""
                SELECT operator_id, operator_name 
                FROM operators
                ORDER BY id DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print("Error getting operators: {0}".format(str(e)))
            return []

    def load_current_settings(self):
        """从数据库加载最新设置，过滤掉不需要在UI显示的字段"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()

                # 获取最新的 measure 记录
                c.execute("""
                                SELECT id, sample_name, position_name, group_name, operator, slide_id, sample_number
                                FROM measures 
                                ORDER BY id DESC LIMIT 1
                            """)

                measure_row = c.fetchone()
                if not measure_row:
                    return None

                measure_id, sample_name, position_name, group_name, operator, slide_id, sample_number = measure_row

                # 构建基本设置
                settings = {
                    "sample_name": sample_name,
                    "position_name": position_name,
                    "group_name": group_name,
                    "operator": operator,
                    "slide_id": slide_id,  # 完整ID
                    "sample_number": sample_number,  # 試片編號
                    "measurement_fields": []
                }

                # 获取所有 measured_data
                c.execute("""
                    SELECT id, data_name, identity_path 
                    FROM measured_data
                    WHERE measure_id = ?
                """, (measure_id,))

                for data_row in c.fetchall():
                    data_id, data_name, identity_path = data_row

                    # 获取该 measured_data 的所有 attributes
                    c.execute("""
                        SELECT attribute_name, attribute_value
                        FROM measure_attributes
                        WHERE measured_data_id = ?
                    """, (data_id,))

                    # 添加量测字段
                    field = {
                        "name": data_name,
                        "path": identity_path
                    }
                    settings["measurement_fields"].append(field)

                    # 添加 attributes 到设置中
                    # 过滤掉不需要显示的字段
                    for attr_name, attr_value in c.fetchall():
                        if attr_name not in ['appx_filename','slide_id']:  # 在这里过滤掉不需要显示的字段
                            settings[attr_name] = attr_value

                return settings

        except Exception as e:
            print("Error loading settings: %s", str(e))
            return None

    # 在 settings_manager.py 中修改 import_settings 方法:
    def import_settings(self, file_path):
        """导入设置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            if "ps_patterns" in settings:
                del settings["ps_patterns"]

            # 获取 appx_filename
            try:
                appx_filename = mx.get_application_path() or "Unknown.appx"
            except:
                appx_filename = "Unknown.appx"

            # 生成 slide_id (如果需要)
            import time
            today = time.strftime("%Y%m%d")
            sample_name = settings.get("sample_name", "")
            sample_number = settings.get("sample_number", "")
            slide_id = "{0}-{1}-{2}".format(
                sample_name,
                today,
                sample_number
            ) if sample_name and sample_number else ""

            # 準備 SOP 參數
            params = {}
            params["measurement_fields"] = settings.get("measurement_fields", [])

            # 添加其他參數(除了基本信息外都是 SOP 參數)
            excluded_fields = [
                "sample_name", "position_name", "group_name",
                "operator", "measurement_fields", "slide_id",
                "sample_number", "appx_filename"
            ]
            for key, value in settings.items():
                if key not in excluded_fields:
                    params[key] = value

            # 調用 save_settings
            return self.save_settings(
                settings.get("sample_name", ""),
                settings.get("position_name", ""),
                settings.get("group_name", ""),
                settings.get("operator", ""),
                appx_filename,
                slide_id,
                sample_number,
                params
            )

        except Exception as e:
            print("Error importing settings: {0}".format(str(e)))
            return False

    def save_settings(self, sample_name, position_name, group_name, operator,
                      appx_filename, slide_id, sample_number, params):
        """保存设置到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()

                # 插入 Measure
                c.execute("""
                    INSERT INTO measures 
                    (sample_name, position_name, group_name, operator, 
                     appx_filename, slide_id, sample_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sample_name,
                    position_name,
                    group_name,
                    operator,
                    appx_filename,
                    slide_id,
                    sample_number
                ))

                measure_id = c.lastrowid

                # 插入 MeasuredData
                for field in params.get("measurement_fields", []):
                    c.execute("""
                        INSERT INTO measured_data
                        (measure_id, data_name, data_value, identity_path)
                        VALUES (?, ?, ?, ?)
                    """, (measure_id, field["name"], 0.0, field["path"]))

                    measured_data_id = c.lastrowid

                    # 只插入 SOP 參數
                    for attr_name, attr_value in params.items():
                        if attr_name != "measurement_fields":  # 移除過濾條件,只要不是measurement_fields都保存
                            c.execute("""
                                INSERT INTO measure_attributes
                                (measured_data_id, attribute_name, attribute_value)
                                VALUES (?, ?, ?)
                            """, (measured_data_id, attr_name, str(attr_value)))

                conn.commit()
                return True

        except Exception as e:
            print("Error saving settings:", str(e))
            if 'conn' in locals():
                conn.rollback()
            return False

    def export_settings(self, file_path):
        settings = {
            "sample_name": self.sample_name.get().strip(),
            "group_name": self.group_name.get().strip(),
            "position_name": self.position.get().strip(),
            "operator": self.operator.get().strip(),
            "sample_number": self.sample_number.get().strip(),
            "measurement_fields": []
        }

        # 添加量測欄位
        for item in self.field_tree.get_children():
            values = self.field_tree.item(item)["values"]
            settings["measurement_fields"].append({
                "name": values[0],
                "path": values[1]
            })

        # 添加 SOP 參數
        params = self.get_current_params()
        for name, value in params.items():
            settings[name] = value

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", "設置已導出")
        except Exception as e:
            messagebox.showerror("錯誤", "導出失敗: {}".format(e))

    def save_ps_patterns(self, measure_id, patterns):
        """保存PS重复模式设置"""
        try:
            # 确保数据一致性
            repeat_patterns = patterns['repeat_patterns']
            normalized_patterns = {
                'repeat_patterns': {
                    'HT': repeat_patterns['HT'],
                    'DOM': {str(k): v for k, v in repeat_patterns['DOM'].items()}
                },
                'current_ht_index': patterns['current_ht_index'],
                'current_dom_index': patterns['current_dom_index']
            }

            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()

                # 将patterns字典的内容转换为JSON字符串
                ht_values = json.dumps(normalized_patterns['repeat_patterns']['HT'])
                dom_values = json.dumps(normalized_patterns['repeat_patterns']['DOM'])

                c.execute("""
                    INSERT OR REPLACE INTO ps_patterns 
                    (measure_id, ht_values, dom_values, current_ht_index, current_dom_index)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    measure_id,
                    ht_values,
                    dom_values,
                    normalized_patterns['current_ht_index'],
                    normalized_patterns['current_dom_index']
                ))

                conn.commit()
                return True

        except Exception as e:
            print(f"Error saving PS patterns: {str(e)}")
            return False

    def get_ps_patterns(self, measure_id):
        """获取PS重复模式设置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()

                c.execute("""
                    SELECT ht_values, dom_values, current_ht_index, current_dom_index
                    FROM ps_patterns
                    WHERE measure_id = ?
                """, (measure_id,))

                row = c.fetchone()
                if row:
                    return {
                        'repeat_patterns': {
                            'HT': json.loads(row[0]),
                            'DOM': json.loads(row[1])
                        },
                        'current_ht_index': row[2],
                        'current_dom_index': row[3]
                    }
                return None

        except Exception as e:
            print(f"Error getting PS patterns: {str(e)}")
            return None

    def get_latest_measure_id(self):
        """获取最新的 measure_id"""
        try:
            self.cursor.execute("SELECT MAX(id) FROM measures")
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print("Error getting latest measure id:", str(e))
            return None


    def close(self):
        """關閉數據庫連接"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print("Error closing database: {0}".format(str(e)))
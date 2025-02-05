# settings_manager.py
from __future__ import print_function
import os
import json
import sqlite3
from datetime import datetime
from logging import fatal
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
                    SELECT id, sample_name, position_name, group_name, operator
                    FROM measures 
                    ORDER BY id DESC LIMIT 1
                """)

                measure_row = c.fetchone()
                if not measure_row:
                    return None

                measure_id, sample_name, position_name, group_name, operator = measure_row

                # 构建基本设置 (不包含 appx_filename)
                settings = {
                    "sample_name": sample_name,
                    "position_name": position_name,
                    "group_name": group_name,
                    "operator": operator,
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
                        if attr_name not in ['appx_filename']:  # 在这里过滤掉不需要显示的字段
                            settings[attr_name] = attr_value

                return settings

        except Exception as e:
            print("Error loading settings: %s", str(e))
            return None

    def import_settings(self, file_path):
        """导入设置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # 打印导入的设置内容
            print("Importing settings:", settings)

            # 验证必要字段
            required_fields = ["sample_name", "position_name", "group_name", "operator"]
            for field in required_fields:
                if field not in settings:
                    settings[field] = ""

            # 获取 appx_filename
            try:
                appx_filename = mx.get_application_path() or "Unknown.appx"
            except:
                appx_filename = "Unknown.appx"

            # 准备参数字典
            params = {}
            params["measurement_fields"] = settings.get("measurement_fields", [])

            # 添加其他参数
            for key, value in settings.items():
                if key not in ["sample_name", "position_name", "group_name",
                               "operator", "measurement_fields", "appx_filename"]:
                    params[key] = value

            # 调用 save_settings
            return self.save_settings(
                settings["sample_name"],
                settings["position_name"],
                settings["group_name"],
                settings["operator"],
                appx_filename,
                params
            )

        except Exception as e:
            print("Error importing settings: {0}".format(str(e)))
            return False

    def save_settings(self, sample_name, position_name, group_name, operator,
                      appx_filename, params):
        """保存设置到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()

                # 插入 Measure
                c.execute("""
                    INSERT INTO measures 
                    (sample_name, position_name, group_name, operator, appx_filename)
                    VALUES (?, ?, ?, ?, ?)
                """, (sample_name, position_name, group_name, operator, appx_filename))

                measure_id = c.lastrowid

                # 插入 MeasuredData
                for field in params.get("measurement_fields", []):
                    c.execute("""
                        INSERT INTO measured_data
                        (measure_id, data_name, data_value, identity_path)
                        VALUES (?, ?, ?, ?)
                    """, (measure_id, field["name"], 0.0, field["path"]))

                    measured_data_id = c.lastrowid

                    # 插入 MeasureAttribute
                    for attr_name, attr_value in params.items():
                        if attr_name not in ["measurement_fields"]:
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
        """導出設置到JSON文件"""
        try:
            settings = self.save_settings()
            if settings:
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
                return True
            return False
        except Exception as e:
            print("Error exporting settings: {0}".format(str(e)))
            return False



    def close(self):
        """關閉數據庫連接"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print("Error closing database: {0}".format(str(e)))
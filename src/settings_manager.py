# settings_manager.py
from __future__ import print_function
import os
import json
import sqlite3
from datetime import datetime
from logging import fatal


class SettingsManager(object):
    def __init__(self, db_path="measurements.db"):
        self.db_path = db_path
        self.initialize_database()
        self.load_current_settings()

    def initialize_database(self):
        """初始化數據庫"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # 創建measurements表
            self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS measurements (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sample_name TEXT NOT NULL,
                            position_name TEXT NOT NULL,
                            group_name TEXT NOT NULL,
                            operator TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

            # 創建measurement_params表來儲存參數
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS measurement_params (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER,
                    param_name TEXT NOT NULL,
                    param_value TEXT NOT NULL,
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id)
                )
            """)

            # 創建measurement_fields表來儲存欄位設置
            self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS measurement_fields (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        measurement_id INTEGER,
                        field_name TEXT NOT NULL,
                        identity_path TEXT NOT NULL,
                        FOREIGN KEY (measurement_id) REFERENCES measurements(id)
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
        try:
            self.cursor.execute("""
                SELECT m.id, m.sample_name, m.position_name, m.group_name, m.operator,
                       mf.field_name, mf.identity_path,
                       mp.param_name, mp.param_value
                FROM measurements m
                LEFT JOIN measurement_fields mf ON m.id = mf.measurement_id
                LEFT JOIN measurement_params mp ON m.id = mp.measurement_id
                WHERE m.id = (SELECT MAX(id) FROM measurements)
            """)

            rows = self.cursor.fetchall()
            if not rows:
                return None

            settings = {
                "sample_name": rows[0][1],
                "position_name": rows[0][2],
                "group_name": rows[0][3],
                "operator": rows[0][4],
                "measurement_fields": []
            }

            # 處理量測欄位
            fields_seen = set()
            for row in rows:
                if row[5] and row[6] and (row[5], row[6]) not in fields_seen:
                    settings["measurement_fields"].append({
                        "name": row[5],
                        "path": row[6]
                    })
                    fields_seen.add((row[5], row[6]))

            # 處理SOP參數
            for row in rows:
                if row[7] and row[8]:
                    settings[row[7]] = row[8]

            return settings

        except Exception as e:
            print("Error loading settings: {0}".format(str(e)))
            return None

    def save_settings(self, sample_name, position_name, group_name, params=None):
        """保存設置到數據庫"""
        try:
            # 插入基本信息
            self.cursor.execute("""
                INSERT INTO measurements 
                (sample_name, position_name, group_name, operator)
                VALUES (?, ?, ?, ?)
            """, (
                sample_name,
                position_name,
                group_name,
                params.get("operator", "")  # operator 從 params 取得
            ))

            measurement_id = self.cursor.lastrowid

            # 插入量測欄位
            measurement_fields = params.get("measurement_fields", [])
            for field in measurement_fields:
                self.cursor.execute("""
                    INSERT INTO measurement_fields 
                    (measurement_id, field_name, identity_path)
                    VALUES (?, ?, ?)
                """, (measurement_id, field["name"], field["path"]))

            # 插入其他參數
            for name, value in params.items():
                if name not in ["measurement_fields", "parameter_name", "group_name"]:
                    self.cursor.execute("""
                        INSERT INTO measurement_params 
                        (measurement_id, param_name, param_value)
                        VALUES (?, ?, ?)
                    """, (measurement_id, name, str(value)))

            self.conn.commit()
            return self

        except Exception as e:
            print("Error saving settings: {0}".format(str(e)))
            self.conn.rollback()
            return

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

    def import_settings(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:  # 添加 encoding
                settings = json.load(f)

            # 在調用 save_settings 前先打印看看內容
            print("Importing settings:", settings)

            # 驗證必要欄位
            required_fields = ["sample_name", "position_name", "group_name"]
            if not all(field in settings for field in required_fields):
                print("Missing required fields")
                return False

            # 準備參數
            params = {}
            params["operator"] = settings.get("operator", "")
            params["measurement_fields"] = settings.get("measurement_fields", [])

            # 其他參數
            for k, v in settings.items():
                if k not in required_fields + ["operator", "measurement_fields"]:
                    params[k] = v

            # 調用 save_settings
            return self.save_settings(
                settings["sample_name"],
                settings["position_name"],
                settings["group_name"],
                params
            )

        except Exception as e:
            print("Error importing settings: {0}".format(str(e)))
            return False

    def close(self):
        """關閉數據庫連接"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print("Error closing database: {0}".format(str(e)))
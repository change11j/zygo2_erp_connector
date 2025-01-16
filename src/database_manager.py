# database_manager.py
from __future__ import print_function
import sqlite3
import json
from datetime import datetime
import os


class DatabaseManager(object):
    def __init__(self, db_path="mx_measurement.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化數據庫表"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # 設置表
            c.execute('''CREATE TABLE IF NOT EXISTS settings
                        (key TEXT PRIMARY KEY, value TEXT)''')
            # 測量數據表
            c.execute('''CREATE TABLE IF NOT EXISTS measurements
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         sample_name TEXT,
                         parameter_name TEXT,
                         position_name TEXT,
                         measurement_data TEXT,
                         erp_upload_status INTEGER DEFAULT 0,
                         timestamp TEXT,
                         datx_path TEXT,
                         report_path TEXT)''')
            conn.commit()

    def save_settings(self, sample_name, parameter_name, position_name):
        """保存設置"""
        settings = {
            "sample_name": sample_name,
            "parameter_name": parameter_name,
            "position_name": position_name,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                      ("current_settings", json.dumps(settings)))
            conn.commit()

    def get_settings(self):
        """獲取當前設置"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key=?", ("current_settings",))
            row = c.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def save_measurement(self, sample_name, parameter_name, position_name,
                         measurement_data, datx_path=None, report_path=None):
        """保存測量數據"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO measurements 
                (sample_name, parameter_name, position_name, measurement_data, 
                 timestamp, datx_path, report_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sample_name,
                parameter_name,
                position_name,
                json.dumps(measurement_data),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datx_path,
                report_path
            ))
            conn.commit()
            return c.lastrowid

    def update_erp_upload_status(self, measurement_id, status):
        """更新ERP上傳狀態"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE measurements 
                SET erp_upload_status = ?
                WHERE id = ?
            """, (status, measurement_id))
            conn.commit()

    def get_unuploaded_measurements(self):
        """獲取未上傳到ERP的測量數據"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM measurements 
                WHERE erp_upload_status = 0 
                ORDER BY timestamp ASC
            """)
            return c.fetchall()

    def get_measurements(self, limit=100, sample_name=None,
                         parameter_name=None, position_name=None):
        """獲取測量記錄"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            query = "SELECT * FROM measurements WHERE 1=1"
            params = []

            if sample_name:
                query += " AND sample_name = ?"
                params.append(sample_name)
            if parameter_name:
                query += " AND parameter_name = ?"
                params.append(parameter_name)
            if position_name:
                query += " AND position_name = ?"
                params.append(position_name)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            c.execute(query, params)
            return c.fetchall()
# erp_util.py
from __future__ import print_function
import json
import sys
if sys.version_info[0] >= 3:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
else:
    from urllib2 import Request, urlopen, HTTPError, URLError
from config import ERPConfig
from zygo import mx
import sqlite3
import logging

class ERPAPIUtil:
    @staticmethod
    def get_attribute_columns():
        try:
            conn = sqlite3.connect('measurements.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT param_name 
                FROM measurement_params
                ORDER BY param_name
            """)
            columns = [row[0] for row in cursor.fetchall()]
            conn.close()
            return columns
        except Exception as e:
            logging.error("Error getting attribute columns: %s", str(e))
            return []

    @staticmethod
    def send_to_erp(data):
        try:
            data_string = json.dumps(data, indent=2).encode('utf-8')
            logging.info("Sending request to ERP: %s", data_string.decode('utf-8'))

            req = Request(ERPConfig.API_URL)
            req.add_header('Content-Type', 'application/json')

            try:
                response = urlopen(req, data_string)
                response_body = response.read()
                if sys.version_info[0] >= 3:
                    response_body = response_body.decode('utf-8')
                logging.info("ERP Response: %s", response_body)

                # Check for error in XML response
                if 'IsError="true"' in response_body:
                    error_start = response_body.find("<_0:Error>") + 10
                    error_end = response_body.find("</_0:Error>")
                    if error_start > 9 and error_end > 0:
                        error_message = response_body[error_start:error_end]
                        return False, error_message

                # Check for success (presence of Record IDs without IsRolledBack="true")
                if 'RecordID=' in response_body and 'IsRolledBack="true"' not in response_body:
                    return True, None

                return False, "Unexpected response format"

            except HTTPError as e:
                error_body = e.read()
                if sys.version_info[0] >= 3:
                    error_body = error_body.decode('utf-8')
                logging.error("HTTP Error: %s - %s", e.code, error_body)
                return False, "HTTP {0}: {1}".format(e.code, error_body)
            except URLError as e:
                logging.error("URL Error: %s", str(e))
                return False, str(e)

        except Exception as e:
            logging.error("Error sending to ERP: %s", str(e))
            return False, str(e)

    @staticmethod
    def create_measure_request(sample_name, group_name, position_name, measurement_data):
        try:
            appx_filename = mx.get_application_path() or "Unknown.appx"
        except:
            appx_filename = "Unknown.appx"

        request_data = {
            "CompositeRequest": {
                "ADLoginRequest": ERPConfig.LOGIN_INFO,
                "serviceType": "setMeasureDataSet",
                "operations": {
                    "operation": []
                }
            }
        }

        # Add single measure record
        measure_operation = {
            "TargetPort": "createData",
            "ModelCRUD": {
                "serviceType": "setMeasure",
                "TableName": "Measure",
                "RecordID": 0,
                "Action": "Create",
                "DataRow": {
                    "field": [
                        {"@column": "APPXFileName", "val": appx_filename},
                        {"@column": "GroupName", "val": group_name},
                        {"@column": "SampleName", "val": sample_name},
                        {"@column": "PositionName", "val": position_name},
                        {"@column": "operator", "val": measurement_data.get("operator", "Unknown")}
                    ]
                }
            }
        }
        request_data["CompositeRequest"]["operations"]["operation"].append(measure_operation)

        # Get measurement fields and attributes
        for key, value in measurement_data.items():
            if key not in ['timestamp', 'operator'] and isinstance(value, (int, float)):
                # Add measurement data
                data_operation = {
                    "TargetPort": "createData",
                    "ModelCRUD": {
                        "serviceType": "setMeasureData",
                        "TableName": "MeasuredData",
                        "RecordID": 0,
                        "Action": "Create",
                        "DataRow": {
                            "field": [
                                {"@column": "DataName", "val": measurement_data['field_name']},
                                {"@column": "DataValue", "val": "{:.6f}".format(measurement_data['value'])},
                                {"@column": "Measure_ID", "val": "@Measure.Measure_id"},
                                {"@column": "Name", "val": measurement_data['field_name']}
                            ]
                        }
                    }
                }
                request_data["CompositeRequest"]["operations"]["operation"].append(data_operation)

        # Add MeasureAttribute operations
        columns = [col for col in ERPAPIUtil.get_attribute_columns() if col != 'operator']
        for column in columns:
            if column in measurement_data and measurement_data[column] is not None:
                attr_operation = {
                    "TargetPort": "createData",
                    "ModelCRUD": {
                        "serviceType": "setMeasureAttribute",
                        "TableName": "MeasureAttribute",
                        "RecordID": 0,
                        "Action": "Create",
                        "DataRow": {
                            "field": [
                                {"@column": "AttributeName", "val": column},
                                {"@column": "AttributeValue", "val": str(measurement_data[column])},
                                {"@column": "MeasuredData_ID", "val": "@MeasuredData.MeasuredData_ID"}
                            ]
                        }
                    }
                }
                request_data["CompositeRequest"]["operations"]["operation"].append(attr_operation)

        return request_data

    @staticmethod
    def upload_measurement(sample_name, group_name, position_name, measurement_data):
        try:
            request_data = ERPAPIUtil.create_measure_request(  # 改為直接調用
                sample_name,
                group_name,
                position_name,
                measurement_data
            )
            return ERPAPIUtil.send_to_erp(request_data)
        except Exception as e:
            return False, str(e)
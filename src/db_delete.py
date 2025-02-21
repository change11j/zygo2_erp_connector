import sqlite3


def delete_data():
    conn = sqlite3.connect("measurements.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS ps_repeat_patterns")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    delete_data()
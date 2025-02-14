import sys
import os
from datetime import datetime

# 設置日誌文件
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 使用較舊的字符串格式化語法
log_file = os.path.join(log_dir, "monitor_{0}.log".format(
    datetime.now().strftime("%Y%m%d_%H%M%S")))

# 創建日誌文件並重定向stdout和stderr
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_file)
sys.stderr = Logger(log_file)

# 導入並運行監控程式
from monitor_and_upload import main
if __name__ == "__main__":
    try:
        print("\n{0}".format("="*50))
        print("Starting monitor at {0}".format(datetime.now()))
        print("Log file: {0}".format(log_file))
        print("{0}\n".format("="*50))
        main()
    except KeyboardInterrupt:
        print("\nMonitor stopped by user")
    except Exception as e:
        print("\nError occurred: {0}".format(str(e)))
    finally:
        print("\nMonitor stopped at {0}".format(datetime.now()))
        print("{0}\n".format("="*50))
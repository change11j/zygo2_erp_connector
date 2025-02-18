import requests


def check_network():
    """检查网络连接状态"""
    try:
        # 尝试连接到ERP服务器
        response = requests.get("https://erp.topgiga.com.tw/", timeout=5)
        return True
    except:
        return False
if __name__ == '__main__':
    print(check_network())
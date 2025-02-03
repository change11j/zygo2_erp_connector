FROM --platform=linux/arm64/v8 python:3.4.3-slim

WORKDIR /app

# 如果有依賴文件就複製
COPY requirements.txt .
RUN pip install -r requirements.txt

# 保持容器運行
CMD ["tail", "-f", "/dev/null"]
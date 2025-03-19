#FROM python:3.9-slim
#
#WORKDIR /app
#
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
#EXPOSE 5000
#ENV FLASK_RUN_HOST=0.0.0.0
#
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建 instance 目录并设置权限
RUN mkdir -p /app/instance && chown -R root:root /app/instance
RUN mkdir -p /app/website/uploads && chmod -R 777 /app/website/uploads && chown -R root:root /app/website/uploads

# 声明卷，用于存储数据库文件
# VOLUME /app/instance
# VOLUME /app/website/uploads

EXPOSE 5000
ENV FLASK_RUN_HOST=0.0.0.0

# 使用非root用户运行应用
USER root

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
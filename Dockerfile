# 使用官方的 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 将 requirements.txt 文件复制到容器中
COPY ../requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY biz /app/biz
COPY core /app/core
COPY api.py /app/api.py

# 创建日志目录
RUN mkdir -p /app/log

# 暴露 Flask 默认端口
EXPOSE 5001

# 设置环境变量（可选）
ENV FLASK_ENV=production

# 启动命令
CMD ["python", "api.py"]

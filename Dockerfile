# FROM ubuntu:latest

# RUN apt-get update -y
# RUN apt install -y python3-pip python3-dev build-essential
# COPY . /app
# WORKDIR /app 
# RUN pip3 install --break-system-packages -r requirements.txt
# ENTRYPOINT ["python3"]
# CMD ["app.py"]

# =========================================================================

# # Используем официальный базовый образ Python
# FROM python:3.11-slim

# # Устанавливаем переменные окружения
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Создаем рабочую директорию внутри контейнера
# WORKDIR /app

# # Копируем только нужные файлы и папки
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Копируем остальные необходимые файлы
# COPY app.py .
# COPY aiPredict.py .
# COPY generalUtils.py .
# COPY models ./models
# COPY templates ./templates
# COPY test ./test

# # Открываем нужный порт (предположим, что используется 8000)
# EXPOSE 8000

# # Команда по умолчанию для запуска сервера
# CMD ["python", "app.py"]

# ==================================================================

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY templates/ ./templates

# Копируем тесты (если нужно запускать pytest)
COPY tests/ ./tests

EXPOSE 8000
CMD ["python", "app/app.py"]
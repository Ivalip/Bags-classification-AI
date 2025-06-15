# FROM ubuntu:latest

# RUN apt-get update -y
# RUN apt install -y python3-pip python3-dev build-essential
# COPY . /app
# WORKDIR /app 
# RUN pip3 install --break-system-packages -r requirements.txt
# ENTRYPOINT ["python3"]
# CMD ["app.py"]

# =========================================================================

# # Устанавливаем переменные окружения
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1





# ==================================================================

# Базовый образ
FROM python:3.11-slim

# # Установка системных зависимостей
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Устанавливаем системные библиотеки, включая libGL
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем зависимости

# Копируем исходный код приложения и тесты
COPY . .
# COPY app/ ./app/
# COPY tests/ ./tests/

# Переменная окружения для Flask
# ENV FLASK_APP=app
# ENV FLASK_ENV=production

# # Команда по умолчанию — запуск тестов
# CMD ["pytest", "tests"]

# Открываем нужный порт (предположим, что используется 8000)
EXPOSE 5000

# Команда по умолчанию для запуска сервера
CMD ["python", "app/app.py"]
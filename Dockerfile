FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание директории для данных
RUN mkdir -p /app/data

# Запуск бота
CMD ["python", "-m", "app.main"]

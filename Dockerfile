FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

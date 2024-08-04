# Використовуємо офіційний Python-образ як базовий
FROM python:3.9-slim

# Встановлюємо робочу директорію в контейнері
WORKDIR /app

# Копіюємо requirements.txt в робочу директорію контейнера
COPY . /app

# Встановлюємо необхідні пакети, зазначені в requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Відкриваємо порт 80 для зовнішнього доступу до контейнера
EXPOSE 5000

# Виконуємо app.py при запуску контейнера
CMD ["python", "app.py"]




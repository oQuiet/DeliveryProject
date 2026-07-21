# Базовый образ с нужной версией Python 
FROM python:3.12-slim  # Рабочая директория внутри контейнера 
WORKDIR /app  # Копируем файлы зависимостей 
COPY pyproject.toml poetry.lock ./  # Устанавливаем Poetry и зависимости проекта 
RUN pip install poetry && poetry install --no-root  # Копируем всё остальное 
COPY . .  # Команда, которая запускает приложение 
CMD ["poetry", "run", "python", "app.py"]`
FROM python:3.12

# Обновление пакетов
RUN apt-get update

# Установка рабочей директории
WORKDIR /code

# Настройки среды
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Установка Poetry
RUN pip install poetry

# Копирование зависимостей и конфигов
COPY pyproject.toml poetry.lock .env pytest.ini ./

# Установка зависимостей без dev-зависимостей
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Копирование тестов и скрипта запуска
COPY tests tests
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# Точка входа
ENTRYPOINT ["/code/entrypoint.sh"]

FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y gcc libssl-dev

# Устанавливаем последнюю версию redis-py
RUN pip install --no-cache-dir redis==5.0.0

# Копируем и устанавливаем остальные зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade pip
RUN pip install redis==5.0.0 --force-reinstall

COPY ./app /app

CMD ["python", "bot.py"]
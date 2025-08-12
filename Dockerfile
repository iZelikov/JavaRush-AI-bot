FROM python:3.13-slim

WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    ffmpeg \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

# Копируем и устанавливаем остальные зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install redis==6.2.0 --force-reinstall

COPY ./app /app

CMD ["python", "bot.py"]
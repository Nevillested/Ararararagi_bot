FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все .py файлы
COPY *.py ./

# Копируем assets, кроме music
RUN mkdir -p assets
COPY assets/maids assets/maids
COPY assets/stickers assets/stickers
COPY assets/temp assets/temp

# Точка входа
CMD ["python", "-u", "PyBot.py"]

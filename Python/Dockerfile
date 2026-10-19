FROM python:3.11-slim

WORKDIR /app

# ──────────────
# Python deps
# ──────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ──────────────
# Bot source
# ──────────────
COPY *.py ./

# ──────────────
# ffmpeg (static, локальный)
# ──────────────
COPY ffmpeg/ ffmpeg/
RUN chmod +x ffmpeg/ffmpeg ffmpeg/ffprobe

# ──────────────
# ENV для ffmpeg
# ──────────────
ENV FFMPEG_PATH=/app/ffmpeg/ffmpeg

# ──────────────
# Start bot
# ──────────────
CMD ["python", "-u", "PyBot.py"]


# Python 3.10 use karenge (Most Stable for Music Bots)
FROM python:3.10-slim

# Working directory
WORKDIR /app

# FFmpeg aur Git install (Zaroori hai)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    apt-get clean

# Files copy karo
COPY . .

# Requirements install karo
RUN pip install --no-cache-dir -r requirements.txt

# Bot start command
CMD ["python", "main.py"]


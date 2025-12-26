FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# ─── Install Dependencies (Node.js + FFmpeg + LibOpus) ───
# Note: libopus0 aur libopus-dev bahut jaruri hain audio ke liye
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    ffmpeg \
    git \
    libopus0 \
    libopus-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && node -v \
    && npm -v \
    && ffmpeg -version \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ─── Python Deps ───
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ─── App Code ───
COPY . .

# Container start command
CMD ["python", "main.py"]


# Pre-built Image (Python 3.10 + Node.js 19)
FROM nikolaik/python-nodejs:python3.10-nodejs19-bullseye

# FFmpeg install karna zaroori hai music play karne ke liye
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Code copy setup
COPY . /app/
WORKDIR /app/

# Requirements install
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

# --- START COMMAND ---
# Humara main file 'main.py' hai, isliye ye command use karenge
CMD ["python", "main.py"]


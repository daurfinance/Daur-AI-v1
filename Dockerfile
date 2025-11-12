FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    xvfb \
    scrot \
    tesseract-ocr \
    tesseract-ocr-eng \
    libx11-dev \
    libxtst-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps

COPY . .

RUN mkdir -p /app/data /app/logs

RUN useradd -m -u 1000 daur && chown -R daur:daur /app
USER daur

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD Xvfb :99 -screen 0 1920x1080x24 & python3 -m src.main

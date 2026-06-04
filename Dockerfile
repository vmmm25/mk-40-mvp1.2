# Dockerfile
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Development stage ---
FROM base AS dev
COPY . .
CMD ["python", "main.py"]

# --- Production stage ---
FROM base AS prod
COPY . .
RUN useradd -m jarvis
USER jarvis
CMD ["python", "main.py"]

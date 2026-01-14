# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ============================================
# Stage 2: Backend Runtime
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install system packages needed by Python libs
RUN apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy optional data directories
COPY chroma_db/ ./chroma_db/
COPY dravis_data/ ./dravis_data/

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Flask environment
ENV FLASK_APP=backend/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the Flask server
CMD ["flask", "run"]

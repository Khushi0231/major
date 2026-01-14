# Multi-stage Dockerfile for DRAVIS Project
# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Backend & Runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    python3-opencv \
    libsndfile1 \
    ffmpeg \
    portaudio19-dev \
    tesseract-ocr \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy static files
COPY chroma_db/ ./chroma_db/ 2>/dev/null || true
COPY dravis_data/ ./dravis_data/ 2>/dev/null || true

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the backend server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

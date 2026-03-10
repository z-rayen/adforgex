# ── Stage 1: Build React Frontend ────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files first (better layer caching)
COPY frontend-react/package*.json ./
RUN npm ci --silent

# Copy source and build
COPY frontend-react/ ./
RUN npm run build
# Output is in /frontend/dist/


# ── Stage 2: Build Python Dependencies ───────────────────────────────────────
FROM python:3.11-slim AS backend-builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    # Force CPU-only PyTorch FIRST — prevents downloading 2GB+ of NVIDIA CUDA drivers
    # sentence-transformers pulls torch, which defaults to CUDA version without this
    pip install --prefix=/install --no-cache-dir \
        torch==2.3.1+cpu \
        torchvision==0.18.1+cpu \
        --index-url https://download.pytorch.org/whl/cpu && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 3: Final Production Image ──────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /install /usr/local

# Copy backend source code
COPY backend/  ./backend/
COPY llm/      ./llm/
COPY rag/      ./rag/
COPY scraper/  ./scraper/

# Copy built React app from frontend builder
# FastAPI will serve this as static files
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Persistent data directories
RUN mkdir -p /data/chroma_db /data/sqlite

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHROMA_DB_PATH=/data/chroma_db \
    SQLITE_DB_PATH=/data/sqlite/adforge.db \
    STATIC_FILES_PATH=./frontend/dist \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "python rag/seed_data.py && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1"]
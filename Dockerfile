# Development Dockerfile - CRM-Oxii-Chatbot
# Optimized for development with hot reloading and debugging capabilities

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements file first for Docker layer caching
COPY pyproject.toml .

# Copy service account credentials
COPY service-account.json /app/service-account.json

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Install Python dependencies (removed requirements-dev.txt as we use poetry)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p saved_prompt memories logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBUG_MODE=true
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command with auto-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug", "--workers", "8"]

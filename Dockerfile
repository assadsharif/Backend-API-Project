# Personal AI Employee - Production Dockerfile
# Platinum Tier - Cloud Deployment

FROM python:3.13-slim

# Set metadata
LABEL maintainer="Asad Sharif"
LABEL description="Personal AI Employee - Gold Tier Complete"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /vault

# Create non-root user for security
RUN useradd -m -u 1000 fte && \
    chown -R fte:fte /app /vault

# Switch to non-root user
USER fte

# Expose web dashboard port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000 || exit 1

# Default command (can be overridden)
CMD ["python3", "/tmp/fte_dashboard.py"]

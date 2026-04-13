# Use Python 3.10.13 slim image
FROM python:3.10.13-slim

# Build timestamp - change this to force rebuild
# Build: 2026-04-13T07:25:00Z

# Set working directory
WORKDIR /app

# Install minimal system dependencies required for ML libraries
# CRITICAL: libgl1-mesa-glx is REQUIRED for OpenCV (cv2) to work
# These libraries are needed for emotion detection and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for audio and models
RUN mkdir -p audio models/rasa_classification

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "main:app"]

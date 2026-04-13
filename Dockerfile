# Use Python 3.10.13 slim image
FROM python:3.10.13-slim

# Set working directory
WORKDIR /app

# Configure headless runtime for OpenCV on Render
ENV DISPLAY=
ENV LIBGL_ALWAYS_INDIRECT=1
ENV QT_QPA_PLATFORM=offscreen

# Install minimal system dependencies required for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from Backend directory
COPY Backend/requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy only runtime backend files (exclude tests/docs/scripts)
COPY Backend/app ./app
COPY Backend/main.py ./main.py
COPY Backend/models ./models
COPY Backend/data ./data

# Create directories for audio and models
RUN mkdir -p audio models/rasa_classification

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with gunicorn, using PORT environment variable (default 8000)
CMD ["sh", "-c", "gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120 main:app"]

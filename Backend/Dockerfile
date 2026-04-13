# Use Python 3.10.13 slim image
FROM python:3.10.13-slim

# Build timestamp - force rebuild
# Build: 2026-04-13T07:35:00Z - CRITICAL: Headless OpenCV fix

# Set working directory
WORKDIR /app

# Configure OpenCV for headless environment (no display server)
# This prevents "libGL.so.1: cannot open shared object file" errors
ENV DISPLAY=
ENV LIBGL_ALWAYS_INDIRECT=1
ENV QT_QPA_PLATFORM=offscreen

# Install minimal system dependencies required for ML libraries
# CRITICAL LIBS:
# - libgl1-mesa-glx: OpenGL Mesa (for headless OpenCV)
# - libxext6, libxrender-dev: X11 libraries
# - libsm6: For Tk support
# - libgomp1: OpenMP threading
# - libglib2.0-0: GLib runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxext6 \
    libnvidia-compute-470 \
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

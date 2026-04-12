#!/bin/bash
set -e

echo "==> Setting up Python 3.10 environment..."

# Use pyenv or apt to install Python 3.10 if not available
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 not found, installing..."
    apt-get update
    apt-get install -y python3.10 python3.10-venv python3.10-dev
fi

# Create virtual environment with Python 3.10
echo "==> Creating Python 3.10 virtual environment..."
python3.10 -m venv /opt/venv
source /opt/venv/bin/activate

# Upgrade pip
echo "==> Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "==> Installing dependencies from Backend/requirements.txt..."
cd Backend
pip install -r requirements.txt
cd ..

echo "==> Build complete!"

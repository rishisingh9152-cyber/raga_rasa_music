#!/bin/bash

# RagaRasa Music Therapy - Render Build Script
# This script runs during the build phase on Render

set -e

echo "================================"
echo "RagaRasa Backend Build Starting"
echo "================================"

# Install dependencies from Backend directory
echo "Installing Python dependencies..."
cd Backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "================================"
echo "Build completed successfully!"
echo "================================"

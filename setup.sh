#!/bin/bash

# CryptoGuardLite Development Setup Script

echo "Setting up CryptoGuardLite development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/raw data/processed data/models logs

# Set environment variables
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

echo ""
echo "Setup complete!"
echo ""
echo "To activate the environment, run: source venv/bin/activate"
echo "To start the API server, run: python main.py api"
echo "To train a model, run: python scripts/train.py --model hybrid"
echo ""

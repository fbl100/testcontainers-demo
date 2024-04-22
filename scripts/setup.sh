#!/bin/bash

# If .venv exists, delete it
if [ -d ".venv" ]; then
    echo "Removing existing .venv directory..."
    rm -rf .venv
fi

# Verify Python 3.9 is installed
if ! command -v python &> /dev/null; then
    echo "Python 3.9 is not installed. Please install it and try again."
    exit 1
fi

echo "Python 3.9 is installed."

# Create a virtual environment using Python 3.9
python -m venv .venv
echo "Virtual environment created."

# Activate the virtual environment
source .venv/bin/activate
echo "Virtual environment activated."

# Run pip install -e .[testing]
pip install -e .[testing]
echo "Dependencies installed."
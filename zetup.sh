#!/bin/bash

# This script sets up a Python virtual environment and installs the required packages.
#

python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

pre-commit install

echo "Setup complete. Virtual environment activated."
echo "To activate the virtual environment later, run: source .venv/bin/activate"

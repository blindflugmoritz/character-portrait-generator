#!/bin/bash
# PythonAnywhere Setup Script
# Run this in a PythonAnywhere Bash console

set -e  # Exit on error

PROJECT_DIR="/home/blindflugstudios/crew-generator-backend"

echo "=========================================="
echo "PythonAnywhere Setup Script"
echo "=========================================="
echo ""

cd $PROJECT_DIR

echo "Step 1: Creating virtual environment..."
python3.10 -m venv venv
echo "✓ Virtual environment created"
echo ""

echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "✓ Activated"
echo ""

echo "Step 3: Upgrading pip..."
pip install --upgrade pip
echo "✓ Pip upgraded"
echo ""

echo "Step 4: Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "Step 5: Running Django migrations..."
python manage.py migrate
echo "✓ Migrations complete"
echo ""

echo "Step 6: Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next step: Create and configure web app"
echo "Go to: https://www.pythonanywhere.com/web_app_setup/"
echo ""

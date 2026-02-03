#!/bin/bash
# Migration script for Cloud SQL setup

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating .env file (copy from .env.example and update values)..."
cp .env.example .env

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py createsuperuser

echo "Setup complete!"

#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Trying to seed data:
python manage.py seed_data

# Create superuser non-interactively (requires environment variables)
python manage.py createsuperuser --no-input || true

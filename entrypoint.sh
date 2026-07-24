#!/usr/bin/env bash
set -e

# Run migrations, collect static files, then start Gunicorn
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

#!/bin/sh
set -e

cd /app/fantasy_scout

# Apply database migrations
python manage.py migrate --noinput

# Collect static files if STATIC_ROOT is set (safe to run always)
python manage.py collectstatic --noinput || true

# Start Gunicorn server
exec gunicorn fantasy_scout.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-3} \
  --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-120}



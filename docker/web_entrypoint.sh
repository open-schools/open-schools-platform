#!/bin/sh

# Collect static files
echo "Collect static files"

python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
until python manage.py migrate
do
  echo "Waiting for db to be ready..."
  sleep 2
done

# --> Duplicate logs to stdout for portainer console
if [ "$1" == "dev" ]; then
  tail -f /app/logs/gunicorn/dev.log > /dev/stdout &
fi

if [ "$1" == "prod" ]; then
  tail -f /app/logs/gunicorn/access.log > /dev/stdout &
  tail -f /app/logs/gunicorn/error.log > /dev/stderr &
fi

# --> Starting production gunicorn web server
echo "--> Starting production gunicorn web server"
gunicorn -c deploy/gunicorn/config/$1
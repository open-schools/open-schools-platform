#!/bin/sh

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Generate localization files
echo "Generate localization files"
python manage.py compilemessages

# Apply database migrations
echo "Apply database migrations"
until python manage.py migrate
do
  echo "Waiting for db to be ready..."
  sleep 2
done

# --> Duplicate logs to stdout for portainer console
if [[ "$1" == "dev.py" ]]; then
  echo "--> Starting dev logs"
  tail -f /app/logs/gunicorn/dev.log > /dev/stdout &
fi

if [[ "$1" == "production.py" ]]; then
  echo "--> Starting prod logs"
  tail -f /app/logs/gunicorn/access.log > /dev/stdout &
  tail -f /app/logs/gunicorn/error.log > /dev/stderr &
fi

# --> Starting gunicorn web server
echo "--> Starting production gunicorn web server"
gunicorn -c deploy/gunicorn/config/$1
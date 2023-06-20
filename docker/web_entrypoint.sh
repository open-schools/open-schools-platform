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

# --> Starting production gunicorn web server
echo "--> Starting production gunicorn web server"
gunicorn -c deploy/gunicorn/config/$1
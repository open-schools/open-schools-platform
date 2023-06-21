"""Gunicorn *production* config file"""

import multiprocessing

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "config.wsgi:application"
# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1
# The socket to bind
bind = "0.0.0.0:8010"
# Write access and error info to /var/log
accesslog = "/app/logs/gunicorn/access.log"
errorlog = "/app/logs/gunicorn/error.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = "/app/logs/gunicorn/prod.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = False

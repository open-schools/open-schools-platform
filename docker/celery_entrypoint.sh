echo "--> Starting celery process"
celery -A open_schools_platform.tasks beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
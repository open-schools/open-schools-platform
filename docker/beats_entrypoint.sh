echo "--> Starting beats process"
celery -A open_schools_platform.tasks worker -l info --without-gossip --without-mingle --without-heartbeat
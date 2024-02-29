list="django celery flower rabbitmq beats"
for service in $list; do
    docker service update --force "$1_$service"
done

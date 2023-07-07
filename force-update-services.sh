docker stack services -q $1 \
  | while read service; do
    docker service update --force $service
  done
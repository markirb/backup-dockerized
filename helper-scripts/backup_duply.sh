#!/bin/bash

if [ -z "$2" ]
then
  echo "No argument supplied, usage $0 [backup-id] [duply-command]"
  exit 1
fi

docker-compose exec backup-scheduler /docker_backup.py "$@"

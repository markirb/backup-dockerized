#!/bin/bash

IMG_NAME="backup_duply"
BACKUP_DIR="/mnt/backup"

if [ -z "$1" ]; then
  echo "Please give backup-id as first argument"
  exit 1
fi

read -r -p "Please enter a new volume name you want to restore to: " RESTORE_VOL_NAME

docker volume inspect $RESTORE_VOL_NAME >/dev/null 2>&1
if [[ $? == 0 ]]; then
  echo "ERROR: Volume with name ${RESTORE_VOL_NAME} already exists, exiting"
  exit 1
else
  docker volume create $RESTORE_VOL_NAME >/dev/null 2<&1
  if [[ $? != 0 ]]; then
    echo "Error creating volume ${RESTORE_VOL_NAME}"
    exit 1;
  fi
  echo "Created docker volume with name ${RESTORE_VOL_NAME}"
fi


echo "Starting and attaching to container"
echo "Mounting volume '${RESTORE_VOL_NAME}' to /restore as rw"
echo "You can restore the backup by typing 'duply backup restore /restore [AGE]' or look around what 'duply backup' does"
docker run -it --rm \
	-v $RESTORE_VOL_NAME:/restore \
	-v ${BACKUP_DIR}/${1}:/backup:ro \
       	$IMG_NAME bash

echo "Whatever you restored to /restore is now available under the docker volume '${RESTORE_VOL_NAME}', you can now use it to replace the old volume in your docker-compose.yml"

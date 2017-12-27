# Backup Dockerized

## --> WORK IN PROGRESS! <--
I use this on my server. So it might or might not work for you, or fit you use case.
But I aim to make this more flexible, feedback much appreciated

## What is it
This project provides a dockerized backup service for volumes, mysql/mariadb dumps and plain folders. I assembled it to backup the awesome [mailcow-dockerized](https://www.github.com/mailcow/mailcow-dockerized) and other directories.

Backups are scheduled daily via a running cron container (scheduler). Currently full backup is performed once a month, and daily incremental (max of 2 months history is kept). An additional monitoring container will check the backups once a day and notify you via email if your backups get too old or are not functional.

As for now i use it to backup to a mounted NAS and thus don't need encryption.
However the underlying duply/duplicity setup provides many [backends](https://github.com/blacklabelops/volumerize/tree/master/backends) (AWS, Dropbox, ....) and encryption, which provides opportunity for further work.

## Installation
1. build the images with
```
docker-compose build
```
2. create and adjust your backup settings in conf/data/backup/conf.yml (or just rename the mailcow.yml to conf.yml for a mailcow backup) 
3. create and adjust backup.conf (copy your mailcow settings into backup.sample.conf)
4. start everything with
```
docker-compose up -d
```
5. wait for backup to run (check the docker-compose logs, first checks should fail and you should get an email)

## How it works
After starting the services you should have two running containers:
 + backup-scheduler
 + backup-monitor

You will also get one stopped container (which will hang around for docker-compose limitations, if you really care, you can delete it)

Backups are done with one off containers using duply. All volumes and folders except the backup target folder are mounted read only for your own safety.

## Configuration
The backup can be configured in backup_conf.yml (symlink to conf/data/backup/conf.yml)
It is currently very simple and has two options

```yaml
backup_dir: [absolute(!) path of target]
backups:
  [backup_id]:
    src: [volume name or folder path (absoulte!)]
  [backup_id]:
    src: [mysql container name/id]
    mode: sqldump
```

## Helper scripts

Possibilities for restoration:
I put together a basic restoration script and access to the monitor container.
You can look up and use these

+ backup_restore_bash.sh
+ backup_duply.sh

For your own safety you will restore the contents to a newly created container, which you can then use.
You should not override ANY volumes for your own safety...
When youre done, you can replace the volume in your docker-compose and restart your services.

## TODO
 + More backends
 + Pause Containers using a volume during backup (makes almost no sense as the pause would be too long)
 + password and assymetric encryption (very important for online backups)

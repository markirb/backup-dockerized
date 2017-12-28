# Backup Dockerized

## --> WORK IN PROGRESS! <--
I use this on my server. So it might or might not work for you, or fit you use case.
I aim to make this more flexible and stable, your feedback is much appreciated

## What is it
This project provides a dockerized backup service for volumes, mysql/mariadb dumps and plain folders. I assembled it to backup the awesome [mailcow-dockerized](https://www.github.com/mailcow/mailcow-dockerized) and some other stuff.

Backups are scheduled daily via a running cron container (scheduler). Currently full backup is performed once a month, and daily incremental backups (max of 2 months history is kept). An additional monitoring container will check the backups once a day and notify you via email if your backups get too old or are not functional.

As for now i use it to backup to a mounted NAS and thus don't need encryption nor other backends, 
 the underlying duply/duplicity setup provides many [backends](http://duplicity.nongnu.org/index.html) (AWS, Dropbox, ....) and encryption, which provides opportunity for further work.

Right now i have tested Dropbox with working GPG encryption

## Installation
1. build the images with
```
docker-compose build
```
2. create and adjust your backup settings in conf/data/backup/conf.yml (or just rename the mailcow.sample.yml to conf.yml for a mailcow backup)
see also GPG section
3. create and adjust env.conf (copy your mailcow settings into env.sample.conf and rename it to env.conf)
4. start everything with
```
docker-compose up -d
```
5. wait for backup to run (check the docker-compose logs, first checks should fail and you should get an email)
6. if you (understandably) want to test the backup setup right away you can schedule single backup ids (see Configuration)
 with
```
helper-scripts/backup_duply.sh [backupid] [action e.g. status or backup]
```


## How it works
After starting the services you should have two running containers:
 + backup-scheduler
 + backup-monitor

You will also get one stopped container (which will hang around for docker-compose limitations, if you really care, you can delete it)

Backups are done with one off containers using duply. All volumes and folders except the backup target folder are mounted read only for your own safety.

## Configuration
The backup can be configured in local backup_conf.yml (symlink to conf/data/backup/conf.yml)
It is currently very simple and has two options

```yaml
env:
  TARGET: [absolute(!) path of target]
  [optional other env vars]
backups:
  [backup_id]:
    src: [volume name or folder path (absoulte!)]
    [env:]
      [optional custom  env vars]
  [backup_id]:
    src: [mysql container name/id]
    mode: sqldump
```

## Helper scripts

Possibilities for restoration:
I put together a basic restoration script and access to the monitor container.
You can look up and use these in helper-scripts:

+ backup_restore_bash.sh (only usable for offline backups right now, TODO: dynamic python version)

For your own safety you will restore the contents to a newly created container, which you can then use.
You cannot and should not override ANY volumes for your own safety...
When you're done, you can replace the volume in your docker-compose and restart your services.

+ backup_duply.sh

You can directly issue duply commands, e.g. with backupip status to see whether your config is working

## GPG Key

Generate a new GPG key with

```
docker-compose exec backup-scheduler ./gpg.sh gen-key
```

Note you password and Key ID for use in env
be sure to export your key and save it afterwards with

```
docker-compose exec backup-scheduler ./gpg.sh export-key
```

you can use these by setting the env approprately in the conf.yml

```
GPG_PW: '[PW]'
GPG_KEY: '[KEY_ID]'
```


## TODO
 + Test and integrate more backends
 + Pause containers using a volume during backup (makes almost no sense as the pause will most likely be too long)
 + Provide possibility to customize schedule
 + View current status without email

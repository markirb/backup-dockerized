# Backup Dockerized

## Notice
This is work in progress! I use this on my server. So it might or might not work for you, or fit your needs.
As I aim to make this more flexible and stable, your feedback is much appreciated.

**USE AT YOUR OWN RISK!**

Every directory or volume (except if you use a target backup directory) is mounted **read only**.

## Description
This project provides a dockerized backup service for volumes, mysql/mariadb dumps and plain folders. I assembled it to backup the awesome [mailcow-dockerized](https://www.github.com/mailcow/mailcow-dockerized) and some other stuff on my server.

Backups are scheduled daily via a running cron container. Backups are done via [duply](http://duply.net) (kind of a nicer frontend for duplicity).
An additional monitoring container will check the backups once a day and notify you via email if your backups get too old or are not functional.
Backups are done daily (incremental) and monthly (full), history is 2 moths right now (you could adjust this).

Duply/duplicity setup provides many [backends](http://duplicity.nongnu.org/index.html) (AWS, Dropbox, ....) and encryption.
As for now i use it to backup to a mounted NAS and thus don't need encryption.
I added the possibility to do these, up until now I only tested Dropbox with working GPG encryption, others should work if you set the right `[env]`

## Installation
1. build the images with
```
docker-compose build
```

2. create and adjust your backup settings in `./conf/data/backup/conf.yml` 

for mailcow example see [mailcow.sample.yml](../master/data/conf/backup/mailcow.sample.yml)

for a dropbox online backup example with GPG see [dropbox.sample.yml](../master/data/conf/backup/dropbox.sample.yml)
see also GPG section on how to create your key.

if you set a global target folder, every backup creates a subfolder within

3. create and adjust ./env.conf (best is to copy your mailcow settings into env.sample.conf and rename it to env.conf)
4. start everything with
```
docker-compose up -d
```
5. wait for backup and monitor to run (check the docker-compose logs, first checks should fail and you should get an email)
6. if you cannot wait until 1 a.m. and (understandably) want to test the backup setup right away you can test single [backup id]s (see Configuration)
 with
```
helper-scripts/backup_duply.sh [backup_id] [duply action e.g. status or backup]
```


## How it works
After starting the services you should have two running containers:
 + backup-scheduler
 + backup-monitor

You will also get one stopped container (which will hang around for docker-compose limitations, if you really care, you can delete it)

The GPG folder is stored on a crypt volume.

Backups are done with one-off (ephemeral) docker containers running duply. All volumes and folders except the backup target folder are mounted **read only** for your own safety.

## Configuration
The backup can be configured in `conf/data/backup/conf.yml` (there is a also a convenience symlink `./backup_conf.yml`)

Examples:
[mailcow.sample.yml](../master/data/conf/backup/mailcow.sample.yml)
[dropbox.sample.yml](../master/data/conf/backup/dropbox.sample.yml)

It looks like

```yaml
#global env, is valid for all backup_ids 
env:
  TARGET: [target (absolute) path or URI]
  [optional other env vars (for GPG and CREDENDIALS)]
backups:
  [backup_id]:
    src: [volume name or folder path (absoulte!)]
    [env:]
      [optional custom  env vars, overrive global]
  [backup_id]:
    src: [mysql container name/id]
    mode: sqldump
    [env:]
      [optional custom  env vars, overrive global]
```

## Helper scripts

Possibilities for restoration:
I put together a basic restoration script (not yet complete) and access to the monitor container.
You can look up and use these in helper-scripts:

+ backup_duply.sh

You can directly issue duply commands, e.g. with arg `[backup_id] status` to see whether your config is working

+ backup_restore_bash.sh (only usable for offline backups right now, TODO: dynamic python version)

For your own safety you will restore the contents to a newly created container, which you can then use.
You cannot and should not override ANY volumes for your own safety...
When you're done, you can replace the volume in your docker-compose and restart your services.

## GPG Key

Generate a new GPG key with

```
docker-compose exec backup-scheduler ./gpg.sh gen-key
```

**Copy your random password and Key-ID for later use in env**

**You should also export your key and password and back it up somewhere safe with**

```
docker-compose exec backup-scheduler ./gpg.sh export-key
```

Your conf.yml should look like:

```
GPG_PW: '[KEY_PW]'
GPG_KEY: '[KEY_ID]'
```


## TODOs
 + Enhance restoration script (from online backend, restore to fresh sql database, to folder, ...)
 + More consistency
 + Smaller containers with entrypoints
 + Test and integrate more backends
 + Pause containers using a volume during backup (makes almost no sense as the pause will most likely be too long)
 + Provide possibility to customize schedule
 + View current status without email

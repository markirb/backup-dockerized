#!/usr/bin/env python 
import docker
import sys
import os
import yaml

from io import BytesIO
import tarfile

config_file = '/etc/backup/conf.yml'

if len(sys.argv) < 2:
  print "No arguments given"
  sys.exit(1)
name = sys.argv[1]

#parse config
with open(config_file, 'r') as stream:
  data = yaml.load(stream)

config = data['backup']
backup_dir = data['backup_dir']

#commands with one arg
if name == "list_all":
  print " ".join(config.keys())
  sys.exit(0)
elif name == "check_config":
  print "TODO: check pathes/volumes/containers exist"
  sys.exit(0)

#commands with two args
action = "status"
if len(sys.argv) >= 3:
  action = sys.argv[2]

docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')

i_img = "backup_duply"

if name in config:
    i_config = config[name]
    i_hostname =  "backup_%s" % name
    i_backup_path =  os.path.join(backup_dir,name)
    i_source = i_config['src']

    #only needed for offline backups
    i_volumes = {
        i_backup_path: {'bind': '/backup/','mode': 'rw'},
    }
    #for online backups i think the best option is to pack a dynamically generated config file into the container, at the same time the key can be shared

    i_cmd = "duply backup %s" % (action)
    i_mode = i_config.get('mode','default')

    i_tar = False
    if i_mode == 'sqldump':
        if action != 'status':
            #do a sql dump
            try:
                i_dump = docker_client.containers.get(i_source)
            except:
                print "Container %s was not found" % i_source
                sys.exit(1)
            gen = i_dump.exec_run("sh -c 'exec mysqldump --all-databases -uroot -p\"$MYSQL_ROOT_PASSWORD\"'", stream=True)
            
            file_name = "%s.sql" % i_source 
            temp_name = "/tmp/%s" % file_name
            f = open(temp_name,'w')
            for x in gen:
                f.write(x)
            f.close()
            
            #pack temporary dump into an archive (in memory)
            i_tar = BytesIO()
            pw_tar = tarfile.TarFile(fileobj=i_tar, mode='w')
            pw_tar.add(temp_name,arcname="/source/%s" % file_name)
            pw_tar.close()
            i_tar.seek(0)
    else:
        #source image
        i_volumes[i_source] = {'bind': '/source/','mode': 'ro'}

    #now launch the container, remove in case of an error
    try:
        container =  docker_client.containers.create(i_img,hostname=i_hostname,command=i_cmd,volumes=i_volumes)
        if i_tar != False:
            container.put_archive("/", i_tar)
        container.start()
        logs_gen = container.logs(stream=True)
        for x in logs_gen:
            sys.stdout.write(x)
    except:
        print "Error launching backup container, cleaning up"
    container.remove()
else:
    print "Error: name '%s' not found in config file" % name

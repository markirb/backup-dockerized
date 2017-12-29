#!/usr/bin/env python 
import docker
import sys
import os
import yaml

import tarfile
from urlparse import urlparse
from io import BytesIO

config_file = '/etc/backup/conf.yml'

#hostname equals docker container id
self_id = os.environ.get("HOSTNAME")

if len(sys.argv) < 2:
    print("No arguments given, usage: list, check, [profile] [duplycmd]...")
    sys.exit(1)
name = sys.argv[1]

#parse config
with open(config_file, 'r') as stream:
    data = yaml.load(stream)

config = data['backup']

#commands with one arg
if name == "list":
    print(" ".join(config.keys()))
    sys.exit(0)
elif name == "check":
    print("TODO: check pathes/volumes/containers exist")
    sys.exit(0)

#commands with two args
action = "status"
if len(sys.argv) >= 3:
    action = sys.argv[2]

docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')

i_img = "backup_duply"

def get_crypt_volume( docker_client, docker_id):
    #get volume name of container, ugly hack...
    try:
        i_self = docker_client.containers.get(docker_id)
    except:
        print "Container %s was not found" % docker_id
        return None
    idx = i_self.name.find("backup-") #both containers start with backup-
    if idx != -1:
        return "%s%s" % (i_self.name[:idx], "crypt-vol-1")
    else:
        return None


i_env = data.get('env', {}) #default environment

if name in config:
    i_config = config[name]
    i_hostname =  "backup_%s" % name
    i_source = i_config['src']

    #when generalized target is used, we need to add the name to the source
    i_env['TARGET'] =  os.path.join(i_env.get('TARGET',''),name)

    s_env = i_config.get('env',{})
    i_env.update(s_env) #override with specialized env

    assert i_env['TARGET'] != name #neither general not scoped TARGET was set

    i_volumes = {}

    #mount crypt container if available
    i_crypt =  get_crypt_volume( docker_client, self_id)
    if i_crypt != None:
        docker_client.volumes.get(i_crypt) #check if volume exists
        i_volumes[str(i_crypt)] = {'bind': '/root/.gnupg','mode': 'ro'}

    #in case of a file target we need to mount it
    p = urlparse(i_env['TARGET'],'file')
    if p.scheme == 'file':
        #rewrite target and mount folder to this location
        i_env['TARGET'] = "file:///backup"
        assert p.netloc == '' #was no absolute path if this is true, volumes are discouraged!
        i_volumes[p.path] = {'bind': '/backup/','mode': 'rw'}

    #set defaults if not yet set
    i_env.setdefault('GPG_KEY','disabled')
    i_env.setdefault('GPG_PW','')
    i_env.setdefault('GPG_TTY','/dev/console')

    i_profile = 'backup'
    i_cmd = "duply %s %s" % (i_profile,action)
    i_mode = i_config.get('mode','default')

    i_tar = None
    if i_mode == 'sqldump':
        if action != 'status':
            #do a sql dump
            try:
                i_dump = docker_client.containers.get(i_source)
            except:
                print("Container %s was not found" % i_source)
                sys.exit(1)
            gen = i_dump.exec_run("sh -c 'exec mysqldump --all-databases -uroot -p\"$MYSQL_ROOT_PASSWORD\"'", stream=True)
            
            file_name = "%s.sql" % i_source 
            temp_name = "/tmp/%s" % file_name
            f = open(temp_name,'w')
            for x in gen:
                f.write(x)
            f.close()
            
            #pack temporary dump into an archive (packing is done in memory)
            i_tar = BytesIO()
            pw_tar = tarfile.TarFile(fileobj=i_tar, mode='w')
            pw_tar.add(temp_name,arcname="/source/%s" % file_name)
            pw_tar.close()
            i_tar.seek(0)
    else: #source is volume or directory
        src_is_vol = not i_source.startswith('/')
        if src_is_vol:
            docker_client.volumes.get(i_source) #check if volume exists
        #no way to check if dir exists...
        i_volumes[i_source] = {'bind': '/source/','mode': 'ro'}

    #now launch the container, remove afterwards or in case of an error
    try:
        container =  docker_client.containers.create(i_img, hostname=i_hostname, command=i_cmd, volumes=i_volumes, environment=i_env)
        if i_tar != None:
            container.put_archive("/", i_tar)
        container.start()
        logs_gen = container.logs(stream=True)
        for x in logs_gen:
            sys.stdout.write(x)
    except:
        print("Error launching backup container (directories might not exist), cleaning up")
    container.remove()
else:
    print("Error: name '%s' not found in config file" % name)

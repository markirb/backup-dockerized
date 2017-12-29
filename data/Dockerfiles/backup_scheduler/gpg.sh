#!/bin/bash

#The MIT License (MIT)
#Copyright (c) 2017 Jeroen Geusebroek

KEY_TYPE='RSA'
KEY_LENGTH='2048'
SUBKEY_TYPE='RSA'
SUBKEY_LENGTH='2048'
NAME_REAL='Duply backup'
NAME_EMAIL='duply@crypt'
PASSPHRASE='random' 

if [ ! -e /root/.gnupg/gpg.conf ]; then
  cp /gpg/gpg.conf /root/.gnupg
fi

if [ -d /root/.gnupg ]; then
  chmod 700 /root/.gnupg
fi

if [ -d /root/.duply ]; then
  chmod 700 /root/.duply
  find /root/.duply -type d -print0 | xargs -0 -I{} chmod 700 {}
  find /root/.duply -type f -print0 | xargs -0 -I{} chmod 600 {}
fi

case "$1" in
    'gen-key')
        if [ "random" = "$PASSPHRASE" ]; then
            PASSPHRASE=$(pwgen 16 1)
        fi
        cat >/tmp/key_params <<EOF
        %echo Generating a OpenPGP key
        Key-Type: $KEY_TYPE
        Key-Length: $KEY_LENGTH
        Subkey-Type: $SUBKEY_TYPE
        Subkey-Length: $SUBKEY_LENGTH
        Name-Real: $NAME_REAL
        Name-Email: $NAME_EMAIL
        Expire-Date: 0
        Passphrase: $PASSPHRASE
        %commit
        %echo Created key with passphrase '$PASSPHRASE'. Please store this for later use.
EOF
        gpg2 --batch --full-gen-key /tmp/key_params && rm /tmp/key_params
        gpg --keyid-format short --list-secret-keys
	gpg --check-trustdb
        exit
        ;;
    'export-key')
        gpg2 --export -a
        gpg2 --export-secret-key -a
        gpg --keyid-format short --list-secret-keys
        ;;
esac

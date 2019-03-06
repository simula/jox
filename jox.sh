#!/bin/bash

# mount the jox store
DIR_JOX_STORE="/tmp/jox_store"

sudo mkdir -p $DIR_JOX_STORE
sudo mount -o size=100m -t tmpfs none $DIR_JOX_STORE
sudo chown -R $USER /tmp/jox_store
sudo chown -R 777 /tmp/jox_store

python3 src/jox.py "$@"

#!/bin/bash

# mount the jox store
DIR_JOX_STORE="/tmp/jox_store"
sudo service rabbitmq-server start

if [ ! -f es_id ]; then
    touch es_id
fi
if [ ! -s es_id ]; then
    echo "elasticsearch is not running"
    check_es_running=false
else
     check_es_running=$(docker inspect --format="{{.State.Running}}" $(cat es_id))
fi


if [ ! "$check_es_running" = true ]; then
    echo $check_es_running
    echo "running elasticsearch"
    sudo rm es_id
    sudo docker run -itd --cidfile es_id -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:6.6.2
fi
sudo mkdir -p $DIR_JOX_STORE
sudo mount -o size=100m -t tmpfs none $DIR_JOX_STORE
sudo chown -R $USER /tmp/jox_store
sudo chown -R 777 /tmp/jox_store

python3 src/jox.py "$@"

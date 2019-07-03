#!/bin/bash

#sudo service rabbitmq-server start
#if [ ! -f es_id ]; then
#    touch es_id
#fi
#if [ ! -s es_id ]; then
#    echo "elasticsearch is not running"
#    check_es_running=false
#else
#     check_es_running=$(docker inspect --format="{{.State.Running}}" $(cat es_id))
#fi

#if [ ! "$check_es_running" = true ]; then
#    echo $check_es_running
#    echo "running elasticsearch"
#    sudo rm es_id
#    sudo docker run -itd --cidfile es_id -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:6.6.2
#fi

python3 src/core/ro/plugins/flexran.py  

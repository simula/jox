#!/usr/bin/env bash


sudo apt install python3-pip -y
sudo apt-get install python3-setuptools python3-dev libpq-dev build-essential -y
sudo apt install docker.io -y

sudo apt install curl -y

# elasticsearch
#sudo adduser $USER docker
#newgrp docker
sudo docker pull docker.elastic.co/elasticsearch/elasticsearch:6.6.2
sudo docker run -itd -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:6.6.2

# rabbitmq
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
sudo apt install rabbitmq-server -y
sudo service rabbitmq-server start

# juju

sudo apt install snapd -y
sudo apt install  zfsutils-linux -y
sudo snap install lxd || true
sudo snap install juju --classic || true

pip3 install termcolor --user
pip3 install jsonpickle --user
pip3 install elasticsearch --user
pip3 install jsonschema --user
pip3 install pika --user
pip3 install flask --user
pip3 install juju --user

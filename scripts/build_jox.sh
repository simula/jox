#!/bin/bash
# Copyright 2016-2019 Eurecom and Mosaic5G Platforms Authors
# Licensed to the Mosaic5G under one or more contributor license
# agreements. See the NOTICE file distributed with this
# work for additional information regarding copyright ownership.
# The Mosaic5G licenses this file to You under the
# Apache License, Version 2.0  (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    	http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# -------------------------------------------------------------------------------
#   For more information about the Mosaic5G:
#   	contact@mosaic-5g.io
#
#
################################################################################
# file
# brief
# author

# set -u

export DEBIAN_FRONTEND=noninteractive

SUDO='sudo -E'
os_pm="apt-get"
os_pm_remove="apt-add-repository"
os_pm_add="add-apt-repository"
option="-y"
specific_pkgs="zfsutils-linux"

jox_store=/mnt/jox_store


install_required_packages(){
    export LC_ALL="en_US.UTF-8"
    export LC_CTYPE="en_US.UTF-8"

    $SUDO $os_pm  update -y
    $SUDO $os_pm dist-upgrade -y
    # ubunut 16 and 14
    $SUDO add-apt-repository ppa:jonathonf/python-3.6
    $SUDO $os_pm $option update -y
    $SUDO $os_pm $option install python3.6 -y
    $SUDO $os_pm $option remove python3-apt -y
    $SUDO $os_pm $option install python3-apt -y

    $SUDO update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1
    $SUDO update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2

    $SUDO $os_pm $option install  python3-pip || true
    $SUDO $os_pm $option install  docker.io || true
    $SUDO $os_pm $option install  screen || true
    $SUDO $os_pm $option install  git || true
    $SUDO $os_pm $option install  curl || true
    $SUDO $os_pm $option install  tree || true


    echo "Installing elasticsearch"
    install_elasticsearch

    echo "Installing rabbitMQ"
    install_rabbitmq

    echo "Installing required python packages"
    install_python_packages

    echo "Installing juju"
    install_juju

    echo "Installing uvtool_kvm"
    install_uvtool_kvm

}

install_uvtool_kvm(){
    $SUDO $os_pm install $option  qemu-kvm libvirt-bin virtinst bridge-utils cpu-checker || true
    $SUDO $os_pm install $option uvtool || true
    $SUDO adduser $USER libvirtd
    # echo 'fetching cloud image kvm xenial'
    # $SUDO uvt-simplestreams-libvirt --verbose sync release=xenial arch=amd64
}

install_ubuntu_image(){
    echo 'fetching cloud image kvm xenial'
    $SUDO uvt-simplestreams-libvirt --verbose sync release=xenial arch=amd64
}

install_elasticsearch(){
    $SUDO $os_pm install  $option default-jre || true
    JAVA_HOME=/usr/lib/jvm/default-java/bin
    export JAVA_HOME 
    PATH=$PATH:$JAVA_HOME 
    export PATH 
    curl https://artifacts.elastic.co/GPG-KEY-elasticsearch | $SUDO apt-key add -
    $SUDO $os_pm install $option apt-transport-https || true
    echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | $SUDO tee -a /etc/apt/sources.list.d/elastic-6.x.list 
    $SUDO $os_pm update $option && $SUDO $os_pm install elasticsearch || true
    $SUDO -i service elasticsearch start 
}

install_rabbitmq(){
    curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -
    $SUDO $os_pm update
    $SUDO $os_pm install $option rabbitmq-server
}

install_juju(){
    $SUDO $os_pm $option install  snapd || true
    $SUDO $os_pm $option install  zfsutils-linux || true
    sudo snap install lxd || true
    # sudo adduser $USER lxd || true
    # newgrp lxd
    # groups
    sudo snap install juju --classic || true
}
install_python_packages(){
    pip3 install jsonify --user
    pip3 install flask --user
    pip3 install juju --user
    pip3 install termcolor --user
    pip3 install jsonpickle --user
    pip3 install pika --user
    pip3 install elasticsearch --user
    pip3 install jsonschema --user
    pip3 install commentjson --user
}

function jox_store(){

if [ ! -d $jox_store ]; then
    echo "Creating cache dir in $jox_store"
    sudo mkdir -p $jox_store
fi

if grep -qs "$jox_store" /proc/mounts; then
    echo "JoX store is already mounted"
else
    echo "JoX store was not mounted, Mounting ..."
    sudo mount -o size=100m -t tmpfs none "$jox_store"
    if [ $? -eq 0 ]; then
	echo "Mount success"
    else
	echo "Something went wrong with the mount"
    fi
fi

}

function print_help() {
  echo '
This program installs the JoX package dependencies
-h                                  print this help
-i | --install-required-pkg         install required packages for build and/or snap process
-x | --install-ubuntu-xenial-kvm    install ubuntu-xenial image for kvm

'
  exit $1
}

function main() {
    until [ -z "$1" ]; do
        case "$1" in
            -i | --install-required-pkg)
            INSTALL_PKG=1
            echo "Installing the required packages for JoX"
            shift;;
            -h | --help | -help )
            print_help 0
            shift;;
            -x | --install-ubuntu-xenial-kvm )
            INSTALL_PKG=2
            echo "Installing ubuntu xenial image for kvm"
            shift;;
            *)
            echo "Unknown option $1"
            print_help -1
            shift;;
        esac
    done

    if [ "$INSTALL_PKG" = "1" ] ; then
	    echo "Installing the required packages"
	    install_required_packages
	    echo "###### JoX built successfully !!! ######"
    fi
    if [ "$INSTALL_PKG" = "2" ] ; then
	    install_ubuntu_image
	    echo "Installed ubuntu image for kvm"
    fi

    jox_store
}

main  "$@"

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


export DEBIAN_FRONTEND=noninteractive

SUDO='sudo -E'
os_pm="apt-get"
os_pm_remove="apt-add-repository"
os_pm_add="add-apt-repository"
option="-y"
specific_pkgs="zfsutils-linux"
ubuntu_cloud_image_version="xenial"

jox_store=/mnt/jox_store

###################################
# colorful echos
###################################

black='\E[30m'
red='\E[31m'
green='\E[32m'
yellow='\E[33m'
blue='\E[1;34m'
magenta='\E[35m'
cyan='\E[36m'
white='\E[37m'
reset_color='\E[00m'
COLORIZE=1

cecho()  {
    # Color-echo
    # arg1 = message
    # arg2 = color
    local default_msg="No Message."
    message=${1:-$default_msg}
    color=${2:-$green}
    [ "$COLORIZE" = "1" ] && message="$color$message$reset_color"
    echo -e "$message"
    return
}

echo_error()   { cecho "$*" $red          ;}
echo_fatal()   { cecho "$*" $red; exit -1 ;}
echo_warning() { cecho "$*" $yellow       ;}
echo_success() { cecho "$*" $green        ;}
echo_info()    { cecho "$*" $blue         ;}





os=$(grep "^ID=" /etc/os-release | sed "s/ID=//" | sed "s/\"//g")
os_release=$(grep "^VERSION_ID=" /etc/os-release | sed "s/VERSION_ID=//" | sed "s/\"//g")
os_dist=$os$os_release
echo_info "Detected OS Dist:" $os_dist

case "$os" in
  fedora) os_base="fedora"; os_pm="dnf"; os_cmake="cmake" ;;
  rhel)   os_base="fedora"; os_pm="yum"; os_cmake="cmake3" ;;
  centos) os_base="fedora"; os_pm="yum"; os_cmake="cmake3" ;;
  debian) os_base="debian"; os_pm="apt-get"; os_cmake="cmake" ;;
  ubuntu) os_base="debian"; os_pm="apt-get"; os_cmake="cmake" ;;
esac

check_supported_os_dist() {
    case "$os_dist" in
        "ubuntu18.04") return 0 ;;
        "ubuntu16.04") return 0 ;;
    esac
    return 1
}
check_ubuntu_1604() {
    case "$os_dist" in
        "ubuntu16.04") return 0 ;;
    esac
    return 1
}

if ! check_supported_os_dist; then
    echo_error "Your distribution $os_dist is not supported by JoX!"
    exit 1
fi

install_required_packages(){
    echo_info "Installing dependencies for $os_dist"
    if check_ubuntu_1604; then
        $SUDO $os_pm $option install python3.5  || true
    else
        echo_info "Installing python3.6"
        $SUDO $os_pm $option install python3.6  || true
    fi

    $SUDO $os_pm $option install \
                        python3-setuptools \
                        python3-dev \
                        libpq-dev \
                        build-essential

    alias python3=python3.6
    echo_success "Python3.6 is successfully installed"

    echo_info "Installing python3-pip"
    $SUDO $os_pm $option install python3-pip || true

    echo_info "Installing docker.io"
    $SUDO $os_pm $option install docker.io || true

    echo_info "Installing curl"
    $SUDO $os_pm $option install curl || true

    echo_info "Installing tree"
    $SUDO $os_pm $option install tree || true


    install_elasticsearch
}

install_uvtool_kvm(){
    $SUDO $os_pm $option install qemu-kvm libvirt-bin virtinst bridge-utils cpu-checker || true
    $SUDO $os_pm $option install uvtool || true

    jox_store
}

install_ubuntu_image(){
    echo_info "fetching cloud image kvm $1"
    $SUDO uvt-simplestreams-libvirt --verbose sync release=$1 arch=amd64
    echo_success "cloud image $1 was successfully downloaded"
}

install_elasticsearch(){
    echo_info "pulling the docker image of elasticsearch:6.6.2"
    sudo docker pull docker.elastic.co/elasticsearch/elasticsearch:6.6.2

    install_rabbitmq
}

install_rabbitmq(){
    echo_info "Installing rabbitMQ"
    curl https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
    $SUDO $os_pm $option install rabbitmq-server
    $SUDO service rabbitmq-server start

    echo_info "enable rabbitmq-server"
    sudo systemctl start rabbitmq-server
    sudo systemctl enable rabbitmq-server
    echo_success "rabbitmq is successfully installed"


    install_python_packages
}

install_juju(){
    echo_info "installing juju "
    $SUDO $os_pm $option install  snapd || true
    $SUDO $os_pm $option install  zfsutils-linux || true
    sudo snap install lxd || true
    sudo snap install juju --classic || true
    echo_success "juju is successfully installed"


    install_uvtool_kvm
}
install_python_packages(){
    echo_info "Installing python libraries"

    echo_info "Installing cryptography"
    sudo pip3 install --force-reinstall cryptography==2.4.2 --user
    echo_success "cryptography is successfully installed"

    echo_info "Installing paramiko"
    sudo pip3 install --force-reinstall paramiko==2.4.2 --user
    echo_success "paramiko is successfully installed"


    echo_info "Installing flask"
    sudo pip3 install flask --user
    echo_success "flask is successfully installed"

    echo_info "Installing juju"
    sudo pip3 install --force-reinstall juju==0.11.6 --user
    echo_success "juju is successfully installed"

    echo_info "Installing termcolor"
    sudo pip3 install termcolor --user
    echo_success "termcolor is successfully installed"

    echo_info "Installing jsonpickle"
    sudo pip3 install jsonpickle --user
    echo_success "jsonpickle is successfully installed"

    echo_info "Installing pika"
    sudo pip3 install --force-reinstall pika==0.12.0 --user
    echo_success "pika is successfully installed"


    echo_info "Installing netaddr"
    sudo pip3 install netaddr --user
    echo_success "netaddr is successfully installed"

    echo_info "Installing netaddr"
    sudo pip3 install ipaddress --user
    echo_success "netaddr is successfully installed"

    echo_info "Installing elasticsearch"
    sudo pip3 install elasticsearch --user
    echo_success "elasticsearch is successfully installed"

    echo_info "Installing jsonschema"
    sudo pip3 install jsonschema --user
    echo_success "jsonschema is successfully installed"


    install_juju
}

function jox_store(){
    if [ ! -d $jox_store ]; then
        echo_info "Creating cache dir in $jox_store"
        sudo mkdir -p $jox_store
        echo_success "JoX store is successfully created"
    fi

    if grep -qs "$jox_store" /proc/mounts; then
        echo_info "JoX store is already mounted"
    else
        echo_info "JoX store was not mounted, Mounting ..."
        sudo mount -o size=100m -t tmpfs none "$jox_store"
        if [ $? -eq 0 ]; then
        echo_success "Mount success"
        else
        echo_error "Something went wrong with the mount"
        fi
    fi
}

function print_help() {
  echo '
This program installs the JoX package dependencies
-h                                  print this help
-i | --install-required-pkg         install required packages for build and/or snap process
-u | --ubuntu-cloud-version         Download ubuntu cloud image to be used for creating kvm machines. default image is xenial
'
  exit $1
}

function main() {
    until [ -z "$1" ]; do
        case "$1" in
            -i | --install-required-pkg)
            INSTALL_PKG=1
            echo_info "Installing the required packages for JoX"
            shift;;
            -h | --help | -help )
            print_help 0
            shift;;

            -u | --ubuntu-cloud-version)
            INSTALL_PKG=2
            ubuntu_image_version=$2
            if [ "$ubuntu_image_version" == "" ] ; then
                ubuntu_image_version=$ubuntu_cloud_image_version
                shift_val=1
            else
                shift_val=2
            fi
            echo_info "Ubuntu cloud image $ubuntu_image_version will be downloaded"
            shift $shift_val;;

            *)
            echo_error "Unknown option $1"
            print_help -1
            shift;;
        esac
    done

    if [ "$INSTALL_PKG" = "1" ] ; then
	    install_required_packages
	    sudo adduser $USER docker
	    newgrp lxd
	    groups

	    sudo adduser $USER lxd
	    newgrp lxd
	    groups
	    echo_success "###### JoX built successfully !!! ######"
    fi
    if [ "$INSTALL_PKG" = "2" ] ; then
	    install_ubuntu_image $ubuntu_image_version
    fi
}

main  "$@"

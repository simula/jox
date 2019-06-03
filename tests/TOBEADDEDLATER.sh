#!/usr/bin/env bash


juju model-config enable-os-refresh-update=false enable-os-upgrade=false


sudo rm /etc/systemd/system/jujud*
sudo rm -rf /var/lib/juju
sudo rm /usr/bin/juju-run



sudo apt-get update
sudo apt-get upgrade
echo export LC_CTYPE=en_US.UTF-8 >> ~.bashrc
echo export LC_ALL=en_US.UTF-8 >> ~.bashrc
sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y




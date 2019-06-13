#!/usr/bin/env bash

watch -n 1 --color  juju status --relations  -m localhost-borer:default-2 --color


juju model-config enable-os-refresh-update=false enable-os-upgrade=false


juju add-model default-1
juju model-config enable-os-refresh-update=false enable-os-upgrade=false

juju add-model default-2
juju model-config enable-os-refresh-update=false enable-os-upgrade=false

sudo rm /etc/systemd/system/jujud*
sudo rm -rf /var/lib/juju
sudo rm /usr/bin/juju-run



sudo apt-get update
sudo apt-get upgrade
echo export LC_CTYPE=en_US.UTF-8 >> ~.bashrc
echo export LC_ALL=en_US.UTF-8 >> ~.bashrc
sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y



# to install usrp
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt-get update
sudo apt-get install libuhd-dev libuhd003 uhd-host


# remote lxd
# 1- remote machine from which you want to use the lxd
lxc config set core.https_address [::]:8443
lxc config set core.trust_password something-secure

#2- local machine where you want to manage lxd for the remote machine
lxc remote add pou_remote 192.168.1.88
lxc remote add pou_remote_router 192.168.1.5



sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl start_app



         {MCC="208"; MNC="94"; MME_GID="4" ; MME_CODE="1"; }                   # YOUR GUMMEI CONFIG HERE
    # TA (mcc.mnc:tracking area code) DEFAULT = 208.34:1
         {MCC="208"; MNC="95";  TAC="1"; }                                 # YOUR TAI CONFIG HERE


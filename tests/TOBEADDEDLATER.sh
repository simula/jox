#!/usr/bin/env bash

watch -n 1 --color  juju status --relations  -m localhost-borer:default-2 --color


juju model-config enable-os-refresh-update=false enable-os-upgrade=false


juju add-model default-1
juju model-config enable-os-refresh-update=false enable-os-upgrade=false

juju add-model default-2
juju model-config enable-os-refresh-update=false enable-os-upgrade=false



sudo rm /etc/systemd/system/*jujud*
sudo rm -rf /var/lib/juju
sudo rm /usr/bin/juju-run
sudo rm -rf /etc/profile.d/*juju*
sudo rm -rf /etc/systemd/system/*juju*


nymphe-cloud-edu

sudo apt-get update
sudo apt-get upgrade
echo export LC_CTYPE=en_US.UTF-8 >> ~.bashrc
echo export LC_ALL=en_US.UTF-8 >> ~.bashrc
sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y



# to install usrp
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt-get update
sudo apt-get install libuhd-dev libuhd003 uhd-host
sudo /usr/lib/uhd/utils/uhd_images_downloader.py

lxc config set juju-3ad4c5-4 security.privileged true
lxc restart juju-3ad4c5-4
sudo lxc config device add juju-3ad4c5-4 5G_card usb vendorid=2500 productid=0021 path=/usr/bin/uhd_usrp_probe
stgraber@dakara:~$ lxc config device add c1 sony usb vendorid=0fce productid=51da

sudo lxc config device add net2  path=/usr/bin/uhd_usrp_probe


# remote lxd
# 1- remote machine from which you want to use the lxd
lxc config set core.https_address [::]:8443
lxc config set core.trust_password something-secure

#2- local machine where you want to manage lxd for the remote machine
lxc remote add sakura_remote_home 192.168.1.39



passthrough usrp to lxc  container:
 sudo lxc config device add net2 5G_card usb vendorid=2500 productid=0021 path=/usr/bin/uhd_usrp_probe

sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl start_app



curl http://192.168.1.60:9999/stats/ | jq '.'
curl -X POST http://192.168.1.32:9999/slice/enb/-1 --data-binary "@slices_demo.json"

curl -X POST http://192.168.1.32:9999/ue_slice_assoc/enb/-1/ue/12286/slice/1




lxc stop c1
lxc network attach lxdbr0 c1 eth0 eth0
lxc config device set machine-flexran-1 eth0 ipv4.address 192.168.1.32
lxc start c1




 mme_ip_address      = ( { ipv4       = "192.168.1.11";
                              ipv6       = "192:168:30::17";
                              active     = "yes";
                              preference = "ipv4";
                            },
                            { ipv4       = "192.168.1.13";
                              ipv6       = "192:168:30::17";
                              active     = "yes";
                              preference = "ipv4";
                            }
                          );



# connections from outside
sudo iptables -I FORWARD -o virbr0 -d  192.168.122.73 -j ACCEPT
sudo iptables -t nat -I PREROUTING -p tcp --dport 9867 -j DNAT --to 192.168.122.73:22



# Masquerade local subnet
sudo iptables -I FORWARD -o virbr0 -d  192.168.122.73 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -s 192.168.122.0/24 -j MASQUERADE
sudo iptables -A FORWARD -o virbr0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i virbr0 -o enp0s31f6 -j ACCEPT
sudo iptables -A FORWARD -i virbr0 -o lo -j ACCEPT


#for masquarading, we need to add the following iptable rule:
iptables -t nat -A POSTROUTING -s [srcIP/24 -o [ifname] -j MASQUERADEuh
example:
iptables -t nat -A POSTROUTING -s 192.168.122.0/24 -o enp0s31f6 -j MASQUERADE

sudo iptables  -t nat -A POSTROUTING -o enp0s31f6 -s 192.168.122.0/24 -j MASQUERADE



juju config oai-du node_function="enb" eth=enp0s31f6 eutra_band=17 downlink_frequency=737500000L uplink_frequency_offset=-30000000
juju config oai-cu node_function="enb" eth=eth0 eutra_band=17 downlink_frequency=737500000L uplink_frequency_offset=-30000000




juju config oai-enb node_function="du" eth=enp0s31f6 eutra_band=17 downlink_frequency=737500000L uplink_frequency_offset=-30000000 \
cu_if_name=eth0 cu_ip_addr=192.168.1.11   \
du_if_name=enp0s31f6 du_ip_addr=192.168.1.10




juju config oai-cu node_function="cu" eth=eth0 eutra_band=17 downlink_frequency=737500000L uplink_frequency_offset=-30000000 \
cu_if_name=eth0 cu_ip_addr=192.168.1.11   \
du_if_name=enp0s31f6 du_ip_addr=192.168.1.10

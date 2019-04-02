JOX is composed of the following directories: 

|-- charms
|   |-- bundle
|   |  |-- oai-nfv-rf
|   |  |-- oai-nfv-rrh 
|   |  |-- oai-nfv-sim
|   |-- trusty
|   |   |-- oai-enb
|   |   |-- oai-epc
|   |   |-- oai-hss
|   |   |-- oai-mme
|   |   |-- oai-rrh
|   |   |-- oaisim-enb-ue
|   |   |-- oai-spgw
|   |-- xenial
|-- README.md
|-- scripts
    |-- build_jox
    |-- tools
        |-- build_helper
        
        
To add:
- virt type of physical machines
- additional capabilities (tags)
 

juju model-config enable-os-refresh-update=false enable-os-upgrade=false


juju model-config no-proxy=172.24.0.0/16,127.0.0.1,localhost,::1


juju model-config no-proxy=192.168.1.0/24,127.0.0.1,localhost,::1

juju model-config no-proxy=192.168.1.0/24,192.168.122.0/24,10.180.125.0/24,127.0.0.1,localhost,::1






- ES ubunut 16 
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch


./build_jox.sh -i 2>&1 | tee jox_install_log.txt

- issue: machine already provisioned:
sudo rm -rf /etc/init/juju*
sudo rm -rf /var/lib/juju
sudo rm -rf /var/lib/juju
sudo rm -rf /usr/lib/juju
sudo apt-get remove juju*
sudo rm /etc/systemd/system/jujud*
sudo rm -rf /var/lib/juju
sudo rm /usr/bin/juju-run

- 
watch -n 1 --color 'juju status --relations --color'


- to add to build script
* import ipaddress
* import psutil
import random
from netaddr import IPAddress, IPNetwork
import copy
install pika==0.12.0



- accelerate deploying lxd/kvm
ssh ubuntu@192.168.122.8 echo export LC_CTYPE=en_US.UTF-8 >> ~.bashrc
ssh ubuntu@192.168.122.8 echo export LC_ALL=en_US.UTF-8 >> ~.bashrc
ssh ubuntu@192.168.122.8 source .bashrc
ssh ubuntu@192.168.122.8 sudo apt-get update -y
ssh ubuntu@192.168.122.8 sudo apt-get upgrade -y
ssh ubuntu@192.168.122.8 sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y



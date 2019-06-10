https://blog.simos.info/how-to-make-your-lxd-containers-get-ip-addresses-from-your-lan-using-a-bridge/

# macvtap
sudo ip link add link enp0s31f6 name macvtap0 address ec:21:e5:64:44:58 type macvtap mode bridge
sudo ip link add link enp0s31f6 name macvtap0 address 52:54:00:b8:9c:58 type macvtap mode bridge
sudo ip link set macvtap0 up
ip link show macvtap0



sudo ip link add link enp0s31f6 name macvlan0 address 52:54:00:b8:9c:33 type macvlan mode bridge
sudo ip link set macvlan0 up
ip link show macvlan0




config: {}
description: Default LXD profile
devices:
  eth0:
    name: eth0
    nictype: macvlan
    parent: macvtap0
    type: nic
  eth1:
    name: eth1
    nictype: macvlan
    parent: macvtap0
    type: nic
  eth2:
    name: eth2
    nictype: macvlan
    parent: macvlanvepa0
    type: nic
  eth3:
    name: eth3
    nictype: bridged
    parent: lxdbr0
    type: nic
  root:
    path: /
    pool: lxd
    type: disk


sudo ip link add link enp0s31f6 name macvlanvepa0 address 52:54:00:b8:9c:33 type macvlan mode vepa
sudo ip link set macvlanvepa0 up
ip link show macvlanvepa0


 qemu -net nic,model=virtio,addr=52:54:00:b8:9c:60 -net tap,fd=3 3<>/dev/tap11
 

uvt-kvm create machine1  release=xenial --memory 1024 --cpu 1 --disk 3  --ssh-public-key-file /home/borer/.ssh/id_juju2.pub --password linux


in order to link lxd to kvm:
1- create a new and empty LXD profile, called bridgeprofile.


```bash
$ lxc profile create bridgeprofile
```

2- configure the bridge with the parent as the name of the bridge of kvm

```
description: Bridged networking LXD profile
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: virbr0
    type: nic
EOF
```

3- 
```bash
$ cat <<EOF | lxc profile edit bridgeprofile
description: Bridged networking LXD profile
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: virbr0
    type: nic
EOF
```

config: {}
description: Default LXD profile
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: lxdbr0
    type: nic
  root:
    path: /
    pool: lxd
    type: disk
name: default
used_by: []


config: {}
description: Default LXD profile
devices:
  eth0:
    name: eth0
    nictype: macvlan
    parent: macvtap0
    type: nic
  eth1:
    name: eth1
    nictype: bridged
    parent: lxdbr0
    type: nic
  root:
    path: /
    pool: lxd
    type: disk
name: default
used_by:
- /1.0/containers/nympheController
- /1.0/containers/machine-mysql



- for uhd
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt-get update
sudo apt-get install libuhd-dev libuhd003 uhd-host


uvt-kvm create machine1  release=xenial --memory 1024 --cpu 1 --disk 3 --bridge macvtap0  --ssh-public-key-file /home/borer/.ssh/id_juju2.pub --password linux


kvm -hda /home/borer/Downloads/ubuntu-16.04-server-amd64.img -netdev tap,id=net0,ifname=tap0,vhost=on -device e1000,netdev=net0,mac=52:54:00:12:34:60 -smp 1 -m 1G -daemonize -vnc :0


kvm -drive file=/home/borer/Downloads/ubuntu-16.04-server-amd64.img -smp 1 -m 512M -netdev tap,id=net11,ifname=tap5,vhost=on -device e1000,netdev=net11,mac=52:54:00:12:34:cc -netdev tap,id=netMGMT2,ifname=tapM2,vhost=on -device e1000,netdev=netMGMT2,mac=52:54:00:12:aa:bb -daemonize -vnc :2



 kvm -hda /home/borer/Downloads/ubuntu-16.04-server-amd64.img -netdev tap,id=net2,ifname=tap1,vhost=on -device 
e1000,netdev=net2,mac=52:54:00:12:34:58 -smp 3 -m 3G -netdev 
tap,id=net3,ifname=tap2,vhost=on -device e1000,netdev=net3,mac=52:54:00:12:34:59 -netdev 
tap,id=net4,ifname=tap3,vhost=on -device e1000,netdev=net4,mac=52:54:00:12:34:aa -usb 
-usbdevice tablet -daemonize


kvm -hda /var/lib/uvtool/libvirt/images/machine1.qcow -netdev tap,id=net0,ifname=tap0,vhost=on -device  e1000,netdev=net0,mac=52:54:00:12:34:60 -smp 1 -m 1G -daemonize -vnc :0




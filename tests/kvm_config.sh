#!/usr/bin/env bash


# VM image info
IMAGE_PATH=/opt/OAI/images
EPC_IMG=epc.img
SGW_IMG=spgw-mec.vmdk
HTTP_IMG=httpserver.img
IPERF_IMG=ncserver.img

# networking params
MTU=1464
NAT_PUB_IF=wlp2s0
NAT_SGW_IF=tap2
NAT_SGW_IF_MAC=00:11:22:33:44:55
NAT_MEC_IF=brX
SGI_ADDR=172.16.0.100
MEC_GW_ADDR=192.168.0.1
OAI_CTRL_ADDR=10.10.10.11


# create bridges
sudo brctl addbr br0
sudo brctl addbr brX

# start HSS/MME vm
echo "Booting HSS/MME"
kvm -hda $IMAGE_PATH/$EPC_IMG -netdev tap,id=net0,ifname=tap0,vhost=on -device
e1000,netdev=net0,mac=52:54:00:12:34:60 -smp 1 -m 1G -daemonize -vnc :0
sleep 2

# start spgw
echo "Booting SPGW"
kvm -hda $IMAGE_PATH/$SGW_IMG -netdev tap,id=net2,ifname=tap1,vhost=on -device
e1000,netdev=net2,mac=52:54:00:12:34:58 -smp 3 -m 3G -netdev
tap,id=net3,ifname=tap2,vhost=on -device e1000,netdev=net3,mac=52:54:00:12:34:59 -netdev
tap,id=net4,ifname=tap3,vhost=on -device e1000,netdev=net4,mac=52:54:00:12:34:aa -usb
-usbdevice tablet -daemonize
sleep 2

# Configure the MAC addr of the intenal NAT interface
ifconfig $NAT_SGW_IF down
ip link set $NAT_SGW_IF address $NAT_SGW_IF_MAC
ifconfig $NAT_SGW_IF up

echo "Booting MEC servers"
# start mec servers
kvm -drive file=$IMAGE_PATH/$HTTP_IMG -smp 1 -m 512M -netdev
tap,id=net10,ifname=tap4,vhost=on -device e1000,netdev=net10,mac=52:54:00:12:34:bb
-netdev tap,id=netMGMT1,ifname=tapM1,vhost=on -device
e1000,netdev=netMGMT1,mac=52:54:00:12:aa:aa -daemonize -vnc :1
sleep 2
kvm -drive file=$IMAGE_PATH/$IPERF_IMG -smp 1 -m 512M -netdev
tap,id=net11,ifname=tap5,vhost=on -device e1000,netdev=net11,mac=52:54:00:12:34:cc
-netdev tap,id=netMGMT2,ifname=tapM2,vhost=on -device
e1000,netdev=netMGMT2,mac=52:54:00:12:aa:bb -daemonize -vnc :2
sleep 2

# add interfaces to bridges
sudo brctl addif br0 enp0s31f6
sudo brctl addif br0 tap0
sudo brctl addif br0 tap1
# we add the MEC servers' mgmt interfaces on the same bridge, assuming that the MEC platform is
# on the same host or network for simplicity
brctl addif br0 tapM1
brctl addif br0 tapM2

brctl addif brX tap3
brctl addif brX tap4
brctl addif brX tap5

# configure IP addresses and MTU sizes
ifconfig eno1 0
ifconfig br0 $OAI_CTRL_ADDR mtu $MTU
ifconfig tap2 $SGI_ADDR mtu $MTU
ifconfig brX $MEC_GW_ADDR mtu $MTU

# configure iptables
echo "Configuring NAT"
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -F
iptables -F -t nat
iptables -t nat -A POSTROUTING -o enp0s31f6 -j MASQUERADE
iptables -A FORWARD -i enp0s31f6 -o virbr0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i virbr0 -o enp0s31f6 -j ACCEPT

iptables -A FORWARD -i $NAT_PUB_IF -o $NAT_MEC_IF -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $NAT_MEC_IF -o $NAT_PUB_IF -j ACCEPT



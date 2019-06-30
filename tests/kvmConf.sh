
#!/bin/sh
set -x

switch=br0

if [ -n "$1" ];then
        #tunctl -u `whoami` -t $1
        ip tuntap add $1 mode tap user `whoami`
        ip link set $1 up
        sleep 0.5s
        #brctl addif $switch $1
        ip link set $1 master $switch
        exit 0
else
        echo "Error: no interface specified"
        exit 1
fi



ip link add name br0 type bridge
ip addr add 192.168.12.0/24 dev br0
ip link set dev br0 up
sysctl -w net.ipv4.ip_forward=1
iptables --table nat --append POSTROUTING --out-interface ens33 -j MASQUERADE
iptables --insert FORWARD --in-interface br0 -j ACCEPT
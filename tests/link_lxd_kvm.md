https://blog.simos.info/how-to-make-your-lxd-containers-get-ip-addresses-from-your-lan-using-a-bridge/


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
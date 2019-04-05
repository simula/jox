# Build JoX
JoX comes with an automated build script. Note that the steps detailed here are tested with Ubuntu 18.04, Juju version 2.5.1 (Juju version 2+ recommended).
In the following, we refer to `DIR_JOX` to the directory of JoX project. In order to use JoX, please follow the following steps:

# 1. Clone stable source
Firstly, you need to install `git` in order to get the JoX project:
```bash
$ sudo apt install git -y
```
and then you can clone JoX:
```bash
$ git clone -b develop https://gitlab.eurecom.fr/mosaic5g/jox.git 
```
Or
```bash
$ git clone -b develop git@gitlab.eurecom.fr:mosaic5g/jox.git
```

# 2. Build JoX
To build JoX, use the build script (you can find it at DIR_JOX/scripts/build_jox.sh) as follows;

```bash
$ cd DIR_JOX/scripts/ 
$ ./build_jox.sh -i # to build JoX  
```
This will build all the dependencies of JoX. For more options, 

```bash
$ ./build_jox.sh -h # to print help 
$ ./build_jox.sh -i # to build JoX 
$ ./build_jox.sh -x # to download ubuntu-xenial cloud images necessary for kvm
```
 

When building JoX, and at the end of the build, you should see the following message:
```
###### JoX built successfully !!! ######
Creating cache dir in /mnt/jox_store
JoX store was not mounted, Mounting ...
Mount success
```
 
# 3. Fetch cloud image for kvm
If you plan to use kvm (Optional), which is the case for some juju charms like oai-spgw, you should firstly fetch the ubuntu cloud image(xenial) as follows:

```bash
./build_jox.sh -x
```


# 4. Prepare lxd for juju
Before using juju with lxd, you should firstly configure it (please refer to [https://docs.jujucharms.com](https://docs.jujucharms.com) for more details):
```bash
sudo lxd init 
```
Here is an example of the configuration:
```
Would you like to use LXD clustering? (yes/no) [default=no]: 
Do you want to configure a new storage pool? (yes/no) [default=yes]: 
Name of the new storage pool [default=default]: lxd
Name of the storage backend to use (btrfs, ceph, dir, lvm, zfs) [default=zfs]: 
Create a new ZFS pool? (yes/no) [default=yes]: 
Would you like to use an existing block device? (yes/no) [default=no]: 
Size in GB of the new loop device (1GB minimum) [default=15GB]: 
Would you like to connect to a MAAS server? (yes/no) [default=no]: 
Would you like to create a new local network bridge? (yes/no) [default=yes]: 
What should the new bridge be called? [default=lxdbr0]: 
What IPv4 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: none
Would you like LXD to be available over the network? (yes/no) [default=no]: 
Would you like stale cached images to be updated automatically? (yes/no) [default=yes] 
Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]:
```
After lxd configuration, use the following commands to add user as member of the 'lxd' group.
```bash
$ sudo adduser $USER lxd 
$ newgrp lxd
```
# 5. Prepare juju for JoX
In order to use JoX, you should create the juju controller that you can use it later in JoX. To list all the clouds configured with juju, please type:
```bash
$ juju clouds
```
In order to create juju controller, you can use:
```bash
$ juju bootstrap "cloud name" "name of your juju controller"
```

In this documentation we use *localhost* (of lxd type) as cloud.
```bash
$ juju bootstrap localhost localhost
```
where the second `localhost` in the previous command is the name of your controller. After that add your juju controller to the list of 
*"clouds-list"* that is in the file ``DIR_JOX/common/config/jox_config.json``. If the name of your juju controller is
*localhost* then, you the *"clouds-list"* you can add it like
```
"clouds-list":
    [
        {
            "cloud-name": "localhost",
            "description": "name of you juju controller"
        }
    ],
``` 
# 6. Change the set of metrics in jox-config according to your environment
#### 6.1 vim configuration
In the jox-config file that is located at
``DIR_JOX/common/config/jox_config.json``, the entry *"vim-pop"*constains the tree supporte types of vims (lxd, kvm, and physial). The physical stands for the physical machines that you can use them to deploys one or more services of your slice. This entry should be modified according to your environment. In addition, the entry *"zones"* stands for the zones (mostly refer to geographical zone), and the domains that are in every zone. For the moment, oly one zone need to be defined.
#### 6.2 Cloud list
The entry *"clouds-list"* refer to the configuration of your juju controller. You can define one or more clouds.
#### 6.3 ssh configuration
The entry *"ssh-config"* contains the ssh credentional necessary to ssh kvm and lxd machines when they are created manually.
#### 6.4 Additional configurations
If you would like run jox, nbi, and elasticsearch on 
the same machine, then there is no need for further 
changes in the jox_config.json. Otherwise, 
change the host and the port for every component accordingly*



# 7. Run rabbitMQ (RBMQ) and Elasticsearch (ES)
JoX uses RabbitMq (RBMQ) as message bus between jox and nbi modules, it uses Elasticsearch (ES) for monitoring. RBMQ and ES will be run automatically when running jox and nbi.

# 8. Start jox and nbi
At this stage, there is nothing to do other than just run jox and nbi.
For that, go to jox directory *DIR_JOX* and then in two different 
terminals type ``./jox.sh`` in the first and  ``./nbi.sh`` in the second 

# Additional tutorials
- [JoX Home](https://gitlab.eurecom.fr/mosaic5g/jox/wikis/home)
- [Template Descriptor](/tutorials/Template-Descriptor)
- [Package Onboarding](/tutorials/Package-Onboarding)
- [Use Cases](/tutorials/use-cases)
- [Troubleshooting](/Issues/troubleshooting)
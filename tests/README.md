For this documentation, it is assumed that you have already installed and configured JoX, please refer [setup jox](https://gitlab.eurecom.fr/mosaic5g/jox/wikis/tutorials/setup-jox) if you did not yet installed JoX.

In the current use-case, we will deploy a slice (i.e., network slice instance-nsi) that is composed of three subslices (i.e., network slice subnet instance-nssi) that are nssi_1, nssi_2 and nssi3 as shown in the figure below. The first subslcie nssi_1 consists of two services , which are mysql and oai-hss, whereas nssi_2 is composed of oai-mme and oai-spgw. The subslice nssi_3 consist of oai-ran application i.e. oai-enb. Note that the green line between services represents juju relation (service requirements) between services. in this example, oai-spgw is deployed on kvm machine (please refer [here](https://jujucharms.com/new/u/navid-nikaein/oai-spgw/xenial/15) for why oai-spgw is deployed on kvm), and oai-end will be deployed on physical machine, while all the others are deployed on lxc machines.

[//]: # (Here OAI-SPGW is hosted on kvm while all other services are hosted on lxc machines. Follow this descriptor, hyperlink here, file for details of template)


![Screenshot_from_2019-04-03_13-21-55](uploads/b59ab0bb67a49c4c7d7da9f9069d84d3/Screenshot_from_2019-04-03_13-21-55.png)

Deploying the slice illustrated above is done as follows:
### 1. Manual Cloud Setup:
Here we will setup a manual cloud unlike for other tutorials of usecase oai-epc and wordpress, where we setup cloud as local provider. To add cloud, use following command
`juju add-cloud`, and then follow the steps to create a cloud. Here is an example on creating manual cloud:
```
borer@borer:~$ juju add-cloud
Cloud Types
  lxd
  maas
  manual
  openstack
  vsphere

Select cloud type: manual
Enter a name for your manual cloud: mancloud
Enter the controller's hostname or IP address:borer@192.168.1.13
Cloud "mancloud" successfully added
You will need to add credentials for this cloud (`juju add-credential mancloud`)
before creating a controller (`juju bootstrap mancloud`).
```
#### 1.1. Create juju controller:
For this tutorial, we run JoX (jox, and nbi) on the same machine where we create the manual cloud, and use *manual*-type cloud for creating juju controller. Note that *jox* should be run always on the same machine where you create the juju controller, while *nbi* can be run elsewhere . The steps to prepare the environment are as follows:
As mentioned earlier, we use the cloud of type *manual* to create the juju controller as follows:

```bash
$ juju bootstrap mancloud 
``` 

On successful creation of controller you should see following message <br>

```bash
borer@borer:~$ juju bootstrap manual-cloud-home
[sudo] password for borer: 
ubuntu:x:1001:
Creating Juju controller "manual-cloud-home" on manual-cloud-home
Looking for packaged Juju agent version 2.5.4 for amd64
Installing Juju agent on bootstrap instance
Fetching Juju GUI 2.14.0
Running machine configuration script...
Bootstrap agent now started
Contacting Juju controller at 192.168.1.13 to verify accessibility...
Bootstrap complete, "manual-cloud-home" controller now available
Controller machines are in the "controller" model
Initial model "default" added
```
#### 1.2. juju model:
By default, juju will create a model named *default* that can be used for deploying the slice. However, If you would like to create different juju model to be used for deploying a slice, you can simply cretae it by:
```bash 
$ juju add-model default-juju-model-1 
```
Where *default-juju-model-1* is the name of the juju model that can be used to deploy the slice. However, we will use the mode *default* in this tutorial.
#### 1.3. Disable automatic OS update and upgrade:
Adding machine, especially physical machines takes a lot of time. In order to reduce this time, it is highly recomended to disable the automatic update and upgrade of the os of the added machine. This can be done by the following:
```bash
$ juju model-config enable-os-refresh-update=false enable-os-upgrade=false
```

### 2. Add machines to manual cloud:
Now here we will add resources to our cloud. We can add physical machine or virtual machine of type lxc and kvm. Note that this step is necesary only for physical machine, where JoX does not hold for the moment adding physical machines. However, JoX can add manually lxd and kvm machines when needed.

* Example to add lxc <br/>
Here we are adding ubuntu xenial machine of type lxc<br/>
Note:- Make sure you have configured lxd before adding lxc machine. Refer step [prepare-lxd-for-juju from build JoX](https://gitlab.eurecom.fr/mosaic5g/jox/wikis/tutorials/setup-jox#4-prepare-lxd-for-juju)
```bash
lxc launch ubuntu:16.04
```
Sample Output
```
Creating the container
Container name is: lenient-goose            
Starting lenient-goose
```
verify lxc machine details by command `lxc list`
```bash
+---------------+---------+----------------------+------+------------+-----------+
| lenient-goose | RUNNING | 10.199.92.178 (eth0) |      | PERSISTENT |           |
+---------------+---------+----------------------+------+------------+-----------+
```
In order to accelerat the process of adding machine manually to juju model, the following steps are necessary.
* Inject the public ssh key to the machine 
```bash
$ lxc file push "/path/to/ssh-key" lenient-goose/root/.ssh/authorized_keys 
```
where *"/path/to/ssh-key"* is the path to your ssh-key that you will use for ssh the machine. In our steup for this use-case, we use the  following:
```bash
$ lxc file push ~/.ssh/id_rsa.pub lenient-goose/root/.ssh/authorized_keys 
```
* Change the file permission
```bash
$ lxc exec lenient-goose bash
root@lenient-goose:~# chmod 600 /root/.ssh/authorized_keys && sudo chown root: /root/.ssh/authorized_keys
```

* Make sure that you can ssh to your machine:
```ssh root@10.199.92.178```

* As suggested [here](https://github.com/AdamIsrael/osm-hackfest/blob/master/bin/update-juju-lxc-images), install a common set of packes that can help a lot for instally charms:
```bash
$ ssh root@10.199.92.178
root@lenient-goose:~# sudo apt-get update
root@lenient-goose:~# sudo apt-get upgrade
root@lenient-goose:~# sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y
```
* Finally, add this machine to your juju model
```bash
juju add-machine ssh:root@10.199.92.178
```
Sample output
```bash
adm:x:4:syslog,ubuntu
dialout:x:20:ubuntu
cdrom:x:24:ubuntu
floppy:x:25:ubuntu
sudo:x:27:ubuntu
audio:x:29:ubuntu
dip:x:30:ubuntu
video:x:44:ubuntu
plugdev:x:46:ubuntu
netdev:x:109:ubuntu
lxd:x:110:ubuntu
ubuntu:x:1000:
created machine 0
```

* Example to add kvm  <br/>
Here we are adding ubuntu xenial machine of type kvm

```bash
uvt-kvm create oai_spgw_kvm release=xenial --ssh-public-key-file=/home/rosberg/.ssh/id_rsa.pub
```
verify kvm ip details by command `uvt-kvm ip oai_spgw_kvm`<br/>

Now prepar the machine before adding it to juju model<br/>
```bash
$ ssh ubuntu@192.168.122.47
ubuntu@ubuntu:~# sudo apt-get update
ubuntu@ubuntu:~# sudo apt-get upgrade
ubuntu@ubuntu:~# sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y
```
Finally, add this machine to juju manual cloud<br/>
```bash
$ juju add-machine ssh:ubuntu@192.168.122.47
```


* Example to add physical machine<br/>
```bash
$ ssh pou@192.168.1.46
ubuntu@ubuntu:~# sudo apt-get update
ubuntu@ubuntu:~# sudo apt-get upgrade
ubuntu@ubuntu:~# sudo apt-get install tmux curl bridge-utils cloud-image-utils cloud-utils cpu-checker distro-info genisoimage libaio1 libibverbs1 libnl-3-200 libnl-route-3-200 libnspr4 libnss3 librados2 librbd1 msr-tools qemu-block-extra qemu-utils sharutils ubuntu-fan -y
```
juju add-machine ssh:pou@192.168.1.46

To verify added machines use command `juju machines`<br/>
![Screenshot_from_2019-04-04_17-47-14](uploads/2b909d42f8e6bdae5d65a6089261c244/Screenshot_from_2019-04-04_17-47-14.png)

### 3. Package generation and onboarding:
Use the following [tutorial](https://gitlab.eurecom.fr/mosaic5g/jox/wikis/Onboarding-package) to generate your package and onboard it. You can also use a pre-built package [add here]() for this use-case

Make sure that the package is successfully onboarded by using 
```bash
$ curl -i http://localhost:5000/ls
```
If you can see your package at the output of this endpoint, it means that your package is successfully onboarded. Here is an example of the output of the previous endpoint
```
$ curl http://localhost:5000/ls
{
  "data": [
    "oai-4G"
  ], 
  "elapsed-time": "0:00:00.006624"
}
```


### 4. Deploy slice with RESTful NBI interface of JoX
To deploy a slice from already onboarded package, use the following:
```bash
$ curl http://localhost:5000/nsi/oai-4G -X POST
```
Please refer [apidoc](http://mosaic-5g.io/apidocs/jox/) for the full list of endpoints supported by the current version of JoX. After sometime, if you see the following message, it means that your slice was successfully deployed
```
{
  "data": "Creating/updating the slice oai-4G.yaml", 
  "elapsed-time": "0:01:41.521951"
}
```

### 5. Verify slice deployment
There are various ways to verify NSI deployment.
##### 5.1 With the help of JoX NBI
You can use the following endpoint of nbi of JoX to get the full list of all deployed slices
```bash
$ curl -i http://127.0.0.1:5000/nsi
```
Here is an example of the output of the previous endpoint:<br/>
//add output<br/>
Or you can check the template of particular deployed slice by giving the name of that slice:<br/>
//add output<br/>

##### 5.2 With help of Juju CLI interface
You can also check with Juju CLI by using following command
```bash
$ juju status --relations
```
Here is an example of the output of the previous command
// add image
##### 5.2 With help of Juju Web interface
Juju comes with a nice tool to visualize juju model. To access to juju web interface, use following command.
```bash
$ juju gui
```
By typing ``juju gui`` it will give you the url, username and password to access and visualize your model<br/>
//add output here

---

******Note******

While using juju interface (web/cli), just make sure you are in right juju model with command `juju models` or switch to the right model by command `juju switch`

---


### 6. Slice monitoring
JoX nbi can be used to get monitoring statistics related to slices, as well as subslices (please refer [apidoc](http://mosaic-5g.io/apidocs/jox/#api-Monitoring) for more granular statistics)<br/>

To get monitoring information on the whole slice, you can use the following:

### 7. Slice components access
There are various ways to access VM instance.<br />
* ssh with juju
```bash
$ juju ssh MACHINE_ID
```
where *MACHINE_ID* is the machine id given by juju that is integer number (i.e., 0, 1, etc). For example;
```bash
$ juju ssh 1
```
to ssh via juju to the machine *1*

you can also ssh to a certain machine through the name of the application (i.e., unit id in juju terminology) deployed on that machine. For example;
```bash
$ juju ssh oai-hss/0
```
to ssh to the machine of the unit *oai-hss/0*
![oai-hss-ssh](uploads/d59d59a952dccc2fef44bee0338d36ad/oai-hss-ssh.png)
 <br />
 
 
 After ssh certain component, and for oai applications, you can verify the status of running service by the following (oai-hss in this example):
```bash
ubuntu@oai-hss-0:~# oai-cn.hss-journal
```
![oai-hss-journel](uploads/d56552ac682b23916a8249731fb4d57e/oai-hss-journel.png)<br />


If your application is deployed in lxc, you can ssh to it also using lxc commands
```bash
$ lxc exec juju-7a566b-1 -- bash
```
where *juju-7a566b-1* is the name of the container given by lxd. After that, you can play without any command you want inside that machine
```
mante@mante:~$ lxc exec juju-7a566b-1 -- bash
root@oai-hss-0:~# oai-cn.hss-status 
Service      Startup  Current  Notes
oai-cn.hssd  enabled  active   -
root@oai-hss-0:~#
```


# Additional tutorials
- [JoX Home](https://gitlab.eurecom.fr/mosaic5g/jox/wikis/home)
- [Build JoX](/tutorials/setup-jox)
- [Template Descriptor](/tutorials/Template-Descriptor)
- [Package Onboarding](/tutorials/Package-Onboarding)
- [Use Cases](/tutorials/use-cases)
- [Troubleshooting](/Issues/troubleshooting)

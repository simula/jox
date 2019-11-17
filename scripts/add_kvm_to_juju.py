import os
import logging
import asyncio
from asyncio import subprocess
from juju import loop, utils

import datetime
from netaddr import IPNetwork, IPAddress
async def run_command(*args):
	arguments = (args[1] if len(args) > 1 else args[0])
	process = await asyncio.create_subprocess_exec(
		*arguments,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)
	stdout, stderr = await process.communicate()
	return (stdout.decode("utf-8")).strip()

def machine_configuration_for_jujuCharm(ssh_user, machine_ip, ssh_key_private):
	cmd_ssh_1 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "echo", "export", "LC_CTYPE=en_US.UTF-8", ">>" "~.bashrc"]
	cmd_ssh_2 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "echo", "export", "LC_ALL=en_US.UTF-8", ">>" "~.bashrc"]
	cmd_ssh_3 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "source", ".bashrc"]

	cmd_ssh_4 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "sudo", "apt-get", "update", "-y"]
	cmd_ssh_5 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "sudo", "apt-get", "upgrade", "-y"]
	cmd_ssh_6 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "sudo", "apt-get", "install",
				 "tmux",
				 "curl",
				 "bridge-utils",
				 "cloud-image-utils",
				 "cloud-utils",
				 "cpu-checker",
				 "distro-info",
				 "genisoimage",
				 "libaio1",
				 "libibverbs1",
				 "libnl-3-200",
				 "libnl-route-3-200",
				 "libnspr4",
				 "libnss3",
				 "librados2",
				 "librbd1",
				 "msr-tools",
				 "qemu-block-extra",
				 "qemu-utils",
				 "sharutils",
				 "ubuntu-fan",
				 "-y"]

	cmd_kvm_ssh_vm = "ssh -o StrictHostKeyChecking -i"+ ssh_key_private+''+ssh_user+'@'+machine_ip+"pwd"

	print(cmd_kvm_ssh_vm)
	cmd_kvm_ssh_vm_out = os.system(str(cmd_kvm_ssh_vm))
	#os.system()
	message = "ensuring ssh to the machine {}".format(machine_ip)
	print(message)

	cmd_ssh_1_out = os.system(str(cmd_ssh_1))
	message = "configure local {} to the machine {}".format(cmd_ssh_1[4], machine_ip)
	print(message)

	cmd_ssh_2_out = os.system(str(cmd_ssh_2))
	message = "configure local {} to the machine {}".format(cmd_ssh_2[4], machine_ip)
	print(message)
	cmd_ssh_3_out = os.system(str(cmd_ssh_3))

	cmd_ssh_4_out = os.system(str(cmd_ssh_4))
	message = "doing sudo apt-get update to the machine {}".format(cmd_ssh_2[4], machine_ip)
	print(message)

	cmd_ssh_5_out = os.system(str(cmd_ssh_5))
	message = "doing sudo apt-get upgrade to the machine {}".format(cmd_ssh_2[4], machine_ip)
	print(message)

	cmd_ssh_6_out = os.system(str(cmd_ssh_6))
	message = "installing required packages for charms in the machine {}".format(cmd_ssh_2[4], machine_ip)
	print(message)



if __name__ == '__main__':
	kvm_ip_list = {'machine_1':'192.168.122.71', 'machine_2':'192.168.122.233', 'machine_3':'192.168.122.96', 'machine_4':'192.168.122.118', 'machine_5':'192.168.122.48', 'machine_6':'192.168.122.33'}
	for num in range (len(kvm_ip_list.keys())):
		machine_ip = (kvm_ip_list['machine_'+str(num+1)])
		machine_configuration_for_jujuCharm('ubuntu', machine_ip, '.ssh/id_rsa')


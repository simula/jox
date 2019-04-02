from juju.model import Model
from juju import loop
import logging
from juju import utils

logger = logging.getLogger('jox.jmodel')
import asyncio
from asyncio import subprocess
import json
import time
async def get_juju_status(type, cloud_name=None, model_name=None, user_name="admin"):
	model = Model()
	if (cloud_name is None) and (model_name is None):
		try:
			await model.connect_current()
		except:
			message = "Error while trying to connect to the current juju model"
			logger.error(message)
			return [False, message]
	else:
		try:
			model_name = cloud_name + ":" + user_name + '/' + model_name
			await model.connect(model_name)
		except:
			message = "Error while trying to connect to the juju model {}:{}/{}".format(cloud_name, user_name,
			                                                                            model_name)
			logger.error(message)
			return [False, message]
	juju_status = (await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop))
	if type == 'machines':
		return [True, juju_status.machines]
	elif type == 'applications':
		return [True, juju_status.applications]
	elif type == 'relations':
		return [True, get_all_relations(juju_status)]
	elif type == 'all':
		juju_status_relations = get_all_relations(juju_status)
		full_status = ({'machines': [juju_status.machines],
		                'services': [juju_status.applications],
		                'relations': [juju_status_relations]})
		return [True, full_status]
	else:
		message = "The key {} is not supported. Only the following keys are supported: machines, applications, relations, all". \
			format(type)
		return [False, message]


def get_all_relations(juju_status):
	relations = {}
	container = {}
	node = 1
	juju_status_relations = juju_status.relations
	for item in juju_status_relations:
		container['interface'] = item.interface
		container['Provider:Requirer'] = item.key
		node = ("relation-" + str(node))
		relations.update({node: [container.copy()]})
		node = +1
	return relations


async def run_command(args):
	process = await asyncio.create_subprocess_exec(
		*args,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)
	stdout, stderr = await process.communicate()
	return (stdout.decode("utf-8")).strip()


from juju.model import Model
import asyncio
from juju import loop
from juju.controller import Controller
from juju import loop



async def add_machine(SSH_USER, machine_ip, ssh_key_private="/home/nymphe/.ssh/id_rsa"):
	model = Model()
	await model.connect_current()
	
	cloud_type = model.info.provider_type
	await asyncio.sleep(10)
	juju_cmd = "".join(["ssh:", SSH_USER, "@", machine_ip, ":", ssh_key_private])
	juju_machine = await model.add_machine(juju_cmd)
	
	await model.disconnect()

if __name__ == '__main__':
	start_time = time.time()
	cloud_name = None
	model_name = None
	juju_key_val = "machines"
	data = loop.run(get_juju_status(juju_key_val, cloud_name, model_name))
	cmd_lxc_net_list = ["lxc", "network", "list", "--format", "json"]
	cmd_lxc_net_list_out = loop.run(run_command(cmd_lxc_net_list))

	cmd_lxc_net_list_out = json.loads(cmd_lxc_net_list_out)
	print("cmd_lxc_net_list_out={}".format(cmd_lxc_net_list_out))

	from netaddr import IPNetwork, IPAddress

	if IPAddress("192.168.0.1") in IPNetwork("192.168.0.0/24"):
		print("Ok!")

	ssh_key_public = "/home/nymphe/.ssh/id_rsa.pub"
	ssh_key_private = "/home/nymphe/.ssh/id_rsa"

	""" START: KVM TEST"""
	# """
	time_1 = time.time()
	mid_user_defined = "machine1"
	cmd_list_kvm = ["uvt-kvm", "list"]

	cmd_list_kvm_out = loop.run(run_command(cmd_list_kvm))
	cmd_list_kvm_out = str(cmd_list_kvm_out).split('\n')

	machine_ip = ""
	for current_machine in cmd_list_kvm_out:
		if mid_user_defined == current_machine:

			cmd_ip = ["uvt-kvm", "ip", mid_user_defined]
			cmd_ip_out = loop.run(run_command(cmd_ip))
			machine_ip = (str(cmd_ip_out).split('\n'))[0]
			break
	if machine_ip == "":
		os_series = "xenial"
		memory = 1024
		cpu = 1
		disc_size = 5
		SSH_PASSWORD = "linux"
		cmd_create_kvm = ["uvt-kvm", "create",
				  mid_user_defined,
				  "release={}".format(os_series),
				  "--memory", str(memory),
				  "--cpu", str(cpu),
				  "--disk", str(disc_size),
				  "--ssh-public-key-file", ssh_key_public,
				  "--password", SSH_PASSWORD
		]
		cmd_create_kvm_out = loop.run(run_command(cmd_create_kvm))

		cmd_wait_kvm = ["uvt-kvm", "wait", mid_user_defined]
		cmd_ip = ["uvt-kvm", "ip", mid_user_defined]

		cmd_wait_kvm_out = loop.run(run_command(cmd_wait_kvm))
		cmd_ip_out = loop.run(run_command(cmd_ip))
		machine_ip = (str(cmd_ip_out).split('\n'))[0]

	cmd_ssh_1 = ["ssh", "{}@{}".format("ubuntu", machine_ip), "echo", "export", "LC_CTYPE=en_US.UTF-8", ">>" "~.bashrc"]
	cmd_ssh_2 = ["ssh", "{}@{}".format("ubuntu", machine_ip), "echo", "export", "LC_ALL=en_US.UTF-8", ">>" "~.bashrc"]
	cmd_ssh_3 = ["ssh", "{}@{}".format("ubuntu", machine_ip), "source", ".bashrc"]

	cmd_ssh_4 = ["ssh", "{}@{}".format("ubuntu", machine_ip), "sudo", "apt-get", "update", "-y"]
	cmd_ssh_5 = ["ssh", "{}@{}".format("ubuntu", machine_ip), "sudo", "apt-get", "upgrade", "-y"]
	cmd_ssh_6 = ["ssh", "{}@{}".format("ubuntu", machine_ip), "sudo", "apt-get", "install",
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

	SSH_USER_kvm = "ubuntu"
	cmd_kvm_ssh_vm = ["ssh", "-o", "StrictHostKeyChecking={}".format("no"), "-i", ssh_key_private,
					  "{}@{}".format(SSH_USER_kvm, machine_ip), "pwd"]

	cmd_kvm_ssh_vm_out = loop.run(run_command(cmd_kvm_ssh_vm))

	cmd_ssh_1_out = loop.run(run_command(cmd_ssh_1))
	cmd_ssh_2_out = loop.run(run_command(cmd_ssh_2))
	cmd_ssh_3_out = loop.run(run_command(cmd_ssh_3))
	cmd_ssh_4_out = loop.run(run_command(cmd_ssh_4))
	cmd_ssh_5_out = loop.run(run_command(cmd_ssh_5))
	cmd_ssh_6_out = loop.run(run_command(cmd_ssh_6))

	loop.run(add_machine(SSH_USER_kvm, machine_ip))
	time_2 = time.time() - time_1
	print("total time to create kvm machine is {} minutes".format(float(time_2)/60))
	pass
	# """
	""" STOP: KVM TEST"""




	container_name = "c2"

	
	cmd_list_lxc = ["lxc", "list", "--format", "json"]
	# cmd_lxc_create = ["lxc", "launch", "ubuntu:16.04", container_name]
	# cmd_lxc_create = ["lxc", "launch", "juju/bionic/amd64", container_name]
	cmd_lxc_create = ["lxc", "launch", "juju/xenial/amd64", container_name]

	"""juju/xenial/amd64"""

	
	"""
	lxc file push ~/.ssh/id_rsa.pub nginx-test/root/.ssh/authorized_keys
	lxc exec -T c2 'chmod 777 /root/.ssh/authorized_keys && sudo chown root: /root/.ssh/authorized_keys'
	ssh root@10.87.183.245
	
	lxc exec c2 -- sh -c  'chmod 600 /root/.ssh/authorized_keys && sudo chown root: /root/.ssh/authorized_keys'
	"""
	
	
	
	cmd_lxc_inject_ssh_key = ["lxc", "file", "push", ssh_key_public, "{}/root/.ssh/authorized_keys".format(container_name)]
		
	cmd_lxc_chmod = ["lxc", "exec", container_name, "--", "sh", "-c",
                     str("chmod 600 /root/.ssh/authorized_keys && sudo chown root: /root/.ssh/authorized_keys")]
	
	
	
	""" juju add-machine ssh:root@10.99.104.141 """
	
	
	cmd_lxc_create_out = loop.run(run_command(cmd_lxc_create))
	print("cmd_lxc_create_out={}".format(cmd_lxc_create_out))
	
	# time.sleep(3)
	# get all ip global ipv4 address fro certain machine
	machine_ip_tmp = list()
	while len(machine_ip_tmp) == 0:
		cmd_list_lxc_out = loop.run(run_command(cmd_list_lxc))
		cmd_list_lxc_out = json.loads(cmd_list_lxc_out)
		for lxc_md in cmd_list_lxc_out:
			if lxc_md['name'] == container_name:
				for iface in lxc_md['state']['network']:
					for add_config in lxc_md['state']['network'][iface]['addresses']:
						if (add_config['family'] == 'inet') and (add_config['scope'] == 'global'):
							machine_ip_tmp.append(add_config['address'])
							print("ip addres v4=:{}".format(add_config['family']))
		
	# get list of valid IP (ip that can be pinged)
	machine_ip = list()
	for ip_add in machine_ip_tmp:
		packet_transmitted = 0
		packet_received = 0
		cmd_ping = ["ping", "-c", "3", ip_add]
		cmd_ping_out = loop.run(run_command(cmd_ping))
		lst = cmd_ping_out.split('\n')
		for i in range(2, len(lst)):
			if 'received' in str(lst[i]):
				items = (str(lst[i])).split(',')
				for item in items:
					if 'received' in str(item):
						item = [x for x in (str(item)).split(' ') if x]
						packet_received = int(item[0])
					if ('packets' in str(item)) and ('transmitted' in str(item)):
						item = [x for x in (str(item)).split(' ') if x]
						packet_transmitted = int(item[0])
						pass
				print(lst[i])
		if packet_received > 0:
			machine_ip.append(ip_add)
	#ssh -o "StrictHostKeyChecking no"
	SSH_USER = "root"
	machine_ip = machine_ip[0]

	cmd_lxc_ssh_vm = ["ssh", "-o", "StrictHostKeyChecking={}".format("no"), "-i", ssh_key_private, "{}@{}".format(SSH_USER, machine_ip), "pwd"]
	
	
	""" -o StrictHostKeyChecking=no ssh_key_private"""
	
	
	
	cmd_lxc_inject_ssh_key_out = loop.run(run_command(cmd_lxc_inject_ssh_key))
	# cmd_lxc_inject_ssh_key_out = json.loads(cmd_lxc_inject_ssh_key_out)
	
	cmd_lxc_chmod_out = loop.run(run_command(cmd_lxc_chmod))
	# cmd_lxc_chmod_out = json.loads(cmd_lxc_chmod_out)
	
	cmd_lxc_ssh_vm_out = loop.run(run_command(cmd_lxc_ssh_vm))
	
	# loop.run(add_machine(SSH_USER, machine_ip))
	
	print("START")
	cmd_juju_addmachine = ["juju", "add-machine", "ssh:{}@{}".format(SSH_USER, machine_ip)]
	
	
	print("add achine: {}".format(cmd_juju_addmachine))
	cmd_lxc_ssh_vm_out = loop.run(run_command(cmd_juju_addmachine))

	check_out_add_machine = cmd_lxc_ssh_vm_out.split('\n')
	cmd_to_execute = list()
	cmd_found = False
	for line in check_out_add_machine:
		if "Add correct host key in" in str(line):
			cmd_found = True
		if cmd_found and ("ssh-keygen -f" in str(line)):
			temp_val = str(line).split('-f')
			temp_val = str(temp_val[1]).split('-R')
			temp_val_1 = temp_val[0]
			temp_val_2 = temp_val[1]
			if ('\r') in temp_val_1:
				temp_val_1 = str(temp_val_1).split('\r')
				temp_val_1 = temp_val_1[0]
			if ('\r') in temp_val_2:
				temp_val_2 = str(temp_val_2).split('\r')
				temp_val_2 = temp_val_2[0]
			temp_val_1 = str(temp_val_1).split('"')
			temp_val_1 = temp_val_1[1]

			temp_val_2 = str(temp_val_2).split('"')
			temp_val_2 = temp_val_2[1]

			cmd_to_execute.append("ssh-keygen")
			cmd_to_execute.append("-f")
			cmd_to_execute.append(temp_val_1)
			cmd_to_execute.append("-R")
			cmd_to_execute.append(temp_val_2)


	if cmd_found:
		print("cmd_found: {}".format(cmd_to_execute))
		cmd_found_out = loop.run(run_command(cmd_to_execute))
		print("Try to add achine: {}".format(cmd_juju_addmachine))

		cmd_lxc_ssh_vm_out = loop.run(run_command(cmd_lxc_ssh_vm))
		print("Try cmd_lxc_ssh_vm: {}".format(cmd_lxc_ssh_vm_out))

		cmd_lxc_ssh_vm_out = loop.run(run_command(cmd_juju_addmachine))
	#'Add correct host key in /home/nymphe/.ssh/known_hosts to get rid of this message.
	#'  ssh-keygen -f "/home/nymphe/.ssh/known_hosts" -R "10.180.125.12"

	end_time = time.time() - start_time
	
	print("total time: {} minutes".format(float(end_time)/60))
	print("EXIT")
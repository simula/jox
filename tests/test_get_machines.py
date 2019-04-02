from juju.model import Model
from juju import loop
import logging
from juju import utils
logger = logging.getLogger('jox.jmodel')
import asyncio
from asyncio import subprocess

import ipaddress
iface = ipaddress.ip_interface('10.99.104.1/255.255.255.0')

domain = iface.exploded
print(iface)

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
if __name__ == '__main__':
	cloud_name = None
	model_name = None
	juju_key_val = "machines"
	data = loop.run(get_juju_status(juju_key_val, cloud_name, model_name))
	if data[0]:
		list_machine = data[1]
		for id in list_machine:
			machine = list_machine[id]
			
			
			hostname = None
			dns_name = machine['dns-name']
			# status_alive = machine['dns-name']
			# status_alive = machine['dns-name']
			
			
			set_interfaces = dict()
			for interface in machine['network-interfaces']:
				set_interfaces[interface] = {
					"ip-address": machine['network-interfaces'][interface]['ip-addresses'],
					"mac-address": machine['network-interfaces'][interface]['mac-address'],
					"is-up": machine['network-interfaces'][interface]['is-up'],
				}
				
			# memory
			# tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
			get_mem = ["free", "-t", "-m"]
			
			import psutil
			
			addrs = psutil.net_if_addrs()
			psutil.net_if_stats()
			print(addrs.keys())
			print(psutil.net_if_stats())
			psutil.cpu_stats()
			
			get_mac_address = ["ip", "addr", "show", "wlp2s0"]
			machine_name = "ubuntu"
			set_addresses = machine['ip-addresses']
			
			get_cpu_info = ["ssh", "{}@{}".format(machine_name, set_addresses[0]),
			                 "cat", "/proc/cpuinfo"]
			get_cpu_info_out = loop.run(run_command(get_cpu_info))
			get_cpu_info_out = get_cpu_info_out.split('\n')
			core_id = list()
			for item in get_cpu_info_out:
				if "core id" in str(item):
					item = [x for x in str(item).split(':') if x]
					if int(item[1]) not in core_id:
						core_id.append(int(item[1]))
			
			number_cpu = len(core_id)
			
			get_cpu_usage = ["ssh", "{}@{}".format(machine_name, set_addresses[0]),
			                 "grep", "'cpu '",
			                 "/proc/stat"]
			get_cpu_usage_out = loop.run(run_command(get_cpu_usage))
			#"|", "awk", "{usage=($2+$4)*100/($2+$4+$5)} END {print usage }"
			get_cpu_usage_out = get_cpu_usage_out.split('\n')
			
			cpu_val = [x for x in str(get_cpu_usage_out[0]).split(' ') if x]
			cpu_val.remove(cpu_val[0])
			cpu_val = [int(x) for x in cpu_val]
			cpu_usage =  (cpu_val[0]+cpu_val[2])*100/(cpu_val[0]+cpu_val[2]+cpu_val[3])
			
			get_cpu = ["ssh", "{}@{}".format(machine_name, set_addresses[0]), "lscpu"]
			cpu_out = loop.run(run_command(get_cpu))
			
			get_mem = ["ssh", "{}@{}".format(machine_name, set_addresses[0]), "free", "-t", "-m"]
			mem_out = loop.run(run_command(get_mem))
			mem_out = mem_out.split('\n')
			import json
			
			
			
			
			
			mem_tot = 0
			mem_used = 0
			mem_free = 0
			counter = 0
			for item in mem_out:
				tmp_val = str(item).split(' ')
				if tmp_val[0] == "Total:":
					for val in tmp_val:
						if val != "Total:" and val != "":
							if counter == 0:
								mem_tot = int(val)
								counter += 1
							elif counter == 1:
								mem_used = int(val)
								counter += 1
							elif counter == 2:
								mem_free = int(val)
								counter += 1
							else:
								pass
			
			cmd_check_lxc = ["ssh", "{}@{}".format(machine_name, set_addresses[0]), "lxc", "list"]
			cmd_check_lxc_out = loop.run(run_command(cmd_check_lxc))
			
			if ("error" in str(cmd_check_lxc_out)) or ("ERROR" in str(cmd_check_lxc_out)):
				lxc_support = False
			else:
				lxc_support = True
			cmd_check_kvm = ["ssh", "{}@{}".format(machine_name, set_addresses[0]), "uvt-kvm", "list"]
			cmd_check_kvm_out = loop.run(run_command(cmd_check_kvm))
			if ("error" in str(cmd_check_kvm_out)) or ("ERROR" in str(cmd_check_kvm_out)):
				kvm_support = False
			else:
				kvm_support = True
			import os
			os.terminal_size
			
			import psutil
			
			# gives a single float value
			number_cpus = psutil.cpu_count()
			percentage_use = psutil.cpu_percent()
			
			# gives an object with many fields
			psutil.virtual_memory()
			# you can convert that object to a dictionary
			dict(psutil.virtual_memory()._asdict())
			
		
			pass
	print(data)

#list all interfaces: ip -o link show | awk -F': ' '{print $2}'
#get ip addrress: ip addr show wlp2s0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1
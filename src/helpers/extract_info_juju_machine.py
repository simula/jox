import ipaddress
import asyncio
from asyncio import subprocess
from juju import loop
import json

class extract_info(object):
	def __init__(self, global_variables, juju_machine,  username="ubuntu", ssh_private_key=None, lxc_anchor="local"):
		self.juju_machine = juju_machine
		self.username = username
		self.ssh_private_key = ssh_private_key
		self.lxc_anchor = lxc_anchor
		self.gv = global_variables
	def extract_info_juju_machine(self):
		set_addresses = self.juju_machine['ip-addresses']
		ip_address = set_addresses[0]
		ip_address_final = ''
		for ip_addr in set_addresses:
			test_message = "testConnection"
			check_conn = ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no", "echo", test_message]
			[check_conn.insert(5, item) for item in self.ssh_format(ip_addr)]

			check_conn_out = loop.run(self._run_command(check_conn))
			check_conn_out = check_conn_out.split('\n')
			for item in check_conn_out:
				if item == test_message:
					# ip_address = ip_addr
					if ip_addr in self.juju_machine['instance-id']:
						ip_address_final = ip_addr
						break

		if ip_address_final != '':
			ip_address = ip_address_final
		sys_info = self.get_system_info(ip_address)
		sys_info = sys_info[1]
		if sys_info["virt_type"] is None:
			get_memory = self._phy_get_memory_info(ip_address)
			get_cpu = self._phy_get_cpu_info(ip_address)
			sys_info["virt_type"] = self.gv.PHY
		else:
			get_cpu = [0, 0, 0]
			get_memory = [0, 0, 0, 0]
		domain_all = dict()
		domain = self._phy_get_iface_info(ip_address)
		print("========================================ip_address:{} net_domain =: {}".format(ip_address, domain))
		domain_all[ip_address] = domain[1]
		
		machine_hw = [x for x in str(self.juju_machine['hardware']).split(' ') if x]

		machine_config = {
			"machine_name":"",
			"machine_available": True,
			"host":{
				"disk_size": None, #GB # related to virtual machines only
				"num_cpus": int((str(machine_hw[1]).split('='))[1]), # related to virtual machines only
				"mem_size": int((str((str(machine_hw[2]).split('='))[1]).split('M'))[0]), #MB # related to virtual machines only
				"cpu_number": get_cpu[1],
				"cpu_percent": get_cpu[2],
				"mem_total": get_memory[1],
				"mem_used": get_memory[2],
				"mem_free": get_memory[3],
			},
			"os":{
				"architecture": sys_info["architecture"],
				"type": sys_info["os_type"],
				"distribution": sys_info["os_distribution"],
				"version":  sys_info["os_version"],
			},
			"juju_id": "",
			"virt_type": sys_info["virt_type"],
			"dns_name": self.juju_machine['dns-name'],
			"domain": domain_all,
			"interfaces": self._get_interfaces_machine(self.juju_machine),
			"ip_addresses": ip_address,
		}
		return [True, machine_config]
	
	def get_system_info(self, ip_address):
		# lxc_info = self._lxc_get_info(ip_address)
		get_virt = ["ssh", "hostnamectl", "status"]
		[get_virt.insert(1, item) for item in self.ssh_format(ip_address)]
		
		get_virt_out = loop.run(self._run_command(get_virt))
		get_virt_out = get_virt_out.split('\n')
		system_info = {
			"os_distribution": "",
			"os_version": "",
			"os_type": "",
			"os_kernel_version": "",
			"architecture": "",
			"virt_type": None,
		}
		for item in get_virt_out:
			if "Operating System" in str(item):
				item = [x for x in str(item).split(':') if x]
				item.remove(item[0])
				item = [x for x in str(item[0]).split(" ") if x]
				system_info["os_distribution"] = item[0]
				system_info["os_version"] = item[1]
			if "Kernel" in str(item):
				item = [x for x in str(item).split(':') if x]
				item.remove(item[0])
				item = [x for x in str(item[0]).split(" ") if x]
				
				system_info["os_type"] = item[0]
				system_info["os_kernel_version"] = item[1]
			if "Architecture" in str(item):
				item = [x for x in str(item).split(':') if x]
				item.remove(item[0])
				item = [x for x in str(item[0]).split(" ") if x]
				
				system_info["architecture"] = item[0]
			if "Virtualization" in str(item):
				item = [x for x in str(item).split(':') if x]
				item.remove(item[0])
				item = [x for x in str(item[0]).split(" ") if x]
				
				system_info["virt_type"] = item[0]
		return [True, system_info]
	
	def _get_interfaces_machine(self, machine):
		set_interfaces = dict()
		for interface in machine['network-interfaces']:
			set_interfaces[interface] = {
				"ip-address": machine['network-interfaces'][interface]['ip-addresses'],
				"mac-address": machine['network-interfaces'][interface]['mac-address'],
				"is-up": machine['network-interfaces'][interface]['is-up'],
			}
		return set_interfaces
	
	def _phy_get_iface_info(self, ip_address):
		get_list_iface = ["ssh", "ls", "/sys/class/net"]
		[get_list_iface.insert(1, item) for item in self.ssh_format(ip_address)]
		
		get_list_iface_out = loop.run(self._run_command(get_list_iface))
		get_list_iface_out = get_list_iface_out.split('\n')
		for iface in get_list_iface_out:
			if self.ssh_private_key is None:
				get_iface = ["ssh", "{}@{}".format(self.username, ip_address), "ifconfig", iface]
			else:
				get_iface = ["ssh", "-i", self.ssh_private_key, "{}@{}".format(self.username, ip_address), "ifconfig", iface]
			get_iface_out = loop.run(self._run_command(get_iface))
			get_iface_out = get_iface_out.split('\n')
			for item in get_iface_out:
				if "inet" in str(item):
					item = [x for x in str(item).split(" ") if x]
					ip_add = item[1]
					if ip_address in ip_add:
						netmask = item[3]
						if ":" in str(ip_add):
							ip_add = str(ip_add).split(":")
							ip_add = ip_add[1]

							netmask = str(netmask).split(":")
							netmask = netmask[1]
						iface = ipaddress.ip_interface('{}/{}'.format(ip_add, netmask))
						domain = iface.network.compressed
						##print("========================================domain={}".format(iface.network))
						return [True, domain]
			"""ip addr show wlp2s0"""
		return [False, None]
	
	def _phy_get_cpu_info(self, ip_address):
		get_cpu_percent = ["ssh", "grep", "'cpu '", "/proc/stat"]
		[get_cpu_percent.insert(1, item) for item in self.ssh_format(ip_address)]
		
		get_cpu_usage_out = loop.run(self._run_command(get_cpu_percent))
		get_cpu_usage_out = get_cpu_usage_out.split('\n')
		
		cpu_val = [x for x in str(get_cpu_usage_out[0]).split(' ') if x]
		cpu_val.remove(cpu_val[0])
		cpu_val = [int(x) for x in cpu_val]
		cpu_usage = (cpu_val[0] + cpu_val[2]) * 100 / (cpu_val[0] + cpu_val[2] + cpu_val[3])
		
		if self.ssh_private_key is None:
			get_cpu_info = ["ssh", "{}@{}".format(self.username, ip_address), "cat", "/proc/cpuinfo"]
		else:
			get_cpu_info = ["ssh", "-i", self.ssh_private_key, "{}@{}".format(self.username, ip_address), "cat", "/proc/cpuinfo"]
		get_cpu_info_out = loop.run(self._run_command(get_cpu_info))
		get_cpu_info_out = get_cpu_info_out.split('\n')
		core_id = list()
		for item in get_cpu_info_out:
			if "core id" in str(item):
				item = [x for x in str(item).split(':') if x]
				if int(item[1]) not in core_id:
					core_id.append(int(item[1]))
		
		cpu_number = len(core_id)
		return [True, cpu_number, cpu_usage]
	
	def _lxc_get_info(self, lxc_machine_ip):
		"""lxc list --format json"""
		get_lxc_list = ["lxc", "list", "{}:".format(self.lxc_anchor), "--format", "json"]
		get_lxc_list_out = loop.run(self._run_command(get_lxc_list))
		get_lxc_list_out = json.loads(get_lxc_list_out)
		machine_config = None
		for item in get_lxc_list_out:
			for iface in item['state']['network']:
				for addr in item['state']['network'][iface]['addresses']:
					if addr['address'] == lxc_machine_ip:
						machine_config = item
						return [True, addr['netmask']]
		return [True, None]
	
	def _phy_get_memory_info(self, ip_address):
		get_mem = ["ssh", "free", "-t", "-m"]
		[get_mem.insert(1, item) for item in self.ssh_format(ip_address)]
		
		mem_out = loop.run(self._run_command(get_mem))
		mem_out = mem_out.split('\n')
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
		return [True, mem_tot, mem_used, mem_free]
	
	async def _run_command(self, args):
		process = await asyncio.create_subprocess_exec(
			*args,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT)
		stdout, stderr = await process.communicate()
		return (stdout.decode("utf-8")).strip()
	def ssh_format(self, ip_address):
		if self.ssh_private_key is None:
			return ["{}@{}".format(self.username, ip_address)]
		else:
			return ["{}@{}".format(self.username, ip_address), self.ssh_private_key, "-i"]
#!/usr/bin/env python3
"""
 * Copyright 2016-2019 Eurecom and Mosaic5G Platforms Authors
 * Licensed to the Mosaic5G under one or more contributor license
 * agreements. See the NOTICE file distributed with this
 * work for additional information regarding copyright ownership.
 * The Mosaic5G licenses this file to You under the
 * Apache License, Version 2.0  (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the Mosaic5G:
 *      contact@mosaic5g.io
 """
__author__ = 'Eurecom'
__date__ = "11-January-2019"
__version__ = '1.0'
__maintainer__ = 'Osama Arouk, Navid Nikaein, Kostas Kastalis, and Rohan Kharade'
__email__ = 'contact@mosaic5g.io'
__description__ = "Define the list of driver that are supported by JOX." \
                  "The supported VIM drivers are:" \
                  "- LXC" \
                  "- KVM"

import os, time, sys
import pika, uuid, json

import logging
from juju.model import Model
from juju import loop, utils
import traceback
import jsonpickle, json
import asyncio
from asyncio import subprocess
import datetime
dir_path = os.path.dirname(os.path.abspath(__file__ + "/../../../"))
from src.core.nso.template_manager import template_manager
from src.common.config import gv as global_varialbles

from netaddr import IPNetwork, IPAddress

#
class LxcDriver(object):
	def __init__(self, pop_config, global_variable, jesearch):
		self.driver_name = pop_config["pop-name"]
		self.lxc_anchor = pop_config["lxc-anchor"]
		self.zone = pop_config["zone"]
		self.domain = pop_config["domain"]
		self.scope = pop_config["scope"]
		self.driver_ssh_private_key = pop_config["ssh-private-key"]
		self.driver_ssh_username = pop_config["ssh-user"]
		self.driver_ssh_password = pop_config["ssh-password"]
		self.managed_by = pop_config["managed-by"]
		self.prebuilt_image = pop_config["prebuilt-image"]
		self.gv = global_variable
		self.jesearch = jesearch
		
		self.machine_list = list()
		
		self.max_retry = self.gv.JUJU_MAX_RETRY_CONNECTION_MODEL_ACCESSIBLE # number of tentative to connect to juju. every tentative is after one second
		self.interval_access = self.gv.JUJU_INTERVAL_CONNECTION_MODEL_ACCESSIBLE
		self.logger = logging.getLogger('jox.LxcDriver.{}'.format(self.driver_name))
		self.log_config()
		self.template_manager = template_manager.TemplateManager(global_variable, jesearch)
		
	def log_config(self):
		if self.gv.LOG_LEVEL == 'debug':
			self.logger.setLevel(logging.DEBUG)
		elif self.gv.LOG_LEVEL == 'info':
			self.logger.setLevel(logging.INFO)
		elif self.gv.LOG_LEVEL == 'warn':
			self.logger.setLevel(logging.WARNING)
		elif self.gv.LOG_LEVEL == 'error':
			self.logger.setLevel(logging.ERROR)
		elif self.gv.LOG_LEVEL == 'critic':
			self.logger.setLevel(logging.CRITICAL)
		else:
			self.logger.setLevel(logging.INFO)
	def check_machine_exist(self, cloud_name, model_name, machine_config):
		if "ip_addresses" in machine_config.keys():
			entity = 'ip_addresses'
		else:
			entity = 'ip'
		for machine in self.machine_list:
			if type(machine.ip) is str:
				if (machine.ip == machine_config[entity]) or (machine.ip in machine_config[entity]):
					return True
			else:
				for ip_addr in machine.ip:
					if (ip_addr == machine_config['ip_addresses']) or (ip_addr in machine_config[entity]):
						return True
				return True
		return False
	def get_machines_status(self):
		"""
		:return:
		"""
		data_str = jsonpickle.encode(self.machine_list)  # returns str
		data = json.loads(data_str)
		return data
	
	def get_machine_status(self, model_machine_name):
		for machine in self.machine_list:
			if machine.model_machine_name == model_machine_name:
				data_str = jsonpickle.encode(machine)  # returns str
				data = json.loads(data_str)
				return data
	
	def get_machine_object(self, model_machine_name):
		for machine in self.machine_list:
			if machine.model_machine_name == model_machine_name:
				return machine
	
	def get_mid_juju_from_mid_jmodel(self, mid_user_defined, machine_type):
		for vm in self.machine_list:
			if vm.mid_user_defined == mid_user_defined:
				return vm.mid_vnfm
		return -1
	def machine_exists(self, mid_user_defined):
		try:
			for vm in self.machine_list:
				if vm.mid_user_defined == mid_user_defined:
					return True
			return False
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			# raise ex
			return False
	def remove_machine_object(self, mid_user_defined):
		try:
			for mch in self.machine_list:
				if mch.mid_user_defined == mid_user_defined:
					self.machine_list.remove(mch)
			return False
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			return False
	
	def add_machine(self, machine_config, service_name, mid_ro, slice_name, model_name, cloud_name, nsi_id, machine_id_service=None):
		try:
			new_machine = _VmLxc()
			new_machine.build(slice_name,
			                  cloud_name,
			                  model_name,
			                  mid_ro,
			                  machine_config)
			add_new_context_machine = loop.run(self.deploy_machine(new_machine, service_name, slice_name, nsi_id, "admin", machine_id_service))

			machine_exist = False
			for machine in self.machine_list:
				if machine.mid_vnfm == new_machine.mid_vnfm:
					machine_exist = True
			if add_new_context_machine or (not machine_exist):
				self.machine_list.append(new_machine)
			self.allocate_machine(new_machine, service_name, mid_ro, machine_config['machine_name'])


		except Exception as ex:
			raise ex

	async def get_deployed_applications(self, machine_id_service, service_name, c_name, m_name, user="admin"):
		model = Model()

		add_new_context_machine = True
		if machine_id_service is not None:
			add_new_context_machine = False

		application_NotExist = None
		try:
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
																							   model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)

			app_keys = model.applications.keys()
			application_NotExist = True
			#
			provider_type = model.info.provider_type
			for app in app_keys:
				if service_name == app and len(model.applications[app].units) > 0:
					application_NotExist = False
					app_values = model.applications.get(app)
					machine_id_service = app_values.units[0].machine.id
					add_new_context_machine = False
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
		return [machine_id_service, application_NotExist, add_new_context_machine, provider_type]

	async def get_juju_machine(self, machine_id_service, c_name, m_name, user="admin"):
		model = Model()
		try:
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
																							   model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)
			juju_machine = model.machines.get(machine_id_service)
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
		return juju_machine

	async def deploy_machine(self, new_machine, service_name, slice_name, nsi_id, user="admin", machine_id_service=None):
		model = Model()

		add_new_context_machine = True
		if machine_id_service is not None:
			add_new_context_machine = False
		try:
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
																							   model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)

			app_keys = model.applications.keys()
			application_NotExist = True
			#
			provider_type = model.info.provider_type
			for app in app_keys:
				if service_name == app and len(model.applications[app].units) > 0:
					application_NotExist = False
					app_values = model.applications.get(app)
					machine_id_service = app_values.units[0].machine.id
					add_new_context_machine = False
			if application_NotExist and machine_id_service is None:
				if provider_type == "lxd":
					if new_machine.auto:
						juju_machine = await model.add_machine()
					else:
						juju_machine = await model.add_machine(
							constraints={
								'mem': int(new_machine.memory) * self.gv.GB,
								'tags': [new_machine.mid_user_defined],
							},
							disks=[{
								'pool': 'rootfs',
								'size': int(new_machine.disc_size) * self.gv.GB,
								'count': 1,
							}],
							series=new_machine.os_series,
						)
				else:
					cmd_list_lxc = ["lxc", "list", "{}:".format(self.lxc_anchor), "--format", "json"]
					cmd_list_lxc_out = await run_command(cmd_list_lxc)
					cmd_list_lxc_out = json.loads(cmd_list_lxc_out)
					machine_name_exist = True

					tmp_counter = 0
					machine_lxd_name = "machine-{}".format(service_name)
					machine_lxd_name_tmp = machine_lxd_name
					while machine_name_exist:
						machine_name_exist_tmp = False
						for lxc_md in cmd_list_lxc_out:
							if lxc_md['name'] == machine_lxd_name_tmp:
								machine_name_exist_tmp = True
						if machine_name_exist_tmp:
							tmp_counter += 1
							machine_lxd_name_tmp = "{}-{}".format(machine_lxd_name, tmp_counter)
						else:
							machine_name_exist = False
							machine_lxd_name = machine_lxd_name_tmp

					container_name = machine_lxd_name
					isPrebuiltImage = False

					cmd_lxc_create = ["lxc", "launch", "ubuntu:{}".format(new_machine.os_version),
									  "{}:{}".format(self.lxc_anchor, container_name)]
					#"""

					machine_series = self.gv.OS_SERIES[new_machine.os_version]
					prebuilt_image = self.prebuilt_image[machine_series]
					cmd_lxc_create = ["lxc", "launch", "{}:{}".format(self.lxc_anchor, prebuilt_image), "{}:{}".format(self.lxc_anchor, container_name)]
					cmd_lxc_create_out = await run_command(cmd_lxc_create)
					if 'error' in str(cmd_lxc_create_out).lower() and 'not' in str(cmd_lxc_create_out).lower() and 'found' in str(cmd_lxc_create_out).lower():
						cmd_lxc_create = ["lxc", "launch", "ubuntu:{}".format(new_machine.os_version), "{}:{}".format(self.lxc_anchor, container_name)]
						cmd_lxc_create_out = await run_command(cmd_lxc_create)
					else:
						isPrebuiltImage = False

					self.logger.info(cmd_lxc_create_out)
					""" Get the ip addresss of the machine"""
					machine_ip_tmp = list()
					while len(machine_ip_tmp) == 0:
						cmd_list_lxc_out = await run_command(cmd_list_lxc)
						cmd_list_lxc_out = json.loads(cmd_list_lxc_out)
						for lxc_md in cmd_list_lxc_out:
							if lxc_md['name'] == container_name:
								for iface in lxc_md['state']['network']:
									for add_config in lxc_md['state']['network'][iface]['addresses']:
										if (add_config['family'] == 'inet') and (add_config['scope'] == 'global'):
											machine_ip_tmp.append(add_config['address'])
											self.logger.info("ip addres v4=:{}".format(add_config['family']))
					machine_ip = list()
					for ip_add in machine_ip_tmp:
						packet_transmitted = 0
						packet_received = 0
						cmd_ping = ["ping", "-c", "3", ip_add]
						cmd_ping_out = await run_command(cmd_ping)
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
								# print(lst[i])
						if packet_received > 0:
							machine_ip.append(ip_add)
					###########
					SSH_USER_lxd = "root"
					ssh_key_puplic = ''.join([self.gv.SSH_KEY_DIRECTORY, self.gv.SSH_KEY_NAME, '.pub'])
					ssh_key_private = ''.join([self.gv.SSH_KEY_DIRECTORY, self.gv.SSH_KEY_NAME])

					machine_ip = machine_ip[0]

					message = "Injecting the public key in the lxd machine"
					self.logger.info(message)
					cmd_lxc_inject_ssh_key = ["lxc", "file", "push", ssh_key_puplic,
											  "{}:{}/root/.ssh/authorized_keys".format(self.lxc_anchor, container_name)]
					cmd_lxc_inject_ssh_key_out = await run_command(cmd_lxc_inject_ssh_key)

					message = "Injecting the public key in the lxd machine"
					self.logger.info(message)
					cmd_lxc_chmod = ["lxc", "exec", "{}:{}".format(self.lxc_anchor, container_name), "--", "sh", "-c",
									 str(
										 "chmod 600 /root/.ssh/authorized_keys && sudo chown root: /root/.ssh/authorized_keys")]
					cmd_lxc_chmod_out = await run_command(cmd_lxc_chmod)

					message = "Ensuring ssh to the machine {}".format(machine_ip)
					self.logger.info(message)
					cmd_lxc_ssh_vm = ["ssh", "-o", "StrictHostKeyChecking={}".format("no"), "-i", ssh_key_private,
									  "{}@{}".format(SSH_USER_lxd, machine_ip), "pwd"]
					cmd_lxc_ssh_vm_out = await run_command(cmd_lxc_ssh_vm)

					if not isPrebuiltImage:
						await machine_configuration_for_jujuCharm(SSH_USER_lxd, machine_ip, ssh_key_private, self.logger)

					cmd_juju_addmachine = ["juju", "add-machine", "ssh:{}@{}".format(SSH_USER_lxd, machine_ip)]

					self.logger.info("add machine: {}".format(cmd_juju_addmachine))
					cmd_lxc_ssh_vm_out = await run_command(cmd_juju_addmachine)
					machineId = str(cmd_lxc_ssh_vm_out).split('\n')

					cmd_to_execute = list()
					cmd_found = False
					for item in machineId:
						if "created machine" in item:
							val_id = [x for x in str(item).split(' ') if x]
							machine_id_service = val_id[2]
						##########
						if "Add correct host key in" in str(item):
							cmd_found = True
						if cmd_found and ("ssh-keygen -f" in str(item)):
							temp_val = str(item).split('-f')
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

							try:
								temp_val_2 = str(temp_val_2).split('"')
								temp_val_2 = temp_val_2[1]
							except:
								temp_val_2 = temp_val_2[0]
							cmd_to_execute.append("ssh-keygen")
							cmd_to_execute.append("-f")
							cmd_to_execute.append(temp_val_1)
							cmd_to_execute.append("-R")
							cmd_to_execute.append(temp_val_2)
					if cmd_found:
						self.logger.info("cmd_found: {}".format(cmd_to_execute))
						cmd_found_out = await run_command(cmd_to_execute)
						self.logger.info("Try to add achine: {}".format(cmd_juju_addmachine))

						cmd_lxc_ssh_vm_out = await run_command(cmd_lxc_ssh_vm)
						self.logger.info("Try cmd_lxc_ssh_vm: {}".format(cmd_lxc_ssh_vm_out))

						#
						cmd_fix_issues = ["sudo", "apt", "update", "--fix-missing"]
						cmd_fix_issues_out = await run_command(cmd_fix_issues)

						cmd_lxc_ssh_vm_out = await run_command(cmd_juju_addmachine)
						machineId = str(cmd_lxc_ssh_vm_out).split('\n')
						for item in machineId:
							if "created machine" in item:
								val_id = [x for x in str(item).split(' ') if x]
								machine_id_service = val_id[2]

					machine_id_found = False
					while not machine_id_found:
						juju_machine = await self.get_juju_machine(machine_id_service, new_machine.juju_cloud_name,
												  new_machine.juju_model_name)
						try:
							new_machine.mid_vnfm = juju_machine.data["id"]  # Note here Machine ID
							machine_id_found = True
						except:
							await asyncio.sleep(self.interval_access)
			else:
				juju_machine = model.machines.get(machine_id_service)
				self.logger.info(
					"The application {} is already deployed, and thus no machine added".format(service_name))
			new_machine.mid_vnfm = juju_machine.data["id"]  # Note here Machine ID

			cmd_machin_config = ["juju", "show-machine", new_machine.mid_vnfm, "--format", "json"]

			ip_address_notFound = True
			while ip_address_notFound:
				try:
					cmd_machin_config_out = await run_command(cmd_machin_config)
					cmd_machin_config_out = json.loads(cmd_machin_config_out)
					new_machine.ip = cmd_machin_config_out['machines'][new_machine.mid_vnfm]['ip-addresses']
					ip_address_notFound  = False
				except:
					pass


			self.logger.info("The machine {} is added and its juju id is {}".format(new_machine.mid_user_defined,
																					new_machine.mid_vnfm))
			machine_id = new_machine.mid_vnfm

			container_data = {"juju_mid": str(machine_id), "type": self.gv.LXC}
			self.template_manager.update_slice_monitor_index("subslice_monitor_" + slice_name.lower(),
															 "machine_status",
															 service_name,
															 container_data,
															 nsi_id)

			container_data = {"juju_mid": str(machine_id)}
			self.template_manager.update_slice_monitor_index('slice_keys_' + nsi_id.lower(),
															 "machine_keys",
															 service_name,
															 container_data,
															 nsi_id)

			self.logger.info(
				"Deployed LXC Machine {} {} {}".format(new_machine.mid_vnfm, len(juju_machine.data), juju_machine.data))

		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()

		return add_new_context_machine
	async def update_machine(self, machine_config):
		for machine in self.machine_list:
			if machine_config['machine_name'] == machine.mid_user_defined:
				new_machine = machine
		try:
			model = Model()
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			m_user = 'admin'
			model_name = c_name + ":" + m_user + '/' + m_name
			await model.connect(model_name)
			
			#######################
			_id = new_machine.mid_vnfm
			machine_ready = False
			while not machine_ready:
				await model.disconnect()
				await asyncio.sleep(1)
				
				await model.connect(model_name)
				
				if model.machines[str(_id)].data["agent-status"]["current"] == "started":
					if model.machines[str(_id)].data["addresses"]:
						new_machine.mid_vim = model.machines[str(_id)].data["instance-id"]
						self.logger.debug("mid_lxc of the new container is %s", new_machine.mid_vim)
						
						addresses = model.machines[str(_id)].data["addresses"]
						for address in addresses:
							if address["type"] == "ipv4": # and address["scope"] == "local-cloud":
								ip = address["value"]
								new_machine.ip = ip
								self.logger.debug("ip of the new container is {}".format(ip))
								machine_ready = True
						if not machine_ready:
							self.logger.critical("No ip address found for the machine {}".format(new_machine.mid_user_defined))
							self.logger.info("No ip address found for the machine {}".format(new_machine.mid_user_defined))
							machine_ready = True
		except Exception as ex:
			raise ex
		
		finally:
			await model.disconnect()
	async def delete_machine(self, service_name, machine_name_vnfm, machine_id_ro, machine_name_userdefined,
	                         jcloud, jmodel,
	                         slice_name, subslice_name=None, user="admin"):
		model = Model()
		try:
			c_name = jcloud
			m_name = jmodel
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
						                                                                       model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)

			
			try:
				await model.machines[str(machine_name_vnfm)].destroy(force=True)
			except:
				self.logger.critical("Either the application does not exist it can not be removed")
			self.logger.info("Remove the machine {} hosting the application {}".format(machine_name_vnfm, service_name))
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
	def register_machine_juju(self, cloud_name,
								model_name,
								mid_ro,
								machine_config):
		try:
			new_machine = _VmLxc()
			new_machine.register(cloud_name,
						          model_name,
						          mid_ro,
						          machine_config)
			self.machine_list.append(new_machine)
		
		except Exception as ex:
			raise ex
	def allocate_machine(self, new_machine, service_name, mid_ro, machine_name):
		for machine_current in self.machine_list:
			if new_machine.mid_vnfm == machine_current.mid_vnfm:
				machine_current.available = False
				machine_current.tmp_service_name = service_name
				machine_current.tmp_mid_ro = mid_ro
				machine_current.mid_user_defined = machine_name
				machine_current.ip = new_machine.ip

				break
	def release_machine(self):
		raise NotImplementedError()
	def get_stats(self):
		raise NotImplementedError()
	def validate(self):
		raise NotImplementedError()

	def gt(self, dt_str):
		try:
			dt, _, us = dt_str.partition(".")
			dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
			us = int(us.rstrip("Z"), 10) / 1000
			return dt + datetime.timedelta(microseconds=us)
		except Exception as ex:
			raise ex


class KvmDriver(object):
	def __init__(self, pop_config, global_variable, jesearch):
		self.driver_name = pop_config["pop-name"]
		self.zone = pop_config["zone"]
		self.domain = pop_config["domain"]
		self.scope = pop_config["scope"]
		self.driver_ssh_private_key = pop_config["ssh-private-key"]
		self.driver_ssh_username = pop_config["ssh-user"]
		self.driver_ssh_password = pop_config["ssh-password"]
		self.managed_by = pop_config["managed-by"]
		self.jesearch = jesearch

		self.gv = global_variable
		self.machine_list = list()
		self.logger = logging.getLogger('jox.KvmDriver.{}'.format(self.driver_name))
		self.max_retry = self.gv.JUJU_MAX_RETRY_CONNECTION_MODEL_ACCESSIBLE
		self.interval_access = self.gv.JUJU_INTERVAL_CONNECTION_MODEL_ACCESSIBLE
		self.template_manager = template_manager.TemplateManager(global_variable, jesearch)

	def check_machine_exist(self, cloud_name, model_name, machine_config):
		if "ip_addresses" in machine_config.keys():
			entity = 'ip_addresses'
		else:
			entity = 'ip'
		for machine in self.machine_list:
			if type(machine.ip) is str:
				if (machine.ip == machine_config[entity]) or (machine.ip in machine_config[entity]):
					return True
			else:
				for ip_addr in machine.ip:
					if (ip_addr == machine_config['ip_addresses']) or (ip_addr in machine_config[entity]):
						return True
		return False
	def get_machines_status(self):
		data_str = jsonpickle.encode(self.machine_list)
		data = json.loads(data_str)
		return data
	def get_machine_status(self, model_machine_name):
		for machine in self.machine_list:
			if machine.model_machine_name == model_machine_name:
				data_str = jsonpickle.encode(machine)
				data = json.loads(data_str)
				return data
	
	def get_machine_object(self, model_machine_name):
		for machine in self.machine_list:
			if machine.model_machine_name == model_machine_name:
				return machine
	
	def get_mid_juju_from_mid_jmodel(self, mid_user_defined, machine_type):
		for vm in self.machine_list:
			if vm.mid_user_defined == mid_user_defined:
				return vm.mid_vnfm
		return -1
	
	def machine_exists(self, mid_user_defined):
		try:
			for vm in self.machine_list:
				if vm.mid_user_defined == mid_user_defined:
					return True
			return False
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
	
	def add_machine(self, machine_config, service_name, mid_ro, subslice_name, model_name, cloud_name, nsi_id, machine_id_service=None):
		try:
			new_machine = _VmKvm()

			new_machine.build(subslice_name,
			                  cloud_name,
			                  model_name,
			                  mid_ro,
			                  machine_config)
			add_new_context_machine = loop.run(self.deploy_kvm(new_machine, service_name, subslice_name, nsi_id, "admin", machine_id_service))

			machine_exist = False
			for machine in self.machine_list:
				if machine.mid_vnfm == new_machine.mid_vnfm:
					machine_exist = True
			if add_new_context_machine or (not machine_exist):
				self.machine_list.append(new_machine)
			self.allocate_machine(new_machine, service_name, mid_ro, machine_config['machine_name'])
		except Exception as ex:
			raise ex

	async def deploy_kvm(self, new_machine, service_name, subslice_name, nsi_id, m_user="admin", machine_id_service=None):
		model = Model()

		add_new_context_machine = True
		if machine_id_service is not None:
			add_new_context_machine = False
		try:
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			model_name = c_name + ":" + m_user + '/' + m_name

			number_retry = 0
			retry_connect = True
			while number_retry <= self.max_retry and retry_connect:
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
																							   model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)

			app_keys = model.applications.keys()
			application_NotExist = True
			for app in app_keys:
				if service_name == app and len(model.applications[app].units) > 0:
					application_NotExist = False
					app_values = model.applications.get(app)
					machine_id_service = app_values.units[0].machine.id
					add_new_context_machine = False
			if application_NotExist and machine_id_service is None:
				ssh_key_puplic = ''.join([self.gv.SSH_KEY_DIRECTORY, self.gv.SSH_KEY_NAME, '.pub'])
				ssh_key_private = ''.join([self.gv.SSH_KEY_DIRECTORY, self.gv.SSH_KEY_NAME])
				################
				cmd_list_kvm = ["uvt-kvm", "list"]
				cmd_list_kvm_out = await run_command(cmd_list_kvm)
				cmd_list_kvm_out = str(cmd_list_kvm_out).split('\n')

				####################################
				tmp_counter = 0
				machine_kvm_name = "machine-{}".format(service_name)
				machine_kvm_name_tmp = machine_kvm_name
				machine_name_exist = True
				while machine_name_exist:
					machine_name_exist_tmp = False
					for kvm_md in cmd_list_kvm_out:
						if kvm_md == machine_kvm_name_tmp:
							machine_name_exist_tmp = True
					if machine_name_exist_tmp:
						tmp_counter += 1
						machine_kvm_name_tmp = "{}-{}".format(machine_kvm_name, tmp_counter)
					else:
						machine_name_exist = False
						machine_kvm_name = machine_kvm_name_tmp

				new_machine.mid_vim = machine_kvm_name
				#####################################
				machine_ip = ""
				if machine_ip == "":
					cmd_create_kvm = ["uvt-kvm", "create",
									  new_machine.mid_vim,
									  "release={}".format(new_machine.os_series),
									  "--memory", str(new_machine.memory),
									  "--cpu", str(new_machine.cpu),
									  "--disk", str(new_machine.disc_size),
									  "--ssh-public-key-file", ssh_key_puplic,
									  "--password", self.gv.SSH_PASSWORD
									  ]
					cmd_create_kvm_out = await run_command(cmd_create_kvm)

					cmd_wait_kvm = ["uvt-kvm", "wait", new_machine.mid_vim]
					cmd_ip = ["uvt-kvm", "ip", new_machine.mid_vim]

					cmd_wait_kvm_out = await run_command(cmd_wait_kvm)
					cmd_ip_out = await run_command(cmd_ip)
					machine_ip = (str(cmd_ip_out).split('\n'))[0]

				self.logger.debug(
					"The ip address of the machine {} is {}".format(new_machine.mid_user_defined, machine_ip))
				self.logger.info(
					'Adding the kvm machine {} whose ip {} to juju'.format(new_machine.mid_user_defined, machine_ip))
				try:
					ip = IPAddress(machine_ip) # To verify that we get the right ip address of the machine
					await machine_configuration_for_jujuCharm(self.gv.SSH_USER, machine_ip, ssh_key_private, self.logger)
					await asyncio.sleep(10)
					juju_cmd = "".join(["ssh:", self.gv.SSH_USER, "@", machine_ip, ":", ssh_key_private])

					juju_machine = await model.add_machine(juju_cmd)
				except Exception as ex:
					message = "There is error in the ip address of the machine, and thus the machine can not be addedd to juju model"
					self.logger.error(message)
					raise ex


			else:
				juju_machine = model.machines.get(machine_id_service)
			try:
				new_machine.mid_vnfm = juju_machine.data["id"]

				#############
				cmd_machin_config = ["juju", "show-machine", new_machine.mid_vnfm, "--format", "json"]

				cmd_machin_config_out = await run_command(cmd_machin_config)
				cmd_machin_config_out = json.loads(cmd_machin_config_out)
				new_machine.ip = cmd_machin_config_out['machines'][new_machine.mid_vnfm]['ip-addresses']

				machine_id = new_machine.mid_vnfm
				container_data = {"juju_mid": str(machine_id), "type": self.gv.KVM}
				self.template_manager.update_slice_monitor_index("subslice_monitor_" + subslice_name.lower(),
																 "machine_status",
																 service_name,
																 container_data,
																 nsi_id)

				container_data = {"juju_mid": str(machine_id)}
				self.template_manager.update_slice_monitor_index('slice_keys_' + nsi_id.lower(),
																 "machine_keys",
																 service_name,
																 container_data,
																 nsi_id)

				###################################################################################################
				self.logger.debug(
					"The machine {} with juju id {} is already added to juju model".format(new_machine.mid_user_defined,
																						   juju_machine.data["id"]))
			except:
				message = "Error while trying to add machine to the service {}".format(service_name)
				self.logger.error(message)
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
		return add_new_context_machine

	async def update_machine(self, machine_config):
		for machine in self.machine_list:
			if machine_config['machine_name'] == machine.mid_user_defined:
				new_machine = machine
		try:
			model = Model()
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			m_user = 'admin'
			model_name = c_name + ":" + m_user + '/' + m_name
			await model.connect(model_name)
			
			#######################
			_id = new_machine.mid_vnfm
			machine_ready = False
			while not machine_ready:
				await model.disconnect()
				await asyncio.sleep(1)
				
				await model.connect(model_name)
				
				if model.machines[str(_id)].data["agent-status"]["current"] == "started":
					if model.machines[str(_id)].data["addresses"]:
						new_machine.mid_vim = model.machines[str(_id)].data["instance-id"]
						self.logger.debug("mid_lxc of the new container is %s", new_machine.mid_vim)
						
						addresses = model.machines[str(_id)].data["addresses"]
						for address in addresses:
							if address["type"] == "ipv4": # and address["scope"] == "local-cloud":
								ip = address["value"]
								new_machine.ip = ip
								self.logger.debug("ip of the new container is {}".format(ip))
								machine_ready = True
						if not machine_ready:
							self.logger.info("No ip address found for the machine {}".format(new_machine.mid_user_defined))
							machine_ready = True
		except Exception as ex:
			raise ex
		
		finally:
			await model.disconnect()
	
	async def delete_machine(self, service_name, machine_name_vnfm, machine_id_ro, machine_name_userdefined,
	                         jcloud, jmodel,
	                         slice_name, subslice_name=None, user="admin"):
		model = Model()
		try:
			c_name = jcloud
			m_name = jmodel
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
						                                                                       model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)
			
			try:
				await model.machines[str(machine_name_vnfm)].destroy(force=True)
				cmd_destroy_kvm = ["uvt-kvm", "destroy", machine_name_userdefined]
				output_list = await run_command(*cmd_destroy_kvm)
			except:
				self.logger.critical("Either the application does not exist it can not be removed")
			self.logger.info("Remove the machine {} hosting the application {}".format(machine_name_vnfm, service_name))
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
	def register_machine_juju(self, cloud_name,
								model_name,
								mid_ro,
								machine_config):
		try:
			new_machine = _VmKvm()
			new_machine.register(cloud_name,
								 model_name,
								 mid_ro,
								 machine_config)
			self.machine_list.append(new_machine)
		except Exception as ex:
			raise ex

	def allocate_machine(self, new_machine, service_name, mid_ro, machine_name):
		for machine_current in self.machine_list:
			if new_machine.mid_vnfm == machine_current.mid_vnfm:
				machine_current.available = False
				machine_current.tmp_service_name = service_name
				machine_current.tmp_mid_ro = mid_ro
				machine_current.mid_user_defined = machine_name
				machine_current.ip = new_machine.ip
				break
	def release_machine(self):
		raise NotImplementedError()
	def get_stats(self):
		raise NotImplementedError()
	def validate(self):
		raise NotImplementedError()


class PhyDriver(object):
	def __init__(self, pop_config, global_variable, jesearch):
		self.driver_name = pop_config["pop-name"]
		self.zone = pop_config["zone"]
		self.domain = pop_config["domain"]
		self.scope = pop_config["scope"]
		self.driver_ssh_private_key = pop_config["ssh-private-key"]
		self.driver_ssh_username = pop_config["ssh-user"]
		self.driver_ssh_password = pop_config["ssh-password"]
		self.managed_by = pop_config["managed-by"]
		self.jesearch = jesearch
		
		self.gv = global_variable
		self.machine_list = list()
		self.logger = logging.getLogger('jox.PhyDriver.{}'.format(self.driver_name))
		self.max_retry = self.gv.JUJU_MAX_RETRY_CONNECTION_MODEL_ACCESSIBLE
		self.interval_access = self.gv.JUJU_INTERVAL_CONNECTION_MODEL_ACCESSIBLE
		self.template_manager = template_manager.TemplateManager(global_variable, jesearch)

	def check_machine_exist(self, cloud_name, model_name, machine_config):
		if "ip_addresses" in machine_config.keys():
			entity = 'ip_addresses'
		else:
			entity = 'ip'
		for machine in self.machine_list:
			if type(machine.ip) is str:
				if (machine.ip == machine_config[entity]) or (machine.ip in machine_config[entity]):
					return True
			else:
				for ip_addr in machine.ip:
					if (ip_addr == machine_config['ip_addresses']) or (ip_addr in machine_config[entity]):
						return True
		return False
	def get_machines_status(self):
		data_str = jsonpickle.encode(self.machine_list)
		data = json.loads(data_str)
		return data
	
	def get_machine_status(self, model_machine_name):
		for machine in self.machine_list:
			if machine.model_machine_name == model_machine_name:
				data_str = jsonpickle.encode(machine)
				data = json.loads(data_str)
				return data
	
	def get_machine_object(self, model_machine_name):
		for machine in self.machine_list:
			if machine.model_machine_name == model_machine_name:
				return machine
	
	def get_mid_juju_from_mid_jmodel(self, mid_user_defined, machine_type):
		for vm in self.machine_list:
			if vm.mid_user_defined == mid_user_defined:
				return vm.mid_vnfm
		return -1

	def machine_exists(self, mid_user_defined):
		try:
			for vm in self.machine_list:
				if vm.mid_user_defined == mid_user_defined:
					return True
			return False
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			# raise ex
			return False
	def add_machine(self, machine_config, service_name, mid_ro, subslice_name, model_name, cloud_name, nsi_id, machine_id_service=None):
		try:
			new_machine = _PhysicalMachine()
			
			new_machine.build(subslice_name,
							  	cloud_name,
								model_name,
								mid_ro,
								machine_config)


			add_new_context_machine = loop.run(self.deploy_physical_machine(new_machine, service_name, subslice_name, nsi_id, "admin", machine_id_service))
			machine_exist = False
			for machine in self.machine_list:
				if machine.mid_vnfm == new_machine.mid_vnfm:
					machine_exist = True
			if add_new_context_machine or (not machine_exist):
				self.machine_list.append(new_machine)
			self.allocate_machine(new_machine, service_name, mid_ro, machine_config['machine_name'])

		except Exception as ex:
			raise ex
	
	async def get_machines_jujuModel(self, cloud_name=None, model_name=None, user_name="admin"):
		model = Model()
		if (cloud_name is None) and (model_name is None):
			try:
				await model.connect_current()
			except:
				message = "Error while trying to connect to the current juju model"
				self.logger.error(message)
				return [False, message]
		else:
			try:
				model_name = cloud_name + ":" + user_name + '/' + model_name
				await model.connect(model_name)
			except:
				message = "Error while trying to connect to the juju model {}:{}/{}".format(cloud_name, user_name,
				                                                                            model_name)
				self.logger.error(message)
				return [False, message]
		juju_status = (await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop))
		return [True, juju_status.machines]

	async def deploy_physical_machine(self, new_machine, service_name, subslice_name, nsi_id, m_user="admin",
						 machine_id_service=None):
		model = Model()

		add_new_context_machine = True
		if machine_id_service is not None:
			add_new_context_machine = False
		try:
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			model_name = c_name + ":" + m_user + '/' + m_name

			number_retry = 0
			retry_connect = True
			while number_retry <= self.max_retry and retry_connect:
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
																							   model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)

			app_keys = model.applications.keys()
			application_NotExist = True
			for app in app_keys:
				if service_name == app and len(model.applications[app].units) > 0:
					application_NotExist = False
					app_values = model.applications.get(app)
					machine_id_service = app_values.units[0].machine.id
					add_new_context_machine = False
			if application_NotExist and machine_id_service is None:
				# TODO Add physical machine to juju model by providing the username, ip address, and private and public ssh_key
				self.logger.error("Adding physical machine is not supported yet. You have to add the physical machine manually. ")
			else:
				juju_machine = model.machines.get(machine_id_service)
			new_machine.mid_vnfm = juju_machine.data["id"]
			#############
			cmd_machin_config = ["juju", "show-machine", new_machine.mid_vnfm, "--format", "json"]

			cmd_machin_config_out = await  run_command(cmd_machin_config)
			cmd_machin_config_out = json.loads(cmd_machin_config_out)
			new_machine.ip = cmd_machin_config_out['machines'][new_machine.mid_vnfm]['ip-addresses']

			###################################################################################################
			machine_id = new_machine.mid_vnfm
			container_data = {"juju_mid": str(machine_id), "type": self.gv.PHY}
			self.template_manager.update_slice_monitor_index("subslice_monitor_" + subslice_name.lower(),
															 "machine_status",
															 service_name,
															 container_data,
															 nsi_id)

			container_data = {"juju_mid": str(machine_id)}
			self.template_manager.update_slice_monitor_index('slice_keys_' + nsi_id.lower(),
															 "machine_keys",
															 service_name,
															 container_data,
															 nsi_id)
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
		return add_new_context_machine

	async def update_machine(self, machine_config):
		for machine in self.machine_list:
			if machine_config['machine_name'] == machine.mid_user_defined:
				new_machine = machine
		try:
			model = Model()
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			m_user = 'admin'
			model_name = c_name + ":" + m_user + '/' + m_name
			await model.connect(model_name)
			
			#######################
			_id = new_machine.mid_vnfm
			machine_ready = False
			while not machine_ready:
				await model.disconnect()
				await asyncio.sleep(1)
				
				await model.connect(model_name)
				
				if model.machines[str(_id)].data["agent-status"]["current"] == "started":
					if model.machines[str(_id)].data["addresses"]:
						new_machine.mid_vim = model.machines[str(_id)].data["instance-id"]
						self.logger.debug("mid_lxc of the new container is %s", new_machine.mid_vim)
						
						addresses = model.machines[str(_id)].data["addresses"]
						for address in addresses:
							if address["type"] == "ipv4":  # and address["scope"] == "local-cloud":
								ip = address["value"]
								new_machine.ip = ip
								self.logger.debug("ip of the new container is {}".format(ip))
								machine_ready = True
						if not machine_ready:
							self.logger.info(
								"No ip address found for the machine {}".format(new_machine.mid_user_defined))
							machine_ready = True
		except Exception as ex:
			raise ex
		
		finally:
			await model.disconnect()
	
	async def delete_machine(self, service_name, machine_name_vnfm, machine_id_ro, machine_name_userdefined,
	                         jcloud, jmodel,
	                         slice_name, subslice_name=None, user="admin"):
		model = Model()
		try:
			c_name = jcloud
			m_name = jmodel
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug(
						"{} time trying to connect to juju model:{} to add lxc machine".format(number_retry,
						                                                                       model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)
			
			try:
				await model.machines[str(machine_name_vnfm)].destroy(force=True)
				cmd_destroy_kvm = ["uvt-kvm", "destroy", machine_name_userdefined]
				output_list = await run_command(*cmd_destroy_kvm)
			except:
				self.logger.critical("Either the application does not exist it can not be removed")
			self.logger.info("Remove the machine {} hosting the application {}".format(machine_name_vnfm, service_name))
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
	
	def register_machine_juju(self, cloud_name,
								model_name,
								mid_ro,
								machine_config):
		try:
			new_machine = _PhysicalMachine()
			new_machine.register(cloud_name,
								 model_name,
								 mid_ro,
								 machine_config)
			self.machine_list.append(new_machine)
		except Exception as ex:
			raise ex

	def allocate_machine(self, new_machine, service_name, mid_ro, machine_name):
		for machine_current in self.machine_list:
			if new_machine.mid_vnfm == machine_current.mid_vnfm:
				machine_current.available = False
				machine_current.tmp_service_name = service_name
				machine_current.tmp_mid_ro = mid_ro
				machine_current.mid_user_defined = machine_name
				machine_current.ip = new_machine.ip
				break
	
	def release_machine(self):
		raise NotImplementedError()
	
	def get_stats(self):
		raise NotImplementedError()
	
	def validate(self):
		raise NotImplementedError()


class SwitchDriver(object):
	def __init__(self, switch_type, global_variable, jesearch):
		self.switch_type = switch_type
		self.jesearch = jesearch
		self.gv = global_variable
		self.switch_list = list()
		self.logger = logging.getLogger('jox.SwitchDriver.{}'.format(self.switch_type))
		self.template_manager = template_manager.TemplateManager(global_variable, jesearch)
		self.tsn_agent = tsn_plugin_agent(self.gv)

	def add_switch(self, switch_config):
		object_check_switchDriver = list(filter(lambda x:
			                                    (x.tsn_switch_name == switch_config["tsn-switch-name"]),
			                                    self.switch_list))
		if len(object_check_switchDriver) > 0:
			message = "The switch {} is already exist, updating the switch".format(switch_config["tsn-switch-name"])
			self.logger.info(message)
			self.logger.debug(message)
			#update
			object_check_switchDriver = object_check_switchDriver[0]
			message = object_check_switchDriver.update(switch_config)
			return [message[1]]
		else:
			new_switch = _TsnSwitch(self.tsn_agent)
			message = new_switch.register(switch_config)
			if message[0]:
				self.switch_list.append(new_switch)
			return [message[1]]
class _TsnSwitch():
	def __init__(self, tsn_agent):
		self.logger = logging.getLogger('jox.SwitchDriver._TsnSwitch')
		self.tsn_agent = tsn_agent
		self.tsn_switch_name = ""
		self.tsnptp_interface = list()
		#self.tsntas_cycle_time = list()
		#self.tsntas_schedule_entry = list()
		"""
		Example on self.list_vlan
		list_vlan = {
			"vlan-id":{
				"attached-slices": list() # NSI names
				"vlan":{
					"id": 600,
					"ports": "ge2,ge3",
					"untagged-ports": "ge2"
				},
				"pvlan": {               
					"port": "ge<0-7>",
					"id": 200
				}
			}
		}
		"""
		self.list_vlan = dict()
		self.alive = False
		self.list_phy_machines = list()

	def register(self, switch_config):
		try:
			self.tsn_switch_name = switch_config["tsn-switch-name"]
			self.tsnptp_interface = switch_config["interface"]
			#self.tsnptp_interface = switch_config["tsnptp-interface"]
			#self.tsntas_cycle_time = switch_config["tsntas-cycle-time"]
			#self.tsntas_schedule_entry = switch_config["tsntas-schedule-entry"]
			message = "The switch {} is successfully added".format(switch_config["tsn-switch-name"])
			return [True, message]
		except Exception as ex:
			message = "The following error raised while adding the switch {}".format(switch_config["tsn-switch-name"], ex)
			return [False, message]
	def update(self, switch_config):
		try:
			self.tsn_switch_name = switch_config["tsn-switch-name"]
			self.tsnptp_interface = switch_config["interface"]
			#self.tsnptp_interface = switch_config["tsnptp-interface"]
			#self.tsntas_cycle_time = switch_config["tsntas-cycle-time"]
			#self.tsntas_schedule_entry = switch_config["tsntas-schedule-entry"]
			message = "The configuration of switch {} is successfully updated".format(switch_config["tsn-switch-name"])
			return [True, message]
		except Exception as ex:
			message = "The following error raised while updating the switch {}".format(switch_config["tsn-switch-name"], ex)
			return [False, message]
	def create_add_vlan(self, request, slice_name):
		vlan_id = str(request["vlan"]["id"])
		###########################################
		ports_to_add = str(request["vlan"]["ports"]).split(",")
		untagged_ports_to_add = str(request["vlan"]["untagged-ports"]).split(",")
		used_ports = list()
		used_untagged_ports = list()
		for vln_id in self.list_vlan:
			for slice in self.list_vlan[vln_id]["vlan"]["ports"]:
				for port in ports_to_add:
					if port in self.list_vlan[vln_id]["vlan"]["ports"][slice]:
						used_ports.append(port)
			for slice in self.list_vlan[vln_id]["vlan"]["untagged-ports"]:
				for port in untagged_ports_to_add:
					if port in self.list_vlan[vln_id]["vlan"]["untagged-ports"][slice]:
						used_untagged_ports.append(port)
		ports_to_add_final = ""
		untagged_ports_to_add_final = ""
		if len(used_ports) == 0:
			ports_to_add_final = request["vlan"]["ports"]
		else:					
			for port in ports_to_add:
				if port not in used_ports:
					ports_to_add_final = ','.join(ports_to_add_final, port)
		if len(used_untagged_ports) == 0:
			untagged_ports_to_add_final = request["vlan"]["untagged-ports"]
		else:
			for port in untagged_ports_to_add:
				if port not in used_untagged_ports:
					untagged_ports_to_add_final = ','.join(untagged_ports_to_add_final, port)
		###########################################
		if str(vlan_id) in self.list_vlan.keys():
			if request["vlan"]["operation"] == "add":
				response = None
				try:
					self.logger.info("The vlan {} is already exist. Adding the vlan with ports{} ".format(vlan_id, request["vlan"]["ports"]))
					# vlan-add
					if (ports_to_add_final != "") or (untagged_ports_to_add_final != ""):
						queue_name_tsn = "QueueTSN"
						current_time = datetime.datetime.now()
						enquiry={}
						enquiry["plugin_message"] = "vlan_add"
						enquiry["node"] = self.tsn_switch_name
						enquiry["vid"] = str(vlan_id)
						if ports_to_add_final != "":
							enquiry["pbm_list"] = ports_to_add_final
						if untagged_ports_to_add_final != "":
							enquiry["ubm_list"] = untagged_ports_to_add_final
						enquiry["datetime"] = str(current_time)
						enquiry = json.dumps(enquiry)
						enquiry.encode("utf-8")
						response = self.tsn_agent.send_to_plugin(enquiry, queue_name_tsn)
						data = response.decode(self.gv.ENCODING_TYPE)
						data = json.loads(data)
						print("data_vlan_add={}".format(data))
					########################################################
					if slice_name not in self.list_vlan[vlan_id]["attached-slices"]:
						self.list_vlan[vlan_id]["attached-slices"].append(slice_name)
						#self.list_vlan[vlan_id]["vlan"]["id"] = vlan_id
						self.list_vlan[vlan_id]["vlan"]["ports"][slice_name] = request["vlan"]["ports"]
						self.list_vlan[vlan_id]["vlan"]["untagged-ports"][slice_name] = request["vlan"]["untagged-ports"]
						#pvlan
						self.list_vlan[vlan_id]["pvlan"]["port"][slice_name] = request["pvlan"]["port"]
						self.list_vlan[vlan_id]["pvlan"]["id"][slice_name] = request["pvlan"]["id"]
						message = "The slice {} is successfully registedred to the vlan {} with ports {}. TSN_PLUGIN={}".format(slice_name, vlan_id, request["vlan"]["ports"], response)
						return [True, message]
					else:
						#self.list_vlan[vlan_id]["attached-slices"].append(slice_name)
						current_ports = self.list_vlan[vlan_id]["vlan"]["ports"][slice_name]
						current_ports = '{},{}'.format(current_ports, request["vlan"]["ports"])
						self.list_vlan[vlan_id]["vlan"]["ports"][slice_name] = current_ports
						curren_untagged_ports = self.list_vlan[vlan_id]["vlan"]["untagged-ports"][slice_name]
						curren_untagged_ports = '{},{}'.format(curren_untagged_ports, request["vlan"]["untagged-ports"])

						self.list_vlan[vlan_id]["vlan"]["untagged-ports"][slice_name] = curren_untagged_ports
						#pvlan
						self.list_vlan[vlan_id]["pvlan"]["port"][slice_name] = request["pvlan"]["port"]
						self.list_vlan[vlan_id]["pvlan"]["id"][slice_name] = request["pvlan"]["id"]
						message = "The slice {} registered to the vlan {} is successfully updated with ports {}. TSN_PLUGIN={}".format(slice_name, vlan_id, request["vlan"]["ports"], response)
						#message = "The slice {} is successfully registered to the vlan {}. TSN_PLUGIN={}".format(slice_name, vlan_id, response)
						#message = "The vlan {} with ports {} is successfully added".format(vlan_id, request["vlan"]["ports"])
						return [True, message]
				except Exception as ex:
					#raise ex	
					message = "The following error raised while adding the vlan {} with ports {}. TSN_PLUGIN={}".format(vlan_id, request["vlan"]["ports"], response)
					return [True, message]
			else:
				message = "Error creating the vlan {}, it is already exist, and thus the ports {} are no added to the vlan ".format(vlan_id, request["vlan"]["ports"])
				return [False, message]
		else:
			if request["vlan"]["operation"] == "create":
				response = None
				try:
					# # vlan-create
					self.logger.info("creating the vlan {} , and dding the ports".format(vlan_id, request["vlan"]["ports"]))
					##################
					queue_name_tsn = "QueueTSN"
					current_time = datetime.datetime.now()
					enquiry={}
					enquiry["plugin_message"] = "vlan_create"
					enquiry["node"] = self.tsn_switch_name
					enquiry["vid"] = str(vlan_id)
					enquiry["pbm_list"] = request["vlan"]["ports"]
					enquiry["ubm_list"] = request["vlan"]["untagged-ports"]
					enquiry["datetime"] = str(current_time)
					enquiry = json.dumps(enquiry)
					enquiry.encode("utf-8")
					response = self.tsn_agent.send_to_plugin(enquiry, queue_name_tsn)
					data = response.decode(self.gv.ENCODING_TYPE)
					data = json.loads(data)
					print(data)
					#######################
					new_vlan = {
						"attached-slices": [slice_name], # NSI names
						"vlan":{
							"id": request["vlan"]["id"],
							"ports": {
								slice_name: request["vlan"]["ports"]
								},
							"untagged-ports": {
								slice_name: request["vlan"]["untagged-ports"]
								}
						},
						"pvlan": {               
							"port": {
								slice_name: request["pvlan"]["port"]
								},
							"id": {
								slice_name: request["pvlan"]["id"]
								}
						}
					}
					self.list_vlan[str(request["vlan"]["id"])] = new_vlan

					message = "The vlan {} is successfully created, and the slice {} is registered to this vlan {}. TSN_PLUGIN={}".format(vlan_id, slice_name, vlan_id, response)

					return [True, message]
				except Exception as ex:
					#raise ex
					message = "The following error raised while creating the vlan {} with ports {}: {}. TSN_PLUGIN={}".format(vlan_id, request["vlan"]["ports"], ex, response)
					return [True, message]
			else:
				message = "Error, the ports {} can not be added, since the vlan {} does not exist".format(request["vlan"]["ports"], vlan_id)
				return [False, message]
	
	def get_vlan(self, vlan_id, slice_name=None):
		if vlan_id == "0":
			# get all vlans
			return [False, self.list_vlan]
		else:
			# get specific vlan
			if str(vlan_id) in self.list_vlan.keys():
				message = "Getting the config of vlan {}".format(vlan_id)
				return [True, self.list_vlan[str(vlan_id)]]
			else:
				message = "The vlan {} can not be found".format(vlan_id)
				self.logger.error(message)
				return [False, message]
	def destroy_vlan(self, vlan_id, slice_name):
		response = None
		if str(vlan_id) in self.list_vlan:
			attached_slices = self.list_vlan[str(vlan_id)]["attached-slices"]
			if slice_name in attached_slices:
				self.logger.info("The slice {} is registered to the vlan {}".format(slice_name, vlan_id))
				if len(attached_slices) == 1: # there is only one slice registered to this vlan
					# destroy vlan
					try:
						############################
						queue_name_tsn = "QueueTSN"
						current_time = datetime.datetime.now()
						enquiry={}
						enquiry["plugin_message"] = "vlan_destroy"
						enquiry["node"] = self.tsn_switch_name
						enquiry["vid"] = str(vlan_id)
						enquiry["datetime"] = str(current_time)
						enquiry = json.dumps(enquiry)
						enquiry.encode("utf-8")
						response = self.send_to_plugin(enquiry, queue_name_tsn)
						########################################################
						self.logger.info("Trying to destrying the vlan {}".format(vlan_id))
						message = "The vlan {} is successfully destroyed. TSN_PLUGIN={}".format(vlan_id, response)
						del self.list_vlan[str(vlan_id)]	
						return [True, message]
					except Exception as ex:
						message = "The following error raised while trying to detroy the vlan {}. TSN_PLUGIN={}".format(ex, vlan_id, response)
						return [False, message]
						#raise ex
				else:
					message = "The vlan {} can not be destroyed, since the following slices are registered: {}".format(vlan_id, attached_slices)
					return [False, message]
			else:
				message = "The slice {} is NOT registered to the vlan {}. TSN_PLUGIN={}".format(slice_name, vlan_id, response)
				self.logger.error(message) 
				return [False, message]
		else:
			message = "The vlan {} can not be found, thus not destroyed. TSN_PLUGIN={}".format(vlan_id, response)
			self.logger.error(message) 
			return [False, message]
	###################
	def remove_vlan(self, request, slice_name):
		vlan_id = str(request["vlan"]["id"])
		response = None
		if str(vlan_id) in self.list_vlan:
			attached_slices = self.list_vlan[str(vlan_id)]["attached-slices"]
			if slice_name in attached_slices:
				self.logger.info("The slice {} is registered to the vlan {}".format(slice_name, vlan_id))				
				ports_to_remove = str(request["vlan"]["ports"]).split(",")
				ports_untagged_to_remove = str(request["vlan"]["untagged-ports"]).split(",")
				if len(attached_slices) == 1:
					######### ports
					current_ports = str(self.list_vlan[str(vlan_id)]["vlan"]["ports"][slice_name]).split(',')
					ports_to_keep = ""
					ports_not_exist = ""
					for port in current_ports:
						if port not in request["vlan"]["ports"]:
							ports_to_keep = ','.join(ports_to_keep, port)
					for port in ports_to_remove:
						if port not in self.list_vlan[str(vlan_id)]["vlan"]["ports"][slice_name]:
							ports_not_exist = ','.join(ports_not_exist, port)
					######### untagged-ports
					current_untagged_ports = str(self.list_vlan[str(vlan_id)]["vlan"]["untagged-ports"][slice_name]).split(',')
					ports_untagged_to_keep = ""
					ports_untagged_not_exist = ""
					for port in current_untagged_ports:
						if port not in request["vlan"]["untagged-ports"]:
							ports_untagged_to_keep = ','.join(ports_untagged_to_keep, port)
					for port in ports_untagged_to_remove:
						if port not in self.list_vlan[str(vlan_id)]["vlan"]["untagged-ports"][slice_name]:
							ports_untagged_not_exist = ','.join(ports_untagged_not_exist, port)
					#########
					if (ports_not_exist != "") or (ports_untagged_not_exist != ""):
						message = "Error, the following ports do not exist for the vlan {}: port={}, untagged-ports={}. TSN_PLUGIN={}".format(vlan_id, ports_not_exist, ports_untagged_not_exist, response)
						self.logger.error(message) 
						return [False, message]
					else:
						try:
							############################
							queue_name_tsn = "QueueTSN"
							current_time = datetime.datetime.now()
							enquiry={}
							enquiry["plugin_message"] = "vlan_remove"
							enquiry["node"] = self.tsn_switch_name
							enquiry["vid"] = str(vlan_id)
							enquiry["pbm_list"] = request["vlan"]["port"]
							enquiry["ubm_list"] = request["vlan"]["untagged-ports"]
							enquiry["datetime"] = str(current_time)
							enquiry = json.dumps(enquiry)
							enquiry.encode("utf-8")
							response = self.send_to_plugin(enquiry, queue_name_tsn)
							########################################################
							self.logger.info("There are more than one slice is attached to the vlan {}".format(vlan_id))
							self.list_vlan[str(vlan_id)]["vlan"]["ports"][slice_name] = ports_to_keep
							self.list_vlan[str(vlan_id)]["vlan"]["untagged-ports"][slice_name] = ports_untagged_to_keep
							message = "The the following ports of the slice {} are successfully removed from the vlan {}; ports={}, untagged-ports={}. TSN_PLUGIN={}".format(slice_name, vlan_id, request["vlan"]["ports"], request["vlan"]["untagged-ports"], response)
							self.logger.info(message) 
							return [True, message]
						except Exception as ex:
							message = "The following error raised while trying to remove ports of the the vlan {}: {}. TSN_PLUGIN={}".format(vlan_id, ex, response)
							self.logger.error(message) 
							return [False, message]
							#raise ex
				else:
					# untegister only the non-shared ports	
					# ports
					ports_can_be_removed = ""
					for slice in self.list_vlan[str(vlan_id)]["attached-slices"]:
						for ports in self.list_vlan[vlan_id]["vlan"]["ports"][slice]:
							if slice != slice_name:
								for port in ports_to_remove:
									if port not in ports:
										ports_can_be_removed = ','.join(ports_can_be_removed, port)
					# untagged_ports
					ports_untagged_can_be_removed = ""
					for slice in self.list_vlan[str(vlan_id)]["attached-slices"]:
						for ports in self.list_vlan[vlan_id]["vlan"]["untagged-ports"][slice]:
							if slice != slice_name:
								for port in ports_untagged_to_remove:
									if port not in ports:
										ports_untagged_can_be_removed = ','.join(ports_untagged_can_be_removed, port)
					##########
					if ports_can_be_removed != "":
						# ports to be removed
						############################
						queue_name_tsn = "QueueTSN"
						current_time = datetime.datetime.now()
						enquiry={}
						enquiry["plugin_message"] = "vlan_remove"
						enquiry["node"] = self.tsn_switch_name
						enquiry["vid"] = str(vlan_id)
						enquiry["ports"] = ports_can_be_removed
						enquiry["datetime"] = str(current_time)
						enquiry = json.dumps(enquiry)
						enquiry.encode("utf-8")
						response = self.send_to_plugin(enquiry, queue_name_tsn)
						########################################################
						message = "The ports {} are successfully unregistered from the slice {} on the vlan {}. The following ports are removed from the switch: {}".format(request["vlan"]["ports"], slice_name, vlan_id, ports_can_be_removed)
					else:
						# no ports to be removed
						message = "The ports {} are successfully unregistered from the slice {} on the vlan {}".format(request["vlan"]["ports"], slice_name, vlan_id)
					return [True, message]
			else:
				message = "Error, the slice {} is NOT registered to the vlan {}. TSN_PLUGIN={}".format(slice_name, vlan_id, response)
				self.logger.error(message) 
				return [False, message]
		else:
			message = "Error, the vlan {} can not be found. TSN_PLUGIN={}".format(vlan_id, response)
			self.logger.error(message) 
			return [False, message]
class _VmKvm():
	def __init__(self):
		self.logger = logging.getLogger('jox.VimDriver.VmKvm')
		self.subslice_name = list() # list of subslice srerved by the machine
		
		# credential of juju
		self.juju_cloud_name = ""
		self.juju_model_name = ""
		self.juju_endpoint = ""
		self.juju_user_passwd = dict() # list of user names and password
		
		self.mid_user_defined = ""
		self.mid_vnfm = "" # juju id of the machine in case of juju
		self.mid_vim = "" # value assigned by LXD hypervisor
		self.mid_ro  = "" # name given by the resource controller
		
		self.ip = ""
		self.template = ""
		
		self.cpu = ""
		self.memory = ""
		self.disc_size = ""
		
		self.os_series = ""
		self.os_version = ""

		self.auto = False
		
		self.available = True

		self.tmp_service_name = None
		self.tmp_mid_ro = None
		# parameters related to TSN switch
		self.switch = {
			"tsn":{
				"switch_name": "",
				"switch_port": ""
			}
		}
	
	def build(self,
	          subslice_name,
	          cloud_name,
	          model_name,
	          mid_ro,
	          machine_config):
		try:
			self.subslice_name.append(subslice_name)
			
			# credential of juju
			self.juju_cloud_name = cloud_name
			self.juju_model_name = model_name
			self.juju_endpoint = None
			
			self.mid_user_defined = machine_config['machine_name']
			self.mid_vim = ""  # value assigned by LXD hypervisor
			self.mid_ro = mid_ro  # name given by the resource controller
			
			self.cpu = machine_config['host']['num_cpus']
			self.disc_size = machine_config['host']['disk_size']
			self.memory = machine_config['host']['mem_size']
			if machine_config['os']['distribution'] == "Ubuntu":
				os_version = str(machine_config['os']['version'])
				try:
					self.os_series = global_varialbles.OS_SERIES[os_version]
				except:
					message = "The os version {} for the machine {} from the subslice {} is not defined. Please define it in gv file in the variable OS_SERIES".format(os_version, machine_config['machine_name'], subslice_name)
					self.logger.debug(message)
					self.logger.critical(message)
					self.logger.info(message)
		except Exception as ex:
			raise ex

	def register(self,
				 cloud_name,
				 model_name,
				 mid_ro,
				 machine_config):
		try:
			# credential of juju
			self.juju_cloud_name = cloud_name
			self.juju_model_name = model_name
			self.juju_endpoint = None

			self.mid_user_defined = machine_config['machine_name']
			self.mid_vim = ""
			self.mid_vnfm = machine_config['juju_id']
			self.mid_ro = mid_ro  # name given by the resource controller

			self.cpu = machine_config['host']['num_cpus']
			self.disc_size = machine_config['host']['disk_size']
			self.memory = machine_config['host']['mem_size']
			if machine_config['os']['distribution'] == "Ubuntu":
				os_version = str(machine_config['os']['version'])
				for os_v in global_varialbles.OS_SERIES:
					if (os_version in os_v) or (os_v in os_version):
						self.os_series = global_varialbles.OS_SERIES[os_v]
				if self.os_series == "":
					message = "The os version {} for the machine {} is not defined. Please define it in gv file in the variable OS_SERIES".format(
						os_version, machine_config['machine_name'])
					self.logger.critical(message)
					self.logger.info(message)
			self.ip = machine_config['ip_addresses']
			self.available = machine_config['machine_available']

		except ValueError as ex:
			raise ex

	def validate(self, cloud_name, model_name, machine_config):
		raise NotImplementedError()


class _VmLxc():
	
	def __init__(self):
		self.logger = logging.getLogger('jox.VimDriver.VmLxc')
		self.subslice_name = list()  # list of subslice srerved by the machine
		
		# credential of juju
		self.juju_cloud_name = ""
		self.juju_model_name = ""
		self.juju_endpoint = ""
		self.juju_user_passwd = dict()  # list of user names and password
		
		self.mid_user_defined = ""
		self.mid_vnfm = ""  # juju id of the machine in case of juju
		self.mid_vim = ""  # value assigned by LXD hypervisor
		self.mid_ro = ""  # name given by the resource controller
		
		self.ip = ""
		self.template = ""
		
		self.cpu = ""
		self.memory = ""
		self.disc_size = ""
		
		self.os_series = ""
		self.os_version = ""

		self.auto = False
		self.available = True

		self.tmp_service_name = None
		self.tmp_mid_ro = None

		
	def build(self,
	          subslice_name,
	          cloud_name,
	          model_name,
	          mid_ro,
	          machine_config):
		try:
			self.subslice_name.append(subslice_name)
			
			# credential of juju
			self.juju_cloud_name = cloud_name
			self.juju_model_name = model_name
			self.juju_endpoint = None
			
			self.mid_user_defined = machine_config['machine_name']
			self.mid_vim = ""  # value assigned by LXD hypervisor
			self.mid_ro = mid_ro  # name given by the resource controller
			
			self.cpu = machine_config['host']['num_cpus']
			self.disc_size = machine_config['host']['disk_size']
			self.memory = machine_config['host']['mem_size']
			if machine_config['os']['distribution'] == "Ubuntu":
				self.os_version = str(machine_config['os']['version'])
				try:
					self.os_series = global_varialbles.OS_SERIES[self.os_version]
				except:
					message = "The os version {} for the machine {} from the subslice {} is not defined. Please define it in gv file in the variable OS_SERIES".format(
							self.os_version, machine_config['machine_name'], subslice_name)
					self.logger.critical(message)
					self.logger.info(message)
		except ValueError as ex:
			raise ex
	
	def register(self,
	          cloud_name,
	          model_name,
	          mid_ro,
	          machine_config):
		try:
			# credential of juju
			self.juju_cloud_name = cloud_name
			self.juju_model_name = model_name
			self.juju_endpoint = None
			
			self.mid_user_defined = machine_config['machine_name']
			self.mid_vim = ""
			self.mid_vnfm = machine_config['juju_id']
			self.mid_ro = mid_ro  # name given by the resource controller
			
			self.cpu = machine_config['host']['num_cpus']
			self.disc_size = machine_config['host']['disk_size']
			self.memory = machine_config['host']['mem_size']
			if machine_config['os']['distribution'] == "Ubuntu":
				self.os_version = str(machine_config['os']['version'])
				for os_v in global_varialbles.OS_SERIES:
					if (self.os_version  in os_v) or (os_v in self.os_version):
						self.os_series = global_varialbles.OS_SERIES[os_v]
				if self.os_series == "":
					message = "The os version {} for the machine {} is not defined. Please define it in gv file in the variable OS_SERIES".format(
							self.os_version, machine_config['machine_name'])
					self.logger.critical(message)
					self.logger.info(message)
			self.ip = machine_config['ip_addresses']
			self.available = machine_config['machine_available']
			
		except ValueError as ex:
			raise ex
		
	def validate(self, cloud_name, model_name, machine_config):
		"""
		:param cloud_name:
		:param model_name:
		:param machine_config:
		:return:
		"""
		raise NotImplementedError()


class _PhysicalMachine():
	
	def __init__(self):
		self.logger = logging.getLogger('jox.VimDriver.PhysicalMachine')
		self.zone = None
		self.domain = list()  # a physical machine could be connected to different domains through two interfaces
		self.hostname = None
		self.dns_name = None
		# machine status
		self.alive = False
		self.connected = False
		
		self.available = True # to indicate whether the machine as a whole is reserved for certain application

		self.tmp_service_name = None
		self.tmp_mid_ro = None
		self.addresses = list()
		self.ip = None
		self.interfaces = None
		
		""" total resources """
		self.host_cpu_tot = 0
		self.host_mem_tot = 0
		self.host_disc_size_tot = 0
		""" available resources """
		self.host_cpu_ava_percent = 0
		self.host_mem_ava = 0
		self.host_disc_size_ava= 0
		
		""" os characteristics """
		self.os_arch = "" # e.g. x86_64
		self.os_type = "" # e.g. linux
		self.os_dist = "" # e.g. Ubuntu
		self.os_version = "" # e.g. 16.04
		self.os_series = "" # e.g. xenial
		
		"""virtualization support"""
		self.virt_lxd = False
		self.virt_kvm = False
		
		self.tags = None
		
		self.list_lxd_machines = list()
		self.list_kvm_machines = list()
		
		self.subslice_name = list() # list of subslice srerved by the machine
		
		# credential of juju
		self.juju_cloud_name = ""
		self.juju_model_name = ""
		self.juju_endpoint = ""
		self.juju_user_passwd = dict()  # list of user names and password
		
		self.mid_user_defined = list()
		self.mid_vnfm = ""  # juju id of the machine in case of juju
		self.mid_vim = ""  # value assigned by LXD hypervisor
		self.mid_ro = ""  # name given by the resource controller
		
		#parameters related to TSN switch
		self.tsn_switch_name = None
		self.tsn_port_id = None

	def build(self,
			  subslice_name,
			  cloud_name,
			  model_name,
			  mid_ro,
			  machine_config):
		try:
			self.subslice_name.append(subslice_name)

			# credential of juju
			self.juju_cloud_name = cloud_name
			self.juju_model_name = model_name
			self.juju_endpoint = None

			self.mid_user_defined = machine_config['machine_name']
			self.mid_vim = ""  # value assigned by LXD hypervisor
			self.mid_ro = mid_ro  # name given by the resource controller

			self.cpu = machine_config['host']['num_cpus']
			self.disc_size = machine_config['host']['disk_size']
			self.memory = machine_config['host']['mem_size']
			if machine_config['os']['distribution'] == "Ubuntu":
				os_version = str(machine_config['os']['version'])
				try:
					self.os_series = global_varialbles.OS_SERIES[os_version]
				except:
					message = "The os version {} for the machine {} from the subslice {} is not defined. Please define it in gv file in the variable OS_SERIES".format(
						os_version, machine_config['machine_name'], subslice_name)
					self.logger.debug(message)
					self.logger.critical(message)
					self.logger.info(message)
			if "switch" in machine_config['additional_requirements']["properties"].keys():
				self.tsn_switch_name = machine_config['additional_requirements']["properties"]["switch"]["switch_name"]
				self.tsn_port_id = machine_config['additional_requirements']["properties"]["switch"]["port_id"]
		except Exception as ex:
			raise ex
	def register(self,
				 cloud_name,
				 model_name,
				 mid_ro,
				 machine_config):
		try:
			# credential of juju
			self.juju_cloud_name = cloud_name
			self.juju_model_name = model_name
			self.juju_endpoint = None

			self.mid_user_defined = machine_config['machine_name']
			self.mid_vim = ""
			self.mid_vnfm = machine_config['juju_id']
			self.mid_ro = mid_ro  # name given by the resource controller

			self.cpu = machine_config['host']['num_cpus']
			self.disc_size = machine_config['host']['disk_size']
			self.memory = machine_config['host']['mem_size']
			if machine_config['os']['distribution'] == "Ubuntu":
				os_version = str(machine_config['os']['version'])
				for os_v in global_varialbles.OS_SERIES:
					if (os_version in os_v) or (os_v in os_version):
						self.os_series = global_varialbles.OS_SERIES[os_v]
				if self.os_series == "":
					message = "The os version {} for the machine {} is not defined. Please define it in gv file in the variable OS_SERIES".format(
						os_version, machine_config['machine_name'])
					self.logger.critical(message)
					self.logger.info(message)
			self.addresses = machine_config['ip_addresses']
			self.ip = machine_config['ip_addresses']
			self.available = machine_config['machine_available']
			self.domain = machine_config['domain']
			self.hostname = machine_config['domain']
			self.dns_name = machine_config['dns_name']
			self.interfaces = machine_config['interfaces']

			""" total resources """
			self.host_cpu_tot = machine_config['host']['cpu_number']
			self.host_mem_tot = machine_config['host']['mem_total']
			self.host_disc_size_tot = None
			""" available resources """
			self.host_cpu_ava_percent = machine_config['host']['cpu_percent']
			self.host_mem_ava = machine_config['host']['mem_free']
			self.host_disc_size_ava = None

		except ValueError as ex:
			raise ex

		
	def release(self, subslice, machine_user_defined_name):
		self.available = True
		self.subslice_name.remove(subslice)
		self.mid_user_defined.remove(machine_user_defined_name)
		
	def validate(self, cloud_name, model_name, machine_config):
		raise NotImplementedError()


async def run_command(*args):
	arguments = (args[1] if len(args) > 1 else args[0])
	process = await asyncio.create_subprocess_exec(
		*arguments,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)
	stdout, stderr = await process.communicate()
	return (stdout.decode("utf-8")).strip()
async def machine_configuration_for_jujuCharm(ssh_user, machine_ip, ssh_key_private, logger):
	cmd_ssh_1 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "echo", "export", "LC_CTYPE=en_US.UTF-8", ">>" "~.bashrc"]
	cmd_ssh_2 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "echo", "export", "LC_ALL=en_US.UTF-8", ">>" "~.bashrc"]
	cmd_ssh_3 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "source", ".bashrc"]

	cmd_ssh_4 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "sudo", "apt-get", "update", "-y"]
	cmd_ssh_5 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "sudo", "apt-get", "upgrade", "-y"]
	cmd_ssh_6 = ["ssh", "{}@{}".format(ssh_user, machine_ip), "sudo", "apt-get", "install",
				 "iperf",
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

	cmd_kvm_ssh_vm = ["ssh", "-o", "StrictHostKeyChecking={}".format("no"), "-i", ssh_key_private,
					  "{}@{}".format(ssh_user, machine_ip), "pwd"]

	cmd_kvm_ssh_vm_out = await run_command(cmd_kvm_ssh_vm)
	message = "ensuring ssh to the machine {}".format(machine_ip)
	logger.info(message)

	cmd_ssh_1_out = await run_command(cmd_ssh_1)
	message = "configure local {} to the machine {}".format(cmd_ssh_1[4], machine_ip)
	logger.info(message)

	cmd_ssh_2_out = await run_command(cmd_ssh_2)
	message = "configure local {} to the machine {}".format(cmd_ssh_2[4], machine_ip)
	logger.info(message)

	cmd_ssh_3_out = await run_command(cmd_ssh_3)

	cmd_ssh_4_out = await run_command(cmd_ssh_4)
	message = "doing sudo apt-get update to the machine {}".format(cmd_ssh_2[4], machine_ip)
	logger.info(message)

	cmd_ssh_5_out = await run_command(cmd_ssh_5)
	message = "doing sudo apt-get upgrade to the machine {}".format(cmd_ssh_2[4], machine_ip)
	logger.info(message)

	cmd_ssh_6_out = await run_command(cmd_ssh_6)
	message = "installing required packages for charms in the machine {}".format(cmd_ssh_2[4], machine_ip)
	logger.info(message)


class tsn_plugin_agent():
	def __init__(self, global_var):
		self.logger = logging.getLogger("jox-agent.tsn")
		#self.jox_config = ""
		self.gv = global_var
		"""
		try:
			with open(gv.CONFIG_FILE) as data_file:
				data = json.load(data_file)
				data_file.close()
			self.jox_config = data

		except IOError as ex:
			message = "Could not load Plugin Configuration file.I/O error({0}): {1}".format(ex.errno, ex.strerror)
			self.logger.error(message)
		except ValueError as error:
			message = "invalid json"
			self.logger.error(message)
		except Exception as ex:
			message = "Error while trying to load plugin configuration"
			self.logger.error(message)
		else:
			message = " Plugin Configuration file Loaded"
			self.logger.info(message)
		"""
		## Loading global variables ##
		#### TSN and RBMQ configuration
		#self.gv.RBMQ_SERVER_IP = self.jox_config['rabbit-mq-config']["rabbit-mq-server-ip"]
		#self.gv.RBMQ_SERVER_PORT = self.jox_config['rabbit-mq-config']["rabbit-mq-server-port"]
		#elf.gv.RBMQ_QUEUE_TSN = self.jox_config["tsn-plugin-config"]["rabbit-mq-queue"]
		self.rbmq_server_ip = self.gv.RBMQ_SERVER_IP
		self.rbmq_server_port = self.gv.RBMQ_SERVER_PORT
		self.rbmq_queue_name = self.gv.RBMQ_QUEUE_TSN
		#self.gv.TSN_PLUGIN_STATUS = self.jox_config["tsn-plugin-config"]["plugin-status"]
		self.tsn_plugin_status=self.gv.TSN_PLUGIN_STATUS
       
	def run(self, retry=False):
		if retry:
			self.connection.close()
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port='5672'))
		#self.connection.add_timeout(self.timeout, self.on_timeout)
		self.channel = self.connection.channel()
		self.result = self.channel.queue_declare(self.gv.RBMQ_QUEUE_TSN,exclusive=False)
		self.callback_queue = self.result.method.queue

		#self.channel.basic_consume(self.callback_queue,self.on_response)
		self.channel.basic_consume(self.on_response, no_ack=True,
		                           queue=self.callback_queue)
	def send_to_plugin(self, msg, rbmq_queue_name, reply=True):
		print("reply {}".format(reply))
		if reply:
			message_not_sent = True
			while message_not_sent:
				try:
					self.response = None
					self.corr_id = str(uuid.uuid4())
					self.channel.basic_publish(exchange='',
											routing_key=rbmq_queue_name,
											properties=pika.BasicProperties(
                                                   reply_to=self.callback_queue,
                                                   correlation_id=self.corr_id,
                                               ),
                                               body=msg)
					message_not_sent = False
				except:
					time.sleep(0.5)
					self.run()
			while self.response is None:
				if self.gv.TSN_PLUGIN_STATUS == self.gv.TSN_ENABLED:
					self.connection.process_data_events()
				else:
					self.response = 'Not received'
		else:
			message_not_sent = True
			while message_not_sent:
				try:
					self.response = None
					self.corr_id = str(uuid.uuid4())
					self.channel.basic_publish(exchange='',
                                               routing_key=rbmq_queue_name,
                                               properties=pika.BasicProperties(
                                               ),
                                               body=msg)
					message_not_sent = False
				except:
					time.sleep(0.5)
					self.run()
			return None
		return self.response
	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body.decode("utf-8")

	def on_timeout(self, ):
		self.connection.close()
        # self.gv.FLEXRAN_PLUGIN_STATUS =self.gv.DISABLE

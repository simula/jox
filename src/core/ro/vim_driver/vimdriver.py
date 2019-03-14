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

import os
import logging
from juju.model import Model
from juju import loop, utils
import traceback
import jsonpickle, json
from subprocess import check_output
import asyncio
from asyncio import subprocess
import datetime
dir_path = os.path.dirname(os.path.abspath(__file__ + "/../../../"))
from src.core.nso.template_manager import template_manager
from src.common.config import gv as global_varialbles
#
class LxcDriver(object):
	def __init__(self, driver_name, global_variable):
		self.driver_name = driver_name # name of the vim driver, it is important epsecially when there are many vim drivers from the same type
		self.machine_list = list()
		self.gv = global_variable
		self.max_retry = self.gv.JUJU_MAX_RETRY_CONNECTION_MODEL_ACCESSIBLE # number of tentative to connect to juju. every tentative is after one second
		self.interval_access = self.gv.JUJU_INTERVAL_CONNECTION_MODEL_ACCESSIBLE
		self.logger = logging.getLogger('jox.LxcDriver.{}'.format(self.driver_name))
		self.log_config()
		self.template_manager = template_manager.TemplateManager(global_variable)

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
	
	def add_machine(self, machine_config, service_name, mid_ro, slice_name, model_name, cloud_name, nsi_id):
		try:
			new_machine = _VmLxc()
			new_machine.build(slice_name,
			                  cloud_name,
			                  model_name,
			                  mid_ro,
			                  machine_config)
			loop.run(self.deploy_machine(new_machine, service_name, slice_name, nsi_id))
			self.machine_list.append(new_machine)

		except Exception as ex:
			raise ex

	async def deploy_machine(self, new_machine, service_name, slice_name, nsi_id, user="admin"):
		model = Model()
		try:
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			model_name = c_name + ":" + user + "/" + m_name
			retry_connect = True
			number_retry = 0
			while number_retry <= self.max_retry and retry_connect:
				number_retry += 1
				try:
					self.logger.debug("{} time trying to connect to juju model:{} to add lxc machine".format(number_retry, model_name))
					await model.connect(model_name)
					retry_connect = False
					self.logger.debug("Successful connection to the model {} ".format(model_name))
				except:
					await model.disconnect()
					await asyncio.sleep(self.interval_access)
			
			app_keys = model.applications.keys()
			application_NotExist = True
			#
			for app in app_keys:
				if service_name == app and len(model.applications[app].units) > 0:
					application_NotExist = False
					app_values = model.applications.get(app)
					machine_id_service = app_values.units[0].machine.id
			if application_NotExist:
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
				juju_machine = model.machines.get(machine_id_service)
				self.logger.info("The application {} is already deployed, and thus no machine added".format(service_name))
			new_machine.mid_vnfm = juju_machine.data["id"]  # Note here Machine ID

			self.logger.info("The machine {} is added and its juju id is {}".format(new_machine.mid_user_defined, new_machine.mid_vnfm))
			machine_id = new_machine.mid_vnfm

			
			self.template_manager.update_slice_monitor_index("slice_monitor_"+slice_name.lower(),
			                                                 "machine_status",
			                                                 service_name,
			                                                 "juju_mid",
			                                                 str(machine_id),
			                                                 nsi_id)
			self.template_manager.update_slice_monitor_index('slice_keys_'+nsi_id.lower(),
			                                                 "machine_keys",
			                                                 service_name,
			                                                 "juju_mid",
			                                                 str(machine_id),
			                                                 nsi_id)
			self.template_manager.update_slice_monitor_index("slice_monitor_"+slice_name.lower(),
			                                                 "machine_status",
			                                                 service_name,
			                                                 "type",
			                                                 "lxc",
			                                                 nsi_id)


			self.logger.info("Deployed LXC Machine {} {} {}".format(new_machine.mid_vnfm, len(juju_machine.data), juju_machine.data))

		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()

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
	def allocate_machine(self):
		raise NotImplementedError()
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
	def __init__(self, driver_name, global_variable):
		self.driver_name = driver_name
		self.gv = global_variable
		self.machine_list = list()
		self.logger = logging.getLogger('jox.KvmDriver.{}'.format(self.driver_name))
		self.max_retry = self.gv.JUJU_MAX_RETRY_CONNECTION_MODEL_ACCESSIBLE
		self.interval_access = self.gv.JUJU_INTERVAL_CONNECTION_MODEL_ACCESSIBLE
		self.template_manager = template_manager.TemplateManager(global_variable)

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
	
	def add_machine(self, machine_config, service_name, mid_ro, subslice_name, model_name, cloud_name, nsi_id):
		try:
			new_machine = _VmKvm()

			new_machine.build(subslice_name,
			                  cloud_name,
			                  model_name,
			                  mid_ro,
			                  machine_config)
			loop.run(self.deploy_kvm(new_machine, service_name, subslice_name, nsi_id))
			self.machine_list.append(new_machine)
		except Exception as ex:
			raise ex
	
	async def deploy_kvm(self, new_machine, service_name, subslice_name, nsi_id):
		model = Model()
		try:
			c_name = new_machine.juju_cloud_name
			m_name = new_machine.juju_model_name
			m_user = "admin"
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
			if application_NotExist:
				ssh_key_puplic = ''.join([self.gv.SSH_KEY_DIRECTORY, self.gv.SSH_KEY_NAME, '.pub'])
				ssh_key_private = ''.join([self.gv.SSH_KEY_DIRECTORY, self.gv.SSH_KEY_NAME])
				################
				cmd_list_kvm = "uvt-kvm list"
				list_output_tmp = check_output(cmd_list_kvm, shell=True)
				list_output_tmp = (list_output_tmp.decode("utf-8")).rstrip()
				list_machine = list()
				temp_item = ""
				for item in list_output_tmp:
					if str(item).encode() == b'\n':
						list_machine.append(temp_item)
						temp_item = ""
					else:
						temp_item = "".join([temp_item, item])
				list_machine.append(temp_item)
				machine_ip = ""
				for current_machine in list_machine:
					if new_machine.mid_user_defined == current_machine:
						cmd_ip = "uvt-kvm ip " + new_machine.mid_user_defined
						output = check_output(cmd_ip, shell=True)
						machine_ip = (output.decode("utf-8")).rstrip()
						break
				###################
				if machine_ip == "":
					os.system("uvt-kvm create " +
					          new_machine.mid_user_defined +
					          " release=" + new_machine.os_series +
					          " --memory " + str(new_machine.memory) +
					          " --cpu " + str(new_machine.cpu) +
					          " --disk " + str(new_machine.disc_size) +
					          " --ssh-public-key-file " + ssh_key_puplic +
					          " --password " + self.gv.SSH_PASSWORD)
					self.logger.debug("Trying to get KVM IP")
					
					cmd_wait = "uvt-kvm wait " + new_machine.mid_user_defined
					os.system(cmd_wait)  # more time
					cmd_ip = "uvt-kvm ip " + new_machine.mid_user_defined
					output = check_output(cmd_ip, shell=True)
					machine_ip = (output.decode("utf-8")).rstrip()
				self.logger.debug(
					"The ip address of the machine {} is {}".format(new_machine.mid_user_defined, machine_ip))
				self.logger.info(
					'Adding the kvm machine {} whose ip {} to juju'.format(new_machine.mid_user_defined, machine_ip))
				await asyncio.sleep(10)
				juju_cmd = "".join(["ssh:", self.gv.SSH_USER, "@", machine_ip, ":", ssh_key_private])
				juju_machine = await model.add_machine(juju_cmd,
				                                       constraints={
					                                       'tags': [new_machine.mid_user_defined],
					                                       'virt_type': 'kvm'
				                                       }
				                                       )
			else:
				juju_machine = model.machines.get(machine_id_service)
			new_machine.mid_vnfm = juju_machine.data["id"]
			
			self.template_manager.update_slice_monitor_index("slice_monitor_" + subslice_name.lower(),
			                                                 "machine_status",
			                                                 service_name,
			                                                 "juju_mid",
			                                                 str(new_machine.mid_vnfm),
			                                                 nsi_id)
			self.template_manager.update_slice_monitor_index('slice_keys_' + nsi_id.lower(), "machine_keys",
			                                                 service_name, "juju_mid", str(new_machine.mid_vnfm),
			                                                 nsi_id)
			self.template_manager.update_slice_monitor_index("slice_monitor_" + subslice_name.lower(),
			                                                 "machine_status", service_name, "type", "kvm", nsi_id)
			
			self.logger.debug(
				"The machine {} with juju id {} is already added to juju model".format(new_machine.mid_user_defined,
				                                                                       juju_machine.data["id"]))
		except Exception as ex:
			self.logger.error(traceback.format_exc())
			raise ex
		finally:
			await model.disconnect()
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
	def allocate_machine(self):
		raise NotImplementedError()
	def release_machine(self):
		raise NotImplementedError()
	def get_stats(self):
		raise NotImplementedError()
	def validate(self):
		raise NotImplementedError()
	
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
		self.auto = False
	
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
		self.auto = False
		
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
					self.logger.critical(message)
					self.logger.info(message)
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
		"""
		every address will have the following characteristics
		self.addresses[0] = {
				"value": "ip address"
				"type": "ipv4, ipv6"
				"scope": "private, public, local-machine"
				}
		"""
		self.addresses = list()
		
		""" total resources """
		self.host_cpu_tot = 0
		self.host_mem_tot = 0
		self.host_disc_size_tot = 0
		""" available resources """
		self.host_cpu_ava = 0
		self.host_mem_ava = 0
		self.host_disc_size_ava= 0
		
		""" os characteristics """
		self.os_arch = "" # e.g. x86_64
		self.os_type = "" # e.g. linux
		self.os_dist = "" # e.g. Ubuntu
		self.os_version = "" # e.g. 16.04
		
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
	def build(self,
	          zone,
	          domain,
	          hostname,
	          dns_name,
	          status_alive,
	          status_connected,
	          set_addresses,
	          cpu_tot,
	          mem_tot,
	          disc_size_tot,
	          cpu_ava,
	          mem_ava,
	          disc_size_ava,
	          os_arch,
	          os_type,
	          os_dist,
	          os_version,
	          lxd_support,
	          kvm_support,
	          tags
	          ):
		try:
			self.zone = zone
			self.domain = domain
			self.hostname = hostname
			self.dns_name = dns_name
			self.dns_name = dns_name
			self.alive = status_alive
			self.connected = status_connected
			self.addresses = set_addresses
			
			self.host_cpu_tot = cpu_tot
			self.host_mem_tot = mem_tot
			self.host_disc_size_tot = disc_size_tot
			
			self.host_cpu_ava = cpu_ava
			self.host_mem_ava = mem_ava
			self.host_disc_size_ava = disc_size_ava
			
			self.os_arch = os_arch
			self.os_type = os_type
			self.os_dist = os_dist
			self.os_version = os_version
			
			self.virt_lxd = lxd_support
			self.virt_kvm = kvm_support
			
			# TODO to deal with tags here
			self.tags = tags
		except ValueError as ex:
			raise ex
	
	def allocate(self, subslice, machine_user_defined_name):
		self.available = False
		self.subslice_name.append(subslice)
		self.mid_user_defined.append(machine_user_defined_name)
		
	def release(self, subslice, machine_user_defined_name):
		self.available = True
		self.subslice_name.remove(subslice)
		self.mid_user_defined.remove(machine_user_defined_name)
		
	def validate(self, cloud_name, model_name, machine_config):
		raise NotImplementedError()


async def run_command(*args):
	process = await asyncio.create_subprocess_exec(
		*args[1],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)
	stdout, stderr = await process.communicate()
	return (stdout.decode("utf-8")).strip()
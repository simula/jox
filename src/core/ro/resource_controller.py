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
 * \file jox.py
 * \brief description:
 * \authors:
 * \company: Eurecom
 * \email:contact@mosaic5g.io
"""

__author__ = 'Eurecom'
__date__ = "11-January-2019"
__version__ = '1.0'
__maintainer__ = 'Osama Arouk, Navid Nikaein, Kostas Kastalis, and Rohan Kharade'
__email__ = 'contact@mosaic5g.io'
__description__ = "This responsible for managine the available resources"

import logging
import threading, time
from juju import loop
from src.core.ro import cloud

from src.core.ro.vim_driver import vimdriver


class ResourcesController(object):
	def __init__(self, global_variables):
		self.gv = global_variables
		self.jox_config = "" # jox config
		self.jclouds = list()  # List with Juju JoxClouds
		self.pop_lxc_list = list()
		self.pop_kvm_list = list()
									#full name  short name
		self.pop_type_supported = {self.gv.LXC, self.gv.KVM}
		self.machine_id = 0
		self.logger = logging.getLogger('jox.RO.rsourceController')
		self.log_config()
		self.jesearch = None
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
	def pop_register(self, pop_name, pop_type):
		if pop_type == self.gv.LXC:
			driver_object = list(filter(lambda x: x.driver_name == pop_name, self.pop_lxc_list))
			if len(driver_object):
				self.logger.error("The VIM driver {0} is already exist, please choose another one from the " \
				          "following supported VIMs: {1}".format(pop_name, self.pop_type_supported))
				return False
			else:
				new_driver = vimdriver.LxcDriver(pop_name, self.gv)
				self.pop_lxc_list.append(new_driver)
				return True
		elif pop_type == self.gv.KVM:
			driver_object = list(filter(lambda x: x.driver_name == pop_name, self.pop_kvm_list))
			if driver_object:
				self.logger.error("The VIM driver {0} is already exist, please choose another one from the "
				                  "following supported VIMs: {1}".format(pop_name, self.pop_type_supported))
				return False
			else:
				new_driver = vimdriver.KvmDriver(pop_name, self.gv)
				self.pop_kvm_list.append(new_driver)
				return True
		else:
			message = "The VIM driver {0} is not supported, please choose one of the following supported ones: {1}".format(
				pop_type, self.pop_type_supported)
			self.logger.error(message)
	def get_list_all_pop(self):
		list_all_pop = {"lxc": list(),
		                "kvm": list(),
		                }
		for pop in self.pop_lxc_list:
			list_all_pop["lxc"].append(pop.driver_name)
		for pop in self.pop_kvm_list:
			list_all_pop["kvm"].append(pop.driver_name)
		return list_all_pop
		
	def _get_pop_object(self, pop_name, pop_type):
		if pop_type == self.gv.LXC:
			for driver in self.pop_lxc_list:
				if driver.driver_name == pop_name:
					return [True, driver]
		elif pop_type == self.gv.KVM:
			for driver in self.pop_kvm_list:
				if driver.driver_name == pop_name:
					return [True, driver]
		else:
			message = "The VIM driver {0} is not supported, please choose one of the following supported ones: {1}".format(
				pop_type, self.pop_type_supported)
			self.logger.error(message)
			return [False, message]
	
	def _new_machine_id(self, pop_type):
		self.machine_id = self.machine_id + 1
		return ':'.join([str(self.machine_id), pop_type])
	
	def build(self, jox_config, jesearch):
		try:
			self.jox_config = jox_config
			self.jesearch = jesearch
		except Exception as ex:
			raise ex
	def remove_machine(self, machine_config, service_config, slice_name, subslice_name):
		vim_type = machine_config["vim_type"]
		vim_location = machine_config["vim_location"]
		machine_id_ro = machine_config["machine_name_ro"]
		
		
		currem_vim = self._get_pop_object(vim_location, vim_type)
		if currem_vim[0]:
			currem_vim = currem_vim[1]
			service_name = service_config["service_name"]
			machine_name_vnfm = machine_config["machine_name_vnfm"]
			machine_name_userdefined = machine_config["machine_name_userdefined"]
			jcloud = service_config["jcloud"]
			jmodel = service_config["jmodel"]
			user = "admin"
			loop.run(currem_vim.delete_machine(service_name, service_name,
			                                   machine_name_vnfm, machine_id_ro, machine_name_userdefined,
			                                   jcloud, jmodel, slice_name, subslice_name, user))
			
		else:
			message = "The machine {} can not be found due to the followinf error\n"
			message = ''.join([message, currem_vim[1]])
			return [False, message]
		
		pass
	def add_machines(self, machines_config, services_config, subslice_name, model_name, cloud_name, slice_name):
		threads = []
		list_midRo_machineConfig = {}
		list_machines = {} # jcloud_id <> juju id
		list_machines_id_jmodel = {} # service name <> juju id
		machine_types = list()
		try:
			service_list = list(services_config.keys())
			for service in range(len(service_list)):
				message = "Adding machine for the application {}".format(service_list[service])
				self.logger.info(message)
				
				service_name = service_list[service]
				machine_name = services_config[service_name]['machine_name']
				machine_config = machines_config[machine_name]
				
				machine_type = machines_config[machine_name]['vim_type']
				pop_name = machines_config[machine_name]['vim_location']
				if machine_type == self.gv.LXC:
					curren_driver = self._get_pop_object(pop_name, self.gv.LXC)
					if curren_driver[0]:
						curren_driver = curren_driver[1]
						if curren_driver.machine_exists(service_name):
							message[machine_config["mid_model"]] = " already in LXC machines"
							self.logger.debug(str(message))
						else:
							mid_ro = self._new_machine_id(self.gv.LXC)
							list_machines[mid_ro] = ''
							list_machines_id_jmodel[service_name] = machine_name
							machine_types.append(self.gv.LXC)
							
							self.logger.info("Adding lxc machine whose id is: machine_name= {}, mid_ro = {}".format(mid_ro, machine_config['machine_name']))
							t = threading.Thread(target=curren_driver.add_machine(machine_config,
							                                                      service_name, mid_ro,
							                                                      subslice_name, model_name, cloud_name, slice_name),daemon=True)
							list_midRo_machineConfig[mid_ro] = machine_config
							
							threads.append(t)
							t.start()
							
							message = service_name, " lxc machine added"
							self.logger.debug(message)
					else:
						self.logger.error(curren_driver[1])

				if machine_type == self.gv.KVM:
					curren_driver = self._get_pop_object(pop_name, self.gv.KVM)
					if curren_driver[0]:
						curren_driver = curren_driver[1]
						if curren_driver.machine_exists(service_name):
							message[machine_config["mid_model"]] = " already in LXC machines"
							self.logger.debug(str(message))
						else:
							mid_ro = self._new_machine_id(self.gv.KVM)
							list_machines[mid_ro] = ''
							list_machines_id_jmodel[service_name] = machine_name
							
							machine_types.append(self.gv.KVM)
							
							self.logger.info("Adding kvm machine whose id is: machine_name= {}, mid_ro = {}".format(mid_ro,
							                                                                                        machine_config[
								                                                                                        'machine_name']))
							t = threading.Thread(target=curren_driver.add_machine(machine_config, service_name, mid_ro,
							                          subslice_name, model_name, cloud_name,
							                                                      slice_name), daemon=True)
							
							
							list_midRo_machineConfig[mid_ro] = machine_config
							
							threads.append(t)
							t.start()
							
							message = service_name, " kvm machine added"
							self.logger.debug(message)
					else:
						self.logger.error(curren_driver[1])
			for th in threads:
				th.join()
			self.logger.debug("Waiting for the machines to start to deploy the services")
			if [self.gv.LXC == pop_type for pop_type in machine_types]:
				for machine_id in list_machines.keys():
					for driver in self.pop_lxc_list:
						for mid in driver.machine_list:
							if machine_id == mid.mid_ro:
								list_machines[machine_id] = mid.mid_vnfm
								list_machines_id_jmodel[mid.mid_user_defined] = mid.mid_vnfm
			if [self.gv.KVM == pop_type for pop_type in machine_types]:
				for machine_id in list_machines.keys():
					for driver in self.pop_kvm_list:
						for mid in driver.machine_list:
							if machine_id == mid.mid_ro:
								list_machines[machine_id] = mid.mid_vnfm
								list_machines_id_jmodel[mid.mid_user_defined] = mid.mid_vnfm
			return [list_machines, list_machines_id_jmodel]
		except Exception as ex:
			raise ex
	def add_cloud(self, config):
		try:
			new_jcloud = cloud.JCloud(self.gv)
			new_jcloud.build_and_deploy(config, self.jesearch)
			self.jclouds.append(new_jcloud)
			self.logger.debug("jcloud {} was added to jox".format(new_jcloud.controller_name))
		except Exception as ex:
			raise ex
		
	def get_cloud_object(self, cloud_name):
		try:
			self.jcloud = list(filter(lambda x: x.controller_name == cloud_name, self.jclouds))[0]  # find right cloud object
			if self.jcloud:
				return self.jcloud
			else:
				return None
		except Exception as ex:
			raise ex

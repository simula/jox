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

import logging
from src.core.nso.nsi.slice import JSlice
from juju import loop
class NetworkSliceController(object):
	def __init__(self, global_variables):
		self.gv = global_variables
		self.jox_config = "" # configuration of JOX
		self.slices = list() # List with jslices
		self.logger = logging.getLogger('jox.NetworkSliceController')
		self.log_config()
		
		self.resourceController = None # pointer to resource controller
		self.logger.info("Initial configuration of network slice controller")
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
	
	def build(self, resourceController, jox_config, jesearch):
		try:
			self.jesearch = jesearch
			self.jox_config = jox_config
			self.resourceController = resourceController
			self.logger.info("The resource controller is built")
		except Exception as ex:
			self.logger.error(ex)
			raise ex
	
	def get_slices_data(self):
		
		list_slices = dict()
		for slice_temp in self.slices:
			slice_name = slice_temp.slice_name
			sub_slices = slice_temp.list_NSSI
			inter_nssi_relation = slice_temp.list_inter_nssi_relations
			slice_data = {
				"slice_name": slice_name,
				"sub_slices": sub_slices,
				"inter_nssi_relation": inter_nssi_relation,
			}
			list_slices[slice_data["slice_name"]] = slice_data
		return list_slices
	def get_slice_data(self, slice_temp):
		for slice_obj in self.slices:
			if slice_obj.slice_name == slice_temp:
				slice_name = slice_obj.slice_name
				sub_slices = slice_obj.list_NSSI
				inter_nssi_relation = slice_obj.list_inter_nssi_relations
				slice_data = {
					"slice_name": slice_name,
					"sub_slices": sub_slices,
					"inter_nssi_relation": inter_nssi_relation,
				}
				return [True, slice_data]
		slice_data = "The slice {} does not exists".format(slice_temp)
		return [False, slice_data]
	def check_exist_slice(self, slice_temp):
		for slice_obj in self.slices:
			if slice_obj.slice_name == slice_temp:
				return True
		return False
	
	def add_network_slice(self, slice_name_yml, subslices_controller, nsi_dir, nssi_dir):
		self.logger.info("Adding the slice {}".format(slice_name_yml))
		new_slice = JSlice(self.gv, self.jesearch)
		build_slice = new_slice.build_jslice(slice_name_yml, nsi_dir, nssi_dir)
		if build_slice[0]:
			add_nsi = new_slice.add_slice(subslices_controller)
			if add_nsi:
				message = "The slice {} is successfully added".format(slice_name_yml)
				self.logger.info(message)
				self.slices.append(new_slice)
				return [True, message]
			else:
				message = "The slice {} is not deployed, due to the failure of adding at least one subslice".format(slice_name_yml)
				self.logger.info(message)
				self.logger.debug(message)
				self.logger.error(message)
				return [False, message]
		else:
			return build_slice
	def remove_network_slice(self, slice_name, subslices_controller, jesearch):
		slice_data = self.get_slice_data(slice_name)
		if slice_data[0]:
			slice_data = slice_data[1]
			list_subslices = slice_data['sub_slices']
			list_inter_nssi_relations = slice_data['inter_nssi_relation']
			for current_nssi in list_subslices:
				subslices_controller.destroy_subslice(current_nssi, slice_name)
				index_subslcie_monitor = ''.join(['slice_monitor_', str(current_nssi).lower()])


				if self.jesearch.ping():
					self.jesearch.del_index_from_es(current_nssi)
					self.jesearch.del_index_from_es(index_subslcie_monitor)
			for relation in list_inter_nssi_relations:
				juju_controller_a = relation['service_a']['jcloud']
				juju_model_a = relation['service_a']['jmodel']
				
				cloud_object = self.resourceController.get_cloud_object(juju_controller_a)
				juju_controller_object = cloud_object.juju_controller
				try:
					loop.run(juju_controller_object.destroy_juju_model(juju_model_a))
				except:
					pass
				
				juju_controller_b = relation['service_a']['jcloud']
				juju_model_b = relation['service_a']['jmodel']
				if (juju_controller_a != juju_controller_b) or (juju_model_a != juju_model_b):
					cloud_object = self.resourceController.get_cloud_object(juju_controller_b)
					juju_controller_object = cloud_object.juju_controller
					try:
						loop.run(juju_controller_object.destroy_juju_model(juju_model_b))
					except:
						pass
				
			self.remove_slice_object(slice_name)
			if self.jesearch.ping():
				slice_keys_tmp = ''.join(['slice_keys_tmp_', str(slice_name).lower()])
				slice_keys = ''.join(['slice_keys_', str(slice_name).lower()])
				self.jesearch.del_index_from_es(slice_name)
				self.jesearch.del_index_from_es(slice_keys_tmp)
				self.jesearch.del_index_from_es(slice_keys)
			
			return [True, "Removing the slice {} already started in the background".format(slice_name)]
		else:
			return [False, slice_data[1]]
	def remove_slice_object(self, slice_name):
		for item in self.slices:
			if item.slice_name == slice_name:
				self.slices.remove(item)
				return True
		return False
	def attach_network_slice(self):
		raise NotImplementedError()
	
	def detach_network_slice(self):
		raise NotImplementedError()

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
import traceback
from src.core.nso.nssi import subslice
logger = logging.getLogger('jox.nssiController')

class SubSlicesController(object):
	
	def __init__(self, global_variables):
		"""Definition of the JOX Network Slices Controller Class. This is the place where all NS reside"""
		self.gv = global_variables
		self.jox_config = ""
		self.subslices = list() # List with jslices
		self.resourceController = None # pointer to resource controller
		self.logger = logging.getLogger('jox.SubSlicesController')
		self.log_config()
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
	def build(self, resourceController, jox_config):
		try:
			self.resourceController = resourceController
			self.jox_config = jox_config
		except Exception as ex:
			raise ex
	
	def get_subslice_object(self, subslice_name):
		try:
			my_slice = list(filter(lambda x: x.subslice_name == subslice_name, self.subslices))[
				0]  # find correct cloud object
			if my_slice:
				return my_slice
			else:
				return None
		except Exception as ex:
			raise ex
	def remove_subslcie_object(self, subslice_name):
		for item in self.subslices:
			if item.subslice_name == subslice_name:
				self.subslices.remove(item)
				return True
		return False
	def get_subslice_runtime_data(self, subslice_name):
		if subslice_name is None:
			# get all the sub slcies
			list_subslice = dict()
			for my_slice in self.subslices:
				list_items = {
					"subslice_template_version": my_slice.subslice_template_version,
					"subslice_template_date": my_slice.subslice_template_date,
					"subslice_name": my_slice.subslice_name,
					"subslice_owner": my_slice.subslice_owner,
					"services": my_slice.subslice_services,
					"machines": my_slice.subslice_machines,
					"relations": my_slice.subslice_relations,
				}
				subslice_name = my_slice.subslice_name
				list_subslice[subslice_name] = list_items
			return [True, list_subslice]
		else:
			try:
				
				my_slice = self.get_subslice_object(subslice_name)
				list_items = {
				"subslice_template_version" : my_slice.subslice_template_version,
				"subslice_template_date" : my_slice.subslice_template_date,
				"subslice_name" : my_slice.subslice_name,
				"subslice_owner" : my_slice.subslice_owner,
				"services" : my_slice.subslice_services,
				"machines" : my_slice.subslice_machines,
				"relations" : my_slice.subslice_relations,
				}
				return [True, (list_items)]
			except Exception as ex:
				message = "There is no deployed subslice with the given name {}".format(subslice_name)
				return [False, message]
	
	def add_subslice(self, subslice_config, list_all_jujuModel_attachedWatcher):
		##
		""" The structure of subslice_config is as follows
		subslice_config = {
			"subslice_name": nssi_id,
			"slice_version": list_service_machine[2],
			"list_services": list_service_machine[0],
			"list_machines": list_service_machine[1],
		}
		"""
		try:
			new_slice = subslice.JSubSlice(self.gv)
			new_slice.build_jsubslice(subslice_config, self.resourceController, list_all_jujuModel_attachedWatcher)
			self.subslices.append(new_slice)
			logger.info("Slice %s was added", new_slice.subslice_name)
			return True
		except Exception as ex:
			logger.error(str(ex))
			logger.error(traceback.format_exc())
			return False
	
	
	def destroy_subslice(self, subslice_name, slice_name):
		subslice_data = self.get_subslice_runtime_data(subslice_name)
		if subslice_data[0]:
			subslice_object = None
			for item in self.subslices:
				if item.subslice_name == subslice_name:
					subslice_object = item
					break
			if subslice_object is None:
				return [False, "The subslice object of the subslice {} can not be found".format(subslice_name)]
			else:
				res = subslice_object.remove_jsubslice(slice_name)
				if self.remove_subslcie_object(subslice_name):
					return [True, "The subslice {} is successfully removed".format(subslice_name)]
				else:
					return [False, "The subslice {} can not be removed".format(subslice_name)]
		else:
			return [False, subslice_data[1]]
	def add_relation_intra_model(self, subslice_name, service_a, service_b, jcloud, jmodel):
		try:
			my_subslice = self.get_subslice_object(subslice_name)
			relations = my_subslice.subslice_relations
			for rel in relations:
				if (rel["source"]["service"] == service_a or rel["target"]["service"] == service_a) and \
					(rel["source"]["service"] == service_b or rel["target"]["service"] == service_b):
					message = "Relation already exist between {} and {}".format(service_a, service_b)
					self.logger.info(message)
					return[False, message]
			my_subslice.add_intra_mode_relation(service_a, service_b, jcloud, jmodel)
			model_relation = {
							"source": {
								"service": service_a,
								"juju_cloud": jcloud,
								"juju_model": jmodel
							},
							"target": {
								"service": service_b,
								"juju_cloud": jcloud,
								"juju_model": jmodel
							}
						}
			my_subslice.subslice_relations.append(model_relation)
			message = "The relation between {} and {} is successfully added".format(service_a, service_b)
			self.logger.info(message)
			return[True, message]
		except Exception as ex:
			message = "The following error while trying to add relation between {} and {}: {}".format(service_a, service_b, ex)
			message_2 = "Error: {}".format(ex)
			self.logger.info(message)
			self.logger.info(message_2)
			return[False, message]
	def remove_relation_intra_model(self, subslice_name, service_a, service_b, jcloud, jmodel):
		try:
			my_subslice = self.get_subslice_object(subslice_name)
			relations = my_subslice.subslice_relations
			for rel in relations:
				local_app = rel["source"]["service"]
				remote_app = rel["target"]["service"]
				if ":" in local_app:
					local_app = str(local_app).split(":")
					local_app = local_app[0]
				if ":" in remote_app:
					remote_app = str(remote_app).split(":")
					remote_app = remote_app[0]
				if (local_app in service_a or remote_app in service_a) and \
					(local_app in service_b or remote_app in service_b):
					message = "Removing the relation between {} and {}".format(service_a, service_b)
					self.logger.info(message)
					results = my_subslice.remove_intra_mode_relation(service_a, service_b, jcloud, jmodel)
					if results[0]: #success
						my_subslice.subslice_relations.remove(rel)
					return results
			message = "No relation found  between {} and {}".format(service_a, service_b)
			return [False, message]
			"""			
			model_relation = {
							"source": {
								"service": service_a,
								"juju_cloud": jcloud,
								"juju_model": jmodel
							},
							"target": {
								"service": service_b,
								"juju_cloud": jcloud,
								"juju_model": jmodel
							}
						}
			my_subslice.subslice_relations.append(model_relation)
			message = "The relation between {} and {} is successfully added".format(service_a, service_b)
			self.logger.info(message)
			return[True, message]
			"""
		except Exception as ex:
			message = "The following error while trying to add relation between {} and {}: {}".format(service_a, service_b, ex)
			message_2 = "Error: {}".format(ex)
			self.logger.info(message)
			self.logger.info(message_2)
			return[False, message]


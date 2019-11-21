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
from juju.model import Model
from json import JSONEncoder
from juju import loop
from src.core.nso.template_manager import template_manager
import traceback
import time

class JSlice(JSONEncoder):
	
	def __init__(self, global_variables, jesearch):
		self.gv = global_variables
		self.logger = logging.getLogger('jox.jslice')
		self.log_config()
		self.slice_template_version = ""
		self.slice_template_date = ""
		self.slice_name = ""
		self.slice_owner = ""
		self.jesearch = jesearch
		
		self.template_manager = template_manager.TemplateManager(self.gv, self.jesearch) # to analyse the template
		self.list_NSSI = None # liste of the sub-slices composing the current slice
		self.list_inter_nssi_relations = list()
		self.list_all_jujuModel_attachedWatcher = list()
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
	def build_jslice(self, slice_name_yml, nsi_dir, nssi_dir):
		
		build_slice = self.template_manager.build(slice_name_yml, nsi_dir, nssi_dir)
		if build_slice[0]:
			self.slice_name = self.template_manager.get_NSI_ID()
			self.list_NSSI = self.template_manager.get_NSSIs_ID()
			return build_slice
		else:
			return build_slice
		
	def validate_jslice_config(self):
		raise NotImplementedError()
	
	def get_inter_nssi_relations(self, add_inter_nssi_relation=False):
		try:
			self.logger.info("getting the inter relations of the slice {}".format(self.slice_name))
			return self.template_manager.get_inter_nssi_relations(add_inter_nssi_relation)
		except Exception as ex:
			self.logger.error(str(ex))
			self.logger.error(traceback.format_exc())
			raise ex
		
	def add_slice(self, subslices_controller):
		list_config_NSSI = {}
		add_nssi_success = True
		for nssi_id in self.template_manager.get_NSSIs_ID():
			list_service_machine = self.template_manager.get_NSSI_requirements(nssi_id)
			abort_deploy_subslice = list_service_machine[3]
			if abort_deploy_subslice:
				add_nssi_success = False
				return add_nssi_success
			subslice_config = {
				"slice_name": self.slice_name,
				"subslice_name": nssi_id,
				"slice_version": list_service_machine[0],
				"list_services": list_service_machine[1],
				"list_machines": list_service_machine[2],
			}
			list_config_NSSI[nssi_id] = subslice_config
			self.logger.info("trying to add the subslice {}".format(nssi_id))
			add_nssi = self.add_subslice(subslices_controller, subslice_config)
			if add_nssi:
				self.logger.info("the subslice {} is successfully added".format(nssi_id))
			else:
				add_nssi_success = False
				self.logger.info("the subslice {} is NOT added. Exit...".format(nssi_id))

		self.logger.info("adding entre-nssi relations")
		Inter_relations = self.get_inter_nssi_relations(True)
		self.add_Inter_NSSI_relation(Inter_relations, list_config_NSSI)
		return add_nssi_success
	def add_Inter_NSSI_relation(self, Inter_relations, list_config_NSSI):
		for relation in Inter_relations:
			"""
			Inter_relations[relation] = {
				'nssi_source': nssi_source,
				'nssi_node_source': nssi_node_source,
				'nssi_node_source_charm_name': nssi_node_source_charm_name,
				'nssi_target': nssi_target,
				'nssi_node_target': nssi_node_target,
				'nssi_node_target_charm_name': nssi_node_target_charm_name

			}
			"""
			nssi_source = Inter_relations[relation]['nssi_source']
			nssi_node_source = Inter_relations[relation]['nssi_node_source']
			nssi_node_source_charm_name = Inter_relations[relation]['nssi_node_source_charm_name']

			nssi_target = Inter_relations[relation]['nssi_target']
			nssi_node_target = Inter_relations[relation]['nssi_node_target']
			nssi_node_target_charm_name = Inter_relations[relation]['nssi_node_target_charm_name']

			cloud_credential = self.get_cloud_credential(list_config_NSSI, nssi_source, nssi_node_source)
			if not cloud_credential:
				self.logger.error("No cloud credentional found for service {} in the nssi {}".format(nssi_node_target, nssi_target))
				credential_source = False
			else:
				credential_source = True
				source_jcloud = cloud_credential[0]
				source_jmodel = cloud_credential[1]
			
			cloud_credential = self.get_cloud_credential(list_config_NSSI, nssi_target, nssi_node_target)
			if not cloud_credential:
				self.logger.error("No cloud credentional found for service {} in the nssi {}".format(nssi_node_target, nssi_target))
				credential_target = False
			else:
				credential_target = True
				target_jcloud = cloud_credential[0]
				target_jmodel = cloud_credential[1]
			if credential_source and credential_target:
				if source_jcloud == target_jcloud and source_jmodel == target_jmodel:
					message = "adding relation between {} from the nssi {} and {} from the nssi {}".format(nssi_node_source, nssi_source, nssi_node_target, nssi_target)
					self.logger.debug(message)
					time.sleep(10)
					#loop.run(self.add_relation_interNssi_IntraModel(nssi_source, source_jcloud, source_jmodel, nssi_node_source,
					#											nssi_target, target_jcloud, target_jmodel, nssi_node_target))
					loop.run(self.add_relation_interNssi_IntraModel(source_jcloud, source_jmodel, nssi_source, nssi_node_source,
																nssi_target, nssi_node_target))
				else:
					message = "adding relation between {} from the nssi {} hosted in {}:{} and {} from the nssi {} hosted in {}:{}".format(nssi_node_source,
									nssi_source, source_jcloud, source_jmodel, nssi_node_target, nssi_target, target_jcloud, target_jmodel)
					self.logger.debug(message)
					loop.run(self.add_relation_interNssi_interModel(nssi_source, source_jcloud, source_jmodel, nssi_node_source, nssi_node_source_charm_name, nssi_target, target_jcloud, target_jmodel, nssi_node_target, nssi_node_target_charm_name))

	async def add_relation_interNssi_IntraModel(self, source_jcloud, source_jmodel, nssi_source, nssi_node_source,
																nssi_target, nssi_node_target):
		if ":" in nssi_node_source:
			local_app = str(nssi_node_source).split(":")
			local_app = local_app[0]
		else:
			local_app = nssi_node_source
		if ":" in nssi_node_target:
			remote_app = str(nssi_node_target).split(":")
			remote_app = remote_app[0]
		else:
			remote_app = nssi_node_target
		for rel in self.list_inter_nssi_relations:
			if ((rel["service_a"]["nssi"] == nssi_source and local_app in rel["service_a"]["service"]) or \
				(rel["service_b"]["nssi"] == nssi_source and local_app in rel["service_b"]["service"])) \
				and \
				((rel["service_a"]["nssi"] == nssi_target and remote_app in rel["service_a"]["service"]) or \
				(rel["service_b"]["nssi"] == nssi_target and remote_app in rel["service_b"]["service"]))  \
				and \
				(rel["service_a"]["jcloud"] == source_jcloud and rel["service_a"]["jmodel"] == source_jmodel):
				message = "The relation between {}:{} and {}:{} already exist".format(nssi_source, nssi_node_source, nssi_target, nssi_node_target)
				return[False, message]
		try:
			model = Model()
			c_name = source_jcloud
			m_name = source_jmodel
			model_name = c_name + ":" + m_name
			await model.connect(model_name)
			await model.add_relation(nssi_node_source, nssi_node_target)
			relation = {
			"service_a": {
				"nssi": nssi_source,
				"jcloud": source_jcloud,
				"jmodel": source_jmodel,
				"service": nssi_node_source,
			},
			"service_b": {
				"nssi": nssi_target,
				"jcloud": source_jcloud,
				"jmodel": source_jmodel,
				"service": nssi_node_target,
			}}
			self.list_inter_nssi_relations.append(relation)
			message = "Successful add the relation between {}:{} and {}:{} already exist".format(nssi_source, nssi_node_source, nssi_target, nssi_node_target)
			return[True, message]
		except Exception as ex:
			message = "Error while trying to add relation between {}:{} and {}:{}. Error: {}".format(nssi_source, nssi_node_source, nssi_target, nssi_node_target, ex)
			self.logger.error(message)
			self.logger.debug(message)
			return[False, message]
		finally:
			await model.disconnect()
	async def add_relation_interNssi_interModel(self, nssi_source, source_jcloud, source_jmodel, nssi_node_source, nssi_node_source_charm_name,
	                                      nssi_target, target_jcloud, target_jmodel, nssi_node_target, nssi_node_target_charm_name):
		set_relations = {
			"mysql":{
				"oai-hss":[":db", ":db"],
				"wordpress":[":db", ":db"],
			},
			"wordpress": {
				"mysql": [":db", ":db"],
			},
			"oai-enb": {
				"oai-mme": [":mme", ":mme"],
				"flexran-rtc": [":rtc", ":rtc"],
			},
			"oai-hss": {
				"mysql": [":db", ":db"],
				"oai-mme": [":hss", ":hss"],
			},
			"oai-mme": {
				"oai-hss": [":hss", ":hss"],
				"oai-spgw": [":spgw", ":spgw"],
				"oai-enb": [":mme", ":mme"],
			},
			"flexran-rtc": {
				"oai-enb": [":rtc", ":rtc"],
			},
		}
		from src.core.ro.vim_driver.vimdriver import run_command

		try:
			#relation_endpoint_source = set_relations[nssi_node_source][nssi_node_target]
			relation_endpoint_source = set_relations[nssi_node_source_charm_name][nssi_node_target_charm_name]
			relation_endpoint_target = '{}{}'.format(nssi_node_target, relation_endpoint_source[1])
			#relation_endpoint_source = relation_endpoint_source[0]
			relation_endpoint_source = '{}{}'.format(nssi_node_source, relation_endpoint_source[0])
			# relation_endpoint_target = set_relations[nssi_node_target][nssi_node_source]
		except:
			relation_endpoint_target = '{}:{}'.format(nssi_node_target, nssi_node_target)
			relation_endpoint_source = '{}:{}'.format(nssi_node_source, nssi_node_target)

		cmd_juju_offer_application_endpoint = ["juju", "offer",
											   "-c", "{}".format(target_jcloud),
											   relation_endpoint_target]
		cmd_juju_add_cmr = ["juju", "add-relation",
							"-m", "{}:{}".format(source_jcloud, source_jmodel),
							relation_endpoint_source,
							"{}:{}/{}.{}".format(target_jcloud, "admin", target_jmodel, nssi_node_target)]

		cmd_juju_switch_to_target_model = ["juju", "switch", "{}:{}".format(target_jcloud, target_jmodel)]
		cmd_juju_switch_to_source_model = ["juju", "switch", "{}:{}".format(source_jcloud, source_jmodel)]


		cmd_out_juju_switch_to_target_model = await run_command(cmd_juju_switch_to_target_model)
		cmd_out_offer_app_endpoint = await run_command(cmd_juju_offer_application_endpoint)

		cmd_out_juju_switch_to_source_model = await run_command(cmd_juju_switch_to_source_model)
		cmd_out_add_cmr = await run_command(cmd_juju_add_cmr)

		relation = {
			"service_a": {
				"nssi": nssi_source,
				"jcloud": source_jcloud,
				"jmodel": source_jmodel,
				"service": nssi_node_source,
			},
			"service_b": {
				"nssi": nssi_target,
				"jcloud": target_jcloud,
				"jmodel": target_jmodel,
				"service": nssi_node_target,
			}}
		self.list_inter_nssi_relations.append(relation)
		"""
        juju offer mysql:db
        juju bootstrap localhost lxd-cmr-2
        juju add-model cmr-model-2
        juju deploy mediawiki
        juju add-relation mediawiki:db lxd-cmr-1:admin/cmr-model-1.mysql
        """

	def get_cloud_credential(self, list_config_NSSI, nssi_target, nssi_node_target):
		for service in list_config_NSSI[nssi_target]['list_services']:
			if service == nssi_node_target:
				jcloud = list_config_NSSI[nssi_target]['list_services'][service]['jcloud']
				jmodel = list_config_NSSI[nssi_target]['list_services'][service]['jmodel']
				return [jcloud, jmodel]
		return False

	def add_subslice(self, subslices_controller, subslice_config):
		add_nssi = subslices_controller.add_subslice(subslice_config, self.list_all_jujuModel_attachedWatcher)
		return add_nssi
	def attache_subslice(self): # attache the current slice to already exist NSSI
		raise NotImplementedError()
	def dettache_subslice(self):# dettache from a certain NSSI. After that the NSSI is still alive and can be used by other NSIs
		raise NotImplementedError()
	def destroy_slice(self):
		raise NotImplementedError()
	
	def delete_jmodel(self, model_name):
		from  src.core.nso.plugins.juju2_plugin import Model
		jmodel = self.get_jmodel_object(model_name)
		jmodel_uuid = jmodel.juju_model_uuid
		loop.run(jmodel.jcloud.juju_controller.destroy_juju_model(jmodel_uuid))
		self.subslice_models.remove(jmodel)







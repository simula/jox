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

import os
import logging

logger = logging.getLogger('jox.templateManager')


dir_path = os.path.dirname(os.path.abspath(__file__ + "/../../../"))
import json, yaml
from core.ro.plugins import es
from elasticsearch import Elasticsearch
import datetime, time

service_keys = {}    # local key dictionary for slice component's context matching
machine_keys = {}
relation_keys = {}

dsl_definitions = {
	"host":{
			"tiny":{
				"disk_size": 5, #GB
				"num_cpus": 1,
				"mem_size": 512, #MB
			},
			"small":{
				"disk_size": 5, #GB
				"num_cpus": 1,
				"mem_size": 512, #MB
			}
		},
	"os":{
			"ubuntu_14_64":{
				"architecture": "x86_64",
				"type": "Linux",
				"distribution": "Ubuntu",
				"version": "14.04"
			},
			"ubuntu_16_64":{
				"architecture": "x86_64",
				"type": "Linux",
				"distribution": "Ubuntu",
				"version": "16.04"
			},
			"ubuntu_18_64":{
				"architecture": "x86_64",
				"type": "Linux",
				"distribution": "Ubuntu",
				"version": "18.04"
			}
		},
}
class TemplateManager():

	def __init__(self, global_variables):
		self.gv = global_variables
		self.es_host = self.gv.ELASTICSEARCH_HOSt
		self.es_port = self.gv.ELASTICSEARCH_PORT
		self.es_log_level = self.gv.ELASTICSEARCH_LOG_LEVEL
		self.es_retry_on_conflict = self.gv.ELASTICSEARCH_RETRY_ON_CONFLICT
		
		self.NSI_ID = None
		self.NSSI_ID = list()
		self.map_userNssiId_NssiId = {}
		self.NSI_template = None
		self.NSSI_template = list()
		self.jesearch = None

		es.del_all_from_es(self.es_host, self.es_port, 'slice_keys')
		
		self.logger = logging.getLogger('jox.TemplateManager')
		self.log_config()
	def log_config(self):
		if self.es_log_level == 'debug':
			self.logger.setLevel(logging.DEBUG)
		elif self.es_log_level == 'info':
			self.logger.setLevel(logging.INFO)
		elif self.es_log_level == 'warn':
			self.logger.setLevel(logging.WARNING)
		elif self.es_log_level == 'error':
			self.logger.setLevel(logging.ERROR)
		elif self.es_log_level == 'critic':
			self.logger.setLevel(logging.CRITICAL)
		else:
			self.logger.setLevel(logging.INFO)
	def build(self, slice_name_yml, nsi_dir, nssi_dir):

                self.jesearch = es.JESearch(self.es_host, self.es_host, self.es_log_level)
                slice_full_path = ''.join([nsi_dir, slice_name_yml])
                try:
                        with open(slice_full_path) as stream:
                                slice_data_file = yaml.safe_load(stream)
                except:
                        message = "Error while trying to load the slice template {}".format(slice_full_path)
                        self.logger.error(message)
                        return [False, message]
                
                slice_data_file['metadata']['date'] = str(slice_data_file['metadata']['date'])
                self.NSI_template = slice_data_file
                self.NSI_ID = slice_data_file['metadata']['ID']
                self.set_NSI_monitor_index(self.NSI_ID)
                message = "Deleting the index {} from elasticsearch if alredy exist".format((self.NSI_ID).lower())
                logger.info(message)
                logger.debug(message)
                self.jesearch.del_index_from_es((self.NSI_ID).lower())
                message = "Saving the index {} to elasticsearch".format((self.NSI_ID).lower())
                logger.info(message)
                logger.debug(message)
                self.jesearch.set_json_to_es(self.NSI_ID, slice_data_file)

                for sub_slice in self.NSI_template['imports']:
                        subslice_name_yml = ''.join([nssi_dir, sub_slice, '.', 'yaml'])
                        try:
                                with open(subslice_name_yml) as stream:
                                        subslice_data_file = yaml.safe_load(stream)
                        except:
                                message = "Error while trying to load the subslice template {}".format(subslice_name_yml)
                                self.logger.error(message)
                                return [False, message]

                        subslice_data_file['metadata']['date'] = str(subslice_data_file['metadata']['date'])

                        nssi_id = subslice_data_file['metadata']['ID']
                        self.NSSI_template.append(subslice_data_file)
                        self.NSSI_ID.append(nssi_id)

                        message = "Deleting the index {} from elasticsearch if already exist".format(nssi_id)
                        logger.info(message)
                        logger.debug(message)
                        self.jesearch.del_index_from_es(nssi_id)

                        message = "Saving the index {} to elasticsearch".format(nssi_id)
                        logger.info(message)
                        logger.debug(message)
                        self.jesearch.set_json_to_es(nssi_id, subslice_data_file)

                message = "the slice {} is successfully deployed".format(slice_name_yml)
                return [True, message]
	def get_NSSIs_ID(self): # return the IDs of the NSSI composing the NSI
		return self.NSSI_ID
	def get_NSI_ID(self): # return the ID of the NSI
		return self.NSI_ID

	def get_NSI_requirements(self):
		list_name_id_nssi = {}
		for item in self.NSI_template['topology_template']['node_templates']:
			if 'NSSI' in self.NSI_template['topology_template']['node_templates'][item]['type']:
				req = self.NSI_template['topology_template']['node_templates'][item]['requirements']

				nssi_id = req['nssi']
				if nssi_id not in  self.NSSI_ID:
					message = "The NSSI {} should be defined in imports".format(nssi_id)
					logger.error(message)
				list_name_id_nssi[item] = nssi_id
			else:
				message = "The node_templates shoud define NSSI"
				logger.error(message)
		inter_nssi_relation = {}
		for item in self.NSI_template['relationships_template']:
			inter_nssi_relation[item] = {
				'source': {
					'nssi': None,
					'node': None
				},
				'target': {
					'nssi': None,
					'node': None
				}
			}

			nssi_name = self.NSI_template['relationships_template'][item]['source']['node']
			inter_nssi_relation[item]['source']['nssi'] = list_name_id_nssi[nssi_name]
			inter_nssi_relation[item]['source']['node'] = self.NSI_template['relationships_template'][item]['source']['inputs']['node']


			nssi_name = self.NSI_template['relationships_template'][item]['target']['node']
			inter_nssi_relation[item]['target']['nssi'] = list_name_id_nssi[nssi_name]
			inter_nssi_relation[item]['target']['node'] = self.NSI_template['relationships_template'][item]['target']['inputs']['node']
		return inter_nssi_relation

	def get_NSSI_requirements(self, nssi_id):
		NSSI_template = self.get_NSSI_object(nssi_id)
		list_services = {}
		list_machines = {}
		slice_version = NSSI_template['metadata']['version']
		for item in NSSI_template['topology_template']['node_templates']:

			if 'JOX' in NSSI_template['topology_template']['node_templates'][item]['type']:
				app_name = item
				charm = NSSI_template['topology_template']['node_templates'][item]['properties']['charm']
				jcloud = NSSI_template['topology_template']['node_templates'][item]['properties']['endpoint']
				jmodel = NSSI_template['topology_template']['node_templates'][item]['properties']['model']
				list_services[app_name] = {
					'service_name':app_name,
					'jcloud': jcloud,
					'jmodel': jmodel,
					'charm': charm,
					'machine_name': None,
					'relation': None,
				}
				#  check the requirements
				for req in NSSI_template['topology_template']['node_templates'][item]['requirements']:
					if 'HostedOn' in NSSI_template['topology_template']['node_templates'][item]['requirements'][req]['relationship']:
						# the required machine to host the applications
						machine_name = NSSI_template['topology_template']['node_templates'][item]['requirements'][req]['node']
						list_services[app_name]['machine_name'] = machine_name
					elif 'AttachesTo' in NSSI_template['topology_template']['node_templates'][item]['requirements'][req]['relationship']:
						# relation
						relation = NSSI_template['topology_template']['node_templates'][item]['requirements'][req]['node']
						list_services[app_name]['relation'] = relation
					else:
						raise NotImplementedError

			if 'Compute' in NSSI_template['topology_template']['node_templates'][item]['type']:
				machine_name = item
				list_machines[machine_name] = {
					'machine_name':machine_name,
					'host': None,
					'os': None,
					'vim_type': None,
					'vim_location': None,
				}
				host = NSSI_template['topology_template']['node_templates'][item]['capabilities']['host']['properties']
				os_sys = NSSI_template['topology_template']['node_templates'][item]['capabilities']['os']['properties']
				for item_tmp in dsl_definitions: #
					if item_tmp == 'host':
						for sub_item_tmp in dsl_definitions[item_tmp]:
							if host == sub_item_tmp:
								host = dsl_definitions[item_tmp][sub_item_tmp]
					if item_tmp == 'os':
						for sub_item_tmp in dsl_definitions[item_tmp]:
							if os_sys == sub_item_tmp:
								os_sys = dsl_definitions[item_tmp][sub_item_tmp]
				
				list_machines[machine_name]['host'] = host
				
				list_machines[machine_name]['os'] = os_sys
				vim_type = NSSI_template['topology_template']['node_templates'][item]['artifacts']['sw_image']['properties']['supported_virtualisation_environments']['type']
				list_machines[machine_name]['vim_type'] = vim_type
				vim_location = NSSI_template['topology_template']['node_templates'][item]['artifacts']['sw_image']['properties']['supported_virtualisation_environments']['entry_schema']
				list_machines[machine_name]['vim_location'] = vim_location

		self.set_NSSI_monitor_index(nssi_id, self.get_NSI_ID(), list_services, list_machines) # Add monitoring template for this subslice
		return [slice_version, list_services, list_machines]

	def get_inter_nssi_relations(self):
		Inter_relations = {}
		for relation in self.NSI_template['relationships_template']:
			nssi_source = self.NSI_template['relationships_template'][relation]['source']['parameters']
			nssi_node_source = self.NSI_template['relationships_template'][relation]['source']['inputs']['node']

			nssi_target = self.NSI_template['relationships_template'][relation]['target']['parameters']
			nssi_node_target = self.NSI_template['relationships_template'][relation]['target']['inputs']['node']

			Inter_relations[relation] = {
				'nssi_source': nssi_source,
				'nssi_node_source': nssi_node_source,
				'nssi_target': nssi_target,
				'nssi_node_target': nssi_node_target
			}
		return Inter_relations

	def get_NSSI_object(self, nssi_id):
		for nssi_template in self.NSSI_template:
			if nssi_template['metadata']['ID'] == nssi_id:
				return nssi_template

	def set_NSI_monitor_index(self, nsi_id):
		date = (datetime.datetime.now()).isoformat()
		slice_skeleton = {"date": date,
							"machine_keys": [],
							"service_keys": [],
							"relation_keys": []} # Relation key not required for now
		es.del_all_from_es(self.es_host, self.es_port, 'slice_keys_'+nsi_id.lower()) # this is per  slice index (runtime updates)
		es.set_json_to_es(self.es_host, self.es_port, 'slice_keys_'+nsi_id.lower(), slice_skeleton)

		es.del_all_from_es(self.es_host, self.es_port, 'slice_keys_tmp_'+nsi_id.lower()) # this is per  slice index (runtime updates)
		es.set_json_to_es(self.es_host, self.es_port, 'slice_keys_tmp_'+nsi_id.lower(), slice_skeleton)


	def set_NSSI_monitor_index(self, nssi_id, nsi_id, list_services, list_machines):
		es.del_all_from_es(self.es_host, self.es_port, 'slice_monitor_'+nssi_id.lower()) # this is per sub slice index (runtime updates)
		services_list = []
		machines_list = []
		relations_list = []
		date = (datetime.datetime.now()).isoformat()

		slice_skeleton = {"date": date,
							"machine_status": [],
							"service_status": [],
							"relation_status": []}  # Create Empty container
		es.set_json_to_es(self.es_host, self.es_port, 'slice_monitor_'+nssi_id.lower(), slice_skeleton)
		service_list = list(list_services.keys())  # List of applications
		ES = Elasticsearch([{'host': self.es_host, 'port': self.es_port, 'use_ssl': False}])
		for service in range(len(service_list)):
			service_name = {service_list[service]: [{"date": date,
													 "waiting": "0",
													 "maintenance": "0",
													 "active_since": "0",
													 "requirement_wait": "0",
													 "error": "0",
													 "nss_id": nsi_id,
													 "nssi_id": nssi_id
													 }]}
			services_list.append(service_name)
		ES.update(index='slice_monitor_'+nssi_id.lower(), doc_type='post', id=1,
				  body={'doc': {'service_status': services_list}}, retry_on_conflict=0)
		for service in range(len(service_list)):
			service_name = {service_list[service]: [{"date": date,
													 "nssi_id": nssi_id
													 }]}

			tmp_data = service_keys.copy()
			if bool(service_keys) == False:                    # Update local list & check if list is empty
				service_keys.update({nsi_id: [{'service_keys': [service_name]}]})
			else:
				key_list = tmp_data[nsi_id][0]['service_keys']
				data = []
				for num in range(len((list(tmp_data.keys())))):
					if (list(tmp_data.keys())[num]) == nsi_id:
						for num in range(len(key_list)):
							data.append(key_list[num])
				data.append(service_name)
				service_keys.update({nsi_id: [{'service_keys': data}]})  # Update local list
		ES.update(index='slice_keys_'+(self.get_NSI_ID()).lower(), doc_type='post', id=1,
				  body={'doc': {'service_keys': service_keys[nsi_id][0]['service_keys']}}, retry_on_conflict=0)

		for machine in range(len(service_list)):
			machine_name = {service_list[machine]: [{"date":date,
													 "juju_mid":"0",
													 "nss_id": nsi_id,
													 "nssi_id": nssi_id,
													 "type":"0",
                                                     "down":"0",
													 "address_ipv4_public":"0",
                                                     "launch_time":"0"
                                                     }]}
			machines_list.append(machine_name)
		ES.update(index='slice_monitor_'+nssi_id.lower(), doc_type='post', id=1,   # Putting in subslice index
				  body={'doc': {'machine_status': machines_list	}}, retry_on_conflict=0)

		for machine in range(len(service_list)):
			machine_name = {service_list[machine]: [{"date": date,
													 "juju_mid":"0",
													 "nsi_id": nsi_id,
													 "nssi_id": nssi_id
													 }]}
			tmp_data = machine_keys.copy()
			if bool(machine_keys)==False:          # Update local list & check if list is empty
				machine_keys.update({nsi_id: [{'machine_keys': [machine_name]}]})
			else:
				key_list = tmp_data[nsi_id][0]['machine_keys']
				data = []
				for num in range(len((list(tmp_data.keys())))):
					if (list(tmp_data.keys())[num]) == nsi_id:
						for num in range(len(key_list)):
							data.append(key_list[num])
				data.append(machine_name)
				machine_keys.update({nsi_id:[{'machine_keys':data}]})  # Update local list
		ES.update(index='slice_keys_' + (self.get_NSI_ID()).lower(), doc_type='post', id=1,
				  body={'doc': {'machine_keys': machine_keys[nsi_id][0]['machine_keys']}}, retry_on_conflict=0)


		for machine in range(len(service_list)):
			machine_name = {service_list[machine]: [{"date": date,
													 "nsi_id": nsi_id,
													 "nssi_id": nssi_id,
													 "requirement_wait": "0",
													 "requirement": list_services[service_list[machine]]['relation']
													 }]}
			relations_list.append(machine_name)
		ES.update(index='slice_monitor_'+ nssi_id.lower(), doc_type='post', id=1,  # Putting in subslice index
				  body={'doc': {'relation_status': relations_list}}, retry_on_conflict=0)



	def update_slice_monitor_index(self, index_page, container_type, container_name, leaf_key, leaf_value, nsi_id):
		slice_data = self.jesearch.get_json_from_es(self.es_host, self.es_port, index_page, container_type)
		for machines in range(len(slice_data)):  # Update the container
			machines_list = slice_data[machines]
			machine = list(machines_list.keys())
			for num in range(len(machine)):
				if machine[num] == container_name:
					slice_data[machines][container_name][0][leaf_key] = leaf_value
		ES = Elasticsearch([{'host': self.es_host, 'port': self.es_port, 'use_ssl': False}])
		ES.update(index=index_page, doc_type='post', id=1,  # Push the container with updates
				  body={'doc': {container_type: slice_data}}, retry_on_conflict=0)

		if container_type=="machine_keys":
			machine_keys[nsi_id][0]['machine_keys'].clear()
			for machine in range(len(slice_data)):
				machine_keys[nsi_id][0]['machine_keys'].append(slice_data[machine])
		if container_type=="service_keys":
			service_keys[nsi_id][0]['service_keys'][0].clear()
			for service in range(len(slice_data)):
				service_keys[nsi_id][0]['service_keys'].append(slice_data[service])



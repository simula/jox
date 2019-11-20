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

import jsonpickle
import json
import logging

from src.core.nso.nssi.model import JModel
from json import JSONEncoder
from juju import loop
        
class JSubSlice(JSONEncoder):
    def __init__(self, global_variables):
        self.gv = global_variables
        
        self.subslice_services =list()
        self.subslice_machines =list()
        self.subslice_relations =list()
        
        self.slice_data = list()
        # parameters related to the subslice
        self.logger = logging.getLogger('jox.subslice')
        self.log_config()
        self.slice_name = None
        self.subslice_template_version = ""
        self.subslice_template_date = ""
        self.subslice_name = ""
        self.subslice_owner = ""
        self.subslice_models =list() #List with model objects
        self.jclouds=None # a pointer to jclouds that is hosted under resourceController
        self.resourceController=None # a pointer to resourceController
        self.list_crossModelRelations = list()

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
    def build_jsubslice(self, subslice_config, resourceController, list_all_jujuModel_attachedWatcher): #
        """
        subslice_config = {
            "slice_name" :self.template_manager.get_NSI_ID,
        	"subslice_name": nssi_id,
        	"slice_name": nssi_id,
        	"slice_version": ,
        	"list_services": ,
        	"list_machines": ,
        }
        """
        try:
            self.slice_name = subslice_config["slice_name"]
            self.subslice_name = subslice_config["subslice_name"]
            self.subslice_template_version = subslice_config["slice_version"]
            self.jclouds=resourceController.jclouds
            self.resourceController=resourceController
            self.subslice_services = subslice_config["list_services"]
            for item in subslice_config["list_machines"]:
                machine = subslice_config["list_machines"][item]
                host_machine = None
                if machine['additional_requirements']['attributes'] is not None:
                    if 'attributes' in machine['additional_requirements'].keys():
                        host_machine = machine['additional_requirements']['attributes']['host']
                cidr = None
                domain = None
                if machine['additional_requirements']['properties'] is not None:
                    if 'network' in machine['additional_requirements']['properties'].keys():
                        if 'subnet' in machine['additional_requirements']['properties']['network'].keys():
                            domain = machine['additional_requirements']['properties']['network']['subnet']
                        if 'cidr' in machine['additional_requirements']['properties']['network'].keys():
                            cidr = machine['additional_requirements']['properties']['network']['cidr']
                pass
                new_machine = {
					'machine_name_userdefined': machine["machine_name"],
					'machine_name_vnfm': None,
					'machine_name_ro': None,
					'vim_type': machine["vim_type"],
					'vim_location': machine["vim_location"],
                    'zone':machine['additional_requirements']['policies']['region_placement'],
                    'domain':domain,
                    'cidr':cidr,
                    'host_machine':host_machine,
				    }
                self.subslice_machines.append(new_machine)
            # add the models on which the services of the current NSSI will be deployed
            self.logger.info("add the models on which the services of the  NSSI {} will be deployed".format(self.subslice_name))
            self.add_models(subslice_config, resourceController, list_all_jujuModel_attachedWatcher)
        except Exception as ex:
            raise ex
    
    def remove_jsubslice(self, slice_name):
        
        """
        self.subslice_services =list()
        self.subslice_machines =list()
        self.subslice_relations =list()
        self.list_crossModelRelations = list()
        """
        if len(self.list_crossModelRelations) > 0:
            raise NotImplementedError
        if len(self.subslice_services) > 0:
            for service_name in self.subslice_services:
                service_config = self.subslice_services[service_name]
                current_model = None
                service_model = None
                for subslice_model in self.subslice_models:
                    if (subslice_model.cloud_name == service_config["jcloud"])  \
                            and (subslice_model.model_name == service_config["jmodel"]):
                        current_model = subslice_model
                        for item in current_model.services:
                            if item.application_name == service_name:
                                service_model = item
                                break
                
                
                machine_name_userdefined = service_config["machine_name"]
                machine_config = self.get_machine_vnfm_id(machine_name_userdefined)
                if machine_config[0]:
                    # delete service
                    machine_config = machine_config[1]
                    self.resourceController.remove_machine(machine_config, service_config,
                                                           slice_name, self.subslice_name)
                else:
                    # machine not found for the corresponding service
                    message = machine_config[1]
                    pass
                if current_model is not None:
                    loop.run(current_model.destroy_service(service_model.application_name))
        if len(self.subslice_machines) > 0:
            pass
            # relove relations
    def get_machine_vnfm_id(self, machine_name_userdefined):
        for item in self.subslice_machines:
            if item["machine_name_userdefined"] == machine_name_userdefined:
                return [True, item]
        return [False, "machine_vnfm_id not found"]
    def validate_jslice_config(self,subslice_config):
        raise NotImplementedError()

                    
    def add_models(self, subslice_config, resourceController, list_all_jujuModel_attachedWatcher):
        """
        subslice_config = {
            "slice_name": nssi_id,
            "slice_version": list_service_machine[0],
            "list_services": list_service_machine[1],
            "list_machines": list_service_machine[2],
        }
        """
        try:
            list_service = subslice_config["list_services"].keys()
            list_crossModelRelation = list()
            for service_model in subslice_config["list_services"]:
                juju_cloud = subslice_config["list_services"][service_model]['jcloud']
                juju_model = subslice_config["list_services"][service_model]['jmodel']
                # get inter-model relation if any
                try:
                    relation_node = subslice_config["list_services"][service_model]['relation']
                    # search for the cross model relations for among the models of the current NSSI only
                    if len(relation_node) > 0:
                        for service_target in relation_node:
                            if service_target in list_service:
                                juju_cloud_service_target = subslice_config["list_services"][service_target]['jcloud']
                                juju_model_service_target = subslice_config["list_services"][service_target]['jmodel']
                                model_relation = {
                                    "source": {
                                        "service": service_model,
                                        "juju_cloud": juju_cloud,
                                        "juju_model": juju_model
                                    },
                                    "target": {
                                        "service": service_target,
                                        "juju_cloud": juju_cloud_service_target,
                                        "juju_model": juju_model_service_target
                                    }
                                }
                                self.subslice_relations.append(model_relation)
                                if juju_cloud != juju_cloud_service_target or juju_model != juju_model_service_target:
                                    list_crossModelRelation.append(model_relation)
                            # pass
                    # if relation_node in list_service:
                    #     juju_cloud_relation_node = subslice_config["list_services"][relation_node]['jcloud']
                    #     juju_model_relation_node = subslice_config["list_services"][relation_node]['jmodel']
                    #     model_relation = {
                    #         "source": {
                    #             "service": service_model,
                    #             "juju_cloud": juju_cloud,
                    #             "juju_model": juju_model
                    #         },
                    #         "target": {
                    #             "service": relation_node,
                    #             "juju_cloud": juju_cloud_relation_node,
                    #             "juju_model": juju_model_relation_node
                    #         }
                    #     }
                    #     self.subslice_relations.append(model_relation)
                    #     if juju_cloud != juju_cloud_relation_node or juju_model != juju_model_relation_node:
                    #         list_crossModelRelation.append(model_relation)
                except Exception as ex:
                    raise ex
                if not self.check_existence_model(juju_cloud, juju_model):
                    self.add_model(subslice_config, resourceController, juju_cloud, juju_model, list_all_jujuModel_attachedWatcher)
                else:
                    self.logger.debug("The model {} under the juju controller {} is already added".format(juju_model, juju_cloud))
            """
            if len(list_crossModelRelation) > 0:
                self.add_cross_model_relations(list_crossModelRelation)
            """
        except Exception as ex:
            raise ex
                     
    def add_model(self, model_config, resourceController, juju_cloud, juju_model, list_all_jujuModel_attachedWatcher):
        try:
            Watcher_attached = False
            for item in  list_all_jujuModel_attachedWatcher:
                if (item["juju_cloud"] == juju_cloud) and (item["juju_model"] == juju_model):
                    Watcher_attached = True
                    break
            if not Watcher_attached:
                jujuModel_attacheWatcher = {
                    "juju_cloud": juju_cloud,
                    "juju_model": juju_model,
                    "Watcher_attached": True,
                }
                list_all_jujuModel_attachedWatcher.append(jujuModel_attacheWatcher)
            
            new_model = JModel(self.gv)
            new_model.cloud_name = juju_cloud
            new_model.model_name = juju_model
            new_model.build_and_deploy(model_config, self.jclouds, self.subslice_name, self.slice_name,
                                       resourceController, juju_cloud, juju_model, Watcher_attached, self.subslice_machines)
            self.subslice_models.append(new_model)
        except Exception as ex:
            raise ex
    def add_intra_mode_relation(self, service_a, service_b, jcloud, jmodel):

        for current_model in self.subslice_models:
            #print("Current model: cloud={} and model={}".format(current_model.cloud_name, current_model.model_name))
            if jcloud == current_model.cloud_name and jmodel == current_model.model_name:
                #print("Adding relation between {} and {} in juju cloud {} and juju model {}".format(service_a, service_b, jcloud, jmodel))
                self.logger.info("Adding relation between {} and {} in juju cloud {} and juju model {}".format(service_a, service_b, jcloud, jmodel))
                current_model.add_relation_intramodel(service_a, service_b, jcloud, jmodel)
                #print("Relation is added between {} and {} in juju cloud {} and juju model {}".format(service_a, service_b, jcloud, jmodel))
    def add_cross_model_relations(self, list_crossModelRelation):
        for crm in list_crossModelRelation:
            loop.run(self.add_RCM_relation(crm))
            
    async def add_RCM_relation(self, crm):
        """
        on success add cross model relation, appen it to "self.list_crossModelRelations"
        self.list_crossModelRelations.append(crm_relation)
        """
        from src.core.ro.vim_driver.vimdriver import run_command
        controller_source = "localhost"
        model_source = "default"
        application_source = "mysql"
        endpoint_application_source = "db"

        controller_target = "localhost"
        model_source = "default"
        application_target = "mediawiki"
        endpoint_application_target = "db"

        cmd_juju_offer_application_endpoint = ["juju", "offer", "{}:{}".format(application_source, endpoint_application_source)]
        cmd_juju_add_cmr = ["juju", "add-relation",
                                    "-m", "{}:{}".format(controller_target, model_source),
                                    "{}:{}".format(application_source, endpoint_application_source),
                                    "{}:{}/{}.{}".format(controller_source, "admin"), model_source, application_source]

        cmd_out_offer_app_endpoint = loop.run(run_command(cmd_juju_offer_application_endpoint))
        cmd_out_add_cmr = loop.run(run_command(cmd_juju_add_cmr))
        """
        juju offer mysql:db
        juju bootstrap localhost lxd-cmr-2
        juju add-model cmr-model-2
        juju deploy mediawiki
        juju add-relation mediawiki:db lxd-cmr-1:admin/cmr-model-1.mysql
        """
        #raise NotImplementedError
    
    def check_existence_model(self, juju_cloud, juju_model):
        for model in self.subslice_models:
            if model.cloud_name == juju_cloud and model.model_name == juju_model:
                return True
        return False
    def get_jmodel_running_status(self,model_name): 
        try:
            model_object=list(filter(lambda x: x.model_name == model_name, self.subslice_models))[0]
            if model_object:
                data_str=jsonpickle.encode(model_object)
                return json.loads(data_str)
            else: 
                return None
        except Exception as ex:
            raise ex
        
    def get_jmodel_object(self,model_name):
        try:
            model_object=list(filter(lambda x: x.model_name == model_name, self.subslice_models))[0]
            if model_object:
                return model_object
            else:
                return None        
        except Exception as ex:
            raise ex
        
    def check_slice_status(self):        
        raise NotImplementedError
    
    def delete_jmodel(self,model_name):
        jmodel=self.get_jmodel_object(model_name) 
        jmodel_uuid=jmodel.juju_model_uuid
        loop.run(jmodel.jcloud.juju_controller.destroy_juju_model(jmodel_uuid))
        self.subslice_models.remove(jmodel)
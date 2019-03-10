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

import copy
import json
import jsonpickle
import logging
from src.core.nso.nssi import service
#from src.core.ro import jtemplate
from json import JSONEncoder
from juju.model import Model
from juju import loop
import datetime
from src.core.nso.plugins.juju2_plugin import JujuModelServiceController



class JModel(JSONEncoder):
    
    def __init__(self, global_variables):
        self.gv = global_variables
        self.subslice_name= ""
        # parameters of the juju cloud: juju-cloud name and juju model name
        self.cloud_name=""
        self.model_name=""

        self.logger = logging.getLogger('jox.jmodel')
        self.log_config()
        self.credential_name=None
        self.config=""
        self.config_juju=None
        self.region=""
        self.services = []  # List with Services objects
        self.relations = []  # List with Services objects
        # CLOUD
        self.jcloud=None
        self.pointer_juju2_model=None
        self.juju_model_uuid=""
        self.juju_serviceModel = None  # juju service model, to add/remove services, and add/remove relations

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
    def validate_jmodel_config(self,model_config):
        """
        :param model_config:
        :return:
        """
        raise NotImplementedError()

    def build_and_deploy(self, model_config, jclouds, subslice_name, slice_name, resourceController,
                         juju_cloud, juju_model, Watcher_attached, subslice_machines):
        """
        :param model_config:
        :param jclouds:
        :param subslice_name:
        :param resourceController:
        :param juju_cloud:
        :param juju_model:
        :return:
        """
        """
        subslice_config = {
            "slice_name" :self.template_manager.get_NSI_ID,
            "subslice_name": nssi_id,
            "slice_version": list_service_machine[0],
            "list_services": list_service_machine[1],
            "list_machines": list_service_machine[2],
        }
        """
        if model_config != None:
            try:
                self.juju_serviceModel = JujuModelServiceController(self.gv)
                
                # STEP: parse configuration
                self.subslice_name = subslice_name
                self.slice_name = slice_name
                self.config = model_config
                
                self.machines_config = model_config["list_machines"]
                self.services_config = model_config["list_services"]
                
                # jtemplate.create_slice_monitor_template(self.services_config)
            
                _list = list(filter(lambda x: x.controller_name == self.cloud_name, jclouds))
                self.jcloud = _list[0]  # find correct cloud object
                
                # parameters to add juju model
                self.model_name = juju_model
                self.cloud_name = juju_cloud
                self.credential_name = None
                self.owner = None
                self.config_juju = None
                self.region = None

                self.juju_serviceModel.build(self.cloud_name, self.model_name)
                
                # STEP: deploy the model in juju
                self.pointer_juju2_model = self.jcloud.add_juju_model(self.model_name,
                                                                      self.cloud_name,
                                                                      self.credential_name,
                                                                      self.owner,
                                                                      self.config_juju,
                                                                      self.region)
                self.juju_model_uuid = self.pointer_juju2_model.info.uuid
                

                self.logger.info("The juju model {}:{} is configured".format(self.cloud_name, self.model_name))
                self.logger.debug("The ID of the juju model {}:{} is {}".format(self.cloud_name, self.model_name, self.juju_model_uuid))
                
                # STEP: attach live watcher
                if not Watcher_attached:
                    self.jcloud.attach_watcher(self.model_name, self.slice_name)
                # Step: add the machines to the current model
                list_machine = resourceController.add_machines(self.machines_config, self.services_config, self.subslice_name, self.model_name, self.cloud_name, self.slice_name)
                lis_serviceName_grantedJujuMachine = list_machine[1]

                for item in range(len(subslice_machines)):
                    curren_machine = subslice_machines[item]
                    user_definedName = curren_machine["machine_name_userdefined"]
                    subslice_machines[item]["machine_name_vnfm"] = lis_serviceName_grantedJujuMachine[user_definedName]
                    for key in list_machine[0]:
                        val = list_machine[0][key]
                        if val == subslice_machines[item]["machine_name_vnfm"]:
                            subslice_machines[item]["machine_name_ro"] = key
                # ADD SERVICES
                self.add_services(self.services_config, self.machines_config, lis_serviceName_grantedJujuMachine)
                # ADD RELATIONS
                self.add_relations_intraModel(self.services_config)
            except Exception as ex:
                raise ex

    def get_model_services(self):
        data_str = jsonpickle.encode(self.services)  # returns str
        data = json.loads(data_str)        
        return data
    
    def get_model_relations(self):
        data_str = jsonpickle.encode(self.relations)  # returns str
        data = json.loads(data_str)        
        return data
  
    def get_mid_juju_from_mid_jmodel(self, mid_jmodel, machine_type):

        if machine_type == "KVM":
            list_a = self.jcloud.vim_controller.vm_kvm_list
            list_b = []
            for vm in list_a:
                if (vm.slice_name == self.subslice_name and vm.model_name == self.model_name):
                    list_b.append(vm)
            kvm_machine_list = list(filter(lambda x: x.mid_jmodel == mid_jmodel, list_b))
            if kvm_machine_list[0]:
                return kvm_machine_list[0].mid_juju

        if machine_type == "LXC":
            list_a = self.jcloud.vim_controller.vm_lxc_list
            list_b = [vm for vm in list_a if (vm.slice_name == self.subslice_name and vm.model_name == self.model_name)]
            lxc_machine_list = list(filter(lambda x: x.mid_jmodel == mid_jmodel, list_b))
            if lxc_machine_list[0]:
                return lxc_machine_list[0].mid_juju
        return -1   

    def add_services(self, services_config,  machines_config, lis_serviceName_grantedJujuMachine):
        try:
            service_list = list(services_config.keys())
            for service in range(len(service_list)):
                self.logger.info("Deploying the application {}".format(service_list[service]))
                service_name=service_list[service]

                machine_id_userDefined = lis_serviceName_grantedJujuMachine[service_name]
                allocated_machine = lis_serviceName_grantedJujuMachine[machine_id_userDefined]

                self.add_service(services_config[service_name], machines_config, service_list[service], allocated_machine)
        except Exception as ex:
            raise ex
   
    def add_service(self, service_config, machines_config, service_name, allocated_machine):
        """" Initial JService Deployment"""
        try:
            new_service = service.JService(self.gv)
            new_service.build(service_config, service_name, machines_config[service_config["machine_name"]])
            machine_key = allocated_machine
            new_service.to = machine_key
            
            loop.run(self.juju_serviceModel.deploy_service(new_service))
            self.services.append(new_service) 
            return     
        except Exception as ex:
            raise ex
    
    def add_relations_intraModel(self, relations_config):
        try:
            service_name=""
            service_list = list(relations_config.keys())
            for service in range(len(service_list)):
                service_name=service_list[service]
                source = service_name
                target = relations_config[service_name]['relation']
                if relations_config[source]['jcloud'] == relations_config[target]['jcloud'] and \
                    relations_config[source]['jmodel'] == relations_config[target]['jmodel']:
                    self.logger.info("Adding relation between {} and {}".format(source, target))
                    
                    self.add_relation_intramodel(source, target, relations_config[source]['jcloud'], relations_config[source]['jmodel'])
        except Exception as ex:
            self.logger.info("No juju relation requirements for ".format(service_name))
            return
    
    def remove_relation_intramodel(self, service_a, service_b, jcloud, jmodel):
        try:
            loop.run(self.juju_serviceModel.deploy_relation_intra_model(service_a, service_b))
        except Exception as ex:
            self.logger.critical("There is no relation between {} and {} ".format(service_a, service_b))
            
            
    def add_relation_intramodel(self, service_a, service_b, jcloud, jmodel):
        try:
            # loop.run(self.deploy_relation_intra_model(service_a, service_b, jcloud, jmodel))
            loop.run(self.juju_serviceModel.deploy_relation_intra_model(service_a, service_b))
            relation = {"service_a": service_a, "service_b": service_b}
            self.relations.append(relation)
            
    
        except Exception as ex:
            if ex.error_code == 'already exists':
                relation = {"service_a": service_a, "service_b": service_b}
                self.relations.append(relation)
        
    def destroy_services(self, services_config):   
        for service_config in services_config:
            if service_config != None:
                model_service_name=service_config["model-service-name"]    
                service=filter(lambda x: x.model_service_name == model_service_name,self.services)[0]
                loop.run(self.destroy_service(model_service_name))
                self.services.remove(service) 
                print ("service object deleted")
    
    async def destroy_service(self, service_name, user_name="admin"):
        service_removed = False
        try:
            model = Model()
            model_name = self.cloud_name + ":" + user_name + '/' + self.model_name
            await model.connect(model_name)
            """
            while not service_removed:
                try:
                    await model.applications[service_name].destroy()
                    await model.applications[service_name].remove()
                except Exception as ex:
                    service_removed = True
            """
            try:
                await model.applications[service_name].destroy()
                await model.applications[service_name].remove()
                service_removed = True
                message = "The service {} from {}/{} is successfully removed"\
                    .format(service_name, self.cloud_name, self.model_name)
            except Exception as ex:
                message = "The service {} from {}/{} can not be removed due to the following error \n {}" \
                    .format(service_name, self.cloud_name, self.model_name, ex)
            
        except Exception as ex:
            message = "Error while connecting to the juju model {}/{} for deleting the service  {}".format(self.cloud_name, self.model_name, service_name)
        finally:
            await model.disconnect()
        return [service_removed, message]
    
       
    def get_juju_model_status(self):
        status=loop.run(self.pointer_juju2_model.get_status())
        data_str=jsonpickle.encode(status)
        return json.loads(data_str)
    
    def get_juju_model_info(self):
        info=loop.run(self.pointer_juju2_model.get_info())
        data_str=jsonpickle.encode(info)
        return json.loads(data_str)

    def gt(self,dt_str):
        try:
            dt, _, us = dt_str.partition(".")
            dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
            us = int(us.rstrip("Z"), 10) /1000
            return dt + datetime.timedelta(microseconds=us)
        except Exception as ex:
            raise ex


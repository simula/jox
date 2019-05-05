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
import asyncio
from json import JSONEncoder
from src.core.nso.plugins import juju2_plugin

from juju.controller import Controller
import logging

from juju import loop
from threading import Thread
import src.common.config.gv as gv
from src.core.ro import monitor
from src.core.ro.monitor import Monitor



class JCloud(JSONEncoder):
    def __init__(self, global_variables):
        self.gv = global_variables
        """ We control a cloud through the hypervisor or JUJU- ToDo: ADD FlexRAN plugins for the RAN etc """
        self.controller_name=""
        self.juju_controller=None
        self.slice_id=''
        self.jesearch = None
        self.logger = logging.getLogger('jox.JCloud')
        self.log_config()
        self.monitor = None

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
    def validate(self,config):
        raise NotImplementedError()
      
    def build_and_deploy(self,cloud_config, jesearch):
        try:
            self.jesearch = jesearch
            self.monitor = Monitor()
            self.monitor.buil(self.jesearch)

            self.controller_name=cloud_config["cloud-name"]
            self.juju_controller= juju2_plugin.JujuController(self.gv)
            loop.run(self.juju_controller.build(self.controller_name))
        except Exception as ex:
            raise ex

    def get_juju_models(self):
        try:
            data=loop.run(self.juju_controller.get_juju_models())
            response=jsonpickle.encode(data)
            return json.loads(response)
        except Exception as ex:
            raise ex  
    
    
    def add_juju_model(self,model_name, cloud_name=None, credential_name=None,
        owner=None, config=None, region=None):
        try:
            # create model
            model=loop.run(self.juju_controller.add_juju_model(model_name,
                                                        cloud_name,
                                                        credential_name,
                                                        owner,
                                                        config,
                                                        region))
            return model
        except:
            try:
                # try to get the mode if exist
                model = loop.run(self.juju_controller.get_juju_model(model_name))
                return model
            except:
                message = "Error to connect to the model", model_name
                self.logger.critical(message)
                self.logger.info(message)
        
    def attach_watcher(self,model_name, slice_name):
        self.slice_id = slice_name
        new_loop = asyncio.new_event_loop()
        new_loop.create_task(self.watch_model(model_name))
        t = Thread(target=self.start_loop, args=(new_loop,))
        t.daemon = True
        t.start()
    def get_user(self,user_name): 
        try:
            data=loop.run(self.juju_controller.get_user(user_name))
            response=jsonpickle.encode(data)
            return json.loads(response)
        except Exception as ex:
            raise ex  
     
    def add_user(self,slice_name): 
        try:
            data=loop.run(self.juju_controller.add_user(slice_name))
            response=jsonpickle.encode(data)
            return json.loads(response)
        except Exception as ex:
            raise ex
        
    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        
    async def on_model_change(self, delta, old, new, model):
        if self.jesearch.ping():
            """
            print("delta.entity={}".format(delta.entity))
            print("delta.type={}".format(delta.type))
            print("delta.data={}".format(delta.data))
            print('\n ')
            """

            if delta.entity=="machine" and (delta.type=="add" or delta.type=="change"):
                current_state_machine = delta.data['agent-status']['current']
                self.monitor.update_machine_monitor_state(delta.data, delta.type, current_state_machine, self.slice_id)

            if delta.entity=="unit" and (delta.type=="change"):
                current_state_service = delta.data['workload-status']['current']
                self.monitor.update_service_monitor_state(delta.data, delta.type, current_state_service, self.slice_id)
                # print(delta.data)
            """
            if delta.entity=="unit" and delta.type=="change" and delta.data['workload-status']['current']=="error":
                self.monitor.update_service_monitor_state(delta.data['application'], "error", self.slice_id)
                # monitor.update_service_monitor_state(self.jesearch, delta.data['application'], "error", self.slice_id)

            if delta.entity=="unit" and delta.type=="change" and delta.data['workload-status']['current']=="maintenance":   
                self.monitor.update_service_monitor_state(delta.data['application'],"waiting", self.slice_id)
                # monitor.update_service_monitor_state(self.jesearch, delta.data['application'],"waiting", self.slice_id)

            if delta.entity=="unit" and delta.type=="change" and delta.data['workload-status']['current']=="active":
                self.monitor.update_service_monitor_state(delta.data['application'], "maintenance", self.slice_id)
                # monitor.update_service_monitor_state(self.jesearch, delta.data['application'], "active_since", self.slice_id)
            """

            #if delta.entity=="application" and delta.type=="change" and (delta.data['status']['message']=="Running" or delta.data['status']['message']=="Ready"):
             #   self.monitor.update_service_monitor_state(delta.data['name'], "requirement_wait", self.slice_id)
                # monitor.update_service_monitor_state(self.jesearch, delta.data['name'], "requirement_wait", self.slice_id)

   #     else:
    #        message = "Elasticsearch is not working, and thus no update for monitoring information"
     #       self.logger.debug(message)
      #      self.logger.debug(message)
    async def watch_model(self, model_name):
        controller = Controller()
        self.logger.info("Connecting to controller")
        await controller.connect()

        try:
            model = await controller.get_model(model_name)
            model.add_observer(self.on_model_change)

        except Exception as ex:
            self.logger.error(ex)

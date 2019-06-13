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

class JService(object):
        
    def __init__(self, global_variables):
        self.gv = global_variables
        self.logger = logging.getLogger('jox.JService')
        self.log_config()
        self.service_state="NOT DEPLOYED"

        self.description=""
        self.entity_url="" 
        self.application_name=None
        self.bind=None
        self.budget=None
        self.channel=None
        self.config=None
        self.constraints=None, 
        self.force=False
        self.num_units=1
        self.plan=None
        self.resources=None, 
        self.series=None, 
        self.storage=None
        self.to=None
        self.pointer2_juju_app=None
        # flexran related variables. It is necessary only for RAN entities
        self.flexran_enb_id = list()
        self.flexran_slice_id = list()

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
      
    def validate(self, service_config):
#         self.application_name=service_name=service_config["application-name"]
#         check=service_name in self.model.cloud_object.controller.status()['Services']
#         if check:
#             print ("JService name already exists")
#             return
        
        raise NotImplementedError()
      
      
    def build(self,service_config, service_name, machine_config):
        self.entity_url=service_config['charm']
        
        self.application_name=service_name
        self.bind=None 
        self.budget=None
        self.channel="stable"
        self.config=None, 
        self.constraints=None
        self.force=False
        self.num_units=1
        self.plan=None, 
        self.resources=None
        for os_ver in self.gv.OS_SERIES:
            if str(os_ver) in str(machine_config["os"]["version"]):
                self.series = self.gv.OS_SERIES[os_ver]
                break
        self.storage=None
        self.to=service_name


    def get_service_status(self, field):
        """ field = ALL, STATUS or UNITS"""
        raise NotImplementedError()

   
    
    


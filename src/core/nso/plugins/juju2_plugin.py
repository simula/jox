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
from juju.controller import Controller
import asyncio
from juju.model import Model
import time, datetime
import pika, uuid, json
import random

class JujuController(object):
    """Juju JujuController: Shared between Slices """

    def __init__(self, global_variables):
        self.gv = global_variables
        self.controller_name = ""
        self.controller = None
        self.logger = logging.getLogger('jox.juju')
        self.log_config()
    def log_config(self):
        LOGFILE= self.gv.LOGFILE
        file_handler = logging.FileHandler(LOGFILE)
        file_handler.setLevel(logging.DEBUG)
    
        # create console handler with a higher log level
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console.setFormatter(formatter)
       
        # add the handlers to the self.logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console)
        
    
    async def build(self,name):
        """ Initiate the juju cloud controllers"""
        self.controller_name = name    #e.g. manual
        self.controller = Controller()

        
    def validate(self,cloud_name):
        """ Validate the jujuclient and its availability"""    
         
    
    async def get_juju_models(self):
        await self.controller.connect(self.controller_name)
        data=await self.controller.list_models()
        await self.controller.disconnect()
        return data
    async def get_juju_model(self, model_name):
        await self.controller.connect(self.controller_name)
        data = await self.controller.get_model(model_name)
        await self.controller.disconnect()
        return data
    async def reset_juju_model(self, model_name):
        await model_name.reset(force=True)
        return model_name

    async def get_user(self, user_name):
        """JOX slice_name==juju user_name"""
        await self.controller.connect(self.controller_name)
        data=await self.controller.get_user(user_name)
        await self.controller.disconnect()
        return data
    
    async def add_user(self, slice_name):
        """JOX slice_name==juju user_name"""
        await self.controller.connect(self.controller_name)
        data=await self.controller.add_user(slice_name)
        await self.controller.disconnect()
        return data

    async def add_juju_model(self,model_name,cloud_name, credential_name,owner, config, region):
        config = {
            "enable-os-refresh-update": False,
            "enable-os-upgrade": False,
        }
        await self.controller.connect(self.controller_name)
        model=await self.controller.add_model(model_name, credential_name=credential_name, owner=owner, config=config, region=region)

        await self.controller.disconnect()
        """
        """

        retry_connect = True
        number_retry = 0
        max_retry  = 200
        while number_retry <= max_retry and retry_connect:
            model_2 = Model()
            c_name = cloud_name
            m_name = model_name
            model_name_2 = c_name + ":admin/" + m_name
            
            number_retry += 1
            try:
                message = "{} time trying to connect to juju model:{} to add lxc machine".format(number_retry, model_name_2)
                self.logger.info(message)
                self.logger.debug(message)
                await model_2.connect(model_name_2)
                retry_connect = False
                "Successful connection to the model {} ".format(model_name_2)
                self.logger.info(message)
                self.logger.debug(message)
            except:
                await model_2.disconnect()
                await asyncio.sleep(10)
        return model
       
    async def destroy_juju_model(self,model_uuid):
        await self.controller.connect(self.controller_name)
        _response=await self.controller.destroy_model(model_uuid)
        await self.controller.disconnect()
        return _response   
       
       
    def grant_access_level(self, username, acl):
        changes=self.controller.grant(username, acl)
        return changes
        
   
    async def disconnect(self):
        await self.controller.disconnect()


class JujuModelServiceController(object):

    def __init__(self, global_variables):
        self.gv = global_variables
        self.logger = logging.getLogger('jox.JujuModelServiceController')
        self.controller = None
        self.enb_id = None
        self.timeout = 10

        self.controller_name = ""  # juju controller name
        self.model_name = ""  # juju model name
        self.user_name = ""  # juju user name
        self.host_name = self.gv.RBMQ_SERVER_IP
        self.port = self.gv.RBMQ_SERVER_PORT

        self.queue_name_flexran = self.gv.FLEXRAN_RBMQ_QUEUE_NAME
        self.standard_reqst = {
            "datetime": None,
            "plugin_message": None,
            "param": {
                "host": None,
                "port": None,
                "slice_config": None
            }
        }
        # self.watcher = None
        LOGFILE = self.gv.LOGFILE
        file_handler = logging.FileHandler(LOGFILE)
        file_handler.setLevel(logging.DEBUG)
        
        # create console handler with a higher log level
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console.setFormatter(formatter)
        
        # add the handlers to the self.logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console)
    def build(self, juju_controller, juju_model, juju_user="admin"):
        self.controller_name = juju_controller
        self.model_name = juju_model
        self.user_name = juju_user
        self.run()

    async def deploy_service(self, new_service, nsi_name):
        try:
            model = Model()
            model_name = self.controller_name + ":" + self.user_name + '/' + self.model_name
            await model.connect(model_name)
            if nsi_name not in self.gv.NSI_ID_LIST:
                self.gv.NSI_ID = random.randint(1,255)
                self.gv.NSI_ID_LIST.extend([nsi_name , self.gv.NSI_ID])

            app_keys = model.applications.keys()
            application_NotExist = True
            for app in app_keys:
                if new_service.application_name == app:
                    if len(model.applications[app].units) > 0:
                        application_NotExist = False
                        app_values = model.applications.get(app)
                        machine_id_service = app_values.units[0].machine.id
                        application = app_values.units[0]
                    else:
                        await model.applications[app].destroy()
                        message = "Deleting the application {} is finished".format(app)
                        self.logger.info(message)
                        self.logger.debug(message)
            if application_NotExist:
                
                application = await model.deploy(
                    new_service.entity_url,
                    application_name=new_service.application_name,
                    series=new_service.series,
                    channel=new_service.channel,
                    to=new_service.to,
                    )
                time.sleep(10)

            machine_ip = model.machines[new_service.to].dns_name
            self.gv.FLEXRAN_HOST = str(machine_ip)
            if self.gv.FLEXRAN_PLUGIN_STATUS == self.gv.ENABLED:
                if new_service.application_name == self.gv.FLEXRAN_PLUGIN_SERVICE_FLEXRAN:
                    enquiry = self.standard_reqst
                    current_time = datetime.datetime.now()
                    enquiry["datetime"] = str(current_time)
                    enquiry["plugin_message"] = "update_flexRAN_endpoint"
                    enquiry["param"]["host"] = str(machine_ip)
                    enquiry["param"]["port"] = self.gv.FLEXRAN_PORT
                    enquiry = json.dumps(enquiry)
                    enquiry.encode("utf-8")
                    self.send_to_plugin(enquiry, self.queue_name_flexran)


                if new_service.application_name == self.gv.FLEXRAN_PLUGIN_SERVICE_OAI_ENB:
                    enquiry = self.standard_reqst
                    # self.enb_id = hex(random.randint(1040000,1048575)) # 20 bit LTE enb_id
                    # self.enb_id = hex(random.randint(4294900000,4294967295)) # 28 bit LTE enb_id
                    # enquiry = self.standard_reqst
                    # current_time = datetime.datetime.now()
                    # enquiry["datetime"] = str(current_time)
                    # enquiry["plugin_message"] = "set_enb_config"
                    # enquiry["param"]["enb_id"] = '-1' # Last added eNB
                    # enquiry["param"]["nsi_id"] = self.nsi_id # mpped nsi_id
                    # enquiry["param"]["slice_config"] = self.gv.FLEXRAN_SLICE_CONFIG # this config should set enb_id that is generated above
                    # enquiry = json.dumps(enquiry)
                    # enquiry.encode("utf-8")
                    # print(enquiry)
                    # self.send_to_plugin(enquiry, self.queue_name_flexran)

                    self.enb_id = '-1'
                    print(str(self.gv.NSI_ID))
                    current_time = datetime.datetime.now()
                    enquiry["datetime"] = str(current_time)
                    enquiry["plugin_message"] = "create_slice"
                    enquiry["param"]["enb_id"] = self.enb_id  # Last added eNB
                    enquiry["param"]["nsi_id"] = str(self.gv.NSI_ID) # self.nsi_id

                    #self.gv.JOX_SLICE_CONFIG['dl'][0]['id'] = self.gv.NSI_ID
                    #self.gv.JOX_SLICE_CONFIG['ul'][0]['id'] = self.gv.NSI_ID
                    #enquiry["param"]["slice_config"] = self.gv.JOX_SLICE_CONFIG

                    enquiry = json.dumps(enquiry)
                    enquiry.encode("utf-8")
                    self.send_to_plugin(enquiry, self.queue_name_flexran)

            self.logger.info("The servce {} is deployed".format(new_service.application_name))
            self.logger.debug("The servce {} is deployed".format(new_service.application_name))
            
            new_service.pointer2_juju_app = application
        except Exception as ex:
            raise ex
        finally:
            await model.disconnect()
    
    async def destroy_services(self, services_config):
        raise NotImplementedError
    
    async def deploy_relation_intra_model(self, service_a, service_b):
        try:
            model = Model()
            model_name = self.controller_name + ":" + self.user_name + '/' + self.model_name
            await model.connect(model_name)
            await model.add_relation(service_a, service_b)
        except Exception as ex:
            raise ex
        finally:
            await model.disconnect()
    
    async def destroy_relation_intra_model(self, service_a, service_b, jcloud, jmodel):
       raise NotImplementedError

    def run(self, retry=False):
        if retry:
            self.connection.close()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_name, port=self.port))
        self.connection.add_timeout(self.timeout, self.on_timeout)
        self.channel = self.connection.channel()

        self.result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = self.result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def send_to_plugin(self, msg, rbmq_queue_name, reply=True):
        if reply:
            message_not_sent = True
            while message_not_sent:
                try:
                    self.response = None
                    self.corr_id = str(uuid.uuid4())
                    self.channel.basic_publish(exchange='',
                                               routing_key=rbmq_queue_name,
                                               properties=pika.BasicProperties(
                                                   reply_to=self.callback_queue,
                                                   correlation_id=self.corr_id,
                                               ),
                                               body=msg)
                    message_not_sent = False
                except:
                    time.sleep(0.5)
                    self.run()
            while self.response is None:
                if self.gv.FLEXRAN_PLUGIN_STATUS == self.gv.ENABLED:
                    self.connection.process_data_events()
                else:
                    self.response = 'Not received'
        else:
            message_not_sent = True
            while message_not_sent:
                try:
                    self.response = None
                    self.corr_id = str(uuid.uuid4())
                    self.channel.basic_publish(exchange='',
                                               routing_key=rbmq_queue_name,
                                               properties=pika.BasicProperties(
                                               ),
                                               body=msg)
                    message_not_sent = False
                except:
                    time.sleep(0.5)
                    self.run()
            return None
        return self.response

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode("utf-8")
            message = "Response from plgin -> {}".format(self.response)
            self.logger.info(message)

    def on_timeout(self,):
        self.connection.close()
        self.gv.FLEXRAN_PLUGIN_STATUS =self.gv.DISABLED

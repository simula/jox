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
import os, time, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "/../"))
dir_JOX_path = os.path.dirname(os.path.abspath(__file__ + "/../../../"))
sys.path.append(dir_parent_path)
sys.path.append(dir_path)

import logging
from juju.controller import Controller
import asyncio
from juju.model import Model
import time, datetime
import pika, uuid, json
from src.common.config import gv
from juju import loop

class FlexRanpluginTest(object):

    def __init__(self):
        self.gv = gv
        self.logger = logging.getLogger('jox.JujuModelServiceController')
        self.controller = None

        self.nsi_id_list = []  # FlexRAN plugin
        self.nsi_id = 100  # FlexRAN plugin
        self.enb_id = None

        self.controller_name = ""  # juju controller name
        self.model_name = ""  # juju model name
        self.user_name = ""  # juju user name
        self.host_name = "localhost"
        self.port = 5672

        self.queue_name_flexran = "QueueFlexRAN"
        self.standard_reqst = {
            "datetime": None,
            "plugin_message": None,
            "param": {
                "host": None,
                "port": None,
                "slice_config": None
            }
        }

    async def deploy_service(self, new_service_application_name):
        try:
            self.gv.FLEXRAN_PLUGIN_STATUS = self.gv.ENABLED

            machine_ip = "192.168.1.15"
            self.gv.FLEXRAN_HOST = str(machine_ip)
            self.gv.FLEXRAN_PORT = int(9999)

            if self.gv.FLEXRAN_PLUGIN_STATUS == self.gv.ENABLED:
                if new_service_application_name == self.gv.FLEXRAN_PLUGIN_SERVICE_FLEXRAN:
                    enquiry = self.standard_reqst
                    current_time = datetime.datetime.now()
                    enquiry["datetime"] = str(current_time)
                    enquiry["plugin_message"] = "update_flexRAN_endpoint"
                    enquiry["param"]["host"] = str(machine_ip)
                    enquiry["param"]["port"] = self.gv.FLEXRAN_PORT

                # if new_service_application_name == self.gv.FLEXRAN_PLUGIN_SERVICE_OAI_ENB:
                #
                #     # self.enb_id = hex(random.randint(1040000,1048575)) # 20 bit LTE enb_id
                #     # self.enb_id = hex(random.randint(4294900000,4294967295)) # 28 bit LTE enb_id
                #     # enquiry = self.standard_reqst
                #     # current_time = datetime.datetime.now()
                #     # enquiry["datetime"] = str(current_time)
                #     # enquiry["plugin_message"] = "set_enb_config"
                #     # enquiry["param"]["enb_id"] = '-1' # Last added eNB
                #     # enquiry["param"]["nsi_id"] = self.nsi_id # mpped nsi_id
                #     # enquiry["param"]["slice_config"] = self.gv.FLEXRAN_SLICE_CONFIG # this config should set enb_id that is generated above
                #     # enquiry = json.dumps(enquiry)
                #     # enquiry.encode("utf-8")
                #     # print(enquiry)
                #     # self.send_to_plugin(enquiry, self.queue_name_flexran)
                #
                #     # enquiry["param"]["slice_config"] = self.gv.FLEXRAN_SLICE_CONFIG

                enquiry = json.dumps(enquiry)
                enquiry.encode("utf-8")

                self.send_to_plugin(enquiry, self.queue_name_flexran)

                print("The servce {} is deployed".format(new_service_application_name))
                """get stats"""
                enquiry = self.standard_reqst
                current_time = datetime.datetime.now()
                enquiry["datetime"] = str(current_time)
                enquiry["plugin_message"] = "get_ran_stats"
                enquiry = json.dumps(enquiry)
                enquiry.encode("utf-8")
                response = self.send_to_plugin(enquiry, self.queue_name_flexran)

                # response = response.decode(self.gv.ENCODING_TYPE)
                response = json.loads(response)
                data = json.loads(response['data'])

                print("result={}".format(data))
                """create slice"""
                enquiry = self.standard_reqst
                current_time = datetime.datetime.now()
                enquiry["datetime"] = str(current_time)
                enquiry["plugin_message"] = "create_slice"
                enquiry["param"]["enb_id"] = '-1'  # Last added eNB
                enquiry["param"]["nsi_id"] = '8'  # self.nsi_id
                enquiry = json.dumps(enquiry)
                enquiry.encode("utf-8")
                self.send_to_plugin(enquiry, self.queue_name_flexran)


                self.logger.info("The servce {} is deployed".format(new_service_application_name))
                self.logger.debug("The servce {} is deployed".format(new_service_application_name))


        except Exception as ex:
            raise ex

    def run(self, retry=False):
        if retry:
            self.connection.close()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_name, port=self.port))
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
                self.connection.process_data_events()
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


if __name__ == '__main__':
    FLEXRAN_PLUGIN_SERVICE_OAI_ENB = "oai-ran"
    FLEXRAN_PLUGIN_SERVICE_FLEXRAN = "flexran"

    flexran_plugin_test = FlexRanpluginTest()
    try:
        loop.run(flexran_plugin_test.deploy_service(FLEXRAN_PLUGIN_SERVICE_FLEXRAN))
    except:
        pass
    print("TEST FINISHED")

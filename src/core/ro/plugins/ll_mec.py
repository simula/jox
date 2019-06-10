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

 __author__ = 'Eurecom'
__date__ = "11-January-2019"
__version__ = '1.0'
__version_date__ = "01-March-2019"
__copyright__ = 'Copyright 2016-2019, Eurecom'
__license__ = 'Apache License, Version 2.0'
__maintainer__ = 'Osama Arouk, Navid Nikaein, Kostas Kastalis, and Rohan Kharade'
__email__ = 'contact@mosaic5g.io'
__status__ = 'Development'
__description__ = "Plugin to interact with ll-MEC framework"
"""
import atexit
import pika
import os, time, sys
import json
import logging
import requests
import datetime
from threading import Thread
from termcolor import colored
import argparse
import pika.exceptions as pika_exceptions
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "/../"))
dir_JOX_path = os.path.dirname(os.path.abspath(__file__ + "../../../../../"))
sys.path.append(dir_parent_path)
sys.path.append(dir_path)
sys.path.append(dir_parent_path)
sys.path.append(dir_path)

from src.common.config import gv
from src.core.ro.plugins import es
logging.basicConfig(format='%(asctime)s] %(filename)s:%(lineno)d %(levelname)s '
                           '- %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')



class ll_mec_plugin(object):
    def __init__(self, flex_log_level=None,):
        self.logger = logging.getLogger("jox-plugin.LL_MEC")
        atexit.register(self.goodbye)  # register a message to print out when exit

        if flex_log_level:
            if flex_log_level == 'debug':
                self.logger.setLevel(logging.DEBUG)
            elif flex_log_level == 'info':
                self.logger.setLevel(logging.INFO)
            elif flex_log_level == 'warn':
                self.logger.setLevel(logging.WARNING)
            elif flex_log_level == 'error':
                self.logger.setLevel(logging.ERROR)
            elif flex_log_level == 'critic':
                self.logger.setLevel(logging.CRITICAL)

        ## Loading global variables ##
        self.dir_config = dir_JOX_path + '/common/config/'
        self.jox_config = ""
        self.gv = gv

        try:
            with open(''.join([self.dir_config, gv.CONFIG_FILE])) as data_file:
                data = json.load(data_file)
                data_file.close()
            self.jox_config = data
        except IOError as ex:
            message = "Could not load JOX Configuration file.I/O error({0}): {1}".format(ex.errno, ex.strerror)
            self.logger.error(message)
        except ValueError as error:
            message = "invalid json"
            self.logger.error(message)
        except Exception as ex:
            message = "Error while trying to load JOX configuration"
            self.logger.error(message)
        else:
            message = " JOX Configuration file Loaded"
            self.logger.info(message)

        #### Elasticsearch configuration
        self.gv.ELASTICSEARCH_HOST = self.jox_config['elasticsearch-config']["elasticsearch-host"]
        self.gv.ELASTICSEARCH_PORT = self.jox_config['elasticsearch-config']["elasticsearch-port"]
        self.gv.ELASTICSEARCH_LOG_LEVEL = self.jox_config['elasticsearch-config']["elasticsearch-log-level"]
        #### llMEC and RBMQ configuration
        self.gv.LL_MEC_HOST = self.jox_config["ll_mec_config"]["host"]
        self.gv.LL_MEC_PORT = self.jox_config["ll_mec_config"]["port"]
        self.gv.RBMQ_QUEUE_LL_MEC = self.jox_config["ll_mec_plugin_config"]["rabbit-mq-queue"]
        self.gv.LL_MEC_PLUGIN_STATUS = self.jox_config["ll_mec_plugin_config"]["plugin-status"]
        self.gv.LL_MEC_TIMEOUT_REQUEST = self.jox_config["ll_mec_plugin_config"]['timeout-request']
        self.gv.LL_MEC_ES_INDEX_NAME = self.jox_config["ll_mec_plugin_config"]['es-index-name']
        self.gv.RBMQ_SERVER_IP = self.jox_config['rabbit-mq-config']["rabbit-mq-server-ip"]
        self.gv.RBMQ_SERVER_PORT = self.jox_config['rabbit-mq-config']["rabbit-mq-server-port"]
        #### LL_MEC plugin local variables
        self.jesearch = None
        self.credentials=None
        self.parameters=None
        self.connection=None
        self.channel=None
        self.ll_mec_default_slice_config=None
        self.slice_config=None
        self.es_LL_MEC_index = self.gv.LL_MEC_ES_INDEX_NAME
        self.rbmq_server_ip = self.gv.RBMQ_SERVER_IP
        self.rbmq_server_port = self.gv.RBMQ_SERVER_PORT
        self.rbmq_queue_name = self.gv.RBMQ_QUEUE_LL_MEC
        self.ll_mec_host= self.gv.LL_MEC_HOST
        self.ll_mec_port= self.gv.LL_MEC_PORT
        self.ll_mec_plugin_status=self.gv.LL_MEC_PLUGIN_STATUS
        self.ll_mec_endpoint = ''.join(['http://', str(self.ll_mec_host), ':', str(self.ll_mec_port), '/'])

    def build(self):
        try:
            with open(''.join([self.dir_config, gv.LL_MEC_PLUGIN_SLICE_CONFIG_FILE])) as data_file:
                data = json.load(data_file)
                data_file.close()
            self.ll_mec_default_slice_config = data  # This config is to be used if DL % excceed 100
            self.logger.info(" LL_MEC default endpoint is {}".format(self.LL_MEC_endpoint))
            if self.gv.ELASTICSEARCH_ENABLE:
                self.jesearch = es.JESearch(self.gv.ELASTICSEARCH_HOST, self.gv.ELASTICSEARCH_PORT,
                                            self.gv.ELASTICSEARCH_LOG_LEVEL)
            self.parameters = pika.ConnectionParameters(self.rbmq_server_ip, self.rbmq_server_port)
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(self.rbmq_queue_name)
            self.channel.basic_qos(prefetch_count=1)

            #### Create es index to maintain statistics for LL_MEC plugin
            if self.jesearch.ping():
                message = " Deleting the index <{}> from elasticsearch if already exist".format((self.es_LL_MEC_index))
                self.logger.info(message)
                self.jesearch.del_index_from_es((self.es_LL_MEC_index))  # Adding slice data to elasticsearch
                message = " Saving the index {} to elasticsearch".format((self.es_LL_MEC_index))
                self.logger.info(message)
                date = (datetime.datetime.now()).isoformat()
                index_data = {"date": date,
                            "enb_stats": [],
                            "ue_stats": [] }
                self.jesearch.set_json_to_es(self.es_LL_MEC_index, index_data)
                self.logger.info("Elasticsearch: connection Success")
            else:
                message = " Elasticsearch is disabled !! Enable elasticsearch to get LL_MEC notifications"
                self.logger.info(message)
                self.gv.LL_MEC_ES_INDEX_STATUS="disabled"
        except pika_exceptions.ConnectionClosed or \
               pika_exceptions.ChannelAlreadyClosing or \
               pika_exceptions.ChannelClosed or \
               pika_exceptions.ChannelError:
            self.connection.close()

    def start_consuming(self):
        while True:
            try:
                self.channel.basic_consume(self.on_request, queue=self.rbmq_queue_name, no_ack=False)
                print(colored('[*] LL_MEC plugin message thread -- > Waiting for messages. To exit press CTRL+C', 'yellow'))
                self.channel.start_consuming()
            except pika_exceptions.ConnectionClosed or \
                   pika_exceptions.ChannelAlreadyClosing or \
                   pika_exceptions.ChannelClosed or \
                   pika_exceptions.ChannelError:
                self.connection.close()

    def start_notifications(self):
        print(colored('[*] LL_MEC plugin notifications thread -- > Waiting for messages. To exit press CTRL+C', 'blue'))
        while True:
            try:
                if self.get_status_llmec_endpoint():
                    self.get_ran_stats()
                    #enb_agent_id, enb_data = self.get_eNB_list()
                    if self.gv.LL_MEC_ES_INDEX_STATUS == "disabled":
                        message = " Elasticsearch is disabled !! No more notifications are maintained"
                        self.logger.info(message)
                time.sleep(10) # Periodic Notification
            except pika_exceptions.ConnectionClosed or \
                   pika_exceptions.ChannelAlreadyClosing or \
                   pika_exceptions.ChannelClosed or \
                   pika_exceptions.ChannelError:
                self.connection.close()

    def on_request(self, ch, method, props, body):
        enquiry = body.decode(self.gv.ENCODING_TYPE)
        enquiry = json.loads(enquiry)
        message = " Message received -> {} ".format(enquiry["plugin_message"])
        self.logger.info(message)
        elapsed_time_on_request = datetime.datetime.now() - datetime.datetime.strptime(enquiry["datetime"],'%Y-%m-%d %H:%M:%S.%f')

        if elapsed_time_on_request.total_seconds() < self.gv.LL_MEC_TIMEOUT_REQUEST:
            send_reply = True
            ############################################
            if enquiry["plugin_message"] == "get_slice_stats":
                result = self.get_slice_stats()
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_slice_id":
                result = self.get_slice_id(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "create_slice":
                result = self.create_slice(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "remove_slice":
                result = self.remove_slice(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            ############################################
            if enquiry["plugin_message"] == "update_flexRAN_endpoint":
                result = self.update_llmec_endpoint((enquiry["param"]))
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": 'OK'
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_status_flexRAN_endpoint":
                if self.get_status_llmec_endpoint():
                    body = " FlexRAN endpoint is active"
                    status = "OK"
                else:
                    body = " FlexRAN endpoint is not active"
                    status = "NOT OK"
                response= {
                    "ACK": True,
                    "data": body,
                    "status_code": status
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)

    ##### Consume callbacks ######
    def get_slice_stats(self):
        """Get slice statistics.
        *@return: The slice statistics as dictionary in json format
        """
        try:
            response = requests.get(self.ll_mec_endpoint+"stats")
            data = response.text
            return data
        except Exception as ex:
            print(ex)

    def get_slice_id(self, param):
        """Get all or specific slice ids internally used by ll_mec.
        *@slice - specific slice
        *@return: The slice statistics as dictionary in json format
        """
        try:
            response = requests.get(self.ll_mec_endpoint+"slice")
            data = response.text
            return data
        except Exception as ex:
            print(ex)

    def update_llmec_endpoint(self, param):
        """Update the FlexRAN endpoint.
        *@host : host address
        *@port : port number
        *@return: The result
        """
        try:
            self.ll_mec_endpoint = ''.join(['http://', str(param["host"]), ':', str(param["port"]), '/'])
            message = " FlexRAN endpoint updated. New endpoint is {}".format(self.flexran_endpoint)
            self.logger.info(message)
            return "FlexRAN endpoint updated"
        except Exception as ex:
            print(ex)

    def get_status_llmec_endpoint(self):
        """Get default or latest FlexRAN endpoint.
        *@return: The host and port for FlexRAN controller in standard URI format
        """
        try:
            requests.get(self.ll_mec_endpoint + "stats/")
            return True
        except Exception as ex:
            message=" FlexRAN endpoint {} is not active".format(self.flexran_endpoint, ex)
            self.logger.info(message)
            return False

    def create_slice(eparam):
        raise NotImplementedError()

    def remove_slice(eparam):
        raise NotImplementedError()

    # method to update es index with container data
    def update_LL_MEC_plugin_index(self, index_page, container_type, container_name, container_data):
        slice_data = self.jesearch.get_json_from_es(index_page, container_type)
        container_data.items()
        leaf_keys = list(container_data.keys())
        leaf_values = list(container_data.values())
        if slice_data[0]:
            slice_data = slice_data[1]
            for machines in range(len(slice_data)):  # Update the container
                machines_list = slice_data[machines]
                machine = list(machines_list.keys())
                for num in range(len(machine)):
                    if machine[num] == container_name:
                        for number in range(len(container_data)):
                            leaf_key = leaf_keys[number - 1]
                            leaf_value = leaf_values[number - 1]
                            slice_data[machines][container_name][0][leaf_key] = leaf_value
            if bool(slice_data) == False:
                slice_data = [{container_name : [container_data]}]
            self.jesearch.update_index_with_content(index_page, container_type, slice_data)

    # Acknowledge RPC
    def send_ack(self, ch, method, props, response, send_reply):
        if send_reply:
            response = json.dumps(response)
            try:
                ch.basic_publish(exchange='',
                                 routing_key=props.reply_to,
                                 properties=pika.BasicProperties(correlation_id= \
                                                                     props.correlation_id),
                                 body=str(response))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except pika_exceptions.ConnectionClosed:
                pass
            except Exception as ex:
                self.logger.critical("Error while sending response: {}".format(ex))

    def goodbye(self):
        print("\n You are now leaving LL_MEC plugin framework .....")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process commandline arguments and override configurations in jox_config.json')
    parser.add_argument('--log', metavar='[level]', action='store', type=str,
                        required=False, default='debug',
                        help='set the log level: debug, info (default), warning, error, critical')

    args = parser.parse_args()
    fs = ll_mec_plugin(args.log)
    fs.build()
    t1 = Thread(target=fs.start_consuming).start()
    t2 = Thread(target=fs.start_notifications).start()

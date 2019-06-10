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
__description__ = "Plugin to interact with FlexRAN (Flexible and Programmable Platform for SD-RAN) controller"
"""
import atexit
import pika
import os, time, sys
import json
import logging
logging.basicConfig(format='%(asctime)s] %(filename)s:%(lineno)d %(levelname)s '
                           '- %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
import requests
import datetime
from threading import Thread
from termcolor import colored
import argparse
import pika.exceptions as pika_exceptions
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "/../"))
dir_JOX_path = os.path.dirname(os.path.abspath(__file__ + "/../../../"))
sys.path.append(dir_parent_path)
sys.path.append(dir_path)
from src.common.config import gv
from src.core.ro.plugins import es

class FlexRAN_plugin(object):
    def __init__(self, flex_log_level=None,):
        self.logger = logging.getLogger("jox-plugin.flexran")
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
        #### FlexRAN and RBMQ configuration
        self.gv.FLEXRAN_HOST = self.jox_config["flexran-config"]["host"]
        self.gv.FLEXRAN_PORT = self.jox_config["flexran-config"]["port"]
        self.gv.RBMQ_QUEUE_FlexRAN = self.jox_config["flexran-plugin-config"]["rabbit-mq-queue"]
        self.gv.FLEXRAN_PLUGIN_STATUS = self.jox_config["flexran-plugin-config"]["plugin-status"]
        self.gv.FLEXRAN_TIMEOUT_REQUEST = self.jox_config["flexran-plugin-config"]['timeout-request']
        self.gv.FLEXRAN_ES_INDEX_NAME = self.jox_config["flexran-plugin-config"]['es-index-name']
        self.gv.RBMQ_SERVER_IP = self.jox_config['rabbit-mq-config']["rabbit-mq-server-ip"]
        self.gv.RBMQ_SERVER_PORT = self.jox_config['rabbit-mq-config']["rabbit-mq-server-port"]
        #### FlexRAN plugin local variables
        self.jesearch = None
        self.credentials=None
        self.parameters=None
        self.connection=None
        self.channel=None
        self.flexran_default_slice_config=None
        self.slice_config=None
        self.es_flexran_index = self.gv.FLEXRAN_ES_INDEX_NAME
        self.rbmq_server_ip = self.gv.RBMQ_SERVER_IP
        self.rbmq_server_port = self.gv.RBMQ_SERVER_PORT
        self.rbmq_queue_name = self.gv.RBMQ_QUEUE_FlexRAN
        self.flexran_host= self.gv.FLEXRAN_HOST
        self.flexran_port= self.gv.FLEXRAN_PORT
        self.flexran_plugin_status=self.gv.FLEXRAN_PLUGIN_STATUS
        self.flexran_endpoint = ''.join(['http://', str(self.flexran_host), ':', str(self.flexran_port), '/'])
        self.standard_slice_error_percentage = 'resulting DL slice sum percentage exceeds 100'
        self.standard_slice_error_bs_not_found = 'can not find BS'

    def build(self):
        try:
            with open(''.join([self.dir_config, gv.FLEXRAN_PLUGIN_SLICE_CONFIG_FILE])) as data_file:
                data = json.load(data_file)
                data_file.close()
            self.flexran_default_slice_config = data  # This config is to be used if DL % excceed 100
            self.logger.info(" FlexRAN default endpoint is {}".format(self.flexran_endpoint))
            if self.gv.ELASTICSEARCH_ENABLE:
                self.jesearch = es.JESearch(self.gv.ELASTICSEARCH_HOST, self.gv.ELASTICSEARCH_PORT,
                                            self.gv.ELASTICSEARCH_LOG_LEVEL)
            self.parameters = pika.ConnectionParameters(self.rbmq_server_ip, self.rbmq_server_port)
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(self.rbmq_queue_name)
            self.channel.basic_qos(prefetch_count=1)

            #### Create es index to maintain statistics for flexRAN plugin viz. enb_stats, ue_stats
            if self.jesearch.ping():
                message = " Deleting the index <{}> from elasticsearch if already exist".format((self.es_flexran_index))
                self.logger.info(message)
                self.jesearch.del_index_from_es((self.es_flexran_index))  # Adding slice data to elasticsearch
                message = " Saving the index {} to elasticsearch".format((self.es_flexran_index))
                self.logger.info(message)
                date = (datetime.datetime.now()).isoformat()
                index_data = {"date": date,
                            "enb_stats": [],
                            "ue_stats": [] }
                self.jesearch.set_json_to_es(self.es_flexran_index, index_data)
                self.logger.info("Elasticsearch: connection Success")
            else:
                message = " Elasticsearch is disabled !! Enable elasticsearch to get FlexRAN notifications"
                self.logger.info(message)
                self.gv.FLEXRAN_ES_INDEX_STATUS="disabled"
        except pika_exceptions.ConnectionClosed or \
               pika_exceptions.ChannelAlreadyClosing or \
               pika_exceptions.ChannelClosed or \
               pika_exceptions.ChannelError:
            self.connection.close()

    def start_consuming(self):
        while True:
            try:
                if self.gv.FLEXRAN_PLUGIN_STATUS == self.gv.ENABLED:
                    self.channel.basic_consume(self.on_request, queue=self.rbmq_queue_name, no_ack=False)
                    print(colored('[*] FlexRAN plugin message thread -- > Waiting for messages. To exit press CTRL+C', 'yellow'))
                    self.channel.start_consuming()
                else:
                    message = "FlexRAN plugin not enabled"
                    self.logger.error(message)
            except pika_exceptions.ConnectionClosed or \
                   pika_exceptions.ChannelAlreadyClosing or \
                   pika_exceptions.ChannelClosed or \
                   pika_exceptions.ChannelError:
                self.connection.close()

    def start_notifications(self):
        print(colored('[*] FlexRAN plugin notifications thread -- > Waiting for messages. To exit press CTRL+C', 'blue'))
        while True:
            try:
                if self.gv.FLEXRAN_PLUGIN_STATUS == self.gv.ENABLED:
                    if self.get_status_flexRAN_endpoint():
                        self.get_ran_stats()
                        #enb_agent_id, enb_data = self.get_eNB_list()
                        if self.gv.FLEXRAN_ES_INDEX_STATUS == "disabled":
                            message = " Elasticsearch is disabled !! No more notifications are maintained"
                            self.logger.info(message)
                    time.sleep(10) # Periodic Notification
                else:
                    message = "FlexRAN plugin not enabled"
                    self.logger.error(message)
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

        if elapsed_time_on_request.total_seconds() < self.gv.FLEXRAN_TIMEOUT_REQUEST:
            send_reply = True
            ############################################
            if enquiry["plugin_message"] == "get_ran_stats":
                result = self.get_ran_stats()
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_num_enb":
                result = self.get_num_eNB()
                response = {
                    "ACK": True,
                    "data": str(result),
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_num_ue":
                result = self.get_num_ue(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": str(result),
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_enb_id":
                result = self.get_enb_id()
                response = {
                    "ACK": True,
                    "data": str(result),
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_ran_record" :
                result = self.get_ran_record(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_ue_stats" :
                result = self.get_ue_stats(enquiry["param"])
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
            if  enquiry["plugin_message"] == "remove_slice":
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
            if  enquiry["plugin_message"] == "add_ue_to_slice":
                result = self.add_ues_to_slice(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if  enquiry["plugin_message"] == "remove_ue_from_slice":
                result = self.remove_ues_from_slice(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if  enquiry["plugin_message"] == "get_num_slice":
                result = self.get_num_slices(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if  enquiry["plugin_message"] == "set_num_slice":
                result = self.set_num_slices(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if  enquiry["plugin_message"] == "set_slice_rb":
                result = self.set_slice_rb(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if  enquiry["plugin_message"] == "get_slice_rb":
                result = self.get_slice_rb(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if  enquiry["plugin_message"] == "set_slice_max_mcs":
                result = self.set_slice_max_mcs(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "get_slice_max_mcs" :
                result = self.get_slice_max_mcs(enquiry["param"])
                response = {
                    "ACK": True,
                    "data": result,
                    "status_code": "OK"
                }
                self.send_ack(ch, method, props, response, send_reply)
                message=" RPC acknowledged - {}".format(response)
                self.logger.info(message)
            ############################################
            if enquiry["plugin_message"] == "update_flexRAN_endpoint":
                result = self.update_flexRAN_endpoint(enquiry["param"])
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
                if self.get_status_flexRAN_endpoint():
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
    def get_ran_stats(self):
        """Get RAN statistics.
        *@return: The RAN statistics as dictionary in json format
        """
        try:
            response = requests.get(self.flexran_endpoint+"stats/")
            data = response.text
            return data
        except Exception as ex:
            print(ex)

    def get_ran_record(self, id):
        """Get RAN Record.
        *@return: The RAN record as dictionary in json format
        """
        try:
            response = requests.get(self.flexran_endpoint+"record/"+id)
            response = json.loads(response.text)
            return response
        except Exception as ex:
            print(ex)

    def get_ue_stats(self,id):
        """Get UE statistics.
        *@return: The UE statistics as dictionary in json format
        """
        try:
            response = requests.get(self.flexran_endpoint+"stats/ue"+id)
            print(response)
        except Exception as ex:
            print(ex)

    def prepare_slice(self,enb_id, slice_id):
        """Wait for BS to be connected before deploying slice.
        *@enb_id : enb id to add slice
        *@nsi_id : slice id
        *@return: The result
        """
        enb_id = enb_id
        slice_id = slice_id
        try:
            bs_connected = False
            while(bs_connected == False):
                message = " Waiting for BS to be connected"
                self.logger.info(message)
                req=self.flexran_endpoint+"slice/enb/"+enb_id+"/slice/"+slice_id
                response = requests.post(req)
                if (response.text is None) or (response.text == ""):
                    message = " BS is now connected"
                    self.logger.info(message)
                    bs_connected = True
                    message = " Slice is added, or already exist "
                    self.logger.info(message)
                else:
                    response=json.loads(response.text)
                    if response['error'] == self.standard_slice_error_percentage:
                        message = " Create slice attempt unsuccessful, Reseason -  {}".format(self.standard_slice_error_percentage)
                        self.logger.info(message)
                        message = " Reducing default slice resources by  {} percent".format(self.gv.SLICE_ADJUST_FACTOR)
                        self.flexran_default_slice_config['dl'][0]['percentage'] = self.flexran_default_slice_config['dl'][0]['percentage'] -\
                                                                                   self.gv.SLICE_ADJUST_FACTOR
                        self.flexran_default_slice_config['ul'][0]['percentage'] = self.flexran_default_slice_config['ul'][0]['percentage'] -\
                                                                                   self.gv.SLICE_ADJUST_FACTOR

                        self.logger.info(message)
                        self.set_enb_config(enb_id, self.flexran_default_slice_config)
                        response = requests.post(req)
                        if (response.text is None) or (response.text == ""):
                            message = " Slice is added, or already exist "
                            self.logger.info(message)
                        #else:
                            #NotImplementedError()
                        bs_connected = True
                    else:
                        message = " Wait interval of 2 seconds"
                        self.logger.info(message)
                        time.sleep(2)

        except Exception as ex:
            print(ex)
            self.prepare_slice(enb_id, slice_id)

    def create_slice(self,param):
        """Create slice on Flexran.
        *@enb_id : enb id to add slice
        *@nsi_id : slice id
        *@return: The result
        """
        try:
            slice_id=param['nsi_id']
            enb_id=param['enb_id']
            self.slice_config = param['slice_config']
            req = self.flexran_endpoint+"slice/enb/"+enb_id+"/slice/"+slice_id
            response = requests.post(req)
            if (response.text is None) or (response.text == ""):
                response = 'Slice is added, or already exist '
                return response
            else:
                standard_error = (json.loads(response.text))['error']
                if standard_error == self.standard_slice_error_percentage:
                    message = " Create slice attempt unsuccessful, Reseason -  {}".format(self.standard_slice_error_percentage)
                    self.logger.info(message)
                    message = " Reducing default slice resources by  {} percent".format(self.gv.SLICE_ADJUST_FACTOR)
                    self.flexran_default_slice_config['dl'][0]['percentage'] = \
                    self.flexran_default_slice_config['dl'][0]['percentage'] - \
                    self.gv.SLICE_ADJUST_FACTOR
                    self.flexran_default_slice_config['ul'][0]['percentage'] = \
                    self.flexran_default_slice_config['ul'][0]['percentage'] - \
                    self.gv.SLICE_ADJUST_FACTOR
                    self.logger.info(message)
                    self.set_enb_config(enb_id, self.flexran_default_slice_config)
                    response = requests.post(req)
                if standard_error == self.standard_slice_error_bs_not_found:
                    t3 = Thread(target=self.prepare_slice, args=(enb_id, slice_id)).start()
                    #t3.join()
                return response.text
        except Exception as ex:
            print(ex)

    def remove_slice(self,param):
        """Remove slice on Flexran.
        *@enb_id : enb id to add slice
        *@nsi_id : slice id
        *@return: The result
        """
        try:
            response = requests.delete(self.flexran_endpoint+'/enb/'+str(param['enb_id'])+'/slice/'+str(param['nss_id']))
            return response.text
        except Exception as ex:
            print(ex)

    def remove_slices(self,param):
        """Remove slice on Flexran.
        *@enb_id : enb id to add slice
        *@nsi_id : slice id
        *@slice_config : slice config
        *@return: The result
        """
        raise NotImplementedError()

    def add_ues_to_slice(self, param):
        raise NotImplementedError()

    def remove_ues_from_slice(self, param):
        raise NotImplementedError()

    def get_num_slices(self, param):
        raise NotImplementedError()

    def set_num_slices(self, param):
        raise NotImplementedError()

    def set_slice_rb(self, param):
        raise NotImplementedError()

    def get_slice_rb(self, param):
        raise NotImplementedError()

    def set_slice_max_mcs(self, param):
        raise NotImplementedError()

    def get_slice_max_mcs(self, param):
        raise NotImplementedError()

    def update_flexRAN_endpoint(self, param):
        """Update the FlexRAN endpoint.
        *@host : host address
        *@port : port number
        *@return: The result
        """
        try:
            self.flexran_endpoint = ''.join(['http://', str(param["host"]), ':', str(param["port"]), '/'])
            message = " FlexRAN endpoint updated. New endpoint is {}".format(self.flexran_endpoint)
            self.logger.info(message)
            return "FlexRAN endpoint updated"
        except Exception as ex:
            print(ex)

    def get_status_flexRAN_endpoint(self):
        """Get default or latest FlexRAN endpoint.
        *@return: The host and port for FlexRAN controller in standard URI format
        """
        try:
            requests.get(self.flexran_endpoint + "stats/")
            return True
        except Exception as ex:
            message=" FlexRAN endpoint {} is not active".format(self.flexran_endpoint, ex)
            self.logger.info(message)
            return False

    def get_num_eNB(self):
        """Get the number of connected eNB to this controller.
        *@return: The result.
        """
        try:
            response = requests.get(self.flexran_endpoint+"stats/")
            response=json.loads(response.text)
            response = response["eNB_config"]
            return len(response)
        except Exception as ex:
            print(ex)

    def get_num_ue(self, param):
        """Get the number of connected UE to to a given eNB.
        *@enb_id : enb id
        *@return: The result.
        """
        try:
            response = requests.get(self.flexran_endpoint+"stats/")
            return len(response['mac_stats'][(param['enb_id'])]['ue_mac_stats'])
        except Exception as ex:
            print(ex)

    def get_enb_id(self, param):
        """Get enb_id.
        *@return: The result
        """
        raise NotImplementedError()


    def get_enb_config(self):
        """Set slice config.
        *@return: The result
        """
        try:
            response = requests.get(self.flexran_endpoint+'slice/enb_config')
            response=json.loads(response.text)
            return response
        except Exception as ex:
            print(ex)

    def set_enb_config(self, enb_id, slice_config):
        """Set slice config.
        *@enb_id : enb id to add slice
        *@slice_config : slice config
        *@return: The result
        """
        try:
            slice_config = json.dumps(slice_config)
            req = "{}slice/enb/{}".format(self.flexran_endpoint, enb_id)
            header = {'Content-Type':  'application/octet-stream'}
            response = requests.post(req, data=slice_config, headers =header)
            message = " Resources now available for new slices "
            self.logger.info(message)
            return
        except Exception as ex:
            print(ex)

    ###### Notification callbacks ######
    def get_eNB_list(self):
        """Get list of eNBs registered at flexRAN.
        *@return: The result.
        """
        raise NotImplementedError()

    # method to update es index with container data
    def update_flexran_plugin_index(self, index_page, container_type, container_name, container_data):
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
        print("\n You are now leaving FlexRAN plugin framework .....")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process commandline arguments and override configurations in jox_config.json')
    parser.add_argument('--log', metavar='[level]', action='store', type=str,
                        required=False, default='debug',
                        help='set the log level: debug, info (default), warning, error, critical')

    args = parser.parse_args()
    fs = FlexRAN_plugin(args.log)
    fs.build()
    t1 = Thread(target=fs.start_consuming).start()
    t2 = Thread(target=fs.start_notifications).start()

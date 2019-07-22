
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
import copy
import pika.exceptions as pika_exceptions
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "../../../../../"))
dir_JOX_path = os.path.dirname(os.path.abspath(__file__ + "/../../../"))
sys.path.append(dir_parent_path)
sys.path.append(dir_path)
from src.common.config import gv
from src.core.ro.plugins import es


import logging
from juju.controller import Controller
import asyncio
from juju.model import Model
import time, datetime
import pika, uuid, json
import random

class test_plugin(object):
    def __init__(self, ):
        self.standard_reqst = {
            "datetime": None,
            "plugin_message": None,
            "param": {
                "host": None,
                "port": None,
                "slice_config": None
            }
        }
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
            print(ex)
        self.host_name = self.gv.RBMQ_SERVER_IP
        self.port = self.gv.RBMQ_SERVER_PORT
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
        self.credentials = None
        self.parameters = None
        self.connection = None
        self.channel = None
        self.flexran_default_slice_config = None
        self.slice_config = None
        self.es_flexran_index = self.gv.FLEXRAN_ES_INDEX_NAME
        self.rbmq_server_ip = self.gv.RBMQ_SERVER_IP
        self.rbmq_server_port = self.gv.RBMQ_SERVER_PORT
        self.rbmq_queue_name = self.gv.RBMQ_QUEUE_FlexRAN
        self.flexran_host = self.gv.FLEXRAN_HOST
        self.flexran_port = self.gv.FLEXRAN_PORT
        self.flexran_plugin_status = self.gv.FLEXRAN_PLUGIN_STATUS
        self.flexran_endpoint = ''.join(['http://', str(self.flexran_host), ':', str(self.flexran_port), '/'])
    def run(self, retry=False):
        if retry:
            self.connection.close()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port='5672'))
        #self.connection.add_timeout(self.timeout, self.on_timeout)
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


    def on_timeout(self, ):
        self.connection.close()
        # self.gv.FLEXRAN_PLUGIN_STATUS =self.gv.DISABLED

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process commandline arguments and override configurations in jox_config.json')
    parser.add_argument('--log', metavar='[level]', action='store', type=str,
                        required=False, default='debug',
                        help='set the log level: debug, info (default), warning, error, critical')
    enb_data = {"enb_stats": []}
    args = parser.parse_args()
    fs = test_plugin()
    fs.run()
    queue_name_flexran = "QueueFlexRAN"
    standard_reqst = {
            "datetime": None,
            "plugin_message": None,
            "param": {
                "host": None,
                "port": None,
                "slice_config": None
            }
        }
    enquiry = standard_reqst
    current_time = datetime.datetime.now()

################### Sample RPC message encoding ##############

    # Test get ran_stats
    # enquiry["datetime"] = str(current_time)
    # enquiry["plugin_message"] = "get_ran_stats"
    # enquiry = json.dumps(enquiry)
    # enquiry.encode("utf-8")
    # response = fs.send_to_plugin(enquiry, queue_name_flexran)
    # print(response)




    # # Test remove slice
    # enquiry["datetime"] = str(current_time)
    # enquiry["plugin_message"] = "remove_slice"
    # enquiry["param"]["enb_id"] = '-1' # Last added eNB
    # enquiry["param"]["nsi_id"] = 0 # mpped nsi_id
    # enquiry = json.dumps(enquiry)
    # enquiry.encode("utf-8")
    # response = fs.send_to_plugin(enquiry, queue_name_flexran)
    # print(response)



    # Test update slice
    # response=fs.set_slice_config('-1',slice_config)
    # print(response)
    # slice_config = {"ul": [{"id": 0, "percentage": 63}], "dl": [{"id": 0, "percentage": 63}]}
    # enquiry["datetime"] = str(current_time)
    # enquiry["plugin_message"] = "set_slice_config"
    # enquiry["param"]["enb_id"] = '-1' # Last added eNB
    # enquiry["param"]["slice_config"] = slice_config # mpped nsi_id
    # enquiry = json.dumps(enquiry)
    # enquiry.encode("utf-8")
    # response = fs.send_to_plugin(enquiry, queue_name_flexran)
    # print(response)



    # # Get slice resource block
    # enquiry["datetime"] = str(current_time)
    # enquiry["plugin_message"] = "get_slice_FirstRB"
    # enquiry["param"]["nsi_id"] = 0 # mpped nsi_id
    # enquiry = json.dumps(enquiry)
    # enquiry.encode("utf-8")
    # response = fs.send_to_plugin(enquiry, queue_name_flexran)
    # print(response)


    
    # # Get number of slice
    # enquiry["datetime"] = str(current_time)
    # enquiry["plugin_message"] = "get_num_slices"
    # enquiry = json.dumps(enquiry)
    # enquiry.encode("utf-8")
    # response = fs.send_to_plugin(enquiry, queue_name_flexran)
    # print(response)



    # # Get available resources
    # enquiry["datetime"] = str(current_time)
    # enquiry["plugin_message"] = "get_available_resources"
    # enquiry = json.dumps(enquiry)
    # enquiry.encode("utf-8")
    # response = fs.send_to_plugin(enquiry, queue_name_flexran)
    # print(response)
    
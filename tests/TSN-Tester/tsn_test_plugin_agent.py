
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


import logging
import time, datetime
import pika, uuid, json
import random
import gv,es

class test_plugin(object):
    def __init__(self, ):

        self.jox_config = ""
        self.gv = gv

        try:
            with open(''.join([self.dir_config, gv.CONFIG_FILE])) as data_file:
                data = json.load(data_file)
                data_file.close()
            self.jox_config = data
        except IOError as ex:
            message = "Could not load Plugin Configuration file.I/O error({0}): {1}".format(ex.errno, ex.strerror)
            self.logger.error(message)
        except ValueError as error:
            message = "invalid json"
            self.logger.error(message)
        except Exception as ex:
            message = "Error while trying to load plugin configuration"
            self.logger.error(message)
        else:
            message = " Plugin Configuration file Loaded"
            self.logger.info(message)
        ## Loading global variables ##
        #### FlexRAN and RBMQ configuration
        self.gv.RBMQ_QUEUE_TSN = self.jox_config["tsn-plugin-config"]["rabbit-mq-queue"]
        self.gv.RBMQ_SERVER_IP = self.jox_config['rabbit-mq-config']["rabbit-mq-server-ip"]
        self.gv.RBMQ_SERVER_PORT = self.jox_config['rabbit-mq-config']["rabbit-mq-server-port"]
        self.rbmq_server_ip = self.gv.RBMQ_SERVER_IP
        self.rbmq_server_port = self.gv.RBMQ_SERVER_PORT
        self.rbmq_queue_name = self.gv.RBMQ_QUEUE_FlexRAN
       
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
                if self.gv.TSN_PLUGIN_STATUS == self.gv.ENABLED:
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
#     parser = argparse.ArgumentParser(description='Process commandline arguments and override configurations in jox_config.json')
#     parser.add_argument('--log', metavar='[level]', action='store', type=str,
#                         required=False, default='debug',
#                         help='set the log level: debug, info (default), warning, error, critical')
#     enb_data = {"enb_stats": []}
#     args = parser.parse_args()
    fs = test_plugin()
    fs.run()
    queue_name_tsn = "QueueTSN"

################### Sample RPC message encoding ##############

    # Test get ran_stats
    enquiry={}
    enquiry["plugin_message"] = "get_ptp_interface"
    enquiry["node"]="new-tsn-device"
    enquiry["iface"]="0"
    enquiry = json.dumps(enquiry)
    enquiry.encode("utf-8")
    response = fs.send_to_plugin(enquiry, queue_name_tsn)
    print(response)




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
    
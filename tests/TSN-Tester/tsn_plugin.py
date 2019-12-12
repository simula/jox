import atexit
import pika
import os, time, sys
import json
import logging

logging.basicConfig(format='%(asctime)s] %(filename)s:%(lineno)d %(levelname)s '
                           '- %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
import requests
from requests.auth import HTTPBasicAuth
import datetime
from threading import Thread
from termcolor import colored
import argparse
import copy
import pika.exceptions as pika_exceptions
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
print (dir_path)
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "../../"))
print (dir_parent_path)
dir_JOX_path = os.path.dirname(os.path.abspath(__file__ + "/../../../.."))
print(dir_JOX_path)
 
sys.path.append(dir_parent_path)
sys.path.append(dir_path)
sys.path.append(dir_JOX_path)

# import es
import gv
TESTING=False

class TSN_plugin(object):
    def __init__(self, tsn_log_level=None,):
        self.logger = logging.getLogger("jox-plugin.tsn")
        atexit.register(self.goodbye)  # register a message to self.logger.info out when exit
        
       
        ## Loading global variables ##
        self.dir_config = ''
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

        #### Elasticsearch configuration
#         self.gv.ELASTICSEARCH_HOST = self.jox_config['elasticsearch-config']["elasticsearch-host"]
#         self.gv.ELASTICSEARCH_PORT = self.jox_config['elasticsearch-config']["elasticsearch-port"]
#         self.gv.ELASTICSEARCH_LOG_LEVEL = self.jox_config['elasticsearch-config']["elasticsearch-log-level"]
#         #### TSN and RBMQ configuration
        self.gv.TSN_CTRL_HOST = self.jox_config["tsn-ctrl-config"]["odl-host"]
        self.gv.TSN_CTRL_PORT = self.jox_config["tsn-ctrl-config"]["odl-port"]
        self.gv.TSN_CTRL_USERNAME=self.jox_config["tsn-ctrl-config"]["username"]
        self.gv.TSN_CTRL_PASSWORD=self.jox_config["tsn-ctrl-config"]["password"]
        self.gv.TSN_CTRL_PREFIX=self.jox_config["tsn-ctrl-config"]["prefix"]
        self.gv.RBMQ_QUEUE_TSN = self.jox_config["tsn-plugin-config"]["rabbit-mq-queue"]
        self.gv.TSN_PLUGIN_STATUS = self.jox_config["tsn-plugin-config"]["plugin-status"]
        self.gv.TSN_TIMEOUT_REQUEST = self.jox_config["tsn-plugin-config"]['timeout-request']
        self.gv.TSN_ES_INDEX_NAME = self.jox_config["tsn-plugin-config"]['es-index-name']
        self.gv.RBMQ_SERVER_IP = self.jox_config['rabbit-mq-config']["rabbit-mq-server-ip"]
        self.gv.RBMQ_SERVER_PORT = self.jox_config['rabbit-mq-config']["rabbit-mq-server-port"]
        
        #### TSN plugin local variables
        self.jesearch = None
        self.credentials=None
        self.parameters=None
        self.connection=None
        self.channel=None
        self.es_tsn_index = self.gv.TSN_ES_INDEX_NAME
        self.rbmq_server_ip = self.gv.RBMQ_SERVER_IP
        self.rbmq_server_port = self.gv.RBMQ_SERVER_PORT
        self.rbmq_queue_name = self.gv.RBMQ_QUEUE_TSN
                
        self.tsn_ctrl_host= self.gv.TSN_CTRL_HOST
        self.tsn_ctrl_port= self.gv.TSN_CTRL_PORT
        self.tsn_ctrl_prefix=self.gv.TSN_CTRL_PREFIX
        self.tsn_ctrl_endpoint = ''.join(
            ['http://', str(self.tsn_ctrl_host), ':', str(self.tsn_ctrl_port), '/',str(self.tsn_ctrl_prefix)])
        self.tsn_plugin_status=self.gv.TSN_PLUGIN_STATUS
        
        
        
        if tsn_log_level:
            if tsn_log_level == 'debug':
                self.logger.setLevel(logging.DEBUG)
            elif tsn_log_level == 'info':
                self.logger.setLevel(logging.INFO)
            elif tsn_log_level == 'warn':
                self.logger.setLevel(logging.WARNING)
            elif tsn_log_level == 'error':
                self.logger.setLevel(logging.ERROR)
            elif tsn_log_level == 'critic':
                self.logger.setLevel(logging.CRITICAL)
        
    def goodbye(self):
        self.logger.info(colored('[*] You are now leaving TSN plugin', 'red'))
        sys.exit(0)    
    
    
    def build(self):
        
        self.logger.info(" TSN default endpoint is {}".format(self.tsn_ctrl_endpoint))
        
#             if self.gv.ELASTICSEARCH_ENABLE:
#                 self.jesearch = es.JESearch(self.gv.ELASTICSEARCH_HOST, self.gv.ELASTICSEARCH_PORT,
#                                             self.gv.ELASTICSEARCH_LOG_LEVEL)
#             self.parameters = pika.ConnectionParameters(self.rbmq_server_ip, self.rbmq_server_port)
        try:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(self.rbmq_queue_name)
            self.channel.basic_qos(prefetch_count=1)
            #### Create es index to maintain statistics for TSN plugin 
#             if self.jesearch.ping():
#                 message = " Deleting the index <{}> from elasticsearch if already exist".format((self.es_tsn_index))
#                 self.logger.info(message)
#                 self.jesearch.del_index_from_es((self.es_tsn_index))  # Adding slice data to elasticsearch
#                 message = " Saving the index {} to elasticsearch".format((self.es_tsn_index))
#                 self.logger.info(message)
#                 date = (datetime.datetime.now()).isoformat()
#                 index_data = {"date": date,
#                             "ptp_stats": [],
#                             "tsn_stats": [] }
#                 self.jesearch.set_json_to_es(self.es_tsn_index, index_data)
#                 self.logger.info("Elasticsearch: connection Success")
#             else:
#                 message = " Elasticsearch is disabled !! Enable elasticsearch to get TSN notifications"
#                 self.logger.info(message)
#                 self.gv.TSN_ES_INDEX_STATUS="disabled"
        except pika_exceptions.ConnectionClosed or \
               pika_exceptions.ChannelClosed or \
               pika_exceptions.ChannelError:
            self.connection.close()

    
    def build_tsn_slice(self):
        
        try:
            with open(''.join([self.dir_config, gv.TSN_PLUGIN_SLICE_CONFIG_FILE])) as data_file:
                data = json.load(data_file)
                
                for switch_config in data:
                    switch_name=""    
#                     self.logger.info (switch_config)
                    for key in switch_config:
                        if (key=="tsn-switch-name"):
                            switch_name=switch_config[key]
                            
                    for key in switch_config:
                        if (key=="interface"):
                            iface=switch_config[key]
                            for iface_config in iface:
                                self.config_tsn_interface(switch_name,iface_config)             
                
            data_file.close()
        
        except IOError as ex:
            message = "Could not load TSN Slice Configuration file.I/O error({0}): {1}".format(ex.errno, ex.strerror)
    
    def config_tsn_interface(self,switch_name, if_config):
        try:
            iface=""
            for key in if_config: #call indepentently to be sure interface is parsed
                if (key=="iface"):
                    iface= if_config[key]
                    self.logger.info(iface)
                    
            for key in if_config:
                # PTP configuration part
                if (key=="tsnptp-interface"):
                    ptp_config=if_config[key]
                    self.logger.info(ptp_config)   
                    for ptp_key in ptp_config:  
#                         if (ptp_key=="enable"):
#                             self.set_ptp_interface_enable(switch_name,iface,ptp_config[ptp_key])
#                         if (ptp_key=="sync-receipt-timeout"):
#                             self.set_ptp_SyncReceiptTimeout(switch_name,iface,ptp_config[ptp_key])
#                         if (ptp_key=="delay-asymmetry"):
#                             self.set_ptp_SyncdelayAsymmetry(switch_name,iface,ptp_config[ptp_key])
                        if (ptp_key=="priority1"):
                            self.set_ptp_clockPriority1(switch_name,ptp_config[ptp_key])
                    
#                     self.set_ptp_save_config(switch_name)
            
            for key in if_config:
                if (key=="tsntas-interface-enable"):
                    status=if_config[key]
                    self.set_tas_enable(switch_name, iface, status)
                    
            for key in if_config:
                # TSN cycle configuration part
                if (key=="tsntas-cycle-time"):
                    cycle_config=if_config[key]
#                     self.logger.info(cycle_config)
                    for cycle_key in cycle_config:  
                        if (cycle_key=="base-time-sec"):
                            bts=cycle_config[cycle_key]
                        if (cycle_key=="base-time-ns"):
                            btn=cycle_config[cycle_key]
                        if (cycle_key=="cycle-time"):
                            ct=cycle_config[cycle_key]
                        if (cycle_key=="extension-ns"):
                            en=cycle_config[cycle_key]
                            
                    self.set_tas_cycle_time(switch_name,iface,bts,btn,ct,en)         
            for key in if_config:
                # TSN TAS entries configuration part
                if (key=="tsntas-schedule-entries"):
                    entries_list=if_config[key]
                    for tas_entry in entries_list:
                        self.logger.info (tas_entry)
                        for entry_key in tas_entry:  
                            if (entry_key=="entry"):  
                                entry=tas_entry[entry_key]
                            if (entry_key=="hold-preempt"):  
                                hp=tas_entry[entry_key]
                            if (entry_key=="time-interval"):  
                                ti=tas_entry[entry_key]
                            if (entry_key=="gate-state"):  
                                gs=tas_entry[entry_key]     
                        
                        self.set_tas_entry(switch_name,iface,entry,hp,ti,gs)
            
                    
                    
                            
        except Exception as ex:
            message = "Error while trying to load interface configuration"
            self.logger.error(message)
            self.logger.error(ex)
        else:
            message = " Interface Configuration file Loaded"
            self.logger.info(message)

            
            
    def start_consuming(self):
        while True:
            try:
                if self.gv.TSN_PLUGIN_STATUS == self.gv.ENABLED:
                    self.channel.basic_consume(str(self.rbmq_queue_name),self.on_request)
                    self.logger.info(colored('[*] TSN plugin message thread -- > Waiting for messages. To exit press CTRL+C', 'yellow'))
                    self.channel.start_consuming()
                else:
                    message = "TSN plugin not enabled"
                    self.logger.error(message)
                    time.sleep(2)
                    self.goodbye()
            except pika_exceptions.ConnectionClosed or \
                   pika_exceptions.ChannelClosed or \
                   pika_exceptions.ChannelError as ex:
                    print (ex)
            except Exception as ex:    
                print (ex)
                self.connection.close()
    
#     def start_notifications(self):
#         self.logger.info(colored('[*] TSN plugin notifications thread -- > Waiting for messages. To exit press CTRL+C', 'blue'))
#         while True:
#             try:
#                 if self.gv.TSN_PLUGIN_STATUS == self.gv.ENABLED:
#                     if self.get_status_tsn_ctrl_endpoint():
#                         tsn_stats = self.get_tsn_stats()
#                         #enb_agent_id, enb_data = self.get_eNB_list()
#                         if self.gv.TSN_ES_INDEX_STATUS == "disabled":
#                             message = " Elasticsearch is disabled !! No more notifications are maintained"
#                             self.logger.info(message)
#                     else:
#                         message = "Notify >> TSN endpoint not enabled"
#                         self.logger.debug(message)
#                     time.sleep(10) # Periodic Notification
#                 else:
#                     message = "Notify >> TSN plugin not enabled"
#                     self.logger.error(message)
#                     self.goodbye()
# 
#             except pika_exceptions.ConnectionClosed or \
#                    pika_exceptions.ChannelClosed or \
#                    pika_exceptions.ChannelError:
#                 self.connection.close()


    def on_request(self, ch, method, props, body):
        enquiry = body.decode(self.gv.ENCODING_TYPE)
        enquiry = json.loads(enquiry)
        message = " Message received -> {} ".format(enquiry["plugin_message"])
        self.logger.info(message)
#         print (enquiry)
        elapsed_time_on_request = datetime.datetime.now() - datetime.datetime.strptime(enquiry["datetime"],'%Y-%m-%d %H:%M:%S.%f')

        try:
            
            if elapsed_time_on_request.total_seconds() < self.gv.TSN_TIMEOUT_REQUEST:
                send_reply = True
                ################################################################ 
                if enquiry["plugin_message"] == "get_status_tsn_ctrl_endpoint":
                    if self.get_status_tsn_ctrl_endpoint():
                        body = " TSN Controller endpoint is active"
                        status = "OK"
                    else:
                        body = " TSN Controller endpoint is not active"
                        status = "NOT OK"
                    response= {
                        "ACK": True,
                        "data": body,
                        "status_code": status
                    }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message)
                ##############################################################    
                if enquiry["plugin_message"] == "get_ptp_interface":
                    result="kostas"
    #                 result = self.get_ptp_interface(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                    }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message)
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_log_level":
                    result = self.get_ptp_log_level(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                    }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_logSyncInterval":
                    result = self.get_ptp_logSyncInterval(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_LogMinDelayReqInterval":
                    result = self.get_ptp_LogMinDelayReqInterval(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_LogMinDelayReqInterval":
                    result = self.get_ptp_LogMinDelayReqInterval(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
                    self.channel.basic_ack(delivery_tag=method.delivery_tag)
#                     self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_DelayAssymetry":
                    result = self.get_ptp_DelayAssymetry(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                    self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_minNeighborPropDelayThreshold":
                    result = self.get_ptp_minNeighborPropDelayThreshold(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_maxNeighborPropDelayThreshold":
                    result = self.get_ptp_maxNeighborPropDelayThreshold(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clockParent":
                    result = self.get_ptp_clockParent(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock":
                    result = self.get_ptp_clock(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_domain":
                    result = self.get_ptp_clock_domain(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_priority1":
                    result = self.get_ptp_clock_priority1(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_priority2":
                    result = self.get_ptp_clock_priority2(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_class":
                    result = self.get_ptp_clock_class(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_profile":
                    result = self.get_ptp_clock_profile(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_gmCapable":
                    result = self.get_ptp_clock_gmCapable(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_clock_slaveOnly":
                    result = self.get_ptp_clock_slaveOnly(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program":
                    result = self.get_ptp_program(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_timestamping":
                    result = self.get_ptp_program_timestamping(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_delayMechanism":
                    result = self.get_ptp_program_delayMechanism(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message)  
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_transport":
                    result = self.get_ptp_program_transport(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_timeaware_bridge":
                    result = self.get_ptp_program_timeaware_bridge(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_phydelay_compensate_in":
                    result = self.get_ptp_program_phydelay_compensate_in(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_phydelay_compensate_out":
                    result = self.get_ptp_program_phydelay_compensate_out(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_ptp_program_servo_locked_threshold":
                    result = self.get_ptp_program_servo_locked_threshold(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "tsn_ptp_display_time_properties":
                    result = self.tsn_ptp_display_time_properties(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_cycle_time":
                    result = self.get_tas_cycle_time(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_entry":
                    result = self.get_tas_entry(enquiry["node"],enquiry["iface"],enquiry["entry"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_enable":
                    result = self.get_tas_enable(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_ptp_mode":
                    result = self.get_tas_ptp_mode(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_gate_ctrl_period":
                    result = self.get_tas_gate_ctrl_period(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_display_profile":
                    result = self.get_tas_display_profile(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "get_tas_display_interface_status":
                    result = self.get_tas_display_interface_status(enquiry["node"],enquiry["iface"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_interface_enable":
                    result = self.set_ptp_interface_enable(enquiry["node"],enquiry["iface"],enquiry["status"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "set_ptp_LogSyncInterval":
                    result = self.set_ptp_LogSyncInterval(enquiry["node"],enquiry["iface"],enquiry["LogSyncInterval"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_LogAnnounceInterval":
                    result = self.set_ptp_LogAnnounceInterval(enquiry["node"],enquiry["iface"],enquiry["LogAnnounceInterval"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_LogMinDelayReqInterval":
                    result = self.set_ptp_LogMinDelayReqInterval(enquiry["node"],enquiry["iface"],enquiry["LogMinDelayReqInterval"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_SyncReceiptTimeout":
                    result = self.set_ptp_SyncReceiptTimeout(enquiry["node"],enquiry["iface"],enquiry["set_ptp_SyncReceiptTimeout"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_SyncdelayAsymmetry":
                    result = self.set_ptp_SyncdelayAsymmetry(enquiry["node"],enquiry["iface"],enquiry["delayAsymmetry"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_minNeighborPropDelayThreshold":
                    result = self.set_ptp_minNeighborPropDelayThreshold(enquiry["node"],enquiry["iface"],enquiry["minNeighborPropDelayThreshold"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_maxNeighborPropDelayThreshold":
                    result = self.set_ptp_maxNeighborPropDelayThreshold(enquiry["node"],enquiry["iface"],enquiry["maxNeighborPropDelayThreshold"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_clockDomain":
                    result = self.set_ptp_clockDomain(enquiry["node"],enquiry["clockDomain"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_clockPriority1":
                    result = self.set_ptp_clockPriority1(enquiry["node"],enquiry["clockPriority"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_clockPriority2":
                    result = self.set_ptp_clockPriority2(enquiry["node"],enquiry["clockPriority"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_clockClass":
                    result = self.set_ptp_clockClass(enquiry["node"],enquiry["clockClass"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "set_ptp_clockProfile":
                    result = self.set_ptp_clockProfile(enquiry["node"],enquiry["clockProfile"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message)  
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_gmCapable":
                    result = self.set_ptp_gmCapable(enquiry["node"],enquiry["gmCapable"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_slaveOnly":
                    result = self.set_ptp_slaveOnly(enquiry["node"],enquiry["slaveOnly"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "set_ptp_timestamping":
                    result = self.set_ptp_timestamping(enquiry["node"],enquiry["timestamping"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_delayMechanism":
                    result = self.set_ptp_delayMechanism(enquiry["node"],enquiry["delayMechanism"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "set_ptp_timeaware_bridge":
                    result = self.set_ptp_timeaware_bridge(enquiry["node"],enquiry["timeaware_bridge"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_phydelay_compensate_in":
                    result = self.set_ptp_phydelay_compensate_in(enquiry["node"],enquiry["phydelay_compensate_in"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_phydelay_compensate_out":
                    result = self.set_ptp_phydelay_compensate_out(enquiry["node"],enquiry["phydelay_compensate_out"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_servo_locked_threshold":
                    result = self.set_ptp_servo_locked_threshold(enquiry["node"],enquiry["servo_locked_threshold"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_logging_level":
                    result = self.set_ptp_logging_level(enquiry["node"],enquiry["logging_level"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_ptp_save_config":
                    result = self.set_ptp_save_config(enquiry["node"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_tas_cycle_time":
                    result = self.set_tas_cycle_time(enquiry["node"],enquiry["iface"],enquiry["bts"],enquiry["btn"],enquiry["ct"],enquiry["en"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_tas_entry":
                    result = self.set_tas_entry(enquiry["node"],enquiry["iface"],enquiry["entry"],enquiry["hp"],enquiry["ti"],enquiry["gs"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_tas_enable":
                    result = self.set_tas_enable(enquiry["node"],enquiry["iface"],enquiry["status"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_tas_ptp_mode":
                    result = self.set_tas_ptp_mode(enquiry["node"],enquiry["iface"],enquiry["mode"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "set_tas_gate_ctrl_period":
                    result = self.set_tas_gate_ctrl_period(enquiry["node"],enquiry["period"])
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK"
                        }
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "vlan_create":
                    
                    node=enquiry["node"]
                    vid=enquiry["vid"]
                    pbm_list=enquiry["pbm_list"]
                    ubm_list=enquiry["ubm_list"]
                    result = self.vlan_create(node,vid,pbm_list,ubm_list)
                    current_time = datetime.datetime.now()
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK",
                        "plugin_message": "test",
                        "datetime": str(current_time)
                        }
                    
#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "vlan_destroy":
                    result = self.vlan_destroy(enquiry["node"],enquiry["vid"])
                    current_time = datetime.datetime.now()
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK",
                        "plugin_message": "test",
                        "datetime": str(current_time)
                        }

#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ##############################################################
                if enquiry["plugin_message"] == "vlan_add":
                    result = self.vlan_add(enquiry["node"],enquiry["vid"],enquiry["pbm_list"],enquiry["ubm_list"])
                    current_time = datetime.datetime.now()
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK",
                        "plugin_message": "test",
                        "datetime": str(current_time)
                        }

#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message) 
                ############################################################## 
                if enquiry["plugin_message"] == "vlan_remove":
                    result = self.vlan_remove(enquiry["node"],enquiry["vid"],enquiry["ports"])
                    current_time = datetime.datetime.now()
                    response = {
                        "ACK": True,
                        "data": result,
                        "status_code": "OK",
                        "plugin_message": "test",
                        "datetime": str(current_time)
                        }

#                     self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    self.send_ack(ch, method, props, response, send_reply)
                    message=" RPC acknowledged - {}".format(response)
                    self.logger.info(message)
                    
                if enquiry["plugin_message"] == "test":
                    self.logger.info("have to fix the ack problem-decouple the response queue")
            
        except Exception as ex:
                message = "Error while trying to interpret message"
                self.logger.error(message)
                self.logger.error(ex)
            

# ################################################################
#                  GET method calls 
# ################################################################

    def get_status_tsn_ctrl_endpoint(self):
        """Get default or latest TSN CTRL endpoint.
        *@return: The host and port for controller in standard URI format
        """
        try:
            requests.get(self.tsn_ctrl_endpoint + "/")
            return True
        except Exception as ex:
            message="TSN CTRL endpoint {} is not active".format(self.tsn_ctrl_endpoint, ex)
            self.logger.debug(message)
            return False
            
    def get_ptp_interface(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
    
    def get_ptp_log_level(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
        
    def get_ptp_logSyncInterval(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)

    def get_ptp_logAnnounceInterval(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
        
    def get_ptp_LogMinDelayReqInterval(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)    
        
    def get_ptp_SyncReceiptTimeout(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
        
        
    def get_ptp_DelayAssymetry(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
        
    def get_ptp_minNeighborPropDelayThreshold(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)       
         
    def get_ptp_maxNeighborPropDelayThreshold(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)       
    
    
    def get_ptp_clockParent(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-parent"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)  
        
    def get_ptp_clock(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)          
            
    def get_ptp_clock_domain(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    def get_ptp_clock_priority1(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    
    def get_ptp_clock_priority2(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    def get_ptp_clock_class(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    def get_ptp_clock_profile(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    def get_ptp_clock_gmCapable(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    def get_ptp_clock_slaveOnly(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)   

    
    def get_ptp_program(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
            
    def get_ptp_program_timestamping(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
              
    def get_ptp_program_delayMechanism(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
             
    def get_ptp_program_transport(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
            
    def get_ptp_program_timeaware_bridge(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
            
    def get_ptp_program_phydelay_compensate_in(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
             
    def get_ptp_program_phydelay_compensate_out(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        
            
    def get_ptp_program_servo_locked_threshold(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        

    def tsn_ptp_display_time_properties(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-time-properties"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)]                )
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)        

    def get_tas_cycle_time(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-cycle-time"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
             
    def get_tas_entry(self,node,iface,entry):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-entry"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface),"/",
                str(entry)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
        
    def get_tas_enable(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-enable"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)    
            
    def get_tas_ptp_mode(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-ptp-mode"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
            
    def get_tas_gate_ctrl_period(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-gate-ctrl-period"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
            
    def get_tas_display_profile(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-profile"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)
            
            
    def get_tas_display_interface_status(self,node,iface):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-interface-status"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            response = requests.get(url,auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            response=json.loads(response.text)
            return response
        except Exception as ex:
            self.logger.info(ex)

# ################################################################
#                  SET method calls 
# ################################################################

    def set_ptp_interface_enable(self,node,iface,status):
        """Get ptp status per interface .
        *@return: The result.
        """
        if(TESTING):
            self.logger.info("ptp-enable-called")
            return
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "ptp": status
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)

    def set_ptp_LogSyncInterval (self,node,iface,LogSyncInterval):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "log-sync-interval": LogSyncInterval
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)

    def set_ptp_LogAnnounceInterval(self,node,iface,LogAnnounceInterval):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "log-announce-interval": LogAnnounceInterval
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)

    def set_ptp_LogMinDelayReqInterval(self,node,iface,LogMinDelayReqInterval):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "log-min-delay-req-interval": LogMinDelayReqInterval
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)
 
    def set_ptp_SyncReceiptTimeout(self,node,iface,SyncReceiptTimeout):
        """Get ptp status per interface .
        *@return: The result.
        """
        if(TESTING):
            self.logger.info("set_ptp_SyncReceiptTimeout-called")
            return
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "sync-receipt-timeout": SyncReceiptTimeout
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 


    def set_ptp_SyncdelayAsymmetry(self,node,iface,delayAsymmetry):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        if(TESTING):
            self.logger.info("set_ptp_SyncdelayAsymmetry-called")
            return
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "delay-asymmetry": delayAsymmetry  
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 
 
    def set_ptp_minNeighborPropDelayThreshold(self,node,iface,minNeighborPropDelayThreshold):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "min-neighbor-propdelay-threshold": minNeighborPropDelayThreshold  
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 
 
 
    def set_ptp_maxNeighborPropDelayThreshold(self,node,iface,maxNeighborPropDelayThreshold):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-inter"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsnptp-interface":{               
                    "interface": iface ,    
                    "max-neighbor-propdelay-threshold": maxNeighborPropDelayThreshold  
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 
  
    def set_ptp_clockDomain(self,node,clockDomain):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "domain-number": clockDomain
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 
            
    def set_ptp_clockPriority1(self,node,clockPriority):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        if(TESTING):
            self.logger.info("ptp-priority-called")
            return
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "priority1": clockPriority
                    }
                }
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)             
            
    def set_ptp_clockPriority2(self,node,clockPriority):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "priority2": clockPriority
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)
            
            
    def set_ptp_clockClass(self,node,clockClass):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "clock-class": clockClass
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 


    def set_ptp_clockProfile(self,node,clockProfile):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "profile": clockProfile
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 

    def set_ptp_gmCapable(self,node,gmCapable):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "gmcapable": gmCapable
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 
 
    def set_ptp_slaveOnly(self,node,slaveOnly):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-info"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-clock-info":{               
                    "slave-only": slaveOnly
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex) 
                        
                        
    def set_ptp_timestamping(self,node,timestamping):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "ptp-timestamping": timestamping
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                         
                        
                        
    def set_ptp_delayMechanism(self,node,delayMechanism):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "ptp-delay-mechanism": delayMechanism
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                         

    def set_ptp_timeaware_bridge(self,node,timeaware_bridge ):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "ptp-time-aware-bridge-mode": timeaware_bridge
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                                                 
                         
    def set_ptp_phydelay_compensate_in(self,node,phydelay_compensate_in):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "igress-hardware-path-delay-compensation": phydelay_compensate_in
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                             
                        
    def set_ptp_phydelay_compensate_out(self,node,phydelay_compensate_out):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "egress-hardware-path-delay-compensation": phydelay_compensate_out
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                        
                        
                        
                        
    def set_ptp_servo_locked_threshold(self,node,servo_locked_threshold):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "ptp-servo-locked-threshold": servo_locked_threshold
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                      
                        
    def set_ptp_logging_level(self,node,logging_level):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "logging-level": logging_level
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                       
                        
    def set_ptp_save_config(self,node):
        """Get ptp status per interface .
        *@return: The result.
        """
        if(TESTING):
            self.logger.info("ptp-save-called")
            return
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-ptp-clock-program"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsnptp-program":{               
                    "config-type-without-parameters": "save-cfg"
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                         
                        
    def set_tas_cycle_time(self,node,iface,bts,btn,ct,en):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-cycle-time"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsntas-cycle-time":{
                    "interface": iface,
                    "base-time-sec": bts,
                    "base-time-ns": btn,
                    "cycle-time": ct,
                    "extension-ns": en

                    }
                }
            
            if(TESTING):
                self.logger.info(body)
                self.logger.info("tas-set-cycle-called")
                return
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)           

    def set_tas_entry(self,node,iface,entry,hp,ti,gs):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-entry"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface),
                str(entry)])
            
            body={
                "tsntas-schedule-entry":{
                    "interface": iface,         
                    "entry": entry,          
                    "hold-preempt": hp,
                    "time-interval": ti,
                    "gate-state": gs


                    }
                }
            
            if(TESTING):
                self.logger.info(body)
                self.logger.info("tas-set-entry-called")
                return
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                   
                        
                        
    def set_tas_enable(self,node,iface,status):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-enable"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsntas-enable-schedule":{
                    "interface": iface,         
                    "enable": status          
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                        
                        
                        
    def set_tas_ptp_mode(self,node,iface,mode):                   
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-ptp-mode"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(iface)])
            
            body={
                "tsntas-ptp-mode":{
                    "interface": iface,         
                    "ptp-mode": mode          
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                             

    def set_tas_gate_ctrl_period(self,node,period):
        """Get ptp status per interface .
        *@return: The result.
        """
        
        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-tas-gate-ctrl-period"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix)])
            
            body={
                "tsntas-gate-ctrl-period":{
                    "period": period          
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)                   
                        
                        

    def vlan_create(self,node,vid,pbm_list,ubm_list):
        """Get ptp status per interface .
        *@return: The result.
        """
      

        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-vlan"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(vid)])
            
            body={
                "vlan":{
                    "id": vid, 
                    "ports": pbm_list,
                    "untagged-ports": ubm_list,
                    "operation": "create"
         
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)  

    def vlan_destroy(self,node,vid):
        """Get ptp status per interface .
        *@return: The result.
        """

        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-vlan"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(vid)])
            
            body={
                "vlan":{
                    "id": vid, 
                    "operation": "destroy"
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)  

    def vlan_add(self,node,vid,pbm_list,ubm_list):
        """Get ptp status per interface .
        *@return: The result.
        """

        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-vlan"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(vid)])
            
            body={
                "vlan":{
                    "id": vid, 
                    "ports": pbm_list,
                    "untagged-ports": ubm_list,
                    "operation": "add"
         
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)  


    def vlan_remove(self,node,vid,ports):
        """Get ptp status per interface .
        *@return: The result.
        """

        try:
            suffix=self.jox_config["tsn-ctrl-config"]["suffix-vlan"]
            
            url =''.join([
                str(self.tsn_ctrl_endpoint),
                str(node),
                str(suffix),
                str(vid)])
            
            body={
                "vlan":{
                    "id": vid, 
                    "ports": str(ports),
                    "operation": "remove"
         
                    }
                }
            
            response = requests.put(url,
                                    headers={'Content-Type':'application/json'},
                                    json=body,
                                    auth=HTTPBasicAuth(self.gv.TSN_CTRL_USERNAME, self.gv.TSN_CTRL_PASSWORD))
            
            return response.status_code
        except Exception as ex:
            self.logger.info(ex)  

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
        self.logger.info(colored(' [*] Waiting for messages. To exit press CTRL+C', 'green'))


if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Process commandline arguments and override configurations in jox_config.json')
#     parser.add_argument('--log', metavar='[level]', action='store', type=str,
#                         required=False, default='debug',
#                         help='set the log level: debug, info (default), warning, error, critical')
#     
#     args = parser.parse_args()
    ts = TSN_plugin("debug")
    ts.build()
#     ts.build_tsn_slice()
#     for line in sys.path:
#         self.logger.info (line)
     
#     result=ts.get_ptp_interface("new-netconf-device",0)
#     result=ts.get_ptp_log_level("new-netconf-device")
#     result=ts.get_ptp_logSyncInterval("new-netconf-device",0)
#     result=ts.get_ptp_logAnnounceInterval("new-netconf-device",0)
#     result=ts.get_ptp_LogMinDelayReqInterval("new-netconf-device",0)
#     result=ts.get_ptp_SyncReceiptTimeout("new-netconf-device",0)
#     result=ts.get_ptp_DelayAssymetry("new-netconf-device",0)
#     result=ts.get_ptp_minNeighborPropDelayThreshold("new-netconf-device",0)
#     result=ts.get_ptp_maxNeighborPropDelayThreshold("new-netconf-device",0)
#     result=ts.get_ptp_clockParent("new-netconf-device")
#     result=ts.get_ptp_clock("new-netconf-device")
#     result=ts.get_ptp_clock_slaveOnly("new-netconf-device")
#     result=ts.tsn_ptp_display_time_properties("new-netconf-device")
#     result=ts.get_tas_cycle_time("new-netconf-device",0)
#     result=ts.get_tas_entry("new-netconf-device", 0, 2)
#     result=ts.get_tas_display_profile("new-netconf-device",0)
#     result=ts.set_ptp_interface_enable("new-netconf-device",0,"enable")
#     result=ts.set_ptp_LogAnnounceInterval("new-netconf-device",0,0)
#     result=ts.set_ptp_LogMinDelayReqInterval("new-netconf-device",0,1)
#     result=ts.set_ptp_SyncReceiptTimeout("new-netconf-device",0,2)
#     result=ts.set_ptp_SyncdelayAsymmetry("new-netconf-device",0,100)
#     result=ts.set_ptp_minNeighborPropDelayThreshold("new-netconf-device",0,-500000)
#     result=ts.set_ptp_maxNeighborPropDelayThreshold("new-netconf-device",0,2000)
#     result=ts.set_ptp_clockDomain("new-netconf-device",10)
#     result=ts.set_ptp_clockPriority1("new-netconf-device",200)
#     result=ts.set_ptp_clockPriority2("new-netconf-device",10)
#     result=ts.set_ptp_clockClass("new-netconf-device",20)
#     result=ts.set_ptp_clockProfile("new-netconf-device","802dot1AS")
#     result=ts.set_ptp_gmCapable("new-netconf-device","false")
#     result=ts.set_ptp_slaveOnly("new-netconf-device","true") ---- @@200 but not working
#     result=ts.set_ptp_timestamping("new-netconf-device","hardware")
#     result=ts.set_ptp_delayMechanism("new-netconf-device",'e2e') ---- @@200 but not working

#     result=ts.set_ptp_SyncReceiptTimeout("new-netconf-device",0,2)
#     result=ts.set_ptp_SyncReceiptTimeout("new-netconf-device",0,2)
#     result=ts.set_ptp_SyncReceiptTimeout("new-netconf-device",0,2)
#     result=ts.vlan_create("new-netconf-device",200,'ge2','ge5')
#     result=ts.vlan_add("new-netconf-device",200,'ge3,ge4','ge6')
#     result=ts.vlan_remove("new-netconf-device",200,'ge2')
#     result=ts.vlan_destroy("new-netconf-device",200)
#     
#     self.logger.info(result)
    t1 = Thread(target=ts.start_consuming).start()
#     t2 = Thread(target=ts.start_notifications).start()        
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

class TSN_plugin(object):
    def __init__(self, tsn_log_level=None,):
        self.logger = logging.getLogger("jox-plugin.tsn")
        atexit.register(self.goodbye)  # register a message to print out when exit
        
       
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
        self.gv.TSN_CTRL_HOST = self.jox_config["tsn-ctrl-config"]["host"]
        self.gv.TSN_CTRL_PORT = self.jox_config["tsn-ctrl-config"]["port"]
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
        self.tsn_default_slice_config=None
        self.slice_config=None
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
        print(colored('[*] You are now leaving TSN plugin', 'red'))
        sys.exit(0)    
    
    
    def build(self):
        try:
            with open(''.join([self.dir_config, gv.TSN_PLUGIN_SLICE_CONFIG_FILE])) as data_file:
                data = json.load(data_file)
                data_file.close()
            self.tsn_default_slice_config = data  # This config is to be used if DL % excceed 100
            self.logger.info(" TSN default endpoint is {}".format(self.tsn_ctrl_endpoint))
#             if self.gv.ELASTICSEARCH_ENABLE:
#                 self.jesearch = es.JESearch(self.gv.ELASTICSEARCH_HOST, self.gv.ELASTICSEARCH_PORT,
#                                             self.gv.ELASTICSEARCH_LOG_LEVEL)
#             self.parameters = pika.ConnectionParameters(self.rbmq_server_ip, self.rbmq_server_port)
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

        
        
    def start_consuming(self):
        while True:
            try:
                if self.gv.TSN_PLUGIN_STATUS == self.gv.ENABLED:
                    self.channel.basic_consume(self.on_request, queue=self.rbmq_queue_name, no_ack=False)
                    print(colored('[*] TSn plugin message thread -- > Waiting for messages. To exit press CTRL+C', 'yellow'))
                    self.channel.start_consuming()
                else:
                    message = "TSN plugin not enabled"
                    self.logger.error(message)
                    time.sleep(2)
                    self.goodbye()
            except pika_exceptions.ConnectionClosed or \
                   pika_exceptions.ChannelClosed or \
                   pika_exceptions.ChannelError:
                self.connection.close()
    
    def start_notifications(self):
        print(colored('[*] TSN plugin notifications thread -- > Waiting for messages. To exit press CTRL+C', 'blue'))
        while True:
            try:
                if self.gv.TSN_PLUGIN_STATUS == self.gv.ENABLED:
                    if self.get_status_tsn_ctrl_endpoint():
                        tsn_stats = self.get_tsn_stats()
                        #enb_agent_id, enb_data = self.get_eNB_list()
                        if self.gv.TSN_ES_INDEX_STATUS == "disabled":
                            message = " Elasticsearch is disabled !! No more notifications are maintained"
                            self.logger.info(message)
                    else:
                        message = "Notify >> TSN endpoint not enabled"
                        self.logger.debug(message)
                    time.sleep(10) # Periodic Notification
                else:
                    message = "Notify >> TSN plugin not enabled"
                    self.logger.error(message)
                    self.goodbye()

            except pika_exceptions.ConnectionClosed or \
                   pika_exceptions.ChannelClosed or \
                   pika_exceptions.ChannelError:
                self.connection.close()
                
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

# -------- ptp method calls ------------ #
    
    def get_ptp_display_interface(self,node,iface):
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
            print(ex)
    
    def get_ptp_display_log_level(self,node):
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
            print(ex)        
        
    def get_ptp_display_logSyncInterval(self,node,iface):
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
            print(ex)

    def get_ptp_display_logAnnounceInterval(self,node,iface):
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
            print(ex)
        
    def get_ptp_display_LogMinDelayReqInterval(self,node,iface):
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
            print(ex)    
        
    def get_ptp_display_SyncReceiptTimeout(self,node,iface):
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
            print(ex)        
        
        
    def get_ptp_display_DelayAssymetry(self,node,iface):
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
            print(ex)        
        
    def get_ptp_display_minNeighborPropDelayThreshold(self,node,iface):
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
            print(ex)       
         
    def get_ptp_display_maxNeighborPropDelayThreshold(self,node,iface):
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
            print(ex)       
    
    
    def get_ptp_display_clockParent(self,node):
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
            print(ex)  
        
    def get_ptp_display_clock(self,node):
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
            print(ex)          
            
    def get_ptp_display_clock_domain(self,node):
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
            print(ex)   

    def get_ptp_display_clock_priority1(self,node):
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
            print(ex)   

    
    def get_ptp_display_clock_priority12(self,node):
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
            print(ex)   

    def get_ptp_display_clock_class(self,node):
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
            print(ex)   

    def get_ptp_display_clock_profile(self,node):
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
            print(ex)   

    def get_ptp_display_clock_gmCapable(self,node):
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
            print(ex)   

    def get_ptp_display_clock_slaveOnly(self,node):
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
            print(ex)   

    
    def get_ptp_display_program(self,node):
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
            print(ex)        
            
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
            print(ex)        
              
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
            print(ex)        
             
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
            print(ex)        
            
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
            print(ex)        
            
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
            print(ex)        
             
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
            print(ex)        
            
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
            print(ex)        

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
            print(ex)        

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
            print(ex)
             
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
            print(ex)
        
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
            print(ex)    
            
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
            print(ex)
            
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
            print(ex)
            
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
            print(ex)
            
            
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
            print(ex)








            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process commandline arguments and override configurations in jox_config.json')
    parser.add_argument('--log', metavar='[level]', action='store', type=str,
                        required=False, default='debug',
                        help='set the log level: debug, info (default), warning, error, critical')
    
    args = parser.parse_args()
    ts = TSN_plugin(args.log)
    ts.build()
        
#     for line in sys.path:
#         print (line)
     
#     result=ts.get_ptp_display_interface("new-netconf-device",0)
#     result=ts.get_ptp_display_log_level("new-netconf-device")
#     result=ts.get_ptp_display_logSyncInterval("new-netconf-device",0)
#     result=ts.get_ptp_display_logAnnounceInterval("new-netconf-device",0)
#     result=ts.get_ptp_display_LogMinDelayReqInterval("new-netconf-device",0)
#     result=ts.get_ptp_display_SyncReceiptTimeout("new-netconf-device",0)
#     result=ts.get_ptp_display_DelayAssymetry("new-netconf-device",0)
#     result=ts.get_ptp_display_minNeighborPropDelayThreshold("new-netconf-device",0)
#     result=ts.get_ptp_display_maxNeighborPropDelayThreshold("new-netconf-device",0)
#     result=ts.get_ptp_display_clockParent("new-netconf-device")
#     result=ts.get_ptp_display_clock("new-netconf-device")
#     result=ts.get_ptp_display_clock_slaveOnly("new-netconf-device")
#     result=ts.tsn_ptp_display_time_properties("new-netconf-device")
#     result=ts.get_tas_cycle_time("new-netconf-device",0)
#     result=ts.get_tas_entry("new-netconf-device", 0, 2)
    result=ts.get_tas_display_profile("new-netconf-device",0)
    
    print(result)
#     t1 = Thread(target=ts.start_consuming).start()
#     t2 = Thread(target=ts.start_notifications).start()        
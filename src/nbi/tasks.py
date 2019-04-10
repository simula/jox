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
import os, sys

dir_root_path = os.path.dirname(os.path.abspath(__file__ + "/../../"))
sys.path.append(dir_root_path)

import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "/.."))

gv_file = ''.join([dir_parent_path, '/common'])
sys.path.append(gv_file)
from src.common.config import gv as gv
from termcolor import colored
import pika
import logging
import json

logger = logging.getLogger('JOX.NBI')
import uuid
import time


class listTasks(object):
	def __init__(self):
		self.jox_config = ""
		self.gv = gv
		logger = logging.getLogger("NBI.tasks")
		######## STEP 1: Load Configuration ########
		try:
			filename = ''.join([dir_parent_path, '/common/config/jox_config.json'])
			with open(filename, 'r') as f:
				self.jox_config = json.load(f)
				self.gv.RBMQ_SERVER_IP = self.jox_config['rabbit-mq-config']['rabbit-mq-server-ip']
				self.gv.RBMQ_SERVER_PORT = self.jox_config['rabbit-mq-config']['rabbit-mq-server-port']
				self.gv.RBMQ_QUEUE = self.jox_config['rabbit-mq-config']['rabbit-mq-queue']
				# flask
				self.gv.FLASK_SERVER_IP = self.jox_config['flask-config']['flask-server']
				self.gv.FLASK_SERVER_PORT = self.jox_config['flask-config']['flask-port']
				self.gv.FLASK_SERVER_DEBUG = self.jox_config['flask-config']['flask-debug']
				#
				self.gv.STORE_DIR = self.jox_config['store-config']["store-directrory"]
				self.gv.ENCODING_TYPE = self.jox_config['encoding-type']
				
				self.gv.LOG_FILE = self.jox_config['log-config']['log-file']
				self.gv.LOG_LEVEL = self.jox_config['log-config']['log-level']
		
		except IOError as ex:
			message = "Could not load JOX Configuration file.I/O error({0}): {1}".format(ex.errno, ex.strerror)
			logger.info(message)
			logger.debug(message)
		else:
			message = "JOX Configuration file Loaded"
			logger.info(message)
			logger.debug(message)
		
		#########  STEP 3: Logging Configuration ########
		
		if self.gv.LOG_LEVEL == 'debug':
			logger.setLevel(logging.DEBUG)
		elif self.gv.LOG_LEVEL == 'info':
			logger.setLevel(logging.INFO)
		elif self.gv.LOG_LEVEL == 'warn':
			logger.setLevel(logging.WARNING)
		elif self.gv.LOG_LEVEL == 'error':
			logger.setLevel(logging.ERROR)
		elif self.gv.LOG_LEVEL == 'critic':
			logger.setLevel(logging.CRITICAL)
		else:
			logger.setLevel(logging.INFO)
		# create file handler which logs even debug messages
		LOGFILE = self.gv.LOG_FILE
		
		file_handler = logging.FileHandler(LOGFILE)
		file_handler.setLevel(logging.DEBUG)
		
		### RabbitMQ  param ###
		self.queue_name = self.gv.RBMQ_QUEUE
		self.host_name = self.gv.RBMQ_SERVER_IP
		self.port = self.gv.RBMQ_SERVER_PORT
		
		self.connection = None
		self.channel = None
		self.result = None
		self.callback_queue = None
		
		self.run()
	
	def run(self, retry=False):
		if retry:
			self.connection.close()
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_name, port=self.port))
		self.channel = self.connection.channel()

		self.result = self.channel.queue_declare(exclusive=True)
		self.callback_queue = self.result.method.queue
		
		self.channel.basic_consume(self.on_response, no_ack=True,
		                           queue=self.callback_queue)
		
	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body
			
	def call(self, msg):
		messahe_not_sent = True
		while messahe_not_sent:
			try:
				self.response = None
				self.corr_id = str(uuid.uuid4())
				self.channel.basic_publish(exchange='',
				                           routing_key=self.queue_name,
				                           properties=pika.BasicProperties(
					                           reply_to=self.callback_queue,
					                           correlation_id=self.corr_id,
				                           ),
				                           body=msg)
				messahe_not_sent = False
			except:
				time.sleep(0.5)
				self.run(True)
		while self.response is None:
			self.connection.process_data_events()
		
		
		return self.response

	def exit(self):
		self.connection.close()

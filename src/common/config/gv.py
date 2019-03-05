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
 * \brief description: Global Variables -  Used by any file/Class
 * \authors:
 * \company: Eurecom
 * \email:contact@mosaic5g.io
 """


global CONFIG_FILE
global JOX_CONFIG_KEY

global KVM
global LXC
global LOGFILE
global LOG_LEVEL
global console


# config file param
CONFIG_FILE= "jox_config.json"
JOX_CONFIG_KEY=(CONFIG_FILE.split('.'))[0]

# BMQ param
RBMQ_SERVER_IP=""
RBMQ_SERVER_PORT=""
RBMQ_QUEUE=""


# FLASK param
FLASK_SERVER_IP=""
FLASK_SERVER_PORT=""
FLASK_SERVER_DEBUG=""


# Elasticsearch param
ELASTICSEARCH_ENABLE=True
ELASTICSEARCH_HOSt=""
ELASTICSEARCH_PORT=""
ELASTICSEARCH_LOG_LEVEL=""
ELASTICSEARCH_RETRY_ON_CONFLICT=0

# resources types
KVM="kvm"
LXC="lxc"


# config param
LOG_FILE=""
LOG_LEVEL=""



STATS_TIMER=""


# HTTP_status code
# Success
HTTP_200_OK=None
HTTP_204_NO_CONTENT=None
# Error
HTTP_400_BAD_REQUEST=None
HTTP_404_NOT_FOUND=None
HTTP_420_METHOD_FAILURE=None
HTTP_424_FAILED_DEPENDENCY=None

# juju related parameters
JUJU_MAX_RETRY_CONNECTION_MODEL_AVAILABLE=None # maximum number or retries to verify that the new created model is available
JUJU_INTERVAL_CONNECTION_MODEL_AVAILABLE=None  # in seconds

JUJU_MAX_RETRY_CONNECTION_MODEL_ACCESSIBLE=None # maximum number or retries to connect to already exist juju model
JUJU_INTERVAL_CONNECTION_MODEL_ACCESSIBLE=None  # in seconds

# ssh key
SSH_KEY_DIRECTORY = ""
SSH_KEY_NAME = ""
SSH_USER=""
SSH_PASSWORD=""


# cach param
STORE_DIR = ""


ENCODING_TYPE = "utf-8"

XENIAL="xenial"
OS_SERIES={"16.04": "xenial",
			"18.04": "bionic",
                         }

MB = 1
GB = 1024

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

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "/mnt"))

import logging
from src.nbi import tasks
#import json
from flask import Flask, request, jsonify, json
import datetime
import tarfile, io
from termcolor import colored

SLICE_TEMPLATE_DIRECTORY_DEFAULT = ''.join([dir_parent_path, '/jox_store'])

app = Flask(__name__)

logger = logging.getLogger('jox.NBI')
logging.basicConfig(level=logging.INFO)
logger.info('Starting JOX main thread')

listOfTasks = tasks.listTasks()
standard_reqst = {
	"datetime": None,
	"request-uri": None,
	"request-type": None,  # get, post; delete
	"parameters": {
		"template_directory": None,
		"nsi_name": None,
		"nssi_name": None,
		"nsi_directory": None,
		"nssi_directory": None,
		"nssi_key": None,
		"service_name": None,
		# related to the relations between two services
		"nssi_name_source": None,
		"service_name_source": None,
		"nssi_name_target": None,
		"service_name_target": None,
		#
		"machine_name": None,
		"relation": None,
		"service_key": None,
		"machine_key": None,
		"relation_key": None,
		#
		"es_index_page": None,
		"es_key": None,
		# juju
		"juju_key_val": None,
		# package onboarding
		"package_onboard_data": "",
		"package_name": None,
		# related to logs
		"log": None,
		# Parameters to define the disaggregation type; monolithic (mon), functional-split (fs)
		"disaggregation": None,
		# Relations
		"relations": None,
		# Relations
		"configuration": None,
		# vlan
		"vlan": None,# vlan config
		"vlan_id": None
	}
}

"""
@apiDefine GroupJox JOX
This API endpoint contains the main capabilities that are needed
before deploying and monitoring the slices. Through the set of APIs offered in this section, you can vistualize jox configuration, and
jox capabilities, in addition to the possibility to visualize the
template slice/subslice before deploying your slice.
"""

"""
@apiDefine resource_management Resource Management
In this section, we introduce a set of endpoints for managing the resources
"""

"""
@apiDefine GroupOnboarding Onboarding
This section presents the endpoints related to package onboarding.
"""

"""
@apiDefine GroupSlice Slice
This section holds the main functionalities for slice management, like add, update, and remove a slice. Additionaly, 
This section presents endpoints to  get the context of already deployed slices
"""

"""
@apiDefine GroupSubSlice Sub-slice
This API endpoint is dedictaed for subslcies. for the current version of JoX, you can only get the
context of the subslices, without any possibility to add/update/remove subslice.
"""

"""
@apiDefine GroupElasticsearch Elasticsearch
This API endpoint is a wrapper of elasticsearch (ES), where the main functionality that are supported in the current
version of JoX, are:

- get list of all index-pages that are saved to ES
- delete all the index-pages


This section contains the main functionalities to interact with elasticsearch,
like get the page-indexes in elasticsearch, save and delete page-indexe to(from) elasticsearch
"""

"""
@apiDefine GroupMonitoring Monitoring
This section contains the main functionalities for monitoring
slices, sub-slices, services, machines, and relations. Further, this monitoring information can be obtained either from JoX (more specifically from elasticsearch where the monitoring information is saved automatically) or from juju. Another endpoint to get the log from JoX/juju with different log levels is also introduced here.
"""

"""
@apiDefine Relations Relations
This section contains the main functionalities for adding and removing relations
It is particularly helpful when e.g. switching between monolithic and functional split mode of RAN
"""

"""
@apiDefine Configuration Configuration
This section contains the main functionalities to get and set the configuration of applications, as well as the configurations of juju model
"""

@app.route('/')
def jox_homepage():
	"""
    @apiGroup GroupJox
    @apiName GetJoxHomepage

    @api {get}  / Homepage
	@apiDescription The homepage of JoX
    
    @apiExample {curl} Example usage:
         curl -i http://localhost:5000/

    @apiSuccessExample Success-Response:
        HTTP/1.0 200 OK
        {
        Welcome to JOX!
        To get the list of the capabilities and jox configuration, use the following:
        http://localhost:5000/jox
        }
    """
	logger.debug("Receive homepage request")
	logger.info("Receive homepage request")
	message = "Welcome to JOX! \n" \
	          "To get the list of the capabilities and jox configuration, use the following \n" \
	          "{}".format(''.join([request.host_url, 'jox \n']))

	return message


jox_capabilities = \
{
    "jox": {
        "/": "JoX homepge",
        "/jox": "return jox configuration and the list of nbi capabilities",
        "/list": {
            "1": "return the list of onboarded packages",
            "2": "example: curl  http://localhost:5000/list; return the list of onboraded packages in jox store",
            "3": "example: curl  http://localhost:5000/list?url=/home/ubuntu/slice_package; return list of packages in given directory"
    },
    "/ls": "alias to /list",
    "/show/<string:nsi_name>": {
        "1": "show the content of the template nsi_name",
        "3": "example: curl  http://localhost:5000/show/nssi_1.yaml?url=/home/ubuntu/slice_package/mosaic5g/nssi; show the content of the given template in given directory"
        }
    },
    "onboarding": {
        "/onboard": {
            "1": "onboard the given package to jox store",
            "2": "example: curl  http://localhost:5000/onboard --upload-file mosaic5g.tar.gz; onboard the package mosaic5g.tar.gz to jox store"
        }
    },
    "slice": {
        "/nsi": "alias to /nsi/all",
        "/nsi/<string:nsi_name>": {
            "DELETE": "delete the slice nsi_name",
            "GET": "get context of already deployed slice nsi_name",
            "POST": "deploy/update the slice from the package pkg_name(the name of the package in jox store)"
        },
        "/nsi/all": "get the context of all deployed slices"
    },
    "sub-slice": {
        "/nssi": "alias to /nssi/all",
        "/nssi/<string:nsi_name>": {
            "DELETE": "Not supported",
            "GET": "get context of all subslices attached to the slice nsi_name",
            "POST": "Not supported"
        },
        "/nssi/<string:nsi_name>/<string:nssi_name>": {
            "DELETE": "Not supported",
            "GET": "get context of the subslice nssi_name attached to the slice nsi_name",
            "POST": "Not supported"
        },
        "/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>": {
            "DELETE": "Not supported",
            "GET": "get crtain entity nssi_key of subslice nssi_name attached to the slice nsi_name",
            "POST": "Not supported"
        },
        "/nssi/all": {
            "GET": "get the context of all subslices"
        }
    },
    "elasticsearch": {
        "/es": {
            "DELETE": "Delete all the index-pages in elasticsearch",
            "GET": "get all the index-pages in elasticsearch",
            "POST": "Not supported"
        },
        "/es/<string:es_index_page>": {
            "DELETE": "Delete the index-page es_index_page from elasticsearch",
            "GET": "get the content of the index-page es_index_page from  elasticsearch",
            "POST": "save the content of the index-page es_index_page to elasticsearch"
        },
        "/es/<string:es_index_page>/<string:es_key>": {
            "DELETE": "Not supported",
            "GET": "get certain index es_key from the index-page es_index_page from elasticsearch",
            "POST": "Not supported"
        }
    },
    "monitoring": {
        "juju": {
                "/monitor/juju": "get monitoring information on the current juju model (applications,machines, and relations)",
                "/monitor/juju/<string:juju_key_val>": {
                "1": "get specific monitoring information juju_key_val from the current juju model",
                "2": "The allowable values for juju_key_val/monitor/juju/ are:",
                "3": "all: get all the information (equivalent to /monitor/juju)",
                "4": "applications: get only on the applications",
                "5": "machines: get only on the machines",
                "6": "relations: get only on the relations"
            },
            "/monitor/juju/<string:juju_key_val>/<string:cloud_name>/<string:model_name>": {
                "1": "get monitoring information from specific juju model",
                "2": "juju_key_val: the same allowable values fo /monitor/juju/<string:juju_key_val>",
                "3": "cloud_name: the name of juju controller",
                "4": "model_name: the name of juju model hosted at the juju controller cloud_name"
            }
        },
        "log": {
                "/log": "get all the levels of log of jox",
                "/log/<string:log_source>": {
                "1": "get all the levels of log either from jox or from juju. This is defined by the the value of log_source which can be either 'jox' or juju"
            },
                "/log/<string:log_source>/<string:log_type>": {
                "1": "Here you can specifu not only the source of the log (jox or juju), but also the log level that is defined by log_type",
                "2": "The allowable values for log_type are: all, error, debug, info, warning",
                "3": "Notice the default value is 'all'"
            }
        },
        "machine": {
            "/monitor/machine/<string:nsi_name>": "get monitoring information on all machines of the slice nsi_name",
            "/monitor/machine/<string:nsi_name>/<string:nssi_name>": "get monitoring information on all machines of the subslice nssi_name attached to the slice nsi_name",
            "/monitor/machine/<string:nsi_name>/<string:nssi_name>/<string:machine_name>": "get monitoring information on the machine service_name of the subslice nssi_name attached to the slice nsi_name"
        },
        "relation": {
            "/monitor/relation/<string:nsi_name>": "get monitoring information on the relations of the slice nsi_name",
            "/monitor/relation/<string:nsi_name>/<string:nssi_name>": "get monitoring information on the relations of the subslice nssi_name attached to the slice nsi_name"
        },
        "service": {
            "/monitor/service/<string:nsi_name>": "get monitoring information on all services of the slice nsi_name",
            "/monitor/service/<string:nsi_name>/<string:nssi_name>": "get monitoring information on all services of the subslice nssi_name attached to the slice nsi_name",
            "/monitor/service/<string:nsi_name>/<string:nssi_name>/<string:service_name>": "get monitoring information on the service service_name of the subslice nssi_name attached to the slice nsi_name"
        },
        "slice&sub-sclice": {
            "/monitor/nsi": "get monitoring information on all the deployed slices",
            "/monitor/nsi/<string:nsi_name>": "get monitoring information on the deployed slice nsi_name",
            "/monitor/nsi/<string:nsi_name>/<string:nssi_name>": "get monitoring information on the subslice nssi_name from the deployed slice nsi_name",
            "/monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>": "get monitoring information on certain entity of the the subslice nssi_name from the deployed slice nsi_name"
        }
    }
}



@app.route('/jox')
def jox_config():
	"""
    @apiGroup GroupJox
    @apiName GetJoxCapabilities

    @apiDescription This endpoint gives you the configuration of jox, as well as the list of its capabilities
    @api {get}  /jox Configuration and capabilities

    @apiExample {curl} Example usage:
         curl -i http://localhost:5000/jox

	@apiSuccessExample Success-Response:
    {
        "elapsed-time": "0:00:00.053586",
        "jox-capabilities": {
            "jox": {
                "/": "JoX homepge",
                "/jox": "return jox configuration and the list of nbi capabilities",
                "/list": {
                    "1": "return the list of onboarded packages",
                    "2": "example: curl  http://localhost:5000/list; return the list of onboraded packages in jox store",
                    "3": "example: curl  http://localhost:5000/list?url=/home/ubuntu/slice_package; return list of packages in given directory"
                },
                "/ls": "alias to /list",
                "/show/<string:nsi_name>": {
                    "1": "show the content of the template nsi_name",
                    "3": "example: curl  http://localhost:5000/show/nssi_1.yaml?url=/home/ubuntu/slice_package/mosaic5g/nssi; show the content of the given template in given directory"
                }
            },
            "onboarding": {
                "/onboard": {
                    "1": "onboard the given package to jox store",
                    "2": "example: curl  http://localhost:5000/onboard --upload-file mosaic5g.tar.gz; onboard the package mosaic5g.tar.gz to jox store"
                }
            },
            "slice": {
                "/nsi": "alias to /nsi/all",
                "/nsi/<string:nsi_name>": {
                    "DELETE": "delete the slice nsi_name",
                    "GET": "get context of already deployed slice nsi_name",
                    "POST": "deploy/update the slice from the package pkg_name(the name of the package in jox store)"
                },
                "/nsi/all": "get the context of all deployed slices"
            },
            "sub-slice": {
                "/nssi": "alias to /nssi/all",
                "/nssi/<string:nsi_name>": {
                    "DELETE": "Not supported",
                    "GET": "get context of all subslices attached to the slice nsi_name",
                    "POST": "Not supported"
                },
                "/nssi/<string:nsi_name>/<string:nssi_name>": {
                    "DELETE": "Not supported",
                    "GET": "get context of the subslice nssi_name attached to the slice nsi_name",
                    "POST": "Not supported"
                },
                "/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>": {
                    "DELETE": "Not supported",
                    "GET": "get crtain entity nssi_key of subslice nssi_name attached to the slice nsi_name",
                    "POST": "Not supported"
                },
                "/nssi/all": {
                    "GET": "get the context of all subslices"
                }
            },
            "elasticsearch": {
                "/es": {
                    "DELETE": "Delete all the index-pages in elasticsearch",
                    "GET": "get all the index-pages in elasticsearch",
                    "POST": "Not supported"
                },
                "/es/<string:es_index_page>": {
                    "DELETE": "Delete the index-page es_index_page from elasticsearch",
                    "GET": "get the content of the index-page es_index_page from  elasticsearch",
                    "POST": "save the content of the index-page es_index_page to elasticsearch"
                },
                "/es/<string:es_index_page>/<string:es_key>": {
                    "DELETE": "Not supported",
                    "GET": "get certain index es_key from the index-page es_index_page from elasticsearch",
                    "POST": "Not supported"
                }
            },
            "monitoring": {
                "juju": {
                        "/monitor/juju": "get monitoring information on the current juju model (applications,machines, and relations)",
                        "/monitor/juju/<string:juju_key_val>": {
                        "1": "get specific monitoring information juju_key_val from the current juju model",
                        "2": "The allowable values for juju_key_val/monitor/juju/ are:",
                        "3": "all: get all the information (equivalent to /monitor/juju)",
                        "4": "applications: get only on the applications",
                        "5": "machines: get only on the machines",
                        "6": "relations: get only on the relations"
                    },
                    "/monitor/juju/<string:juju_key_val>/<string:cloud_name>/<string:model_name>": {
                        "1": "get monitoring information from specific juju model",
                        "2": "juju_key_val: the same allowable values fo /monitor/juju/<string:juju_key_val>",
                        "3": "cloud_name: the name of juju controller",
                        "4": "model_name: the name of juju model hosted at the juju controller cloud_name"
                    }
                },
                "log": {
                        "/log": "get all the levels of log of jox",
                        "/log/<string:log_source>": {
                        "1": "get all the levels of log either from jox or from juju. This is defined by the the value of log_source which can be either 'jox' or juju"
                    },
                        "/log/<string:log_source>/<string:log_type>": {
                        "1": "Here you can specifu not only the source of the log (jox or juju), but also the log level that is defined by log_type",
                        "2": "The allowable values for log_type are: all, error, debug, info, warning",
                        "3": "Notice the default value is 'all'"
                    }
                },
                "machine": {
                    "/monitor/machine/<string:nsi_name>": "get monitoring information on all machines of the slice nsi_name",
                    "/monitor/machine/<string:nsi_name>/<string:nssi_name>": "get monitoring information on all machines of the subslice nssi_name attached to the slice nsi_name",
                    "/monitor/machine/<string:nsi_name>/<string:nssi_name>/<string:machine_name>": "get monitoring information on the machine service_name of the subslice nssi_name attached to the slice nsi_name"
                },
                "relation": {
                    "/monitor/relation/<string:nsi_name>": "get monitoring information on the relations of the slice nsi_name",
                    "/monitor/relation/<string:nsi_name>/<string:nssi_name>": "get monitoring information on the relations of the subslice nssi_name attached to the slice nsi_name"
                },
                "service": {
                    "/monitor/service/<string:nsi_name>": "get monitoring information on all services of the slice nsi_name",
                    "/monitor/service/<string:nsi_name>/<string:nssi_name>": "get monitoring information on all services of the subslice nssi_name attached to the slice nsi_name",
                    "/monitor/service/<string:nsi_name>/<string:nssi_name>/<string:service_name>": "get monitoring information on the service service_name of the subslice nssi_name attached to the slice nsi_name"
                },
                "slice&sub-sclice": {
                    "/monitor/nsi": "get monitoring information on all the deployed slices",
                    "/monitor/nsi/<string:nsi_name>": "get monitoring information on the deployed slice nsi_name",
                    "/monitor/nsi/<string:nsi_name>/<string:nssi_name>": "get monitoring information on the subslice nssi_name from the deployed slice nsi_name",
                    "/monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>": "get monitoring information on certain entity of the the subslice nssi_name from the deployed slice nsi_name"
                }
            }
        },
        "jox-config": {
            "authors-list": [
            {
                "email": "contact@mosaic-5g.io",
                "name": "Eurecom"
            }
            ],
            "clouds-list": [
            {
                "cloud-endpoint": "192.168.1.81:17070",
                "cloud-name": "nymphe-edu",
                "cloud-password": "0f771f7a3dd172105efc539fd3d93406",
                "cloud-type": "manual",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "192.168.1.42:17070",
                "cloud-name": "nympheController-edu",
                "cloud-password": "841073c837889f34abcb15d205eeccd9",
                "cloud-type": "manual",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "192.168.1.32:17070",
                "cloud-name": "localhost-borer",
                "cloud-password": "8b039930a618e3cd794598d987ca32b7",
                "cloud-type": "lxd",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "10.124.51.249:17070",
                "cloud-name": "sakura-home",
                "cloud-password": "0ff27627bdb42216ec2c0c6296d832c9",
                "cloud-type": "manual",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "192.168.1.100:17070",
                "cloud-name": "psoque-home",
                "cloud-password": "c9db02159a4400f6756af2df370b42c5",
                "cloud-type": "manual",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "10.124.51.83:17070",
                "cloud-name": "localhost",
                "cloud-password": "2dfabf48abb9b4277c5a629645962dfb",
                "cloud-type": "lxd",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "10.146.98.21:17070",
                "cloud-name": "adalia-home",
                "cloud-password": "4f1d6e5586321627aed23473c7a174ef",
                "cloud-type": "lxd",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            },
            {
                "cloud-endpoint": "192.168.12.162:17070",
                "cloud-name": "adalia-edu",
                "cloud-password": "468a141af452b0f096584e86d02d4991",
                "cloud-type": "manual",
                "cloud-username": "admin",
                "description": "credentials of your juju controller"
            }
            ],
            "date": "01-03-2019",
            "description": "Jox configuration file",
            "elasticsearch-config": {
            "elasticsearch-host": "localhost",
            "elasticsearch-log-level": "error",
            "elasticsearch-port": "9200",
            "elasticsearch-retry-on-conflict": 3
            },
            "encoding-type": "utf-8",
            "flask-config": {
            "flask-debug": "FALSE",
            "flask-port": 5000,
            "flask-server": "localhost"
            },
            "flexran-config": {
            "host": "192.168.122.29",
            "port": 9999
            },
            "flexran-plugin-config": {
            "es-index-name": "flexran_plugin",
            "plugin-status": "enabled",
            "rabbit-mq-queue": "QueueFlexRAN",
            "rabbit-mq-server-ip": "localhost",
            "rabbit-mq-server-port": 5672,
            "timeout-request": 300
            },
            "host-config": {
            "small": {
                "Comment": "disk_size is in GB unit",
                "Comment_2": "mem_size is in MB unit",
                "disk_size": 3,
                "mem_size": 512,
                "num_cpus": 1
            },
            "tiny": {
                "Comment": "disk_size is in GB unit",
                "Comment_2": "mem_size is in MB unit",
                "disk_size": 1,
                "mem_size": 256,
                "num_cpus": 1
            }
            },
            "http": {
            "200": {
                "no-content": 204,
                "ok": 200
            },
            "400": {
                "bad-request": 400,
                "not-found": 404
            }
            },
            "jox version": 1,
            "jox-config": {
            "_Comment": "JOX_TIMEOUT_REQUEST is in seconds unit",
            "jox-timeout-request": 300
            },
            "juju-config": {
            "_Comment": "connect-model-available: define the parameters to access to a newly created model is available",
            "_Comment_2": "connect-model-accessible: define parameters to access to already exist juju model",
            "connect-model-accessible-interval": 3,
            "connect-model-accessible-max-retry": 50,
            "connect-model-available-interval": 10,
            "connect-model-available-max-retry": 10
            },
            "juju_version": 2.4,
            "linux-os-series-config": {
            "14.04": "trusty",
            "16.04": "xenial",
            "18.04": "bionic"
            },
            "llmec-config": {
            "llmec-ip": "localhost",
            "llmec-port": "9999",
            "plugin-status": "disabled",
            "rabbit-mq-queue": "QueuellMEC",
            "rabbit-mq-server-port": 5672
            },
            "llmec-plugin-config": {
            "es-index-name": "llmec_plugin",
            "plugin-status": "enabled",
            "rabbit-mq-queue": "QueuellMEC",
            "rabbit-mq-server-ip": "localhost",
            "rabbit-mq-server-port": 5672,
            "timeout-request": 300
            },
            "log-config": {
            "log-file": "jox.log",
            "log-level": "debug",
            "log_colors": [
                {
                "color": "\\033[91m",
                "debug-level": 0,
                "name": "error"
                },
                {
                "color": "\\033[93m",
                "debug-level": 1,
                "name": "warn"
                },
                {
                "color": "\\033[92m",
                "debug-level": 2,
                "name": "notice"
                },
                {
                "color": "\\033[0m",
                "debug-level": 3,
                "name": "info"
                },
                {
                "color": "\\033[0m",
                "debug-level": 4,
                "name": "debug"
                }
            ]
            },
            "os-config": {
            "ubuntu_14_64": {
                "architecture": "x86_64",
                "distribution": "Ubuntu",
                "type": "Linux",
                "version": "14.04"
            },
            "ubuntu_16_64": {
                "architecture": "x86_64",
                "distribution": "Ubuntu",
                "type": "Linux",
                "version": "16.04"
            },
            "ubuntu_18_64": {
                "architecture": "x86_64",
                "distribution": "Ubuntu",
                "type": "Linux",
                "version": "18.04"
            }
            },
            "rabbit-mq-config": {
            "rabbit-mq-queue": "QueueJox",
            "rabbit-mq-server-ip": "localhost",
            "rabbit-mq-server-port": 5672
            },
            "ssh-config": {
            "_Comment": "ssh connection is needed when adding kvm machines",
            "ssh-key-directory": "/home/borer/.ssh/",
            "ssh-key-name": "id_rsa",
            "ssh-password": "linux",
            "ssh-user": "ubuntu"
            },
            "stats-timer": 100,
            "store-config": {
            "_Comment": "it is needed to store the onboarded packages to deploy slices later",
            "store-directrory": "/tmp/jox_store/"
            },
            "vim-pop": {
            "kvm": [
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "192.168.122.0/24",
                "managed-by": "kvm",
                "pop-name": "default",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                }
            ],
            "lxc": [
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "192.168.1.0/24",
                "lxc-anchor": "pou_remote_home",
                "managed-by": "lxd",
                "pop-name": "default-lxc-bridge",
                "prebuilt-image": {
                    "bionic": "juju/bionic/amd64",
                    "trusty": "juju/trusty/amd64",
                    "xenial": "juju/xenial/amd64"
                },
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "192.168.1.0/24",
                "lxc-anchor": "local",
                "managed-by": "lxd",
                "pop-name": "default-lxc",
                "prebuilt-image": {
                    "bionic": "juju/bionic/amd64",
                    "trusty": "juju/trusty/amd64",
                    "xenial": "juju/xenial/amd64"
                },
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "10.206.29.0/24",
                "lxc-anchor": "local",
                "managed-by": "lxd",
                "pop-name": "default",
                "prebuilt-image": {
                    "bionic": "juju/bionic/amd64",
                    "trusty": "juju/trusty/amd64",
                    "xenial": "juju/xenial/amd64"
                },
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "10.180.125.0/24",
                "lxc-anchor": "local",
                "managed-by": "lxd",
                "pop-name": "default-2",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "10.39.202.0/24",
                "lxc-anchor": "local",
                "managed-by": "lxd",
                "pop-name": "default-3",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "10.124.51.0/24",
                "lxc-anchor": "local",
                "managed-by": "lxd",
                "pop-name": "default-4",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "lxc-anchor is the name of the remote lxc endpoint. To get this name, just type in the terminal (lxc remote list), The default local lxc endpoint is 'default'",
                "_Comment_4": "ssh config",
                "domain": "10.184.36.0/24",
                "lxc-anchor": "local",
                "managed-by": "lxd",
                "pop-name": "default-borer",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                }
            ],
            "phy": [
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "192.168.1.0/24",
                "managed-by": "none",
                "pop-name": "zone-1-phy-home",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "172.16.170.0/24",
                "managed-by": "none",
                "pop-name": "zone-1-phy-router",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "192.168.12.0/24",
                "managed-by": "none",
                "pop-name": "zone-1-phy",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "172.24.0.0/16",
                "managed-by": "none",
                "pop-name": "zone-2-phy",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "172.24.10.0/24",
                "managed-by": "none",
                "pop-name": "zone-3-phy",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                },
                {
                "_Comment_1": "pop-name is a user-defined name for the name of the pop. It will be generated randomly if it is empty",
                "_Comment_2": "domain is the subnet, it is optional if the endpoint and subnet-mask are provided",
                "_Comment_3": "ssh config",
                "domain": "172.24.11.0/24",
                "managed-by": "none",
                "pop-name": "zone-4-phy",
                "scope": "private",
                "ssh-password": "",
                "ssh-private-key": "",
                "ssh-user": "",
                "zone": "1"
                }
            ]
            },
            "zones": {
            "1": {
                "domain-1": "192.168.1.0/24",
                "domain-2": "1000.99.104.54/24",
                "domain-3": "192.168.12.0/24",
                "domain-4": "10.104.8.0/24"
            }
            }
        }
    }
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["request-uri"] = "/jox/"
	enquiry["request-type"] = request.method
	enquiry = json.dumps(enquiry)
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	data = data["data"]
	status_code = 200
	
	data = {
		"jox-config": data,
		"jox-capabilities": jox_capabilities,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/list')
@app.route('/ls')
@app.route('/show/<string:nsi_name>')
def list_of_templates(nsi_name=None):
	"""
	@apiGroup GroupJox
	@apiName GetJoxlist GetJoxlistName

	@api {get}  /list?url=full_path List of packages
	@apiDescription Get the list of all packages in jox store or in a given directory
	@apiParam {path} [full_path] Full directory of the packages

	@apiExample {curl} First-Example-Usage:
	     curl -i http://localhost:5000/list

	@apiDescription Get the list of all packages in the default jox store
	@apiSuccessExample First-Example-Success-Response:
	    HTTP/1.0 200 OK
		{
			"data": [
				"mosaic5g"
			],
			"elapsed-time": "0:00:00.001849"
		}
	@apiDescription Get the list of all packages in a given directory
	@apiExample {curl} Second-Example-Usage:
	     curl -i http://localhost:5000/list?url=/home/ubuntu/package_store/

	@apiSuccessExample Second-Example-Success-Response:
	    HTTP/1.0 200 OK
		{
			"data": [
				"oai-epc"
			],
			"elapsed-time": "0:00:00.001849"
		}
	"""
	
	"""
	@apiGroup GroupJox
	@apiName GetJoxLs

	@api {get}  /ls List of packages [Alias]
	@apiDescription It is an alias to [http://localhost:5000/list](http://localhost:5000/list)
	"""
	
	"""
	@apiGroup GroupJox
	@apiName GetJoxShow

	@api {get}  /show/<string:nsi_name>?url=full_path Show template
	@apiDescription Show the content of specific template, where only the following formats are supported: .yaml, .yml, and .json

	@apiParam {string} nsi_name name of the file(template)
	@apiParam {path} full_path Full path where the templates exists

	@apiDescription example usage to show the tenmplate of one nssi
	@apiExample {curl} Example-Usage:
	     curl  -i http://localhost:5000/show/nssi_1.yaml?url=/tmp/jox_store/mosaic5g/nssi
	
	@apiSuccessExample Example-Success-Response:
	    HTTP/1.0 200 OK
	    {
		  "data": {
		    "description": "template for deploying package <oai-epc> with 2 subslices (nssi_1)",
		    "dsl_definitions": {
		      "host_small": {
		        "disk_size": 5,
		        "mem_size": 1024,
		        "num_cpus": 1
		      },
		      "host_tiny": {
		        "disk_size": 5,
		        "mem_size": 512,
		        "num_cpus": 1
		      },
		      "os_linux_u_14_x64": {
		        "architecture": "x86_64",
		        "distribution": "Ubuntu",
		        "type": "Linux",
		        "version": 14.04
		      },
		      "os_linux_u_16_x64": {
		        "architecture": "x86_64",
		        "distribution": "Ubuntu",
		        "type": "Linux",
		        "version": 16.04
		      },
		      "os_linux_u_18_x64": {
		        "architecture": "x86_64",
		        "distribution": "Ubuntu",
		        "type": "Linux",
		        "version": 18.04
		      }
		    },
		    "imports": [
		      "default_slice_nssi_1"
		    ],
		    "metadata": {
		      "ID": "nssi_1",
		      "author": "Eurecom",
		      "date": "2019-03-04",
		      "vendor": "Eurecom",
		      "version": 1.0
		    },
		    "topology_template": {
		      "node_templates": {
		        "VDU_mysql": {
		          "artifacts": {
		            "sw_image": {
		              "properties": {
		                "supported_virtualisation_environments": {
		                  "entry_schema": "local",
		                  "type": "lxc"
		                }
		              },
		              "type": "tosca.artifacts.nfv.SwImage"
		            }
		          },
		          "capabilities": {
		            "host": {
		              "properties": "small"
		            },
		            "os": {
		              "properties": "ubuntu_16_64"
		            }
		          },
		          "properties": null,
		          "type": "tosca.nodes.nfv.VDU.Compute"
		        },
		        "VDU_oai-hss": {
		          "artifacts": {
		            "sw_image": {
		              "properties": {
		                "supported_virtualisation_environments": {
		                  "entry_schema": "local",
		                  "type": "lxc"
		                }
		              },
		              "type": "tosca.artifacts.nfv.SwImage"
		            }
		          },
		          "capabilities": {
		            "host": {
		              "properties": "small"
		            },
		            "os": {
		              "properties": "ubuntu_16_64"
		            }
		          },
		          "properties": null,
		          "type": "tosca.nodes.nfv.VDU.Compute"
		        },
		        "mysql": {
		          "properties": {
		            "charm": "cs:mysql-58",
		            "endpoint": "localhost",
		            "model": "default-juju-model-1",
		            "vendor": "Eurecom",
		            "version": 1.0
		          },
		          "requirements": {
		            "req1": {
		              "node": "VDU_mysql",
		              "relationship": "tosca.relationships.HostedOn"
		            },
		            "req2": {
		              "node": "oai-hss",
		              "relationship": "tosca.relationships.AttachesTo"
		            }
		          },
		          "type": "tosca.nodes.SoftwareComponent.JOX"
		        },
		        "oai-hss": {
		          "properties": {
		            "charm": "cs:~navid-nikaein/xenial/oai-hss-16",
		            "endpoint": "localhost",
		            "model": "default-juju-model-1",
		            "vendor": "Eurecom",
		            "version": 1.0
		          },
		          "requirements": {
		            "req1": {
		              "node": "VDU_oai-hss",
		              "relationship": "tosca.relationships.HostedOn"
		            },
		            "req2": {
		              "node": "oai-spgw",
		              "relationship": "tosca.relationships.AttachesTo"
		            }
		          },
		          "type": "tosca.nodes.SoftwareComponent.JOX"
		        }
		      }
		    },
		    "tosca_definitions_version": "tosca_simple_yaml_1_0"
		  },
		  "elapsed-time": "0:00:00.025439"
		}
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["nsi_name"] = nsi_name
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	if data["ACK"]:
		message = "list of templates in the directory {}".format(data["full_path"])
	
	else:
		message = data["data"]
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(message))
	logger.debug("response: {}".format(message))
	data = jsonify(data)
	return data, status_code

@app.route('/deploy_slice')
def deploy_slice_slice():
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	# enquiry["parameters"]["template_directory"] = request.args.get('url')
	# enquiry["parameters"]["package_onboard_data"] = request.data
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))

	# enquiry["parameters"]["package_onboard_data"] = list(request.data)

	enquiry = json.dumps(enquiry)

	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE), False)

	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)

	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

@app.route('/resource-discovery')
def resource_discovery():
	"""
	@apiGroup resource_management
	@apiName get_available_resources

	@api {get}  /resource-discovery Discover Available Resources
	@apiDescription Get the list of all the resources and add them to the resource controller, so that the free resources can be used later when deploying a slice

	@apiExample {curl} Example-Usage:
		curl  -i http://localhost:5000/resource-discovery

	@apiSuccessExample Example-Success-Response:
	{
		"data": {
			"kvm": [
				{
				"domain": "192.168.122.0/24",
				"machine_list": [
						{
							"available": true,
							"cpu": 1,
							"disc_size": null,
							"ip": "192.168.122.243",
							"juju-id": "3",
							"memory": 488,
							"name": "machine-4:kvm",
							"os_series": "xenial"
						}
					],
				"pop-name": "default",
				"scope": "private",
				"zone": "1"
				}
			],
			"lxc": [
				{
					"domain": "10.180.125.0/24",
					"machine_list": [],
					"pop-name": "default",
					"scope": "private",
					"zone": "1"
				},
				{
					"domain": "10.199.92.0/24",
					"machine_list": [
							{
								"available": true,
								"cpu": 4,
								"disc_size": null,
								"ip": "10.199.92.178",
								"juju-id": "0",
								"memory": 7852,
								"name": "machine-1:lxc",
								"os_series": "xenial"
							},
							{
								"available": true,
								"cpu": 4,
								"disc_size": null,
								"ip": "10.199.92.77",
								"juju-id": "1",
								"memory": 7852,
								"name": "machine-2:lxc",
								"os_series": "xenial"
							},
							{
								"available": true,
								"cpu": 4,
								"disc_size": null,
								"ip": "10.199.92.248",
								"juju-id": "2",
								"memory": 7852,
								"name": "machine-3:lxc",
								"os_series": "xenial"
							}
					],
					"pop-name": "zone-1-domain-2",
					"scope": "private",
					"zone": "1"
				}
			],
			"phy": [
				{
					"domain": "192.168.1.0/24",
					"machine_list": [],
					"pop-name": "zone-1-phy",
					"scope": "private",
					"zone": "1"
				},
				{
					"domain": "172.24.0.0/16",
					"machine_list": [],
					"pop-name": "zone-2-phy",
					"scope": "private",
					"zone": "1"
				},
				{
					"domain": "172.24.10.0/24",
					"machine_list": [],
					"pop-name": "zone-3-phy",
					"scope": "private",
					"zone": "1"
				},
				{
					"domain": "172.24.11.0/24",
					"machine_list": [],
					"pop-name": "zone-4-phy",
					"scope": "private",
					"zone": "1"
				},
				{
				"domain": "192.168.12.0/24",
				"machine_list": [
					{
						"available": true,
						"cpu": 4,
						"disc_size": null,
						"ip": "192.168.12.220",
						"juju-id": "4",
						"memory": 7920,
						"name": "machine-5:phy",
						"os_series": "bionic"
					}
				],
				"pop-name": "zone-1-domain-2",
				"scope": "private",
				"zone": "1"
				}
			]
		},
		"elapsed-time": "0:00:13.785535"
	}
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	# enquiry["parameters"]["template_directory"] = request.args.get('url')
	# enquiry["parameters"]["package_onboard_data"] = request.data
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))

	# enquiry["parameters"]["package_onboard_data"] = list(request.data)

	enquiry = json.dumps(enquiry)
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)

	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

@app.route('/onboard', methods=['PUT'])
def jox_package_onboard():
	"""
    @apiGroup GroupOnboarding
    @apiName PutOnboard

    @api {put}  /onboard Package onboarding
    @apiDescription Through this endpoint, you can onboard a slice's pakcage, so that you can deploy it later. In order to generate your packages containing the slice and subslices and then package it, you can use the package generater (a tool provided with JoX) that is located in *scripts* in JoX directory.
	
	@apiExample {curl} Example-Usage:
		curl  -i http://localhost:5000/onboard --upload-file mosaic5g.tar.gz
		
	@apiSuccessExample Example-Success-Response:
	
	Example
	{
		"data": "The package was successfuly saved to the directory /tmp/jox_store/",
		"elapsed-time": "0:00:00.011638"
	}
    """
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["parameters"]["package_onboard_data"] = request.data
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	
	enquiry["parameters"]["package_onboard_data"] = list(request.data)
	
	
	enquiry = json.dumps(enquiry)
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/nsi/all', methods=['GET'])
@app.route('/nsi', methods=['GET'])
@app.route('/nsi/<string:nsi_name>', methods=['GET', 'POST', 'DELETE'])
def network_slice(nsi_name=None):
	"""
	@apiGroup GroupSlice
	@apiName GetNsiAll

	@api {get}  /nsi/all List all deployed slices
	@apiDescription get the list of all deployed slices


	@apiExample {curl} Example-Usage:
		curl -i http://localhost:5000/nsi/all

	@apiSuccessExample Example-Success-Response:
		HTTP/1.0 200 OK
		{
		  "data": {
		    "mosaic5g": {
		      "inter_nssi_relation": [
		        {
		          "service_a": {
		            "jcloud": "localhost",
		            "jmodel": "default-juju-model-1",
		            "nssi": "nssi_1",
		            "service": "oai-hss"
		          },
		          "service_b": {
		            "jcloud": "localhost",
		            "jmodel": "default-juju-model-1",
		            "nssi": "nssi_2",
		            "service": "oai-mme"
		          }
		        }
		      ],
		      "slice_name": "mosaic5g",
		      "sub_slices": [
		        "nssi_1",
		        "nssi_2"
		      ]
		    }
		  },
		  "elapsed-time": "0:00:00.004858"
		}
	
	"""
	
	"""
	@apiGroup GroupSlice
	@apiName GetNsi

	
	@api {get}  /nsi List deployed slices [alias]
	@apiDescription It is alias to /nsi/all
	"""
	
	"""
	@apiGroup GroupSlice
	@apiName GetNsiName

	@api {get}  /nsi/<string:nsi_name> Get slice template
	@apiDescription get the context of the already deployed slice nsi_name
	@apiParam {string} nsi_name name of the already deployed slice

	@apiExample {curl} First-Example-Usage:
	     curl http://localhost:5000/nsi/mosaic5g
	@apiSuccessExample First-Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": {
	    "mosaic5g": {
	      "inter_nssi_relation": [
	        {
	          "service_a": {
	            "jcloud": "localhost",
	            "jmodel": "default-juju-model-1",
	            "nssi": "nssi_1",
	            "service": "oai-hss"
	          },
	          "service_b": {
	            "jcloud": "localhost",
	            "jmodel": "default-juju-model-1",
	            "nssi": "nssi_2",
	            "service": "oai-mme"
	          }
	        }
	      ],
	      "slice_name": "mosaic5g",
	      "sub_slices": [
	        "nssi_1",
	        "nssi_2"
	      ]
	    }
	  },
	  "elapsed-time": "0:00:00.005475"
	}
	"""
	
	"""
	@apiGroup GroupSlice
	@apiName PostNsiName

	@api {post}  /nsi/<string:package_name> Deploy slice
	@apiDescription Deploy slice through a package already onboarded
	@apiParam {string} package_name name of the package that is already onboarded

	@apiExample {curl} Example-Usage:
	     curl http://localhost:5000/nsi/mosaic5g -X POST
	@apiSuccessExample Second-Example-Success-Response-GET:
	    HTTP/1.0 200 OK
	{
	  "data": "Creating/updating the slice mosaic5g.yaml",
	  "elapsed-time": "0:01:16.079189"
	}
	"""
	"""
	@apiGroup GroupSlice
	@apiName DeleteNsiName

	@api {delete}  /nsi/<string:nsi_name> Remove slice
	@apiDescription Remove an already deployed slice
	@apiParam {string} nsi_name name of the slice

	@apiExample {curl} Example-Usage:
	     curl -i -X DELETE http://localhost:5000/nsi/mosaic5g
	@apiSuccessExample Example-Success-Response:
	    HTTP/1.0 200 OK
	    {
	     "data":"The slice mosaic5g successfully removed"
	     "elapsed-time":"0:00:54.056207"
	    }
    @apiErrorExample Example-Failure-Response:
	HTTP/1.0 404 NOT FOUND
	{
	  "data": "The slice mosaic5g does not exists",
	  "elapsed-time": "0:00:00.011727"
	}
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	if enquiry["request-type"] == 'post':
		enquiry["parameters"]["package_name"] = nsi_name
	else:
		enquiry["parameters"]["nsi_name"] = nsi_name
	
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	enquiry = json.dumps(enquiry)
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/nssi/all')
@app.route('/nssi')  # alias to the previous one
@app.route('/nssi/<string:nsi_name>')
@app.route('/nssi/<string:nsi_name>/<string:nssi_name>')
@app.route('/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>')
def network_sub_slice(nsi_name=None, nssi_name=None, nssi_key=None):
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiAll

	@api {get}  /nssi/all List all subslices
	@apiDescription get the list of all deployed subslices


	@apiExample {curl} First-Example-Usage:
	     curl -i http://localhost:5000/nssi/all

	@apiSuccessExample Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": [
	    {
	      "mosaic5g": {
	        "nssi_1": {
	          "machines": [
	            {
	              "machine_name_ro": "1:lxc",
	              "machine_name_userdefined": "VDU_mysql",
	              "machine_name_vnfm": "0",
	              "vim_location": "local",
	              "vim_type": "lxc"
	            },
	            {
	              "machine_name_ro": "2:lxc",
	              "machine_name_userdefined": "VDU_oai-hss",
	              "machine_name_vnfm": "1",
	              "vim_location": "local",
	              "vim_type": "lxc"
	            }
	          ],
	          "relations": [
	            {
	              "source": {
	                "juju_cloud": "localhost",
	                "juju_model": "default-juju-model-1",
	                "service": "mysql"
	              },
	              "target": {
	                "juju_cloud": "localhost",
	                "juju_model": "default-juju-model-1",
	                "service": "oai-hss"
	              }
	            }
	          ],
	          "services": {
	            "mysql": {
	              "charm": "cs:mysql-58",
	              "jcloud": "localhost",
	              "jmodel": "default-juju-model-1",
	              "machine_name": "VDU_mysql",
	              "relation": "oai-hss",
	              "service_name": "mysql"
	            },
	            "oai-hss": {
	              "charm": "cs:~navid-nikaein/xenial/oai-hss-16",
	              "jcloud": "localhost",
	              "jmodel": "default-juju-model-1",
	              "machine_name": "VDU_oai-hss",
	              "relation": "oai-spgw",
	              "service_name": "oai-hss"
	            }
	          },
	          "subslice_name": "nssi_1",
	          "subslice_owner": "",
	          "subslice_template_date": "",
	          "subslice_template_version": 1.0
	        },
	        "nssi_2": {
	          "machines": [
	            {
	              "machine_name_ro": "3:lxc",
	              "machine_name_userdefined": "VDU_oai-mme",
	              "machine_name_vnfm": "2",
	              "vim_location": "local",
	              "vim_type": "lxc"
	            },
	            {
	              "machine_name_ro": "4:lxc",
	              "machine_name_userdefined": "VDU_oai-spgw",
	              "machine_name_vnfm": "3",
	              "vim_location": "local",
	              "vim_type": "lxc"
	            }
	          ],
	          "relations": [
	            {
	              "source": {
	                "juju_cloud": "localhost",
	                "juju_model": "default-juju-model-1",
	                "service": "oai-spgw"
	              },
	              "target": {
	                "juju_cloud": "localhost",
	                "juju_model": "default-juju-model-1",
	                "service": "oai-mme"
	              }
	            }
	          ],
	          "services": {
	            "oai-mme": {
	              "charm": "cs:~navid-nikaein/xenial/oai-mme-18",
	              "jcloud": "localhost",
	              "jmodel": "default-juju-model-1",
	              "machine_name": "VDU_oai-mme",
	              "relation": null,
	              "service_name": "oai-mme"
	            },
	            "oai-spgw": {
	              "charm": "cs:~navid-nikaein/xenial/oai-spgw-15",
	              "jcloud": "localhost",
	              "jmodel": "default-juju-model-1",
	              "machine_name": "VDU_oai-spgw",
	              "relation": "oai-mme",
	              "service_name": "oai-spgw"
	            }
	          },
	          "subslice_name": "nssi_2",
	          "subslice_owner": "",
	          "subslice_template_date": "",
	          "subslice_template_version": 1.0
	        }
	      }
	    }
	  ],
	  "elapsed-time": "0:00:00.005259"
	}
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssi

	@apiDescription It is alias to [http://localhost:5000/nssi/all](http://localhost:5000/nssi/all)
	@api {get}  /nssi  List all deployed NSSI [Alias]
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiName

	@apiDescription Get the context of all the subslices attached to certain slice
	@api {get}  /nssi/<string:nsi_name> Context of subslices
	@apiParam {string} nsi_name name of slice
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiNameNssiName

	@apiDescription Get the context of certain subslice attached to specified slice
	@api {get}  /nssi/<string:nsi_name>/<string:nssi_name> Context of specific subslice
	@apiParam {string} nsi_name Slice name
	@apiParam {string} nssi_name Subslice name
	
	@apiExample {curl} First-Example-Usage:
	     curl -i http://localhost:5000/nssi/mosaic5g/nssi_2

	@apiSuccessExample Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": {
	    "machines": [
	      {
	        "machine_name_ro": "3:lxc",
	        "machine_name_userdefined": "VDU_oai-mme",
	        "machine_name_vnfm": "2",
	        "vim_location": "local",
	        "vim_type": "lxc"
	      },
	      {
	        "machine_name_ro": "4:lxc",
	        "machine_name_userdefined": "VDU_oai-spgw",
	        "machine_name_vnfm": "3",
	        "vim_location": "local",
	        "vim_type": "lxc"
	      }
	    ],
	    "relations": [
	      {
	        "source": {
	          "juju_cloud": "localhost",
	          "juju_model": "default-juju-model-1",
	          "service": "oai-spgw"
	        },
	        "target": {
	          "juju_cloud": "localhost",
	          "juju_model": "default-juju-model-1",
	          "service": "oai-mme"
	        }
	      }
	    ],
	    "services": {
	      "oai-mme": {
	        "charm": "cs:~navid-nikaein/xenial/oai-mme-18",
	        "jcloud": "localhost",
	        "jmodel": "default-juju-model-1",
	        "machine_name": "VDU_oai-mme",
	        "relation": null,
	        "service_name": "oai-mme"
	      },
	      "oai-spgw": {
	        "charm": "cs:~navid-nikaein/xenial/oai-spgw-15",
	        "jcloud": "localhost",
	        "jmodel": "default-juju-model-1",
	        "machine_name": "VDU_oai-spgw",
	        "relation": "oai-mme",
	        "service_name": "oai-spgw"
	      }
	    },
	    "subslice_name": "nssi_2",
	    "subslice_owner": "",
	    "subslice_template_date": "",
	    "subslice_template_version": 1.0
	  },
	  "elapsed-time": "0:00:00.008035"
	}
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiNameNssiNameNssiKey

	@apiDescription get the context of certain entity fo certain subslcie attached to specified slice
	@api {get}  /nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key> Context of specific entity
	@apiParam {string} nsi_name name of slice
	@apiParam {string} nssi_name name of subslice
	@apiParam {string="services","machines","relations"} nssi_key  name of certain entity
	
	@apiExample {curl} First-Example-Usage:
	     curl -i http://localhost:5000/nssi/mosaic5g/nssi_2/subslice_services
	@apiSuccessExample First-Example-Failure-Response:
	HTTP/1.0 404 NOT FOUND
	{
		"data": "The key subslice_services does not exist in the subslice nssi_2 attached to the slice mosaic5g",
		"elapsed-time": "0:00:00.002774"
	}
	
	@apiExample {curl} Second-Example-Usage:
	     curl -i http://localhost:5000/nssi/mosaic5g/nssi_2/subslice_services
	@apiSuccessExample Second-Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": {
	    "oai-mme": {
	      "charm": "cs:~navid-nikaein/xenial/oai-mme-18",
	      "jcloud": "localhost",
	      "jmodel": "default-juju-model-1",
	      "machine_name": "VDU_oai-mme",
	      "relation": null,
	      "service_name": "oai-mme"
	    },
	    "oai-spgw": {
	      "charm": "cs:~navid-nikaein/xenial/oai-spgw-15",
	      "jcloud": "localhost",
	      "jmodel": "default-juju-model-1",
	      "machine_name": "VDU_oai-spgw",
	      "relation": "oai-mme",
	      "service_name": "oai-spgw"
	    }
	  },
	  "elapsed-time": "0:00:00.003153"
	}
	
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["nsi_name"] = nsi_name
	enquiry["parameters"]["nssi_name"] = nssi_name
	enquiry["parameters"]["nssi_key"] = nssi_key
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/es', methods=['GET', 'DELETE'])
@app.route('/es/<string:es_index_page>', methods=['GET', 'POST', 'DELETE'])
@app.route('/es/<string:es_index_page>/<string:es_key>', methods=['GET', 'POST', 'DELETE'])
def monitor_es(es_index_page=None, es_key=None):
	"""
	@apiGroup GroupElasticsearch
	@apiName GetEs
	@api {get}  /es List index-pages
	@apiDescription Get the list of all index-pages from elasticsearch
	@apiExample {curl} Example-Usage:
		 curl -i http://localhost:5000/es

	@apiDescription Get the list of all index-pages in elasticsearch database
	@apiSuccessExample Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": [
	    "jox_config",
	    "mosaic5g",
	    "nssi_1",
	    "nssi_2",
	    "slice_keys_mosaic5g",
	    "slice_keys_tmp_mosaic5g",
	    "subslice_monitor_nssi_1",
	    "subslice_monitor_nssi_2"
	  ],
	  "elapsed-time": "0:00:00.018397"
	}

   """
	"""
	@apiGroup GroupElasticsearch
	@apiName DeleteEs
	@api {delete}  /es Delete index-pages
	@apiDescription Delete all index-pages from elasticsearch database
	@apiExample {curl} Example-Usage-DELETE:
		 curl -i http://localhost:5000/es -X DELETE
	@apiSuccessExample Example-Success-Response:
		HTTP/1.0 200 OK
			{
				Example here
			}
	"""
	"""
	@apiGroup GroupElasticsearch
	@apiName GetEsIndexPgae
	@api {get}  /es/<string:es_index_page> Get index-page
	@apiDescription Get certain index-page from elasticsearch

	@apiParam {string} es_index_page name of the index-page

	@apiExample {curl} Example-Usage:
		 curl -i http://localhost:5000/es/jox_config

	@apiSuccessExample Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": {
	    "authors-list": [
	      {
	        "email": "contact@mosaic-5g.io",
	        "name": "Eurecom"
	      }
	    ],
	    "clouds-list": [
	      {
	        "cloud-name": "localhost",
	        "description": "name of you juju controller"
	      }
	    ],
	    "date": "01-03-2019",
	    "description": "Jox configuration file",
	    "elasticsearch-config": {
	      "elasticsearch-host": "localhost",
	      "elasticsearch-log-level": "error",
	      "elasticsearch-port": "9200",
	      "elasticsearch-retry-on-conflict": 3
	    },
	    "encoding-type": "utf-8",
	    "flask-config": {
	      "flask-debug": "FALSE",
	      "flask-port": 5000,
	      "flask-server": "localhost"
	    },
	    "http": {
	      "200": {
	        "no-content": 204,
	        "ok": 200
	      },
	      "400": {
	        "bad-request": 400,
	        "not-found": 404
	      }
	    },
	    "jox version": 1,
	    "juju-config": {
	      "_Comment": "connect-model-available: define the parameters to access to a newly created model is available",
	      "_Comment_2": "connect-model-accessible: define parameters to access to already exist juju model",
	      "connect-model-accessible-interval": 3,
	      "connect-model-accessible-max-retry": 50,
	      "connect-model-available-interval": 10,
	      "connect-model-available-max-retry": 10
	    },
	    "juju_version": 2.4,
	    "log-config": {
	      "log-file": "jox.log",
	      "log-level": "debug",
	      "log_colors": [
	        {
	          "color": "\\033[91m",
	          "debug-level": 0,
	          "name": "error"
	        },
	        {
	          "color": "\\033[93m",
	          "debug-level": 1,
	          "name": "warn"
	        },
	        {
	          "color": "\\033[92m",
	          "debug-level": 2,
	          "name": "notice"
	        },
	        {
	          "color": "\\033[0m",
	          "debug-level": 3,
	          "name": "info"
	        },
	        {
	          "color": "\\033[0m",
	          "debug-level": 4,
	          "name": "debug"
	        }
	      ]
	    },
	    "rabbit-mq-config": {
	      "rabbit-mq-queue": "QueueJox",
	      "rabbit-mq-server-ip": "localhost",
	      "rabbit-mq-server-port": 5672
	    },
	    "ssh-config": {
	      "_Comment": "ssh connection is needed when adding kvm machines",
	      "ssh-key-directory": "/home/arouk/.ssh/",
	      "ssh-key-name": "id_juju",
	      "ssh-password": "linux",
	      "ssh-user": "ubuntu"
	    },
	    "stats-timer": 100,
	    "store-config": {
	      "_Comment": "it is needed to store the onboarded packages to deploy slices later",
	      "store-directrory": "/tmp/jox_store/"
	    },
	    "vim-pop": {
	      "kvm": [
	        "local"
	      ],
	      "lxc": [
	        "local"
	      ]
	    }
	  },
	  "elapsed-time": "0:00:00.007593"
	}
	"""
	
	"""
	@apiGroup GroupElasticsearch
	@apiName DeleteEsIndexPgae
	
	@api {delete}  /es/<string:es_index_page> Delete index-page
	@apiDescription Delete index page from elasticsearch
	
	@apiExample {curl} Example-Usage:
		 curl -i http://localhost:5000/es/jox-config -X DELETE
		 
	@apiSuccessExample Example-Success-Response-DELETE:
		HTTP/1.0 200 OK

			{
			"data": "The index jox-config is successfully removed from elasticsearch",
			"elapsed-time": "0:00:00.064590"
			}
	"""
	"""
	@apiGroup GroupElasticsearch
	@apiName GetEsIndexPgaeKeyVal

	@api {get}  /es/<string:es_index_page>/<string:es_key> Get specific key of index-page
	@apiDescription get certain key of certain index-page from elasticsearch

	@apiParam {string} es_index_page name of index-page
	@apiParam {string} es_key key to get from the indexpage es_index_page

	@apiExample {curl} Example-Usage:
		 curl -i http://localhost:5000/es/jox_config/rabbit-mq-config

	@apiSuccessExample Example-Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": {
	    "rabbit-mq-queue": "QueueJox",
	    "rabbit-mq-server-ip": "localhost",
	    "rabbit-mq-server-port": 5672
	  },
	  "elapsed-time": "0:00:00.007253"
	}
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["es_index_page"] = es_index_page
	enquiry["parameters"]["es_key"] = es_key
	
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/monitor/nsi')
@app.route('/monitor/nsi/<string:nsi_name>')
@app.route('/monitor/nsi/<string:nsi_name>/<string:nssi_name>')
@app.route('/monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>')
def monitor_nssi(nsi_name=None, nssi_name=None, nssi_key=None):
	"""
	@apiGroup GroupMonitoring
	@apiName GetNsiMonitorAll

	@apiDescription Get monitoring information on specific slice
	@api {get}  /monitor/nsi/<string:nsi_name> Information on specific slice
	@apiParam {String} nsi_name slice name
	@apiExample {curl} Example usage:
	    curl http://localhost:5000/monitor/nsi/mosaic5g

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_1": {
	            "date": "2019-03-06T18:11:24.679488",
	            "machine_status": [
	              {
	                "mysql": [
	                  {
	                    "address_ipv4_public": "10.70.21.123",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "down": "0",
	                    "juju_mid": "0",
	                    "launch_time": "0:01:45.861699",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "type": "lxc"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "address_ipv4_public": "10.70.21.55",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "down": "0",
	                    "juju_mid": "1",
	                    "launch_time": "0:02:05.814990",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "type": "lxc"
	                  }
	                ]
	              }
	            ],
	            "relation_status": [
	              {
	                "mysql": [
	                  {
	                    "date": "2019-03-06T18:11:24.679488",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement": "oai-hss",
	                    "requirement_wait": "0"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "date": "2019-03-06T18:11:24.679488",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement": "oai-spgw",
	                    "requirement_wait": "0:00:23.239041"
	                  }
	                ]
	              }
	            ],
	            "service_status": [
	              {
	                "mysql": [
	                  {
	                    "active_since": "2019-03-06T18:16:02.227240",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "error": "0",
	                    "maintenance": "0:02:48.005425",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement_wait": "0",
	                    "waiting": "0:01:50.970303"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "active_since": "2019-03-06T18:15:44.785870",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "error": "0",
	                    "maintenance": "0:02:10.633415",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement_wait": "0:00:23.239041",
	                    "waiting": "0:02:09.916849"
	                  }
	                ]
	              }
	            ]
	          },
	          "subslice_monitor_nssi_2": {
	            "date": "2019-03-06T18:12:38.267184",
	            "machine_status": [
	              {
	                "oai-mme": [
	                  {
	                    "address_ipv4_public": "10.70.21.207",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "down": "0",
	                    "juju_mid": "2",
	                    "launch_time": "0:00:50.817423",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "type": "lxc"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "address_ipv4_public": "10.70.21.244",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "down": "0",
	                    "juju_mid": "3",
	                    "launch_time": "0:00:52.790111",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "type": "lxc"
	                  }
	                ]
	              }
	            ],
	            "relation_status": [
	              {
	                "oai-mme": [
	                  {
	                    "date": "2019-03-06T18:12:38.267184",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement": null,
	                    "requirement_wait": "0"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "date": "2019-03-06T18:12:38.267184",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement": "oai-mme",
	                    "requirement_wait": "0"
	                  }
	                ]
	              }
	            ],
	            "service_status": [
	              {
	                "oai-mme": [
	                  {
	                    "active_since": "2019-03-06T18:16:11.957220",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "0",
	                    "maintenance": "0",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:55.036843"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "active_since": "2019-03-06T18:17:11.005552",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "in_error_state",
	                    "maintenance": "0:03:38.510813",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:56.729490"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.544330"
	    }
	    
	@apiErrorExample Error-Response:
	    HTTP/1.0 404 Not Found
	    {
	      "data": "The slice oai-ran does not exists",
	      "elapsed-time": "0:00:00.002289"
	    }
	"""
	
	"""
	@apiGroup GroupMonitoring
	@apiName GetNssiMonitorAll

	@apiDescription Get monitoring information on specific subslice attached to certain slice
	@api {get}  /monitor/nsi/<string:nsi_name>/<string:nssi_name> Information on specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslice name

	@apiExample {curl} Example usage:
	      curl http://localhost:5000/monitor/nsi/oai-epc/nssi_2

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	     "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_2": {
	            "date": "2019-03-06T18:12:38.267184",
	            "machine_status": [
	              {
	                "oai-mme": [
	                  {
	                    "address_ipv4_public": "10.70.21.207",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "down": "0",
	                    "juju_mid": "2",
	                    "launch_time": "0:00:50.817423",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "type": "lxc"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "address_ipv4_public": "10.70.21.244",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "down": "0",
	                    "juju_mid": "3",
	                    "launch_time": "0:00:52.790111",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "type": "lxc"
	                  }
	                ]
	              }
	            ],
	            "relation_status": [
	              {
	                "oai-mme": [
	                  {
	                    "date": "2019-03-06T18:12:38.267184",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement": null,
	                    "requirement_wait": "0"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "date": "2019-03-06T18:12:38.267184",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement": "oai-mme",
	                    "requirement_wait": "0"
	                  }
	                ]
	              }
	            ],
	            "service_status": [
	              {
	                "oai-mme": [
	                  {
	                    "active_since": "2019-03-06T18:16:11.957220",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "0",
	                    "maintenance": "0",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:55.036843"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "active_since": "2019-03-06T18:17:11.005552",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "in_error_state",
	                    "maintenance": "0:03:38.510813",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:56.729490"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.005380"
	    }

	@apiErrorExample Error-Response:
	HTTP/1.0 404 Not Found
	{
		"data": "The subslice nssi_2 does not exist or it is not attached to the slice nssi_3",
		"elapsed-time": "0:00:00.008988"
	}
	"""
	
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["nsi_name"] = nsi_name
	enquiry["parameters"]["nssi_name"] = nssi_name
	enquiry["parameters"]["nssi_key"] = nssi_key
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/monitor/service/<string:nsi_name>')
@app.route('/monitor/service/<string:nsi_name>/<string:nssi_name>')
@app.route('/monitor/service/<string:nsi_name>/<string:nssi_name>/<string:service_name>')
def monitor_srvice(nsi_name=None, nssi_name=None, service_name=None, service_key=None):
	"""
	@apiGroup GroupMonitoring
	@apiName GetNsiMonitorServices

	@api {get}  /monitor/service/<string:nsi_name> Information all services in specific slice

	@apiParam {String} nsi_name slice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_1": {
	            "service_status": [
	              {
	                "mysql": [
	                  {
	                    "active_since": "2019-03-06T18:16:02.227240",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "error": "0",
	                    "maintenance": "0:02:48.005425",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement_wait": "0",
	                    "waiting": "0:01:50.970303"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "active_since": "2019-03-06T18:15:44.785870",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "error": "0",
	                    "maintenance": "0:02:10.633415",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement_wait": "0:00:23.239041",
	                    "waiting": "0:02:09.916849"
	                  }
	                ]
	              }
	            ]
	          },
	          "subslice_monitor_nssi_2": {
	            "service_status": [
	              {
	                "oai-mme": [
	                  {
	                    "active_since": "2019-03-06T18:16:11.957220",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "0",
	                    "maintenance": "0",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:55.036843"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "active_since": "2019-03-06T18:17:11.005552",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "in_error_state",
	                    "maintenance": "0:03:38.510813",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:56.729490"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	    "elapsed-time": "0:00:00.014984"
	    }

	@apiErrorExample Error-Response:
	    HTTP/1.0 404 Not Found
		{
			"data": "The slice oai-ran does not exists",
			"elapsed-time": "0:00:00.008638"
		}
	"""
	
	"""
	@apiGroup GroupMonitoring
	@apiName GetNssiMonitorServices

	@api {get}  /monitor/nsi/service/<string:nsi_name>/<string:nssi_name> Information all services in specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc/nssi_2

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_2": {
	            "service_status": [
	              {
	                "oai-mme": [
	                  {
	                    "active_since": "2019-03-06T18:16:11.957220",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "0",
	                    "maintenance": "0",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:55.036843"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "active_since": "2019-03-06T18:17:11.005552",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "error": "in_error_state",
	                    "maintenance": "0:03:38.510813",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement_wait": "0",
	                    "waiting": "0:00:56.729490"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.006463"
	    }

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc/nssi_3
	@apiErrorExample Error-Response:
	    HTTP/1.0 404 Not Found
		{
			"data": "The subslice nssi_3 attached to slice oai-epc does not exist",
			"elapsed-time": "0:00:00.002461"
		}
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["nsi_name"] = nsi_name
	enquiry["parameters"]["nssi_name"] = nssi_name
	enquiry["parameters"]["service_name"] = service_name
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


#
@app.route('/monitor/machine/<string:nsi_name>')
@app.route('/monitor/machine/<string:nsi_name>/<string:nssi_name>')
@app.route('/monitor/machine/<string:nsi_name>/<string:nssi_name>/<string:machine_name>')
def monitor_machine(nsi_name=None, nssi_name=None, machine_name=None, machine_key=None):
	"""
	@apiGroup GroupMonitoring
	@apiName GetNsiMonitorMachines

	@api {get}  /monitor/machine/<string:nsi_name> Information all machines of specific slice

	@apiParam {String} nsi_name slice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/machine/oai-epc

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_1": {
	            "machine_status": [
	              {
	                "mysql": [
	                  {
	                    "address_ipv4_public": "10.70.21.123",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "down": "0",
	                    "juju_mid": "0",
	                    "launch_time": "0:01:45.861699",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "type": "lxc"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "address_ipv4_public": "10.70.21.55",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "down": "0",
	                    "juju_mid": "1",
	                    "launch_time": "0:02:05.814990",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "type": "lxc"
	                  }
	                ]
	              }
	            ]
	          },
	          "subslice_monitor_nssi_2": {
	            "machine_status": [
	              {
	                "oai-mme": [
	                  {
	                    "address_ipv4_public": "10.70.21.207",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "down": "0",
	                    "juju_mid": "2",
	                    "launch_time": "0:00:50.817423",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "type": "lxc"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "address_ipv4_public": "10.70.21.244",
	                    "date": "2019-03-06T18:12:38.267184",
	                    "down": "0",
	                    "juju_mid": "3",
	                    "launch_time": "0:00:52.790111",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "type": "lxc"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.535296"
	    }
	"""
	
	"""
	@apiGroup GroupMonitoring
	@apiName GetNssiMonitorMachines

	@api {get}  /monitor/nsi/machine/<string:nsi_name>/<string:nssi_name>  Information machines of specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslcie name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/machine/oai-epc/nssi_1

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	      "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_1": {
	            "machine_status": [
	              {
	                "mysql": [
	                  {
	                    "address_ipv4_public": "10.70.21.123",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "down": "0",
	                    "juju_mid": "0",
	                    "launch_time": "0:01:45.861699",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "type": "lxc"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "address_ipv4_public": "10.70.21.55",
	                    "date": "2019-03-06T18:11:24.679488",
	                    "down": "0",
	                    "juju_mid": "1",
	                    "launch_time": "0:02:05.814990",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "type": "lxc"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.005716"
	    }
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["nsi_name"] = nsi_name
	enquiry["parameters"]["nssi_name"] = nssi_name
	enquiry["parameters"]["machine_name"] = machine_name
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


# monitor_relation


@app.route('/monitor/relation/<string:nsi_name>')
@app.route('/monitor/relation/<string:nsi_name>/<string:nssi_name_source>')
# @app.route('/monitor/relation/<string:nsi_name>/<string:nssi_name_source>/<string:service_name_source>'
#            '/<string:nssi_name_target>/<string:service_name_target>/<string:relation_key>')
def monitor_relation(nsi_name=None, nssi_name_source=None, service_name_source=None,
                     nssi_name_target=None, service_name_target=None, relation_key=None):
	"""
	@apiGroup GroupMonitoring
	@apiName GetNsiMonitorRequirements

	@api {get}  /monitor/relation/<string:nsi_name> Information relations of specific slice

	@apiParam {String} nsi_name slice name

	@apiExample {curl} Example usage:
	      curl http://localhost:5000/monitor/relation/oai-epc
	      
	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_1": {
	            "relation_status": [
	              {
	                "mysql": [
	                  {
	                    "date": "2019-03-06T18:11:24.679488",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement": "oai-hss",
	                    "requirement_wait": "0"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "date": "2019-03-06T18:11:24.679488",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement": "oai-spgw",
	                    "requirement_wait": "0:00:23.239041"
	                  }
	                ]
	              }
	            ]
	          },
	          "subslice_monitor_nssi_2": {
	            "relation_status": [
	              {
	                "oai-mme": [
	                  {
	                    "date": "2019-03-06T18:12:38.267184",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement": null,
	                    "requirement_wait": "0"
	                  }
	                ]
	              },
	              {
	                "oai-spgw": [
	                  {
	                    "date": "2019-03-06T18:12:38.267184",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_2",
	                    "requirement": "oai-mme",
	                    "requirement_wait": "0"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.006634"
	    }
	"""
	
	"""
	@apiGroup GroupMonitoring
	@apiName GetNssiMonitorRequirements

	@api {get}  /monitor/nsi/relation/<string:nsi_name>/<string:nssi_name>  Information relations of specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/relation/oai-epc/nssi_1

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "subslice_monitor_nssi_1": {
	            "relation_status": [
	              {
	                "mysql": [
	                  {
	                    "date": "2019-03-06T18:11:24.679488",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement": "oai-hss",
	                    "requirement_wait": "0"
	                  }
	                ]
	              },
	              {
	                "oai-hss": [
	                  {
	                    "date": "2019-03-06T18:11:24.679488",
	                    "nsi_id": "oai-epc",
	                    "nssi_id": "nssi_1",
	                    "requirement": "oai-spgw",
	                    "requirement_wait": "0:00:23.239041"
	                  }
	                ]
	              }
	            ]
	          }
	        }
	      },
	      "elapsed-time": "0:00:00.018176"
	    }
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["nsi_name"] = nsi_name
	enquiry["parameters"]["nssi_name_source"] = nssi_name_source
	# enquiry["parameters"]["service_name_source"] = service_name_source
	# enquiry["parameters"]["nssi_name_target"] = nssi_name_target
	# enquiry["parameters"]["service_name_target"] = service_name_target
	# enquiry["parameters"]["relation_key"] = relation_key
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/monitor/juju')
@app.route('/monitor/juju/<string:juju_key_val>')
@app.route('/monitor/juju/<string:juju_key_val>/<string:cloud_name>/<string:model_name>')
def monitor_juju(juju_key_val=None, cloud_name=None, model_name=None):
	"""
	@apiGroup GroupMonitoring
	@apiName GetJujuMonitorJujuEntityCurrentModel
	@apiDescription Get monitoring information directly from the current juju model for specific entity

	@api {get}  /monitor/juju/<string:juju_entity> Specific information of juju current model
	
	@apiParam {String="all", "services", "machines", "relations"} juju_entity Specify which information that you want to get from the current juju model

	@apiExample {curl} Example usage:
	        curl http://localhost:5000/monitor/juju/applications

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	      "data": {
	        "mysql": {
	          "can-upgrade-to": "",
	          "charm": "cs:mysql-58",
	          "charm-verion": "",
	          "endpoint-bindings": {
	            "ceph": "",
	            "cluster": "",
	            "data": "",
	            "db": "",
	            "db-admin": "",
	            "ha": "",
	            "local-monitors": "",
	            "master": "",
	            "monitors": "",
	            "munin": "",
	            "nrpe-external-master": "",
	            "shared-db": "",
	            "slave": ""
	          },
	          "exposed": false,
	          "life": "",
	          "meter-statuses": null,
	          "public-address": "",
	          "relations": {
	            "cluster": [
	              "mysql"
	            ],
	            "db": [
	              "oai-hss"
	            ]
	          },
	          "series": "xenial",
	          "status": {
	            "data": {},
	            "info": "Ready",
	            "kind": "",
	            "life": "",
	            "since": "2019-03-06T17:15:57.932331667Z",
	            "status": "active",
	            "version": ""
	          },
	          "subordinate-to": [],
	          "units": {
	            "mysql/0": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:16:04.503916259Z",
	                "status": "idle",
	                "version": "2.5.1"
	              },
	              "charm": "",
	              "leader": true,
	              "machine": "0",
	              "opened-ports": [
	                "3306/tcp"
	              ],
	              "public-address": "10.70.21.123",
	              "subordinates": null,
	              "workload-status": {
	                "data": {},
	                "info": "Ready",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:15:57.932331667Z",
	                "status": "active",
	                "version": ""
	              },
	              "workload-version": "5.7.25"
	            }
	          },
	          "workload-version": "5.7.25"
	        },
	        "oai-hss": {
	          "can-upgrade-to": "",
	          "charm": "cs:~navid-nikaein/xenial/oai-hss-16",
	          "charm-verion": "",
	          "endpoint-bindings": {
	            "db": "",
	            "hss": ""
	          },
	          "exposed": false,
	          "life": "",
	          "meter-statuses": null,
	          "public-address": "",
	          "relations": {
	            "db": [
	              "mysql"
	            ],
	            "hss": [
	              "oai-mme"
	            ]
	          },
	          "series": "xenial",
	          "status": {
	            "data": {},
	            "info": "Running",
	            "kind": "",
	            "life": "",
	            "since": "2019-03-06T17:16:07.582399661Z",
	            "status": "active",
	            "version": ""
	          },
	          "subordinate-to": [],
	          "units": {
	            "oai-hss/0": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:16:08.18189912Z",
	                "status": "idle",
	                "version": "2.5.1"
	              },
	              "charm": "",
	              "leader": true,
	              "machine": "1",
	              "opened-ports": null,
	              "public-address": "10.70.21.55",
	              "subordinates": null,
	              "workload-status": {
	                "data": {},
	                "info": "Running",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:16:07.582399661Z",
	                "status": "active",
	                "version": ""
	              },
	              "workload-version": ""
	            }
	          },
	          "workload-version": ""
	        },
	        "oai-mme": {
	          "can-upgrade-to": "",
	          "charm": "cs:~navid-nikaein/xenial/oai-mme-18",
	          "charm-verion": "",
	          "endpoint-bindings": {
	            "hss": "",
	            "mme": "",
	            "spgw": ""
	          },
	          "exposed": false,
	          "life": "",
	          "meter-statuses": null,
	          "public-address": "",
	          "relations": {
	            "hss": [
	              "oai-hss"
	            ],
	            "spgw": [
	              "oai-spgw"
	            ]
	          },
	          "series": "xenial",
	          "status": {
	            "data": {},
	            "info": "Running",
	            "kind": "",
	            "life": "",
	            "since": "2019-03-06T17:16:11.120606764Z",
	            "status": "active",
	            "version": ""
	          },
	          "subordinate-to": [],
	          "units": {
	            "oai-mme/0": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:16:11.24301358Z",
	                "status": "idle",
	                "version": "2.5.1"
	              },
	              "charm": "",
	              "leader": true,
	              "machine": "2",
	              "opened-ports": [
	                "36412/tcp",
	                "2123/udp",
	                "2152/udp"
	              ],
	              "public-address": "10.70.21.207",
	              "subordinates": null,
	              "workload-status": {
	                "data": {},
	                "info": "Running",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:16:11.120606764Z",
	                "status": "active",
	                "version": ""
	              },
	              "workload-version": ""
	            }
	          },
	          "workload-version": ""
	        },
	        "oai-spgw": {
	          "can-upgrade-to": "",
	          "charm": "cs:~navid-nikaein/xenial/oai-spgw-15",
	          "charm-verion": "",
	          "endpoint-bindings": {
	            "spgw": ""
	          },
	          "exposed": false,
	          "life": "",
	          "meter-statuses": null,
	          "public-address": "",
	          "relations": {
	            "spgw": [
	              "oai-mme"
	            ]
	          },
	          "series": "xenial",
	          "status": {
	            "data": {
	              "hook": "update-status"
	            },
	            "info": "hook failed: \"update-status\"",
	            "kind": "",
	            "life": "",
	            "since": "2019-03-06T17:19:19.208573253Z",
	            "status": "error",
	            "version": ""
	          },
	          "subordinate-to": [],
	          "units": {
	            "oai-spgw/0": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:19:19.208573253Z",
	                "status": "idle",
	                "version": "2.5.1"
	              },
	              "charm": "",
	              "leader": true,
	              "machine": "3",
	              "opened-ports": [
	                "2123/udp",
	                "2152/udp"
	              ],
	              "public-address": "10.70.21.244",
	              "subordinates": null,
	              "workload-status": {
	                "data": {},
	                "info": "hook failed: \"update-status\"",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:19:19.208573253Z",
	                "status": "error",
	                "version": ""
	              },
	              "workload-version": ""
	            }
	          },
	          "workload-version": ""
	        }
	      },
	      "elapsed-time": "0:00:00.147294"
	    }
	"""
	"""
	@apiGroup GroupMonitoring
	@apiName GetJujuMonitorJujuEntityCertainModel
	@apiDescription Get monitoring information directly from certain juju model and for specific entity
	
	
	@api {get} /monitor/juju/<string:juju_key_val>/<string:cloud_name>/<string:model_name>
	 Specific information from certain juju model
	
	@apiParam {String="all", "services", "machines", "relations"} juju_entity Specify which information that you want to get from the current juju model
	@apiParam {String} cloud_name juju controller name
	@apiParam {String} model_name juju model name
	

	@apiExample {curl} Example usage:
	        curl http://localhost:5000/monitor/localhost/Default

	@apiErrorExample Success-Response:
	HTTP/1.0 200 OK
	{
	  "data": {
	    "machines": [
	        {
	        }
        ],
        "relations": [
            {
            }
        ],
        "services": [
            {
            }
        ]
      },
	  "elapsed-time": "0:00:00.083747"
	}
	
	@apiExample {curl} Example usage:
	        curl http://localhost:5000/monitor/localhost/model3

	@apiErrorExample Error-Response:
	    HTTP/1.0 200 OK
	    {
			"data": "Error while trying to connect to the juju model localhost:admin/localhost:admin/model3",
			"elapsed-time": "0:00:00.034122"
		}
	"""
	if juju_key_val is None:
		juju_key_val = 'all'
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["juju_key_val"] = juju_key_val
	enquiry["parameters"]["cloud_name"] = cloud_name
	enquiry["parameters"]["model_name"] = model_name
	
	
	
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)
	
	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code


@app.route('/log')
@app.route('/log/<string:log_source>')
@app.route('/log/<string:log_source>/<string:log_type>')
def logging(log_source=None, log_type=None):
	"""
	@apiGroup GroupMonitoring
	@apiName GetJoxlogs

	@api {get}  /log/<string:log_source>/<string:log_type> Logs
	@apiDescription Get the log from JoX or juju with specific log level
	@apiParam {String="jox", "juju"}  log_source=jox The source from which the log will be returned
	@apiParam {String="all", "error", "debug", "info", "warning"} log_type=all the required log level from the target source.
	@apiExample {curl} First-Example-Usage:
		     curl -i http://localhost:5000/log

	@apiSuccessExample First-Example-Success-Response:
	HTTP/1.0 200 OK
	{
	"data": [
			"2019-04-04T22:53:10 INFO jox jox.py:221 Configure elastcisearch if enabled",
			"2019-04-04T22:53:21 ERROR jox.es es.py:63 Elasticsearch: connection Failed",
			"2019-04-04T22:53:21 DEBUG jox jox.py:396 The following cloud is successfully  added",
			"2019-04-04T22:53:21 DEBUG jox.RO.rsourceController resource_controller.py:547 jcloud psoque-home was added to jox",
			"2019-04-04T22:53:21 DEBUG jox jox.py:396 The following cloud is successfully  added",
			"2019-04-04T22:53:21 DEBUG jox.RO.rsourceController resource_controller.py:547 jcloud localhost was added to jox",
			"2019-04-04T22:53:21 DEBUG jox jox.py:396 The following cloud is successfully  added",
			"2019-04-04T22:53:21 INFO jox jox.py:285 All clouds were successfully added!",
			"2019-04-04T22:53:21 INFO jox jox.py:289 Creating slice controller",
			"2019-04-04T22:53:21 INFO jox.NetworkSliceController nsi_controller.py:41 Initial configuration of network slice controller",
			"2019-04-04T22:53:21 INFO jox.NetworkSliceController nsi_controller.py:62 The resource controller is built",
			"2019-04-04T22:53:21 INFO jox jox.py:293 Creating sub-slice controller",
			"2019-04-04T22:53:21 INFO jox jox.py:301 Slices Controller was successfully loaded!",
			"2019-04-04T22:53:21 INFO jox jox.py:306 JOX loading time: 11.045218467712402 ",
			"2019-04-04T22:53:21 INFO jox jox.py:316 JOX Web API loaded!"
		],
	"elapsed-time": "0:00:00.001849"
	}
	
	@apiExample {curl} Second-Example-Usage:
		     curl -i http://localhost:5000/log/jox/error
	@apiSuccessExample Second-Example-Success-Response:
	HTTP/1.0 200 OK
	{
		"data": [
					"2019-04-04T22:53:21 ERROR jox.es es.py:63 Elasticsearch: connection Failed",
					"2019-04-04T22:53:21 ERROR jox jox.py:228 Elasticsearch is not working while it is enabled. Either disable elasticsearch or run it"
				],
		"elapsed-time": "0:00:00.001849"
	}
	@apiExample {curl} Third-Example-Usage:
		     curl -i http://localhost:5000/log/juju
	@apiSuccessExample Third-Example-Success-Response:
	HTTP/1.0 200 OK
	{
		"data": [
			        "unit-mysql-8: 12:01:35 DEBUG unit.mysql/8.config-changed update-alternatives: using /etc/mysql/mysql.cnf to provide /etc/mysql/my.cnf (my.cnf) in auto mode",
				    "unit-mysql-8: 12:01:35 DEBUG unit.mysql/8.config-changed Renaming removed key_buffer and myisam-recover options (if present)",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libhtml-tagset-perl (3.20-2) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up liburi-perl (1.71-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libhtml-parser-perl (3.72-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libcgi-pm-perl (4.26-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libfcgi-perl (0.77-1build1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libcgi-fast-perl (1:2.10-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libencode-locale-perl (1.05-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libhtml-template-perl (2.95-2) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libtimedate-perl (2.3000-2) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libhttp-date-perl (6.02-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libio-html-perl (1.001-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up liblwp-mediatypes-perl (6.02-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up libhttp-message-perl (6.11-1) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Setting up mysql-server (5.7.25-0ubuntu0.16.04.2) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Processing triggers for libc-bin (2.23-0ubuntu11) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Processing triggers for systemd (229-4ubuntu21.17) ...",
				    "unit-mysql-8: 12:01:41 DEBUG unit.mysql/8.config-changed Processing triggers for ureadahead (0.100.0-19) ...",
				    "unit-mysql-8: 12:01:42 INFO unit.mysql/8.juju-log dataset size in bytes: 26860322816",
				    "unit-wordpress-8: 12:01:50 WARNING juju.worker.uniter.operation we should run a leader-deposed hook here, but we can't yet",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.juju-log db:26: Using existing password file '/var/lib/mysql/mysql.passwd'",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined /var/lib/juju/agents/unit-mysql-8/charm/hooks/db-relation-joined:19: Warning: Using GRANT for creating new user is deprecated and will be removed in future release. Create new user with CREATE USER statement.",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined   cursor.execute(sql)",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined /var/lib/juju/agents/unit-mysql-8/charm/hooks/db-relation-joined:19: Warning: Using GRANT statement to modify existing user's properties other than privileges is deprecated and will be removed in future release. Use ALTER USER statement for this operation.",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined   cursor.execute(sql)",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined [grant replication client on *.* to `chum5ic1go5Aexe` identified by 'Aiceico0ahxaech']",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined [grant all on `wordpress`.* to `chum5ic1go5Aexe` identified by 'Aiceico0ahxaech']",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined ['relation-set', 'database=wordpress', 'user=chum5ic1go5Aexe', 'password=Aiceico0ahxaech', 'host=10.70.21.133', 'slave=False']",
				    "unit-mysql-8: 12:01:51 DEBUG unit.mysql/8.db-relation-joined [create database `wordpress` character set utf8]",
				    "unit-mysql-8: 12:01:54 DEBUG unit.mysql/8.juju-log db:26: Excluding /var/lib/mysql/mysql.passwd from peer migration",
				    "unit-mysql-8: 12:01:54 DEBUG unit.mysql/8.db-relation-broken Relationship with wordpress broken.",
				    "unit-mysql-8: 12:01:54 DEBUG unit.mysql/8.db-relation-broken revoked privileges for `chum5ic1go5Aexe` on database `wordpress`",
				    "unit-mysql-8: 12:01:54 ERROR juju.worker.uniter resolver loop error: committing operation \"run relation-broken (26) hook\":relation \"wordpress:db mysql:db\": permission denied",
				    "machine-21: 12:01:55 ERROR juju.worker.dependency \"unit-agent-deployer\" manifold worker returned unexpected error: permission denied",
				    ""
				],
		"elapsed-time": "0:00:00.001849"
	}
	@apiExample {curl} Fourth-Example-Usage:
		     curl -i http://localhost:5000/log/juju/warning
	@apiSuccessExample Fourth-Example-Success-Response:
	HTTP/1.0 200 OK
	{
		"data": [
                    "unit-wordpress-8: 12:01:50 WARNING juju.worker.uniter.operation we should run a leader-deposed hook here, but we can't yet"
				],
		"elapsed-time": "0:00:00.001849"
	}
	"""
	if log_type is None:
		log_type = 'all'
	if log_source is None:
		log_source = 'jox'
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["log_type"] = log_type
	enquiry["parameters"]["log_source"] = log_source

	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)

	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

@app.route('/dis-aggregation')
@app.route('/dis-aggregation/<string:type>')
@app.route('/dis-aggregation/<string:cloud_name>/<string:model_name>/<string:type>')
def Disaggregation(cloud_name=None, model_name=None, type="mon"):
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["cloud_name"] = cloud_name
	enquiry["parameters"]["model_name"] = model_name
	
	enquiry["parameters"]["disaggregation"] = {}
	enquiry["parameters"]["disaggregation"]["type"] = type
	
	enquiry = json.dumps(enquiry)
	logger.info("enquiry: {}".format(enquiry))
	logger.debug("enquiry: {}".format(enquiry))
	# waiting for the response
	response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
	data = response.decode(listOfTasks.gv.ENCODING_TYPE)
	data = json.loads(data)

	status_code = data["status_code"]
	data = data["data"]
	data = {
		"data": data,
		"elapsed-time": str(datetime.datetime.now() - current_time),
	}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

@app.route('/relation', methods=['POST', 'DELETE'])
def Relations():
	"""
	@apiGroup Relations
	@apiName add-relation
	
	@api {post} /relation Add Relation(s)
	@apiDescription This endpoint adds relation(s), as defined by the attached json file. Through this endpoint, we can add multiple relations at the same time.
	@apiParam {json}    file the json file that contains all the relations to be added
	@apiParam {String} slice_name slice name
	@apiParam {String} nssi_source source sub-slice name, where the source application exist
	@apiParam {String} nssi_node_source the source application
	@apiParam {String} source_jcloud juju controller name where the source juju model exists
	@apiParam {String} source_jmodel juju model name where the source application is deployed
	@apiParam {String} nssi_target target sub-slice name, where the target application exist
	@apiParam {String} nssi_node_target the target application
	@apiParam {String} target_jcloud juju controller name where the target juju model exists
	@apiParam {String} target_jmodel juju model name where the target application is deployed
	
	@apiSuccessExample Example of the json file to add relation(s):
	{
		"relation-1": {
			"slice_name": "mosaic5g-slice",
			"nssi_source": "nssi_3",
			"nssi_node_source": "flexran:rtc",
			"source_jcloud": "nymphe-edu",
			"source_jmodel": "default-juju-model-1",
			"nssi_target": "nssi_3",
			"nssi_node_target": "oai-du:rtc",
			"target_jcloud": "nymphe-edu",
			"target_jmodel": "default-juju-model-1"
		},
		"relation-2": {
			"slice_name": "mosaic5g-slice",
			"nssi_source": "nssi_1",
			"nssi_node_source": "oai-hss:hss",
			"source_jcloud": "nymphe-edu",
			"source_jmodel": "default-juju-model-1",
			"nssi_target": "nssi_2",
			"nssi_node_target": "oai-mme:hss",
			"target_jcloud": "nymphe-edu",
			"target_jmodel": "default-juju-model-1"
		},
		"relation-3": {
			"slice_name": "mosaic5g-slice",
			"nssi_source": "nssi_3",
			"nssi_node_source": "flexran:rtc",
			"source_jcloud": "nymphe-edu",
			"source_jmodel": "default-juju-model-1",
			"nssi_target": "nssi_3",
			"nssi_node_target": "oai-cu:rtc",
			"target_jcloud": "nymphe-edu",
			"target_jmodel": "default-juju-model-1"
		}
	}
	@apiExample {curl} Example-Usage:
		     curl -i http://localhost:5000/relation  -X POST  --data-binary "@relations.json"  
	
	@apiSuccessExample Example-Response:
	{
		"data": {
			"relation-1": "The relation between nssi_3:flexran:rtc and nssi_3:oai-du:rtc already exist", 
			"relation-2": "The relation between nssi_1:oai-hss:hss and nssi_2:oai-mme:hss already exist", 
			"relation-3": "The relation between flexran:rtc and oai-cu:rtc is successfully added"
		}, 
		"elapsed-time": "0:00:05.121335"
	}
	"""
	"""
	@apiGroup Relations
	@apiName remove-relation
	
	@api {delete} /relation Remove Relation(s)
	@apiDescription This endpoint removes relation(s), as defined by the attached json file. Through this endpoint, we can remove multiple relations at the same time.
	@apiParam {json} file the json file that contains all the relations to be removed
	@apiParam {String} slice_name slice name
	@apiParam {String} nssi_source source sub-slice name, where the source application exist
	@apiParam {String} nssi_node_source the source application
	@apiParam {String} source_jcloud juju controller name where the source juju model exists
	@apiParam {String} source_jmodel juju model name where the source application is deployed
	@apiParam {String} nssi_target target sub-slice name, where the target application exist
	@apiParam {String} nssi_node_target the target application
	@apiParam {String} target_jcloud juju controller name where the target juju model exists
	@apiParam {String} target_jmodel juju model name where the target application is deployed
	
	
	@apiSuccessExample Example of the json file to add relation(s):
	{
		"relation-1": {
			"slice_name": "mosaic5g-slice",
			"nssi_source": "nssi_3",
			"nssi_node_source": "flexran:rtc",
			"source_jcloud": "nymphe-edu",
			"source_jmodel": "default-juju-model-1",
			"nssi_target": "nssi_3",
			"nssi_node_target": "oai-enb:rtc",
			"target_jcloud": "nymphe-edu",
			"target_jmodel": "default-juju-model-1"
		},
		"relation-2": {
			"slice_name": "mosaic5g-slice",
			"nssi_source": "nssi_1",
			"nssi_node_source": "oai-hss:hss",
			"source_jcloud": "nymphe-edu",
			"source_jmodel": "default-juju-model-1",
			"nssi_target": "nssi_2",
			"nssi_node_target": "oai-spgw:hss",
			"target_jcloud": "nymphe-edu",
			"target_jmodel": "default-juju-model-1"
		},
		"relation-3": {
			"slice_name": "mosaic5g-slice",
			"nssi_source": "nssi_3",
			"nssi_node_source": "flexran:rtc",
			"source_jcloud": "nymphe-edu",
			"source_jmodel": "default-juju-model-1",
			"nssi_target": "nssi_3",
			"nssi_node_target": "oai-cu:rtc",
			"target_jcloud": "nymphe-edu",
			"target_jmodel": "default-juju-model-1"
		}
	}
	@apiExample {curl} Example-Usage:
		     curl -i http://localhost:5000/relation  -X DELETE  --data-binary "@relations.json"  
	
	@apiSuccessExample Example-Response:
	{
		"data": {
			"relation-1": "No relation found  between flexran:rtc and oai-enb:rtc", 
			"relation-2": "No relation between nssi_1:oai-hss:hss and nssi_2:oai-spgw:hss", 
			"relation-3": "The relation betwenn flexran:rtc and oai-cu:rtc is successfuly removed"
		}, 
		"elapsed-time": "0:00:00.314112"
	}
	"""
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	if str(request.content_type) != "None":
		if (request.headers['Content-Type'] == "application/x-www-form-urlencoded") or (request.headers['Content-Type'] == "application/json"):
			relations = request.get_json(force=True)
			enquiry["parameters"]["relations"] = relations
			enquiry = json.dumps(enquiry)
			logger.info("enquiry: {}".format(enquiry))
			logger.debug("enquiry: {}".format(enquiry))
			# waiting for the response
			response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
			data = response.decode(listOfTasks.gv.ENCODING_TYPE)
			data = json.loads(data)

			status_code = data["status_code"]
			data = data["data"]
			data = {
				"data": data,
				"elapsed-time": str(datetime.datetime.now() - current_time),
			}
		else:
			status_code = 400
			data = {
				"data": "No json file found",
				"elapsed-time": str(datetime.datetime.now() - current_time),
			}
	else:
		status_code = 400
		data = {
			"data": "No json file found",
			"elapsed-time": str(datetime.datetime.now() - current_time),
		}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

@app.route('/config', methods=['POST'])
def Configurations():
	"""
	@apiGroup Configuration
	@apiName configAppJujuModel
	
	@api {get} /config Get and set configuration for applicaton and juju model
	@apiDescription This endpoint allosw to get and/or set values of the parameters of applications, as well as the juju model.
	@apiParam {json}    file The json file. It contains the hereunder fields
	@apiParam {String} juju_controler Name of juju controller
	@apiParam {String} juju_model  Name of juju model
	@apiParam {String} app-config Dictionary where its keys are the applications that we need to get/set their parameters,
							while their values are are another dictionary that contains a pair of the parameters, along with 
							their values (if we need to set the value of a parameter) or empty string (if we need to get the value of a parameter)
	@apiParam {String} model-config Dictionary where its keys are the parameters of the configuration of juju model (you can get them through juju CLI using juju model-config),
						and the values of the dictionary are either empty string (if we need to get the value of the parameter) or string value
						(if we need to set the value of the parameter)
	
	@apiExample {curl} Example-1-Usage:
		     curl http://10.42.0.4:5000/config --data-binary "@config_example.json"  
	@apiSuccessExample Example 1 - config_example.json:
	{
		"juju_controler": "nymphe-edu",
		"juju_model": "default-juju-model-1",
		"app-config": {
			"oai-spgw": {
				"pgw-eth": "",
				"sgw-eth": ""
			},
			"oai-du": {
				"node_function": "enb"
			}
		},
		"model-config": {
			"update-status-hook-interval": "45s"
		}
	}
	@apiSuccessExample Example-1-Response:
	{
		"data": {
			"app-config": {
			"oai-du": {
				"node_function": "Set the value of the parameter node_function to enb"
			}, 
			"oai-spgw": {
				"pgw-eth": {
				"default": "ens3", 
				"description": "This is usefull especially when you are in manual environment so you have your own machines. The default value is eth0. NO empty value.\n", 
				"source": "user", 
				"type": "string", 
				"value": "enp7s0"
				}, 
				"sgw-eth": {
				"default": "ens3", 
				"description": "This is usefull especially when you are in manual environment so you have your own machines. The default value is eth0. NO empty value.\n", 
				"source": "user", 
				"type": "string", 
				"value": "enp7s0"
				}
			}
			}, 
			"juju_controler": "nymphe-edu", 
			"juju_model": "default-juju-model-1", 
			"model-config": {
			"update-status-hook-interval": "The parameter update-status-hook-interval is set to the value 45s"
			}
		}, 
		"elapsed-time": "0:00:00.368201"
	}


	@apiExample {curl} Example-2-Usage:
		     curl http://10.42.0.4:5000/config --data-binary "@config_example_2.json"  
	@apiSuccessExample Example 2 - config_example_2.json:
	{
		"juju_controler": "nymphe-edu",
		"juju_model": "default-juju-model-1",
		"app-config": {
			"oai-spgw": {
				"pgw-iface": "",
				"sgw-iface": ""
			},
			"oai-du": {
				"node_type": "enb"
			},
			"oai-enb": {
			}
		},
		"model-config": {
			"update-status-hook-interval": "45 seconds"
		}
	}
	@apiErrorExample Example-2-Response:
	{
		"data": {
			"app-config": {
			"oai-du": {
				"node_type": "unknown option \"node_type\""
			}, 
			"oai-enb": "The application oai-enb can not be found in the juju model nymphe-edu:default-juju-model-1", 
			"oai-spgw": {
				"pgw-iface": "the parameter pgw-iface can not be found in the list of parameters of oai-spgw", 
				"sgw-iface": "the parameter sgw-iface can not be found in the list of parameters of oai-spgw"
			}
			}, 
			"juju_controler": "nymphe-edu", 
			"juju_model": "default-juju-model-1", 
			"model-config": {
			"update-status-hook-interval": "invalid update status hook interval in model configuration; time; unknown unit  seconds in duration 45 seconds"
			}
		}, 
		"elapsed-time": "0:00:00.456093"
	}

	"""
	#@apiSuccessExample Example of the json file to add relation(s):
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	if str(request.content_type) != "None":
		if (request.headers['Content-Type'] == "application/x-www-form-urlencoded") or (request.headers['Content-Type'] == "application/json"):
			configuration = request.get_json(force=True)
			enquiry["parameters"]["configuration"] = configuration
			enquiry = json.dumps(enquiry)
			logger.info("enquiry: {}".format(enquiry))
			logger.debug("enquiry: {}".format(enquiry))
			# waiting for the response
			response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
			data = response.decode(listOfTasks.gv.ENCODING_TYPE)
			data = json.loads(data)

			status_code = data["status_code"]
			data = data["data"]
			data = {
				"data": data,
				"elapsed-time": str(datetime.datetime.now() - current_time),
			}
		else:
			status_code = 400
			data = {
				"data": "No json file found",
				"elapsed-time": str(datetime.datetime.now() - current_time),
			}
	else:
		status_code = 400
		data = {
			"data": "No json file found",
			"elapsed-time": str(datetime.datetime.now() - current_time),
		}
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

###########################################################
@app.route('/vlan', methods=['POST'])
@app.route('/vlan/<string:switch_type>/<string:switch_name>/<string:vlan_id>', methods=['GET'])
def vlan(switch_type=None, switch_name=None, vlan_id=None):
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	
	vlan_id_found = False if vlan_id == None else True
	json_file_found = False
	vlan_json_file = None
	if str(request.content_type) != "None":
		if (request.headers['Content-Type'] == "application/x-www-form-urlencoded") or (request.headers['Content-Type'] == "application/json"):
			vlan_json_file = request.get_json(force=True)
			json_file_found = True
	if json_file_found and vlan_id_found:
		status_code = 400
		data = {
			"data": "Both json file and vlan_id are found, please specify just one of them. For more information, check the apidoc of JoX",
			"elapsed-time": str(datetime.datetime.now() - current_time),
		}
	elif json_file_found or vlan_id_found:
		########################################
		if vlan_json_file == None:
			vlan_json_file = {
				"switch_type": switch_type,
				"switch_name": switch_name,
				"vlan_id": vlan_id,
			}
		enquiry["parameters"]["vlan"] = vlan_json_file

		enquiry = json.dumps(enquiry)
		logger.info("enquiry: {}".format(enquiry))
		logger.debug("enquiry: {}".format(enquiry))
		# waiting for the response
		response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
		data = response.decode(listOfTasks.gv.ENCODING_TYPE)
		data = json.loads(data)

		status_code = data["status_code"]
		data = data["data"]
		data = {
			"data": data,
			"elapsed-time": str(datetime.datetime.now() - current_time),
		}
		########################################
	else:
		status_code = 400
		data = {
			"data": "Neither json file not vlan_if found, please specify just one of them. For more information, check the apidoc of JoX",
			"elapsed-time": str(datetime.datetime.now() - current_time),
		}
	"""
			########################################
			vlan = request.get_json(force=True)
			enquiry["parameters"]["vlan"] = vlan
			enquiry["parameters"]["vlan_id"] = vlan_id

			enquiry = json.dumps(enquiry)
			logger.info("enquiry: {}".format(enquiry))
			logger.debug("enquiry: {}".format(enquiry))
			# waiting for the response
			response = listOfTasks.call(enquiry.encode(listOfTasks.gv.ENCODING_TYPE))
			data = response.decode(listOfTasks.gv.ENCODING_TYPE)
			data = json.loads(data)

			status_code = data["status_code"]
			data = data["data"]
			data = {
				"data": data,
				"elapsed-time": str(datetime.datetime.now() - current_time),
			}
			########################################
		else:
			status_code = 400
			data = {
				"data": "No json file found",
				"elapsed-time": str(datetime.datetime.now() - current_time),
			}
	else:
		status_code = 400
		data = {
			"data": "No json file found",
			"elapsed-time": str(datetime.datetime.now() - current_time),
		}
	"""
	logger.info("response: {}".format(data))
	logger.debug("response: {}".format(data))
	data = jsonify(data)
	return data, status_code

@app.errorhandler(Exception)
def page_not_found(error):
	message = \
	"""<p>The requested page does not exist and the following error was encountered:</p>
<p>{0}</p> 
<p>Please use  <a href={1}>{2}</a> to get the capabilities of JoX</p>
""".format(error,
			   ''.join([request.host_url, 'jox']),
			   ''.join([request.host_url, 'jox']))
	return message

def run():
	print(
		colored(' [*] Waiting for request on  http://{}:{}/ To exit press CTRL+C'.
		        format(listOfTasks.gv.FLASK_SERVER_IP,
		               listOfTasks.gv.FLASK_SERVER_PORT), 'green'))
	app.run(host=listOfTasks.gv.FLASK_SERVER_IP,
	        port=listOfTasks.gv.FLASK_SERVER_PORT,
	        debug=listOfTasks.gv.FLASK_SERVER_DEBUG)
	
if __name__ == '__main__':
	run()

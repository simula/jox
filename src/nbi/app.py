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
import json
from flask import Flask, request, jsonify
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
	}
}

"""
@apiDefine GroupJox JOX
This API endpoint contains the main capabilities that are needed
before deploying and monitoring the slices. Through this APIoffered by this group, you can vistualize jox configuration, and
jox capabilities, in addition to the possibility to see the
template slice/subslice before deploying your slice.
"""

"""
@apiDefine GroupOnboarding Onboarding
To Describe the onboarding later
"""

"""
@apiDefine GroupSlice Slice
This API endpoint holds the main functionalities for slice management,
like add, update, and remove a slice. Additionaly, you can also see the context of the lalready deployed slices

like get the context of deployed slices, add, and remove slices
"""
"""
@apiDefine GroupSubSlice Sub-slice
This API endpoint is dedictaed for subslcies. for the current version of JOX, you can only get the
context of the subslices, without any possibility to add/update/remove subslice.
"""
"""
@apiDefine GroupElasticsearch Elasticsearch
This API endpoint is a wrapper of elasticsearch (ES), where the main functionality that are supported in the current
version of JOX, are:

- get list of all index-pages that are saved to ES
- delete all the index-pages


this section contains the main functionalities to interact with elasticsearch,
like get the page-indexes in elasticsearch, save and delete page-indexe to(from) elasticsearch
"""
"""
@apiDefine GroupMonitoring Monitoring
this section contains the main functionalities for monitoring
slices, sub-slices, services, machines, and relations
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
	          "{}".format(''.join([request.url, 'jox \n']))
	
	return message


jox_capabilities = {
	"jox": {
		"/jox": "return jox configuration and the list of the capabilities",
		"/list": {"1": "return the list of all files in formation .yaml, .yaml and .json",
		          "2": "example: curl  http://localhost:5000/list; return the list in the default directory",
		          "3": "example: curl  http://localhost:5000/list?url=/home/ubunut/Documents/slice_template; return the list in slice_template directory",
		          },
		"/ls": "alias to /list",
		"/show/<string:nsi_name>": {"1": "show the content of the template nsi_name",
		                            "2": "example: curl  http://localhost:5000/show/exmple_template.yaml; show the slice template exmple_template.yaml in the default directory",
		                            "3": "example: curl  http://localhost:5000/list?url=/home/ubunut/Documents/slice_template/exmple_template.yaml; show the slice template exmple_template.yaml in the given directory",
		                            },
	},
	"slice": {
		"/nsi/all": "GET; get the context of all deployed slices",
		"/nsi": "GET ; alias to /nsi/all",
		"/nsi/<string:nsi_name>": {
			"GET": "get context of already deployed slice nsi_name",
			"POST": "deploy/update slice nsi_name",
			"DELET": "delete the slice nsi_name",
		},
	},
	"sub-slice": {
		"/nssi/all": {
			"GET": "get the context of all subslices"
		},
		"/nssi": "alias to /nssi/all",
		"/nssi/<string:nsi_name>": {
			"GET": "get context of the subslices attached to the slice nsi_name",
			"POST": "Not supported",
			"DELET": "Not supported",
		},
		"/nssi/<string:nsi_name>/<string:nssi_name>": {
			"GET": "get context of the subslice nssi_name attached to the slice nsi_name",
			"POST": "Not supported",
			"DELET": "Not supported",
		},
		"/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>": {
			"GET": "get crtain entity nssi_key of subslice nssi_name attached to the slice nsi_name",
			"POST": "Not supported",
			"DELET": "Not supported",
		},
	},
	"elasticsearch": {
		"/es": {
			"GET": "get all the index-pages in elasticsearch",
			"POST": "Not supported",
			"DELET": "Delete all the index-pages in elasticsearch",
		},
		"/es/<string:es_index_page>": {
			"GET": "get the content of the index-page es_index_page from  elasticsearch",
			"POST": "save the content of the index-page es_index_page to elasticsearch",
			"DELET": "Delete the index-page es_index_page from elasticsearch",
		},
		"/es/<string:es_index_page>/<string:es_key>": {
			"GET": "get certain index es_key from the index-page es_index_page from elasticsearch",
			"POST": "Not supported",
			"DELET": "Not supported",
		},
	},
	"monitoring": {
		"slice&sub-sclice": {
			"/monitor/nsi":
				"get monitoring information on all the deployed slices",
			"/monitor/nsi/<string:nsi_name>":
				"get monitoring information on the deployed slice nsi_name",
			"/monitor/nsi/<string:nsi_name>/<string:nssi_name>":
				"get monitoring information on the subslice nssi_name from the deployed slice nsi_name",
			"/monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>":
				"get monitoring information on certain entity of the the subslice nssi_name from the deployed slice nsi_name",
		},
		"service": {
			"/monitor/service/<string:nsi_name>":
				"get monitoring information on all services of the slice nsi_name",
			"/monitor/service/<string:nsi_name>/<string:nssi_name>":
				"get monitoring information on all services of the subslice nssi_name attached to the slice nsi_name",
			"/monitor/service/<string:nsi_name>/<string:nssi_name>/<string:service_name>":
				"get monitoring information on the service service_name of the subslice nssi_name attached to the slice nsi_name",
		},
		"machine": {
			"/monitor/machine/<string:nsi_name>":
				"get monitoring information on all machines of the slice nsi_name",
			"/monitor/machine/<string:nsi_name>/<string:nssi_name>":
				"get monitoring information on all machines of the subslice nssi_name attached to the slice nsi_name",
			"/monitor/machine/<string:nsi_name>/<string:nssi_name>/<string:machine_name>":
				"get monitoring information on the machine service_name of the subslice nssi_name attached to the slice nsi_name",
		},
		"relation": {
			"/monitor/relation/<string:nsi_name>":
				"get monitoring information on the relations of the slice nsi_name",
			"/monitor/relation/<string:nsi_name>/<string:nssi_name>":
				"get monitoring information on the relations of the subslice nssi_name attached to the slice nsi_name",
		},
	},
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
        HTTP/1.0 200 OK
        {
            "elapsed-time": "0:00:00.004795",
            "jox-capabilities":
                {
                // To add jox Capabilities here
                }
            "jox-config": {
                "authors-list": [
                  {
                    "email": "contact@mosaic-5g.io",
                    "name": "Eurecom"
                  }
                ],
                "store-config": {
                  "_Comment": "it is needed to cashe the onboarded packages to deploy slices later",
                  "store-directrory": "/mnt/jox_store"
                },
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
                    "failed-dependency": 424,
                    "method-failure": 420,
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
                  "ssh-key-directory": "/home/ubunut/.ssh/",
                  "ssh-key-name": "id_juju",
                  "ssh-password": "linux",
                  "ssh-user": "ubuntu"
                },
                "stats-timer": 100,
                "vim-pop": {
                  "kvm": [
                    "local"
                  ],
                  "lxc": [
                    "local"
                  ]
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


@app.route('/onboard', methods=['PUT'])
def jox_package_onboard():
	"""
    @apiGroup GroupOnboarding
    @apiName PutOnboard

    @api {put}  /onboard Package onboarding
    @apiDescription Through this endpoint, you can onboard the pakcage of slice(s), so that you can deploy it(them) later
	
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

	@apiDescription get the context of all the subslices attached to certain slice
	@api {get}  /nssi/<string:nsi_name> Context of certain subslices
	@apiParam {string} nsi_name Name of slice
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiNameNssiName

	@apiDescription get the context of certain subslice attached to specified slice
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
	@api {get}  /nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key> Context of certain entity
	@apiParam {string} nsi_name Name of slice
	@apiParam {string} nssi_name Name of subslice
	@apiParam {string="services","machines","relations"} nssi_key  Name of certain entity
	
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
	@apiDescription Get the list of all index-pages in elasticsearch
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
	    "slice_monitor_nssi_1",
	    "slice_monitor_nssi_2"
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
	@apiGroup Monitoring
	@apiName GetNsiMonitorAll

	@apiDescription Get monitoring information on specific slice
	@api {get}  /monitor/nsi/<string:nsi_name> Info. on specific slice
	@apiParam {String} nsi_name slice name
	@apiExample {curl} Example usage:
	    curl http://localhost:5000/monitor/nsi/mosaic5g

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_1": {
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
	          "slice_monitor_nssi_2": {
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
	@apiGroup Monitoring
	@apiName GetNssiMonitorAll

	@apiDescription Get monitoring information on specific subslice attached to certain slice
	@api {get}  /monitor/nsi/<string:nsi_name>/<string:nssi_name> Info. on specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslice name

	@apiExample {curl} Example usage:
	      curl http://localhost:5000/monitor/nsi/oai-epc/nssi_2

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	     "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_2": {
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
	@apiGroup Monitoring
	@apiName GetNsiMonitorServices

	@api {get}  /monitor/service/<string:nsi_name> Info. all services in specific slice

	@apiParam {String} nsi_name slice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_1": {
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
	          "slice_monitor_nssi_2": {
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
	@apiGroup Monitoring
	@apiName GetNssiMonitorServices

	@api {get}  /monitor/nsi/service/<string:nsi_name>/<string:nssi_name> Info. all services in specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc/nssi_2

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_2": {
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
	@apiGroup Monitoring
	@apiName GetNsiMonitorMachines

	@api {get}  /monitor/machine/<string:nsi_name> Info. all machines of specific slice

	@apiParam {String} nsi_name slice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/machine/oai-epc

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_1": {
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
	          "slice_monitor_nssi_2": {
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
	@apiGroup Monitoring
	@apiName GetNssiMonitorMachines

	@api {get}  /monitor/nsi/machine/<string:nsi_name>/<string:nssi_name>  Info. machines of specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslcie name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/machine/oai-epc/nssi_1

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	      "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_1": {
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
	@apiGroup Monitoring
	@apiName GetNsiMonitorRequirements

	@api {get}  /monitor/relation/<string:nsi_name> Info. relations of specific slice

	@apiParam {String} nsi_name slice name

	@apiExample {curl} Example usage:
	      curl http://localhost:5000/monitor/relation/oai-epc
	      
	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_1": {
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
	          "slice_monitor_nssi_2": {
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
	@apiGroup Monitoring
	@apiName GetNssiMonitorRequirements

	@api {get}  /monitor/nsi/relation/<string:nsi_name>/<string:nssi_name>  Info. relations of specific subslice

	@apiParam {String} nsi_name slice name
	@apiParam {String} nssi_name subslice name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/relation/oai-epc/nssi_1

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "oai-epc": {
	          "slice_monitor_nssi_1": {
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
	@apiGroup Monitoring
	@apiName GetJujuMonitorAll

	@apiDescription Get information on all the services, machines and relations of the curren juju model
	@api {get}  /monitor/juju Info. juju current model

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/juju

	@apiSuccessExample Success-Response:
	    HTTP/1.0 200 OK
	    {
	    "data": {
	        "machines": [
	          {
	            "0": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:13:10.467955832Z",
	                "status": "started",
	                "version": "2.5.1"
	              },
	              "constraints": "mem=524288M tags=VDU_mysql",
	              "containers": {},
	              "dns-name": "10.70.21.123",
	              "hardware": "arch=amd64 cores=0 mem=524288M",
	              "has-vote": false,
	              "id": "0",
	              "instance-id": "juju-7a566b-0",
	              "instance-status": {
	                "data": {},
	                "info": "Running",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:12:29.016847134Z",
	                "status": "running",
	                "version": ""
	              },
	              "ip-addresses": [
	                "10.70.21.123"
	              ],
	              "jobs": [
	                "JobHostUnits"
	              ],
	              "network-interfaces": {
	                "eth0": {
	                  "gateway": "10.70.21.1",
	                  "ip-addresses": [
	                    "10.70.21.123"
	                  ],
	                  "is-up": true,
	                  "mac-address": "00:16:3e:c3:71:0c"
	                }
	              },
	              "series": "xenial",
	              "wants-vote": false
	            },
	            "1": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:13:30.375890236Z",
	                "status": "started",
	                "version": "2.5.1"
	              },
	              "constraints": "mem=524288M tags=VDU_oai-hss",
	              "containers": {},
	              "dns-name": "10.70.21.55",
	              "hardware": "arch=amd64 cores=0 mem=524288M",
	              "has-vote": false,
	              "id": "1",
	              "instance-id": "juju-7a566b-1",
	              "instance-status": {
	                "data": {},
	                "info": "Running",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:12:34.314790591Z",
	                "status": "running",
	                "version": ""
	              },
	              "ip-addresses": [
	                "10.70.21.55"
	              ],
	              "jobs": [
	                "JobHostUnits"
	              ],
	              "network-interfaces": {
	                "eth0": {
	                  "gateway": "10.70.21.1",
	                  "ip-addresses": [
	                    "10.70.21.55"
	                  ],
	                  "is-up": true,
	                  "mac-address": "00:16:3e:e0:77:7e"
	                }
	              },
	              "series": "xenial",
	              "wants-vote": false
	            },
	            "2": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:13:28.947200307Z",
	                "status": "started",
	                "version": "2.5.1"
	              },
	              "constraints": "mem=524288M tags=VDU_oai-mme",
	              "containers": {},
	              "dns-name": "10.70.21.207",
	              "hardware": "arch=amd64 cores=0 mem=524288M",
	              "has-vote": false,
	              "id": "2",
	              "instance-id": "juju-7a566b-2",
	              "instance-status": {
	                "data": {},
	                "info": "Running",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:12:50.998958994Z",
	                "status": "running",
	                "version": ""
	              },
	              "ip-addresses": [
	                "10.70.21.207"
	              ],
	              "jobs": [
	                "JobHostUnits"
	              ],
	              "network-interfaces": {
	                "eth0": {
	                  "gateway": "10.70.21.1",
	                  "ip-addresses": [
	                    "10.70.21.207"
	                  ],
	                  "is-up": true,
	                  "mac-address": "00:16:3e:a3:35:77"
	                }
	              },
	              "series": "xenial",
	              "wants-vote": false
	            },
	            "3": {
	              "agent-status": {
	                "data": {},
	                "info": "",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:13:30.922084571Z",
	                "status": "started",
	                "version": "2.5.1"
	              },
	              "constraints": "mem=524288M tags=VDU_oai-spgw",
	              "containers": {},
	              "dns-name": "10.70.21.244",
	              "hardware": "arch=amd64 cores=0 mem=524288M",
	              "has-vote": false,
	              "id": "3",
	              "instance-id": "juju-7a566b-3",
	              "instance-status": {
	                "data": {},
	                "info": "Running",
	                "kind": "",
	                "life": "",
	                "since": "2019-03-06T17:13:00.176443058Z",
	                "status": "running",
	                "version": ""
	              },
	              "ip-addresses": [
	                "10.70.21.244"
	              ],
	              "jobs": [
	                "JobHostUnits"
	              ],
	              "network-interfaces": {
	                "eth0": {
	                  "gateway": "10.70.21.1",
	                  "ip-addresses": [
	                    "10.70.21.244"
	                  ],
	                  "is-up": true,
	                  "mac-address": "00:16:3e:48:9f:54"
	                }
	              },
	              "series": "xenial",
	              "wants-vote": false
	            }
	          }
	        ],
	        "relations": [
	          "The relations is not supported yet"
	        ],
	        "services": [
	          {
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
	          }
	        ]
	      },
	      "elapsed-time": "0:00:00.660348"
	    }
	@apiErrorExample Error-Response:
	    HTTP/1.0 404 Not Found
	    {
	      "data": "Error while trying to connect to the current juju model",
	      "elapsed-time": "0:00:00.002289"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetJujuMonitorJujuEntityCurrentModel

	@api {get}  /monitor/juju/<string:juju_entity> Specific info. of juju current model
	
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
	@apiGroup Monitoring
	@apiName GetJujuMonitorJujuEntityCertainModel

	@api {get} /monitor/juju/<string:juju_key_val>/<string:cloud_name>/<string:model_name>
	 Specific info. from certain juju model
	
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
	      {}
	    ],
	    "relations": [
	      {}
	    ],
	    "services": [
	      {}
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


@app.errorhandler(Exception)
def page_not_found(error):
	return "!!!!" + repr(error) + "\n"


def run():
	print(
		colored(' [*] Waiting for request on  http://localhost:5000/ To exit press CTRL+C'.
		        format(listOfTasks.gv.FLASK_SERVER_IP,
		               listOfTasks.gv.FLASK_SERVER_PORT), 'green'))
	
	app.run(host=listOfTasks.gv.FLASK_SERVER_IP,
	        port=listOfTasks.gv.FLASK_SERVER_PORT,
	        debug=listOfTasks.gv.FLASK_SERVER_DEBUG)
	
if __name__ == '__main__':
	run()

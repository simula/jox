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


SLICE_TEMPLATE_DIRECTORY_DEFAULT = ''.join([dir_parent_path, '/jox_store'])

app = Flask(__name__)

logger = logging.getLogger('jox.NBI')
logging.basicConfig(level=logging.INFO)
logger.info('Staring JOX main thread')

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
		"package_onboard_data": None,
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
	@apiDescription The hoemepage of JoX
    
    @apiExample {curl} Example usage:
         curl -i http://127.0.0.1:5000/
         curl -i  [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

    @apiSuccessExample Success-Response:
        HTTP/1.0 200 OK
        {
        Welcome to JOX!
        To get the list of the capabilities and jox configuration, use the following
        [http://JOX-URL:PORT/jox](http://JOX-URL:PORT/jox)
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
		          "2": "example: curl  http://127.0.0.1:5000/list; return the list in the default directory",
		          "3": "example: curl  http://127.0.0.1:5000/list?url=/home/arouk/Documents/slice_template; return the list in slice_template directory",
		          },
		"/ls": "alias to /list",
		"/show/<string:nsi_name>": {"1": "show the content of the template nsi_name",
		                            "2": "example: curl  http://127.0.0.1:5000/show/exmple_template.yaml; show the slice template exmple_template.yaml in the default directory",
		                            "3": "example: curl  http://127.0.0.1:5000/list?url=/home/arouk/Documents/slice_template/exmple_template.yaml; show the slice template exmple_template.yaml in the given directory",
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
         curl -i http://127.0.0.1:5000/jox

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
                  "ssh-key-directory": "/home/arouk/.ssh/",
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
	@apiName GetJoxlist

	@api {get}  /list List of templates
	@apiDescription Get the list of all template (in format .yaml, .yml, and .json) in default directory or given directory
	@apiParam {path} full_path directory of the templates (Optional)

	@apiExample {curl} First-Example-Usage:
	     curl -i http://127.0.0.1:5000/list

	@apiSuccessExample First-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	        "elapsed-time": "0:00:00.006720",
	        "list of templates in the directory None":
	        [
	            "default_slice_NSI.yaml",
	            "default_slice_NSSI2_2.yaml",
	            "default_slice_NSSI_2.yaml",
	            "default_slice_NSSI2_1.yaml",
	            "default_slice_NSI2.yaml",
	            "default_slice_NSSI_1.yaml"
	        ]
	    }

	@apiDescription Get the list of all template in the default or given directory
	@apiExample {curl} Second-Example-Usage:
	     curl -i http://127.0.0.1:5000/list?url=/home/ubuntu/jox/jox/src/com/config

	@apiSuccessExample Second-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	        "elapsed-time": "0:00:00.005351",
	        "list of templates in the directory None":
	         [
	            "jox_config.json"
	        ]
	    }
	"""
	
	"""
	@apiGroup GroupJox
	@apiName GetJoxLs

	@api {get}  /ls List of templates  [Alias]
	@apiDescription It is alias to /list
	@apiParam {path} full_path directory of the templates (Optional)
	@apiExample {curl} First-Example-Usage:
	     curl -i http://127.0.0.1:5000/ls

	@apiSuccessExample First-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	        "elapsed-time": "0:00:00.006720",
	        "list of templates in the directory None":
	        [
	            "default_slice_NSI.yaml",
	            "default_slice_NSSI2_2.yaml",
	            "default_slice_NSSI_2.yaml",
	            "default_slice_NSSI2_1.yaml",
	            "default_slice_NSI2.yaml",
	            "default_slice_NSSI_1.yaml"
	        ]
	    }

	@apiExample {curl} Second-Example-Usage:
	     curl -i http://127.0.0.1:5000/ls?url=/home/ubuntu/jox/jox/src/com/config

	@apiSuccessExample Second-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	        "elapsed-time": "0:00:00.005351",
	        "list of templates in the directory None":
	         [
	            "jox_config.json"
	        ]
	    }
	"""
	
	"""
	@apiGroup GroupJox
	@apiName GetJoxShow

	@api {get}  /show/<string:nsi_name>?url=full_path Show the defined template
	@apiDescription Show the content of the file nsi_name, only the following formats are supported: .yaml, .yml, and .json

	@apiParam {string} nsi_name name of the file(template)
	@apiParam {path} [full_path=None] full_path directory of the templates

	@apiDescription example usage for to show the template in default directory
	@apiExample {curl} First-Example-Usage:
	     curl -i http://127.0.0.1:5000/show/default_slice_NSI.yaml
	@apiSuccessExample First-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	      "elapsed-time": "0:00:00.029316",
	      "list of templates in the directory None": {
	        "description": "Template for deploying oai-epc with JoX",
	        "imports": [
	          "default_slice_NSSI_1",
	          "default_slice_NSSI_2"
	        ],
	        "metadata": {
	          "ID": "NSI_1",
	          "vendor": "Eurecom",
	          "version": 0.1
	        },
	        "relationships_template": {
	          "connection_server_client": {
	            "source": {
	              "inputs": {
	                "name": "eg1",
	                "node": "oai-hss",
	                "type": "tosca.relationships.AttachesTo"
	              },
	              "node": "NSS_first",
	              "parameters": "NSSI_1"
	            },
	            "target": {
	              "inputs": {
	                "name": "ing1",
	                "node": "oai-mme",
	                "type": "tosca.relationships.DependsOn"
	              },
	              "node": "NSS_second",
	              "parameters": "NSSI_2"
	            },
	            "type": "tosca.relationships.ConnectsTo"
	          }
	        },
	        "topology_template": {
	          "node_templates": {
	            "NSS_first": {
	              "requirements": {
	                "egress": {
	                  "eg1": {
	                    "node": "oai-hss",
	                    "relationship": {
	                      "type": "tosca.relationships.AttachesTo"
	                    }
	                  }
	                },
	                "nssi": "NSSI_1"
	              },
	              "type": "tosca.nodes.JOX.NSSI"
	            },
	            "NSS_second": {
	              "requirements": {
	                "ingress": {
	                  "ing1": {
	                    "node": "oai-mme",
	                    "relationship": {
	                      "type": "tosca.relationships.DependsOn"
	                    }
	                  }
	                },
	                "nssi": "NSSI_2"
	              },
	              "type": "tosca.nodes.JOX.NSSI"
	            }
	          }
	        },
	        "tosca_definitions_version": "tosca_simple_yaml_1_0"
	      }
	    }

	@apiDescription example usage for to show the template in specified directory
	@apiExample {curl} Second-Example-Usage:
	     curl -i http://127.0.0.1:5000/show/default_slice_NSSI_2.yaml?url=/home/ubuntu/Documents/slice_template
	@apiSuccessExample Second-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	      "elapsed-time": "0:00:00.034370",
	      "list of templates in the directory None": {
	        "description": "Template for deploying oai-epc with JoX",
	        "dsl_definitions": {
	          "host_small": {
	            "disk_size": 10,
	            "mem_size": 2048,
	            "num_cpus": 1
	          },
	          "host_tiny": {
	            "disk_size": 3,
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
	          "default_slice_NSSI_2"
	        ],
	        "metadata": {
	          "ID": "NSSI_2",
	          "vendor": "Eurecom",
	          "version": 0.1
	        },
	        "topology_template": {
	          "node_templates": {
	            "VDU_oai-mme": {
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
	                  "properties": {
	                    "disk_size": 5,
	                    "mem_size": 1024,
	                    "num_cpus": 1
	                  }
	                },
	                "os": {
	                  "properties": {
	                    "architecture": "x86_64",
	                    "distribution": "Ubuntu",
	                    "type": "Linux",
	                    "version": 16.04
	                  }
	                }
	              },
	              "properties": null,
	              "type": "tosca.nodes.nfv.VDU.Compute"
	            },
	            "VDU_oai-spgw": {
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
	                  "properties": {
	                    "disk_size": 10,
	                    "mem_size": 2048,
	                    "num_cpus": 1
	                  }
	                },
	                "os": {
	                  "properties": {
	                    "architecture": "x86_64",
	                    "distribution": "Ubuntu",
	                    "type": "Linux",
	                    "version": 16.04
	                  }
	                }
	              },
	              "properties": null,
	              "type": "tosca.nodes.nfv.VDU.Compute"
	            },
	            "oai-mme": {
	              "properties": {
	                "charm": "cs:~navid-nikaein/xenial/oai-mme-18",
	                "endpoint": "localhost",
	                "model": "default-juju-model-1",
	                "vendor": "Eurecom",
	                "version": 1
	              },
	              "requirements": {
	                "req1": {
	                  "node": "VDU_oai-mme",
	                  "relationship": "tosca.relationships.HostedOn"
	                }
	              },
	              "type": "tosca.nodes.SoftwareComponent.JOX"
	            },
	            "oai-spgw": {
	              "properties": {
	                "charm": "cs:~navid-nikaein/xenial/oai-spgw-15",
	                "endpoint": "localhost",
	                "model": "default-juju-model-1",
	                "vendor": "Eurecom",
	                "version": 1
	              },
	              "requirements": {
	                "req1": {
	                  "node": "VDU_oai-spgw",
	                  "relationship": "tosca.relationships.HostedOn"
	                },
	                "req2": {
	                  "node": "oai-mme",
	                  "relationship": "tosca.relationships.AttachesTo"
	                }
	              },
	              "type": "tosca.nodes.SoftwareComponent.JOX"
	            }
	          }
	        },
	        "tosca_definitions_version": "tosca_simple_yaml_1_0"
	      }
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

    @api {put}  /onboard package onboarding
    @apiDescription
    """
	enquiry = standard_reqst
	current_time = datetime.datetime.now()
	enquiry["datetime"] = str(current_time)
	enquiry["request-uri"] = str(request.url_rule)
	enquiry["request-type"] = (request.method).lower()
	enquiry["parameters"]["template_directory"] = request.args.get('url')
	enquiry["parameters"]["package_onboard_data"] = list(request.data)
	
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


@app.route('/nsi/all', methods=['GET'])
@app.route('/nsi', methods=['GET'])
@app.route('/nsi/<string:nsi_name>', methods=['GET', 'POST', 'DELETE'])
def network_slice(nsi_name=None):
	"""
	@apiGroup GroupSlice
	@apiName GetNsiAll

	@api {get}  /nsi/all List all deployed NSI
	@apiDescription get the list of all template (in format .yaml, .yml, and .json) in default directory or given directory

	@apiParam {path} full_path directory of the templates (Optional)

	@apiExample {curl} First-Example-Usage:
	     curl -i http://127.0.0.1:5000/nsi/all

	@apiDescription get the list of all deployed slices
	@apiSuccessExample First-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	       "data":{
	              "NSI_1":{
	                 "inter_nssi_relation":[
	                    {
	                       "service_a":{
	                          "jcloud":"localhost",
	                          "jmodel":"default-juju-model-1",
	                          "nssi":"NSSI_1",
	                          "service":"oai-hss"
	                       },
	                       "service_b":{
	                          "jcloud":"localhost",
	                          "jmodel":"default-juju-model-1",
	                          "nssi":"NSSI_2",
	                          "service":"oai-mme"
	                       }
	                    }
	                 ],
	                 "slice_name":"NSI_1",
	                 "sub_slices":[
	                    "NSSI_1",
	                    "NSSI_2"
	                 ]
	              }
	           },
	        "elapsed-time":"0:00:00.003032"
	    }
	@apiDescription get the list of all template in the given directory /home/arouk/Documents/slice_templet
	@apiExample {curl} Second-Example-Usage:
	     curl -i http://127.0.0.1:5000/list?url=/home/arouk/Documents/slice_templet

	@apiSuccessExample Second-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	        To add example here
	    }
	"""
	
	"""
	@apiGroup GroupSlice
	@apiName GetNsi

	@apiDescription It is alias to /nsi/all
	@api {get}  /nsi List all deployed NSI [Alias]
	"""
	
	"""
	@apiGroup GroupSlice
	@apiName GetNsiName

	@api {get}  /nsi/<string:nsi_name> Get NSI
	@apiDescription get the context, deployed, and delete the slice nsi_name
	@apiParam {string} nsi_name name of the slice

	@apiExample {curl} First-Example-Usage-POST:
	     curl http://localhost:5000/nsi --upload-file "/home/ubuntu/jox-master/jox/src/com/slice_template/default_slice_NS.zip" -XPOST
	@apiSuccessExample First-Example-Success-Response-POST:
	    HTTP/1.1 200 OK
	    {
	     "data":"Ceating/updating the slice default_slice_NSI.yaml",
	     "elapsed-time":"0:01:40.287464"
	    }

	"""
	
	"""
	@apiGroup GroupSlice
	@apiName PostNsiName

	@api {post}  /nsi/<string:nsi_name> Add NSI
	@apiDescription get the context, deployed, and delete the slice nsi_name
	@apiParam {string} nsi_name name of the slice

	@apiExample {curl} Example-Usage:
	     curl http://localhost:5000/nsi --upload-file "/home/ubuntu/jox-master/jox/src/com/slice_template/default_slice_NS.zip" -XPOST

	@apiSuccessExample Second-Example-Success-Response-GET:
	    HTTP/1.1 200 OK
	    {
	       "data":{
	              "NSI_1":{
	                 "inter_nssi_relation":[
	                    {
	                       "service_a":{
	                          "jcloud":"localhost",
	                          "jmodel":"default-juju-model-1",
	                          "nssi":"NSSI_1",
	                          "service":"oai-hss"
	                       },
	                       "service_b":{
	                          "jcloud":"localhost",
	                          "jmodel":"default-juju-model-1",
	                          "nssi":"NSSI_2",
	                          "service":"oai-mme"
	                       }
	                    }
	                 ],
	                 "slice_name":"NSI_1",
	                 "sub_slices":[
	                    "NSSI_1",
	                    "NSSI_2"
	                 ]
	              }
	           },
	        "elapsed-time":"0:00:00.003032"
	    }

	"""
	"""
	@apiGroup GroupSlice
	@apiName DeleteNsiName

	@api {delete}  /nsi/<string:nsi_name> Remove NSI
	@apiDescription get the context, deployed, and delete the slice nsi_name
	@apiParam {string} nsi_name name of the slice

	@apiExample {curl} Example-Usage:
	     curl -i -X DELETE http://127.0.0.1:5000/nsi/NSI_1
	@apiSuccessExample Third-Example-Success-Response-DELETE:
	    HTTP/1.1 200 OK
	    {
	     "data":"The slice NSI_1 successfully removed"
	     "elapsed-time":"0:00:54.056207"
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
@app.route('/nssi/<string:nsi_name>/<string:nssi_name>', methods=['GET', 'POST', 'DELETE'])
@app.route('/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>')
def network_sub_slice(nsi_name=None, nssi_name=None, nssi_key=None):
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiAll

	@api {get}  /nssi/all List all deployed NSSI
	@apiDescription get the list of all deployed subslices


	@apiExample {curl} First-Example-Usage:
	     curl -i http://127.0.0.1:5000/nssi/all

	@apiSuccessExample First-Example-Success-Response:
	    HTTP/1.1 200 OK
	    {
	        To add example here
	    }
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssi

	@apiDescription It is alias to /nssi
	@api {get}  /nssi  List all deployed NSSI [Alias]
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiName

	@apiDescription get the context of all the subslices attached to certain slice
	@api {get}  /nssi/<string:nsi_name> Get context of all slices
	@apiParam {string} nsi_name Name of slice
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiNameNssiName

	@apiDescription get the context of certain subslice attached to specified slice
	@api {get}  /nssi/<string:nsi_name>/<string:nssi_name> Get context of certain nssi
	@apiParam {string} nsi_name Name of slice
	@apiParam {string} nssi_name Name of subslice
	"""
	
	"""
	@apiGroup GroupSubSlice
	@apiName GetNssiNsiNameNssiNameNssiKey

	@apiDescription get the context of certain entity fo certain subslcie attached to specified slice
	@api {get}  /nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key> Get context of certain entity
	@apiParam {string} nsi_name Name of slice
	@apiParam {string} nssi_name Name of subslice
	@apiParam {string="subslice_services","subslice_machines","subslice_relations"} nssi_key  Name of certain entity
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
	@api {get}  /es List all index-pages
	@apiDescription get/delete the list of all index-pages in elasticsearch
	@apiExample {curl} Example-Usage:
		 curl -i http://127.0.0.1:5000/es

	@apiDescription Get the list of all index-pages in elasticsearch database
	@apiSuccessExample Example-Success-Response-GET:
		HTTP/1.1 200 OK

			{
			   "data":
			   [
				".monitoring-es-6-2019.02.28",
				"jox-config",
				"nsi_1",
				"nssi_1",
				"nssi_2",
				"slice_keys_nsi_1",
				"slice_keys_tmp_nsi_1",
				"slice_monitor_nssi_1",
				"slice_monitor_nssi_2"
				],
			"elapsed-time": "0:00:00.021460"
			}

   """
	"""
	@apiGroup GroupElasticsearch
	@apiName DeleteEs
	@api {delete}  /es Delete all index-pages
	@apiDescription Delete of all index-pages from elasticsearch database
	@apiExample {curl} Example-Usage-DELETE:
		 curl -i http://127.0.0.1:5000/es -XDELETE
	@apiSuccessExample Example-Success-Response-DELETE:
		HTTP/1.1 200 OK

			{
				Example here
			}
	"""
	"""
	@apiGroup GroupElasticsearch
	@apiName GetEsIndexPgae
	@api {get}  /es/<string:es_index_page> Get index-page
	@apiDescription Get index-page from elasticsearch

	@apiParam {string} es_index_page name of index-page

	@apiExample {curl} Example-Usage-GET:
		 curl -i http://127.0.0.1:5000/es/jox-config

	@apiSuccessExample Example-Success-Response-GET:
		HTTP/1.1 200 OK
		{
				"data": {
					"RBMQ_SERVER_IP": "localhost",
					"RBMQ_SERVER_PORT": 15672,
					"RBMQ_config": {
						"RBMQ_PASSWORD": "guest",
						"RBMQ_QUEUE": "QueueJox",
						"RBMQ_SERVER_IP": "localhost",
						"RBMQ_SERVER_PORT": 1234,
						"RBMQ_USER": "guest"
					},
					"_Comment": "default slice should be in yaml format",
					"authors-list": [
						{
							"email": "firstname.lastname@eurecom.fr",
							"name": "firstname lastname"
						}
					],
					"clouds-list": [
						{
							"cloud-name": "localhost",
							"description": "local environment accordig to ~/.juju/environments.yaml file"
						}

					}
				},
				"elapsed-time": "0:00:00.015391"
			}
	"""
	"""

	@apiGroup GroupElasticsearch
	@apiName DeleteEsIndexPgae
	@api {delete}  /es/<string:es_index_page> get index-page
	@apiExample {curl} Example-Usage-DELETE:
		 curl -i http://127.0.0.1:5000/es/jox-config -XDELETE

	@api {delete}  /es/<string:es_index_page> Delete index-page
	@apiDescription Delete index page from elasticsearch
	@apiSuccessExample Example-Success-Response-DELETE:
		HTTP/1.1 200 OK

			{
			"data": "The index jox-config is successfully removed from elasticsearch",
			"elapsed-time": "0:00:00.064590"
			}


	"""
	"""
	@apiGroup GroupElasticsearch
	@apiName GetEsIndexPgaeKeyVal

	@api {get}  /es/<string:es_index_page>/<string:es_key> Get a key of index-page
	@apiDescription get certain key of certain index-page from elasticsearch

	@apiParam {string} es_index_page name of index-page
	@apiParam {string} es_key key to get from the indexpage es_index_page

	@apiExample {curl} Example-Usage:
		 curl -i http://127.0.0.1:5000/es/jox-config/RBMQ_config

	@apiSuccessExample Example-Success-Response:
		HTTP/1.1 200 OK
		{
			{
			"data": {
				"RBMQ_PASSWORD": "guest",
				"RBMQ_QUEUE": "QueueJox",
				"RBMQ_SERVER_IP": "localhost",
				"RBMQ_SERVER_PORT": 1234,
				"RBMQ_USER": "guest"
					},
			"elapsed-time": "0:00:00.578988"
			}
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

	@api {get}  /monitor/nsi/<string:nsi_name> NSI all
	@apiParam {String} nsi_name NSI name
	@apiExample {curl} Example usage:
	    curl http://localhost:5000/monitor/nsi/oai-epc

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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


	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "The slice oai-ran does not exists",
	      "elapsed-time": "0:00:00.002289"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetNssiMonitorAll

	@api {get}  /monitor/nsi/<string:nsi_name>/<string:nssi_name>> NSSI all

	@apiParam {String} nsi_name NSI name
	@apiParam {String} nssi_name NSSI name

	@apiExample {curl} Example usage:
	      curl http://localhost:5000/monitor/nsi/oai-epc/nssi_2

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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


	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
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

	@api {get}  /monitor/service/<string:nsi_name> NSI services

	@apiParam {String} nsi_name NSI name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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


	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetNssiMonitorServices

	@api {get}  /monitor/nsi/service/<string:nsi_name>/<string:nssi_name> NSSI services

	@apiParam {String} nsi_name NSI name
	@apiParam {String} nssi_name NSSI name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/service/oai-epc/nssi_2

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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


	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
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

	@api {get}  /monitor/nsi/machine/<string:nsi_name> NSI machines

	@apiParam {String} nsi_name NSI name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/machine/oai-epc

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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

	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetNssiMonitorMachines

	# @api {get}  /monitor/nsi/machine/<string:nsi_name>/<string:nssi_name>  NSSI machines

	@apiParam {String} nsi_name NSI name
	@apiParam {String} nssi_name NSSI name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/machine/oai-epc/nssi_1

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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
	                    "nss_id": "oai-epc",
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
	                    "nss_id": "oai-epc",
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

	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
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

	@api {get}  /monitor/nsi/relation/<string:nsi_name> NSI requirements

	@apiParam {String} nsi_name NSI name

	@apiExample {curl} Example usage:
	      curl http://localhost:5000/monitor/relation/oai-epc

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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


	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetNssiMonitorRequirements

	@api {get}  /monitor/nsi/relation/<string:nsi_name>/<string:nssi_name>  NSSI requirements

	@apiParam {String} nsi_name NSI name
	@apiParam {String} nssi_name NSSI name

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/relation/oai-epc/nssi_1

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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


	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
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
def monitor_juju(juju_key_val=None):
	"""
	@apiGroup Monitoring
	@apiName GetJujuMonitorAll

	@api {get}  /monitor/juju Juju all

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/juju

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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

	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetJujuMonitorServices

	@api {get}  /monitor/juju/<string:juju_entity> Juju services


	@apiExample {curl} Example usage:
	        curl http://localhost:5000/monitor/juju/applications

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
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

	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetJujuMonitorMachines

	@api {get}  /monitor/juju/<string:juju_entity> Juju machines

	@apiParam {String} juju_entity machines

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/juju/machines

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
	    {
	    "data": {
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
	      },
	      "elapsed-time": "0:00:00.135307"
	    }

	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
	    }
	"""
	
	"""
	@apiGroup Monitoring
	@apiName GetJujuMonitorRequirements

	@api {get}  /monitor/juju/<string:juju_entity> Juju machines

	@apiParam {String} juju_entity machines

	@apiExample {curl} Example usage:
	     curl http://localhost:5000/monitor/juju/relations

	@apiSuccess {String} data The required informations.
	@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
	@apiSuccessExample Success-Response:
	    HTTP/1.1 200 OK
	    {
	      "data": "The relations is not supported yet",
	      "elapsed-time": "0:00:00.705974"
	    }

	@apiError {String} data The required infromation can not be found
	@apiError {String} elapsed-time  The elapsed time to get the required the information.
	@apiErrorExample Error-Response:
	    HTTP/1.1 404 Not Found
	    {
	      "data": "Ad add example herer",
	      "elapsed-time": "to add example here"
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
	app.run(host=listOfTasks.gv.FLASK_SERVER_IP,
	        port=listOfTasks.gv.FLASK_SERVER_PORT,
	        debug=listOfTasks.gv.FLASK_SERVER_DEBUG)




if __name__ == '__main__':
	run()

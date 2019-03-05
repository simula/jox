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
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
dir_parent_path = os.path.dirname(os.path.abspath(__file__ + "/mnt"))

import logging
import tasks
import json
from flask import Flask, request,jsonify
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
            "request-type": None, # get, post; delete
            "parameters":{
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
    
    @apiExample {curl} Example usage:
         curl -i http://127.0.0.1:5000/

    @apiSuccessExample Success-Response:
        HTTP/1.0 200 OK
        {
        Welcome to JOX!
        To get the list of the capabilities and jox configuration, use the following
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
    "jox":{
        "/jox": "return jox configuration and the list of the capabilities",
        "/list": {"1":"return the list of all files in formation .yaml, .yaml and .json",
                  "2": "example: curl  http://127.0.0.1:5000/list; return the list in the default directory",
                  "3": "example: curl  http://127.0.0.1:5000/list?url=/home/arouk/Documents/slice_template; return the list in slice_template directory",
                },
        "/ls":"alias to /list",
        "/show/<string:nsi_name>":{"1":"show the content of the template nsi_name",
                  "2": "example: curl  http://127.0.0.1:5000/show/exmple_template.yaml; show the slice template exmple_template.yaml in the default directory",
                  "3": "example: curl  http://127.0.0.1:5000/list?url=/home/arouk/Documents/slice_template/exmple_template.yaml; show the slice template exmple_template.yaml in the given directory",
                },
        },
    "slice":{
            "/nsi/all":"GET; get the context of all deployed slices",
            "/nsi":"GET ; alias to /nsi/all",
            "/nsi/<string:nsi_name>":{
                "GET":"get context of already deployed slice nsi_name",
                "POST":"deploy/update slice nsi_name",
                "DELET":"delete the slice nsi_name",
            },
    },
    "sub-slice":{
            "/nssi/all":{
                "GET":"get the context of all subslices"
            },
            "/nssi":"alias to /nssi/all",
            "/nssi/<string:nsi_name>":{
                "GET":"get context of the subslices attached to the slice nsi_name",
                "POST":"Not supported",
                "DELET":"Not supported",
            },
            "/nssi/<string:nsi_name>/<string:nssi_name>":{
                "GET":"get context of the subslice nssi_name attached to the slice nsi_name",
                "POST":"Not supported",
                "DELET":"Not supported",
            },
            "/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>":{
                "GET":"get crtain entity nssi_key of subslice nssi_name attached to the slice nsi_name",
                "POST":"Not supported",
                "DELET":"Not supported",
            },
    },
    "elasticsearch":{
        "/es":{
                "GET":"get all the index-pages in elasticsearch",
                "POST":"Not supported",
                "DELET":"Delete all the index-pages in elasticsearch",
            },
        "/es/<string:es_index_page>":{
                "GET":"get the content of the index-page es_index_page from  elasticsearch",
                "POST":"save the content of the index-page es_index_page to elasticsearch",
                "DELET":"Delete the index-page es_index_page from elasticsearch",
            },
        "/es/<string:es_index_page>/<string:es_key>":{
                "GET":"get certain index es_key from the index-page es_index_page from elasticsearch",
                "POST":"Not supported",
                "DELET":"Not supported",
            },
    },
    "monitoring":{
        "slice&sub-sclice":{
            "/monitor/nsi":
                "get monitoring information on all the deployed slices",
            "/monitor/nsi/<string:nsi_name>":
                "get monitoring information on the deployed slice nsi_name",
            "/monitor/nsi/<string:nsi_name>/<string:nssi_name>":
                "get monitoring information on the subslice nssi_name from the deployed slice nsi_name",
            "/monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>":
                "get monitoring information on certain entity of the the subslice nssi_name from the deployed slice nsi_name",
        },
        "service":{
            "/monitor/service/<string:nsi_name>":
                "get monitoring information on all services of the slice nsi_name",
            "/monitor/service/<string:nsi_name>/<string:nssi_name>":
                "get monitoring information on all services of the subslice nssi_name attached to the slice nsi_name",
            "/monitor/service/<string:nsi_name>/<string:nssi_name>/<string:service_name>":
                "get monitoring information on the service service_name of the subslice nssi_name attached to the slice nsi_name",
        },
        "machine":{
            "/monitor/machine/<string:nsi_name>":
                    "get monitoring information on all machines of the slice nsi_name",
            "/monitor/machine/<string:nsi_name>/<string:nssi_name>":
                "get monitoring information on all machines of the subslice nssi_name attached to the slice nsi_name",
            "/monitor/machine/<string:nsi_name>/<string:nssi_name>/<string:machine_name>":
                "get monitoring information on the machine service_name of the subslice nssi_name attached to the slice nsi_name",
        },
        "relation":{
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
                      "debug_level": 0,
                      "name": "error"
                    },
                    {
                      "color": "\\033[93m",
                      "debug_level": 1,
                      "name": "warn"
                    },
                    {
                      "color": "\\033[92m",
                      "debug_level": 2,
                      "name": "notice"
                    },
                    {
                      "color": "\\033[0m",
                      "debug_level": 3,
                      "name": "info"
                    },
                    {
                      "color": "\\033[0m",
                      "debug_level": 4,
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
    
    @api {get}  /list List templates
    @apiDescription get the list of all template (in format .yaml, .yml, and .json) in default directory or given directory
    
    @apiParam {path} full_path directory of the templates (Optional)
    
    @apiExample {curl} First-Example-Usage:
         curl -i http://127.0.0.1:5000/list
    
    @apiDescription get the list of all template in the default directory
    @apiSuccessExample First-Example-Success-Response:
        HTTP/1.0 200 OK
        {
          "elapsed-time": "0:00:00.004647",
          "list of templates in the directory None": [
            "default_slice_nssi2_1.yaml",
            "default_slice_nsi.yaml",
            "default_slice_nssi2_2.yaml",
            "default_slice_nssi_2.yaml",
            "default_slice_nsi.json",
            "default_slice_nsi2.yaml",
            "default_slice_nssi_1.yaml"
          ]
        }
    @apiDescription get the list of all template in the given directory /home/arouk/Documents/slice_templet
    @apiExample {curl} Second-Example-Usage:
         curl -i http://127.0.0.1:5000/list?url=/home/arouk/Documents
    
    @apiSuccessExample Second-Example-Success-Response:
        HTTP/1.0 200 OK
        {
          "data": [
            "default_slice_NSSI2_2.yaml",
            "default_slice_NSI2.yaml",
            "default_slice_NSSI2_1.yaml"
          ],
          "elapsed-time": "0:00:00.003740"
        }
    @apiErrorExample Second-Example-NoFound-Response:
        HTTP/1.0 404 NOT FOUND
        {
          "data": "The following path does not exist: /home/arouk/slice_template",
          "elapsed-time": "0:00:00.003495"
        }
    """
    
    """
    @apiGroup GroupJox
    @apiName GetJoxLs
    
    @api {get}  /ls List templates(alias)
    @apiDescription It is alias to /list
    """
    
    """
    @apiGroup GroupJox
    @apiName GetJoxShow

    @api {get}  /show/<string:nsi_name>?url=full_path Show the template
    @apiDescription Show the content of the file nsi_name, only the following formats are supported: .yaml, .yml, and .json
    
    @apiParam {string} nsi_name name of the file(template)
    @apiParam {path} [full_path=None] full_path directory of the templates
    
    @apiDescription example usage for to show the template in default directory
    @apiExample {curl} First-Example-Usage:
         curl -i http://127.0.0.1:5000/show/slice_template1.yaml
    @apiSuccessExample First-Example-Success-Response:
        HTTP/1.0 200 OK
        {
            //  To add example here
        }
    
    @apiDescription example usage for to show the template in specified directory
    @apiExample {curl} Second-Example-Usage:
         curl -i http://127.0.0.1:5000/show/slice_template1.yaml?url=/home/arouk/Documents
    @apiSuccessExample Second-Example-Success-Response:
        HTTP/1.0 200 OK
        {
            // To add example here
        }
    @apiExample {curl} Third-Example-Usage:
         curl -i http://127.0.0.1:5000/show/slice_template3.yaml?url=/home/arouk/Documents
    @apiSuccessExample Thirds-Example-Success-Response:
        HTTP/1.0 404 NOT FOUND
        {
          "data": "The following file does not exist: default_slice_NSI23.yaml",
          "elapsed-time": "0:00:00.002719"
        }
    """
    
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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
@app.route('/nsi/all', methods=['GET'])
@app.route('/nsi', methods=['GET',   'PUT'])
@app.route('/nsi/<string:nsi_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def network_slice(nsi_name=None):
    """
    @apiGroup GroupSlice
    @apiName GetNsiAll
    
    @api {get}  /nsi/all List deployed NSIs
    @apiDescription get the list of all template (in format .yaml, .yml, and .json) in default directory or given directory
    
    @apiParam {path} full_path directory of the templates (Optional)
    
    @apiExample {curl} First-Example-Usage:
         curl -i http://127.0.0.1:5000/list
    
    @apiDescription get the list of all deployed slices
    @apiSuccessExample First-Example-Success-Response:
        HTTP/1.0 200 OK
        {
            To add example here
        }
    @apiDescription get the list of all template in the given directory /home/arouk/Documents/slice_templet
    @apiExample {curl} Second-Example-Usage:
         curl -i http://127.0.0.1:5000/list?url=/home/arouk/Documents/slice_templet
    
    @apiSuccessExample Second-Example-Success-Response:
        HTTP/1.0 200 OK
        {
            To add example here
        }
    """

    """
    @apiGroup GroupSlice
    @apiName GetNsi

    @apiDescription It is alias to /nsi/all
    @api {get}  /nsi List deployed NSI(alias)
    """
    """
    @apiGroup GroupSlice
    @apiName PutNsi

    @apiDescription It allows you to deploy a slice remotely, where all the templates of nsi and nssi should be ziped in one file
    @api {put}  /nsi Deploy slice remotely
    
    
    @apiParam {string} zip_file full path where the zip file exists
    
    @apiExample {curl} First-Example-Usage:
         curl -i -X PUT http://127.0.0.1:5000/nsi --upload-file /path/to/zip_file
    
    @apiSuccessExample First-Example-Success:
        HTTP/1.0 200 OK
        {
            // To add example here
        }
    """

    """
    @apiGroup GroupSlice
    @apiName GetNsiNsiName

    @api {get}{post}{delete}  /nsi/<string:nsi_name> NSI management
    @api {post} /nsi/<string:nsi_name> NSI management
    @api {delete}  /nsi/<string:nsi_name> NSI management
    @apiDescription get the context, deployed, and delete the slice nsi_name

    @apiParam {string} nsi_name name of the slice

    @apiExample {curl} First-Example-Usage:
         curl -i -X GET http://127.0.0.1:5000/nsi/slice_name
         curl -i -X POST http://127.0.0.1:5000/nsi/default_slice.yaml
         curl -i -X DELET http://127.0.0.1:5000/nsi/slice_name
    """

    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
    enquiry["request-uri"] = str(request.url_rule)
    enquiry["request-type"] = (request.method).lower()
    enquiry["parameters"]["nsi_name"] = nsi_name
    nsi_found = True
    nssi_found = True
    save_template_success = True
    if (enquiry["request-type"] == "put"):
        files = request.data
        try:
            with open('/proc/mounts', 'r') as f:
                mounts = [line.split()[1] for line in f.readlines()]
        
            if listOfTasks.gv.STORE_DIR in mounts:
                listOfTasks.gv.STORE_DIR = ''.join([listOfTasks.gv.STORE_DIR, '/'])
            else:
                message = "The directory {} is not mounted, and thus the templates can not be saved. You should firstly mount the directory {} \n\n".format(
                    listOfTasks.gv.STORE_DIR, listOfTasks.gv.STORE_DIR)
                logger.error(message)
                return message, 400
        except:
            message = "The directory {} is not mounted, and thus the templates can not be saved. You should firstly mount the directory {}  \n\n".format(listOfTasks.gv.STORE_DIR, listOfTasks.gv.STORE_DIR)
            logger.error(message)
            return message, 400
        
        tar_file = open_tar_gz(files, enquiry)
        enquiry = tar_file[0]
        nsi_found = tar_file[1]
        nssi_found = tar_file[2]
        save_template_success = tar_file[3]
        message = tar_file[4]
    if nsi_found and nssi_found and save_template_success:
        try:
            logger.info(message)
            logger.debug(message)
        except:
            pass
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
    else:
        return message, 400

@app.route('/nssi/all')
@app.route('/nssi')# alias to the previous one
@app.route('/nssi/<string:nsi_name>')
@app.route('/nssi/<string:nsi_name>/<string:nssi_name>', methods=['GET', 'POST', 'DELETE'])
@app.route('/nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>')
def network_sub_slice(nsi_name=None, nssi_name=None, nssi_key=None):
    """
    @apiGroup GroupSubSlice
    @apiName GetNssiAll
    
    @api {get}  /nssi/all List deployed NSSIs
    @apiDescription get the list of all deployed subslices
    
    
    @apiExample {curl} First-Example-Usage:
         curl -i http://127.0.0.1:5000/nssi/all
    
    @apiSuccessExample First-Example-Success-Response:
        HTTP/1.0 200 OK
        {
            To add example here
        }
    """

    """
    @apiGroup GroupSubSlice
    @apiName GetNssi

    @apiDescription It is alias to /nssi
    @api {get}  /nssi List deployed NSSIs(alias)
    """

    """
    @apiGroup GroupSubSlice
    @apiName GetNssiNsiName

    @apiDescription get the context of all the subslices attached to certain slice
    @api {get}  /nssi/<string:nsi_name> Context of subslices
    @apiParam {string} nsi_name Name of slice
    """
    
    """
    @apiGroup GroupSubSlice
    @apiName GetNssiNsiNameNssiName

    @apiDescription get the context of certain subslice attached to specified slice
    @api {get}  /nssi/<string:nsi_name>/<string:nssi_name> Context of specific subslice
    @apiParam {string} nsi_name Name of slice
    @apiParam {string} nssi_name Name of subslice
    """

    """
    @apiGroup GroupSubSlice
    @apiName GetNssiNsiNameNssiNameNssiKey

    @apiDescription get the context of certain entity fo certain subslcie attached to specified slice
    @api {get}  /nssi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key> Context of certain entity of specific subslice
    @apiParam {string} nsi_name Name of slice
    @apiParam {string} nssi_name Name of subslice
    @apiParam {string="services","machines","relations"} nssi_key  Name of certain entity
    """

    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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

    @api {get, delete}  /es List index-pages
    @apiDescription get/delete the list of all index-pages in elasticsearch


    @apiExample {curl} Example-Usage:
         curl -i http://127.0.0.1:5000/es

    @apiDescription get the list of all deployed slices
    @apiSuccessExample Example-Success-Response:
        HTTP/1.0 200 OK
        {
            To add example here
        }
    """
    """
    @apiGroup GroupElasticsearch
    @apiName GetEsIndexPgae

    @api {get, post, delete}  /es/<string:es_index_page> Manage index-page
    @apiDescription get/save/delete index-page from elasticsearch

    @apiParam {string} es_index_page name of index-page
    
    @apiExample {curl} Example-Usage:
         curl -i http://127.0.0.1:5000/es/<string:es_index_page>

    @apiDescription get the list of all deployed slices
    @apiSuccessExample Example-Success-Response:
        HTTP/1.0 200 OK
        {
            To add example here
        }
    """
    """
    @apiGroup GroupElasticsearch
    @apiName GetEsIndexPgaeKeyVal

    @api {get}  /es/<string:es_index_page>/<string:es_key> Get key of index-page
    @apiDescription get certain key of certain index-page from elasticsearch

    @apiParam {string} es_index_page name of index-page
    @apiParam {string} es_key key to get from the indexpage es_index_page

    @apiExample {curl} Example-Usage:
         curl -i http://127.0.0.1:5000/es/<string:es_index_page>/<string:es_key>

    @apiDescription get the list of all deployed slices
    @apiSuccessExample Example-Success-Response:
        HTTP/1.0 200 OK
        {
            To add example here
        }
    """
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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


"""
@apiGroup Monitoring
@apiName GetNsiMonitor

@api {get}  /monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key> get monitoring information of certain entity of NSSI

@apiParam {String} nsi_name NSI name
@apiParam {String} nssi_name NSSI name
@apiParam {String} nssi_key Required entity of specified NSSI

@apiExample {curl} Example usage:
     curl -i http://127.0.0.1:5000/monitor/nsi/nsi1/nssi1/
     
@apiSuccess {String} data The required informations.
@apiSuccess {String} elapsed-time  The elapsed time to get the required the information.
@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
      "data": "to add example herer",
      "elapsed-time": "to add example here"
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
@app.route('/monitor/nsi')
@app.route('/monitor/nsi/<string:nsi_name>')
@app.route('/monitor/nsi/<string:nsi_name>/<string:nssi_name>')
@app.route('/monitor/nsi/<string:nsi_name>/<string:nssi_name>/<string:nssi_key>')
def monitor_nssi(nsi_name=None, nssi_name=None, nssi_key=None):
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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
    if juju_key_val is None:
        juju_key_val = 'all'
    enquiry = standard_reqst
    current_time = datetime.datetime.now()
    enquiry["datetime"] = str(current_time)
    enquiry["template_directory"] = request.args.get('url')
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
    return "\n !!!!"  + repr(error)

@app.errorhandler(404)
def page_not_found(e):
    return "page not found ".format(e), 404

def run():
    app.run(host=listOfTasks.gv.FLASK_SERVER_IP,
            port=listOfTasks.gv.FLASK_SERVER_PORT,
            debug=listOfTasks.gv.FLASK_SERVER_DEBUG)
def open_tar_gz(files, enquiry):
    nsi_found = False
    nssi_found = False
    save_template_success = True
    try:
        with tarfile.open(mode='r', fileobj=io.BytesIO(files)) as tar:
            for tarinfo in tar:
                tarname = tarinfo.name
                if str(tarname).endswith('yaml') or str(tarname).endswith('yaml'):
                    if 'nsi' in str(tarname):
                        nsi_found = True

                        nsi_name_temp = tarname.split('/')
                        file_name = nsi_name_temp[len(nsi_name_temp) - 1]
                        nsi_dir = '/'.join(nsi_name_temp[x] for x in range(len(nsi_name_temp) - 1))
                        nsi_dir = nsi_dir + '/'
                        nsi_dir = ''.join([listOfTasks.gv.STORE_DIR, nsi_dir])
                        
                        enquiry["parameters"]["nsi_name"] = file_name
                        enquiry["parameters"]["nsi_directory"] = nsi_dir
                        enquiry["request-uri"] = '/nsi/<string:nsi_name>'
                    if 'nssi' in str(tarname):
                        nssi_found = True

                        nsi_name_temp = tarname.split('/')
                        file_name = nsi_name_temp[len(nsi_name_temp) - 1]
                        nssi_dir = '/'.join(nsi_name_temp[x] for x in range(len(nsi_name_temp) - 1))
                        nssi_dir = nssi_dir + '/'
                        nssi_dir = ''.join([listOfTasks.gv.STORE_DIR, nssi_dir])
                        
                        enquiry["parameters"]["nssi_directory"] = nssi_dir
                        
            
            tar.extractall(listOfTasks.gv.STORE_DIR)
        message = "The package was successfuly exctracted"
    except Exception as ex:
        message = "Error while opening the zip file\n {}\n".format(ex)
        

    return [enquiry, nsi_found, nssi_found, save_template_success, message]

if __name__ == '__main__':
  run()

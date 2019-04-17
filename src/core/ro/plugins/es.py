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

from elasticsearch import Elasticsearch
import time
import logging
import json
import os
os.environ['PYTHONASYNCIODEBUG'] = '1'
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('jox.es')

class JESearch(object):
    def __init__(self, els_host, els_port, els_log_level=None):
        self.enable = False
        self.host = els_host
        self.port = els_port
        self.logger = logging.getLogger('jox.es')
        self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
    
        if els_log_level:
            if els_log_level == 'debug':
                self.logger.setLevel(logging.DEBUG)
            elif els_log_level == 'info':
                self.logger.setLevel(logging.INFO)
            elif els_log_level == 'warn':
                self.logger.setLevel(logging.WARNING)
            elif els_log_level == 'error':
                self.logger.setLevel(logging.ERROR)
            elif els_log_level == 'critic':
                self.logger.setLevel(logging.CRITICAL)
            else:
                self.logger.setLevel(logging.INFO)

    def ping(self):
        
        if not self.es.ping():
            self.logger.error("Elasticsearch: connection Failed")
            self.logger.debug("Elasticsearch: connection Failed")
            return False
        else:
            self.logger.info("Elasticsearch: connection Success")
            self.logger.debug("Elasticsearch: connection Success")
            self.enable = True
            return True
    def del_index_from_es(self, index_page):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
            return [False, message]
        try:
            list_index = self.get_all_indices_from_es()
            if list_index[0]:
                list_index = list_index[1]
                if index_page in list_index:
                    self.logger.debug("es -->> Deleting index ".format(index_page))
                    self.es.indices.delete(index=index_page, ignore=[400, 404], )
                    message = "The index {} is successfully removed from elasticsearch".format(index_page)
                    self.logger.info(message)
                    return [True, message]
                else:
                    message = "The index {} does not exist in elasticsearch".format(index_page)
                    self.logger.warning(message)
                    self.logger.info(message)
                    return [False, message]
            else:
                return list_index
        except Exception as ex:
            message = "Error while trying to delete {}: {}".format(index_page, ex)
            self.logger.error(message)
            return [False, message]
    def set_json_to_es(self, index_page, json_object):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
            return False
        try:
            get_page = self.get_source_index(index_page)
            if get_page[0]:
                self.del_index_from_es(index_page)
            self.es.indices.create(index=index_page)
            json_data = json.dumps(json_object)
            self.es.index(index=index_page, doc_type='post', id=1, body=json.loads(json_data))
            message = "The file {} is successfully Loaded to ES".format(index_page)
            self.logger.debug(message)
            self.logger.info(message)
            return True
        except Exception as ex:
            message = "The file {} is not Loaded to ES due to {}".format(index_page, ex)
            self.logger.debug(message)
            self.logger.info(message)
            return False
            # raise ex

    def update_index_with_content(self, index_page, container_type, data):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
        
        self.es.update(index=index_page, doc_type='post', id=1,  # Push the container with updates
                  body={'doc': {container_type: data}}, retry_on_conflict=0)
        
    def update_index_key(self, index_page, container_type, container_name, leaf_key, leaf_value):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
        try:
            slice_data = self.get_json_from_es(index_page, container_type)
            if slice_data[0]:
                slice_data = slice_data[1]
                for machines in range(len(slice_data)):  # Update the container
                    machines_list = slice_data[machines]
                    machine = list(machines_list.keys())
                    for num in range(len(machine)):
                        if machine[num] == container_name:
                            slice_data[machines][container_name][0][leaf_key] = leaf_value
                self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
                self.es.update(index=index_page, doc_type='post', id=1,  # Push the container with updates
                            body={'doc': {container_type: slice_data}}, retry_on_conflict=0)
    
                
                message = "The index {} is successfully updated".format(index_page)
                self.logger.info(message)
                self.logger.debug(message)
                return message
            else:
                return slice_data[1]
        except Exception as ex:
            self.logger.error(ex)
            message = "The index {} can not be updated".format(index_page)
            self.logger.info(message)
            self.logger.debug(message)
            # raise ex

    def get_all_indices_from_es(self):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
            return [False, message]
        
        indices = list()
        for index in self.es.indices.get('*'):
            indices.append(index)
        return [True, indices]
    def delete_all_indices_from_es(self):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
            return [False, message]
            
        message = "The following indexes can not be deleted: "
        all_deleted = True
        for index in self.es.indices.get('*'):
            try:
                self.es.indices.delete(index=index, ignore=[400, 404], )
            except:
                all_deleted = False
                message = "{}, {}".format(message, index)
        if all_deleted:
           message = "All the indexes are successfully deleted from es"
        return [all_deleted, message]
    def get_source_index(self, index_page):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
            return [False, message]
        try:
            return [True, (self.es.get(index_page, doc_type='post', id=1)['_source'])]
        except Exception as ex:
            message = "Error while getting the source of the index of {} from elasticsearch: {}".format(index_page, ex)
            self.logger.error(message)
            return [False, message]

    def get_json_from_es(self, index_page, key):
        try:
            self.es = Elasticsearch([{'host': self.host, 'port': self.port, 'use_ssl': False}])
        except:
            message = "Error while trying to connect to Elasticsearch"
            self.logger.error(message)
            self.logger.debug(message)
            return [False, message]
        try:
            response = self.es.search(index=index_page, doc_type="post", _source_include=key)
            for doc in response['hits']['hits']:
                if key not in doc['_source']:
                    message = "The key {} does not exist in the index {}".format(key, index_page)
                    self.logger.debug(message)
                    self.logger.critical(message)
                    return [False, message]

                else:
                    message = "successfully got the key {} in the index {}".format(key, index_page)
                    self.logger.info(message)
                    return [True, doc['_source'][key]]
        except Exception as ex:
            message = "Could not find the key {} in {}".format(key, index_page)
            self.logger.info(message)
            return [False, message]

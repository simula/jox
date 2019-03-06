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

__author__ = 'Eurecom'
__date__ = "11-January-2019"
__version__ = '1.0'
__maintainer__ = 'Osama Arouk, Navid Nikaein, Kostas Kastalis, and Rohan Kharade'
__email__ = 'contact@mosaic5g.io'
__description__ = "This responsible for managine the available resources"

from src.core.ro.plugins import es
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as els_exceptions
import datetime
import logging
from juju.model import Model
from juju import utils
import json
logger = logging.getLogger('jox.jmodel')
import src.common.config.gv as gv

if gv.LOG_LEVEL == 'debug':
    logger.setLevel(logging.DEBUG)
elif gv.LOG_LEVEL == 'info':
    logger.setLevel(logging.INFO)
elif gv.LOG_LEVEL == 'warn':
    logger.setLevel(logging.WARNING)
elif gv.LOG_LEVEL == 'error':
    logger.setLevel(logging.ERROR)
elif gv.LOG_LEVEL == 'critic':
    logger.setLevel(logging.CRITICAL)
else:
    logger.setLevel(logging.INFO)
    
keys_local = {}   # locally maintaining keys for slice component's context matching

def update_machine_monitor_state(jesearch, machine_id, machine_state, slice_id):
    nssid, container_name, start_time = check_nssid_with_mid(jesearch, machine_id, 'machine_keys', slice_id)
    if (not nssid) and (not nssid) and (not nssid):
        pass
    else:
        end_time = (datetime.datetime.now()).isoformat()
        launch_time = (datetime.datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%S.%f'))-(datetime.datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S.%f'))
        update_index_key(jesearch, 'slice_monitor_'+ nssid.lower(), "machine_status", container_name, machine_state,
                         str(launch_time), slice_id)

def update_service_monitor_state(jesearch , service_name, service_state, slice_id):
    nssid, start_time = check_nssid_with_service(jesearch, service_name, slice_id)
    end_time = (datetime.datetime.now()).isoformat()
    
    service_time = (datetime.datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%S.%f'))-(datetime.datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S.%f'))
    update_index_key(jesearch, 'slice_monitor_'+ nssid.lower(), "service_status", service_name, service_state,
                        str(service_time), slice_id)

def check_nssid_with_mid(jesearch, machine_id, container_type, slice_id):
    for nsi in range(len(keys_local.keys())):
        nsi_list = list(keys_local)
        if nsi_list[nsi] == slice_id:
            machine_key=keys_local[slice_id]

            for data in range(len(machine_key)):
                service_name = list((machine_key[data]).keys())[0]
                if machine_key[data][service_name][0]['juju_mid'] == str(machine_id):
                    nssid = machine_key[data][service_name][0]['nssi_id']
                    container_name = service_name
                    start_time = machine_key[data][service_name][0]['date']
                    return [nssid, container_name, start_time]
        else :
            return [False, False, False]
    machine_key = jesearch.get_json_from_es("slice_keys_"+slice_id.lower(), container_type)
    # machine_key = es.get_json_from_es(es_host, es_port, "slice_keys_"+slice_id.lower(), container_type)
    if machine_key[0]:
        machine_key = machine_key[1]
        keys_local.update({slice_id: machine_key})
        for data in range(len(machine_key)):
            service_name = list((machine_key[data]).keys())[0]
            if machine_key[data][service_name][0]['juju_mid'] == str(machine_id):
                nssid = machine_key[data][service_name][0]['nssi_id']
                container_name = service_name
                start_time = machine_key[data][service_name][0]['date']
                return nssid, container_name, start_time
    else:
        message = "The key {} does not exist in the page {}".format(container_type, "slice_keys_"+slice_id.lower())
        logger.error(message)

def check_nssid_with_service(jesearch, app_name, slice_id):
    for nsi in range(len(keys_local.keys())):
        nsi_list = list(keys_local)
        if nsi_list[nsi] == slice_id:
            machine_key=keys_local[slice_id]

            for data in range(len(machine_key)):
                service_Name = list((machine_key[data]).keys())[0]
                if service_Name == str(app_name):
                    nssid = machine_key[data][service_Name][0]['nssi_id']
                    start_time = machine_key[data][service_Name][0]['date']
                    return nssid, start_time
            else:
                pass
    service_key = jesearch.get_json_from_es("slice_keys_"+slice_id.lower(), 'machine_keys')
    if service_key[0]:
        service_key = service_key[1]
        keys_local.update({slice_id: service_key})
        for data in range(len(service_key)):
            service_name = list((service_key[data]).keys())[0]
            if service_name == str(app_name):
                nssid = service_key[data][service_name][0]['nssi_id']
                start_time = service_key[data][service_name][0]['date']
                return nssid, start_time

def update_index_key(jesearch, index_page, container_type, container_name, leaf_key, leaf_value, slice_id):
    try:
        
        # ES = Elasticsearch([{'host': host, 'port': port, 'use_ssl': False}])
        # slice_data = es.get_json_from_es(host, port, index_page, container_type)
        slice_data = jesearch.get_json_from_es(index_page, container_type)
        if slice_data[0]:
            slice_data = slice_data[1]
            for machines in range(len(slice_data)):
                machines_list = slice_data[machines]
                machine = list(machines_list.keys())
                for num in range(len(machine)):
                    if machine[num] == container_name:
                        if slice_data[machines][container_name][0][leaf_key] == "0" and leaf_key:
                            if leaf_key == 'maintenance':
                                waiting_time=slice_data[machines][container_name][0]['waiting']
                                maintenance=(datetime.datetime.strptime(leaf_value,'%H:%M:%S.%f') -
                                    datetime.datetime.strptime(waiting_time,'%H:%M:%S.%f'))
                                slice_data[machines][container_name][0][leaf_key] = str(maintenance)
                            elif leaf_key == 'requirement_wait':
                                
                                maintenance=slice_data[machines][container_name][0]['maintenance']
                                waiting_time=slice_data[machines][container_name][0]['waiting']
                                wait_time=(datetime.datetime.strptime(waiting_time,'%H:%M:%S.%f')-datetime.datetime.strptime("0:0:0.0",'%H:%M:%S.%f'))
                                if maintenance == '0':
                                    return
                                else:
                                    requirement_wait=(datetime.datetime.strptime(leaf_value,'%H:%M:%S.%f') -
                                        datetime.datetime.strptime(maintenance,'%H:%M:%S.%f')- wait_time)
                                    slice_data[machines][container_name][0][leaf_key] = str(requirement_wait)
                            elif leaf_key == 'error':
                                slice_data[machines][container_name][0][leaf_key] = "in_error_state"
                            elif  leaf_key == 'active_since':
                                slice_data[machines][container_name][0]['error'] = '0'
                                slice_data[machines][container_name][0][leaf_key] = str((datetime.datetime.now()).isoformat())
    
                            else:
                                slice_data[machines][container_name][0][leaf_key] = leaf_value
                            logger.info("Updating {} => {} state {} with value {} ".format(slice_id, container_name, leaf_key, slice_data[machines][container_name][0][leaf_key]))

                            # update_index_key(self, index_page, container_type, container_name, leaf_key, leaf_value):
                            jesearch.update_index_with_content(index_page, container_type, slice_data)
                            
                            # ES.update(index=index_page, doc_type='post', id=1,
                            #           body={'doc': {container_type: slice_data}},
                            #           retry_on_conflict=0)
                            if leaf_key == 'requirement_wait':
                                
                                slice_data = jesearch.get_json_from_es(index_page, "relation_status")
                                if slice_data[0]:
                                    slice_data = slice_data[1]
                                    slice_data[machines][container_name][0][leaf_key] = str(requirement_wait)
                                    
                                    jesearch.update_index_with_content(index_page, "relation_status", slice_data)
                                else:
                                    pass
                                # ES.update(index=index_page, doc_type='post', id=1,
                                #           body={'doc': {"relation_status": slice_data}},
                                #           retry_on_conflict=0)
        else:
            pass
    except els_exceptions.ConflictError:
        logger.critical("Other request is already modified updated the index")
    except Exception as ex:
        raise ex


async def get_juju_status(type):
    model = Model()
    await model.connect_current()
    if type == 'machines':
        juju_status_machines=(await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop)).machines
        return [True, juju_status_machines]
    elif type == 'applications':
        juju_status_apps=(await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop)).applications
        return [True, juju_status_apps]
    elif type == 'relations':
        juju_status_relations=(await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop)).relations
        juju_status_relations = "The relations is not supported yet"
        return [True, juju_status_relations]
    elif type == 'all':
        juju_status=(await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop))
        juju_status_relations = juju_status.relations
        juju_status_relations = "The relations is not supported yet"
        full_status=({'machines':[juju_status.machines],
                      'services':[juju_status.applications],
                      'relations':[juju_status_relations]})
        return [True, full_status]
    else:
        message = "The key {} is not supported. Only the following keys are supported: machines, applications, relations, all".\
            format(type)
        return [False, message]

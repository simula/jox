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

from elasticsearch import exceptions as els_exceptions
import datetime
import logging
from juju.model import Model
from juju import utils
import src.common.config.gv as gv

# keys_local = {}   # locally maintaining keys for slice component's context matching

class Monitor(object):
    def __init__(self):
        self.jesearch = None
        self.keys_local = {}
        self.logger = logging.getLogger('jox.monitor')
        if gv.LOG_LEVEL == 'debug':
            self.logger.setLevel(logging.DEBUG)
        elif gv.LOG_LEVEL == 'info':
            self.logger.setLevel(logging.INFO)
        elif gv.LOG_LEVEL == 'warn':
            self.logger.setLevel(logging.WARNING)
        elif gv.LOG_LEVEL == 'error':
            self.logger.setLevel(logging.ERROR)
        elif gv.LOG_LEVEL == 'critic':
            self.logger.setLevel(logging.CRITICAL)
        else:
            self.logger.setLevel(logging.INFO)

    def buil(self, jesearch):
        self.jesearch = jesearch

    def update_machine_monitor_state(self, machine_data, machine_state, current_state_machine, slice_id): # machine_state=add, change
        if self.jesearch.ping():
            if machine_state == "add":
                pass
            elif machine_state == "change":
                pass
            else:
                # TODO support monitoring information when removing machine
                message  = "The current state of the machine ({}) is not hold yet by JoX"
                self.logger.critical(message)
                self.logger.debug(message)

            end_time = (datetime.datetime.now()).isoformat()
            check_val = self.check_nssid_with_mid(machine_data['id'], 'machine_keys', current_state_machine, slice_id)
            if check_val[0] is not None:
                nssid = check_val[0]
                container_name = check_val[1]
                start_time = check_val[2]
                state_old = check_val[3]
                state_new = check_val[4]
                prepending_time = check_val[5]
                total_time = (datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')) \
                             - (datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f'))
                """
                update_key = "current_state"
                update_value = state_new
                self.update_index_key('slice_monitor_' + nssid.lower(), "machine_status", container_name,
                                      update_key,
                                      str(update_value), slice_id)

                update_key = "{}_{}".format(state_old, 'since')
                update_value = 0
                self.update_index_key('slice_monitor_' + nssid.lower(), "machine_status", container_name,
                                      update_key,
                                      str(update_value), slice_id)
                update_key = "{}_{}".format(state_old, 'time')
                update_value = total_time
                self.update_index_key('slice_monitor_' + nssid.lower(), "machine_status", container_name,
                                      update_key,
                                      str(update_value), slice_id)

                update_key = "{}_{}".format(state_new, 'since')
                update_value = end_time
                self.update_index_key('slice_monitor_' + nssid.lower(), "machine_status", container_name,
                                      update_key,
                                      str(update_value), slice_id)
                """
                # Just update all above values in one go, one es transaction
                if state_new == "started": # then update launch time and ipv4 address too
                    update_value = (datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')) \
                                   - (datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f')) \
                                   # + (datetime.datetime.strptime(prepending_time ,'%H:%M:%S.%f'))

                    container_data = {"current_state": str(state_new), ("{}_{}".format(state_old, 'since')): str(0),
                                      "{}_{}".format(state_old, 'time'): str(total_time),
                                      "{}_{}".format(state_new, 'since'):str(end_time),
                                      "{}_{}".format('launch', 'time'): str(update_value),
                                      "address_ipv4_public": machine_data['addresses'][0]['value']}
                else:
                    container_data = {"current_state": str(state_new),
                                      "{}_{}".format(state_old, 'since'): str(0),
                                      "{}_{}".format(state_old, 'time'): str(total_time),
                                      "{}_{}".format(state_new, 'since'):str(end_time)}

                self.update_slice_monitor_index('slice_monitor_' + nssid.lower(),
                                                                 "machine_status",
                                                                 container_name,
                                                                 container_data)

                """ # this is creating problem,  we have to avoid two consecutive es transaction with same container
                if prepending_time is not None:
                    update_key = "{}_{}".format('launch', 'time')
                    update_value = (datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')) \
                             - (datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f'))
                    self.update_index_key('slice_monitor_' + nssid.lower(), "machine_status", container_name,
                                          update_key,
                                          str(update_value), slice_id)
                """

    """
    def update_service_monitor_state(self, service_name, service_state, slice_id):
        if self.jesearch.ping():
            nssid, start_time = self.check_nssid_with_service(service_name, slice_id)
            end_time = (datetime.datetime.now()).isoformat()

            service_time = (datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')) - (
                datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f'))
            self.update_index_key('slice_monitor_' + nssid.lower(), "service_status", service_name, service_state,
                             str(service_time), slice_id)
    """
    def update_service_monitor_state(self, service_data, service_state, current_state_service, slice_id): # machine_state=add, change
        if self.jesearch.ping():
            if service_state == "unit":
                pass
            elif service_state == "change":
                pass
            else:
                # TODO support monitoring information when removing service
                message  = "The current state of the service ({}) is not hold yet by JoX"
                self.logger.critical(message)
                self.logger.debug(message)

            end_time = (datetime.datetime.now()).isoformat()
            check_val = self.check_nssid_with_service(service_data['application'], 'service_keys', current_state_service, slice_id)
            if check_val[0] is not None:
                nssid = check_val[0]
                container_name = check_val[1]
                start_time = check_val[2]
                state_old = check_val[3]
                state_new = check_val[4]
                waiting_time = check_val[5]
                total_time = (datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')) \
                             - (datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f'))

                container_data = {"current_state": str(state_new),
                                  "{}_{}".format(state_old, 'since'): str(0),
                                  "{}_{}".format(state_old, 'time'): str(total_time),
                                  "{}_{}".format(state_new, 'since'): str(end_time)}

                self.update_slice_monitor_index('slice_monitor_' + nssid.lower(),
                                                "service_status",
                                                container_name,
                                                container_data)

    def check_nssid_with_mid(self, machine_id, container_type, current_state_machine, slice_id):
        machine_key = self.jesearch.get_json_from_es("slice_keys_" + slice_id.lower(), container_type)
        if machine_key[0]:
            machine_key = machine_key[1]
            self.keys_local.update({slice_id: machine_key})
            for data in range(len(machine_key)):
                service_name = list((machine_key[data]).keys())[0]
                if machine_key[data][service_name][0]['juju_mid'] == str(machine_id):
                    nssid = machine_key[data][service_name][0]['nssi_id']
                    container_name = service_name
                    slice_mon_data= self.jesearch.get_json_from_es("slice_monitor_" + nssid.lower(), "machine_status")
                    if slice_mon_data[0]:
                        slice_mon_data=slice_mon_data[1]
                    for num in range(len(slice_mon_data)):
                        application_name = list((slice_mon_data[num]).keys())[0]
                        if application_name == service_name:
                            if current_state_machine == slice_mon_data[num][service_name][0]['current_state']:
                                # there is not change in the state of the machine
                                return [None, None, None, None, None]
                            else:
                                state_old = slice_mon_data[num][service_name][0]['current_state']
                                state_new = current_state_machine

                                if (state_new == 'started') and (state_old == 'pending'):
                                    val = "{}_{}".format('prepending', 'time')
                                    prepending_time = slice_mon_data[num][service_name][0][val]
                                else:
                                    prepending_time = None

                                val = "{}_{}".format(state_old, 'since')
                                start_time = slice_mon_data[num][service_name][0][val]
                                return [nssid, container_name, start_time, state_old, state_new, prepending_time]
            return [None, None, None, None, None,None]
        else:
            message = "The key {} does not exist in the page {}".format(container_type,
                                                                        "slice_keys_" + slice_id.lower())
            self.logger.error(message)
            return [None, None, None, None, None, None]

    """
    def check_nssid_with_service(self, app_name, slice_id):
        print("Here check namec ", app_name, slice_id )
        #if app_name == 'oai-ran':
        #    pass
        for nsi in self.keys_local.keys():
            if nsi == slice_id:
                machine_key = self.keys_local[slice_id]

                for data in range(len(machine_key)):
                    service_Name = list((machine_key[data]).keys())[0]
                    if service_Name == str(app_name):
                        nssid = machine_key[data][service_Name][0]['nssi_id']
                        start_time = machine_key[data][service_Name][0]['date']
                        return [nssid, start_time]
        service_key = self.jesearch.get_json_from_es("slice_keys_" + slice_id.lower(), 'machine_keys')
        if service_key[0]:
            service_key = service_key[1]
            self.keys_local.update({slice_id: service_key})
            for data in range(len(service_key)):
                service_name = list((service_key[data]).keys())[0]
                if service_name == str(app_name):
                    nssid = service_key[data][service_name][0]['nssi_id']
                    start_time = service_key[data][service_name][0]['date']
                    return nssid, start_time
        else:
            print("service_key[1]=[]".format(service_key[1]))
            pass
    """
    def check_nssid_with_service(self, app_name, container_type, current_state_machine, slice_id): # service_state=unit, change
        service_key = self.jesearch.get_json_from_es("slice_keys_" + slice_id.lower(), container_type)
        if service_key[0]:
            service_key = service_key[1]
            self.keys_local.update({slice_id: service_key})
            for data in range(len(service_key)):
                service_name = list((service_key[data]).keys())[0]
                if service_name == str(app_name):
                    nssid = service_key[data][service_name][0]['nssi_id']
                    container_name = service_name
                    slice_mon_data= self.jesearch.get_json_from_es("slice_monitor_" + nssid.lower(), "service_status")
                    if slice_mon_data[0]:
                        slice_mon_data=slice_mon_data[1]
                    for num in range(len(slice_mon_data)):
                        application_name = list((slice_mon_data[num]).keys())[0]
                        if application_name == service_name:
                            if current_state_machine == slice_mon_data[num][service_name][0]['current_state']:
                                # there is not change in the state of the machine
                                return [None, None, None, None, None]
                            else:
                                state_old = slice_mon_data[num][service_name][0]['current_state']
                                state_new = current_state_machine

                                if (state_new == 'active') and (state_old == 'maintenance'):
                                    val = "{}_{}".format('waiting', 'time')
                                    waiting_time = slice_mon_data[num][service_name][0][val]
                                else:
                                    waiting_time = None

                                val = "{}_{}".format(state_old, 'since')
                                start_time = slice_mon_data[num][service_name][0][val]
                                return [nssid, container_name, start_time, state_old, state_new, waiting_time]
            return [None, None, None, None, None,None]
        else:
            message = "The key {} does not exist in the page {}".format(container_type,
                                                                        "slice_keys_" + slice_id.lower())
            self.logger.error(message)
            return [None, None, None, None, None, None]

    def update_slice_monitor_index(self, index_page, container_type, container_name, container_data):
        if self.jesearch.ping():
            slice_data = self.jesearch.get_json_from_es(index_page, container_type)
            container_data.items()
            leaf_keys = list(container_data.keys())
            leaf_values = list(container_data.values())
            if slice_data[0]:
                slice_data = slice_data[1]
                for machines in range(len(slice_data)):  # Update the container
                    machines_list = slice_data[machines]
                    machine = list(machines_list.keys())
                    for num in range(len(machine)):
                        if machine[num] == container_name:
                            for number in range(len(container_data)):
                                leaf_key = leaf_keys[number - 1]
                                leaf_value = leaf_values[number - 1]
                                slice_data[machines][container_name][0][leaf_key] = leaf_value
                self.jesearch.update_index_with_content(index_page, container_type, slice_data)

logger = logging.getLogger('jox.jujuStatus')
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
async def get_juju_status(type, cloud_name=None, model_name=None, user_name="admin"):
    model = Model()
    if (cloud_name is None) and (model_name is None):
        try:
           await model.connect_current()
        except:
            message = "Error while trying to connect to the current juju model"
            logger.error(message)
            return [False, message]
    else:
        try:
            model_name = cloud_name + ":" + user_name + '/' + model_name
            await model.connect(model_name)
        except:
            message = "Error while trying to connect to the juju model {}:{}/{}".format(cloud_name, user_name, model_name)
            logger.error(message)
            return [False, message]
    juju_status=(await utils.run_with_interrupt(model.get_status(), model._watch_stopping, loop=model.loop))
    
    model_info = dict()
    model_info['controller_uuid'] = model.info.controller_uuid
    model_info['model_uuid'] = model.info.uuid
    model_info['cloud_name'] = model._connector.controller_name
    model_info['model_name'] = model.info.name
    model_info['default_series'] = model.info.default_series
    model_info['provider_type'] = model.info.provider_type

    if type == 'machines':
        return [True, juju_status.machines, model_info]
    elif type == 'applications':
        return [True, juju_status.applications, model_info]
    elif type == 'relations':
        return [True, get_all_relations(juju_status), model_info]
    elif type == 'all':
        juju_status_relations =get_all_relations(juju_status)
        full_status=({'machines':[juju_status.machines],
                      'services':[juju_status.applications],
                      'relations':[juju_status_relations]})
        return [True, full_status, model_info]
    else:
        message = "The key {} is not supported. Only the following keys are supported: machines, applications, relations, all".\
            format(type)
        return [False, message]
def get_all_relations(juju_status):
    relations = {}
    container = {}
    node = 1
    juju_status_relations = juju_status.relations
    for item in juju_status_relations:
        container['interface'] = item.interface
        container['Provider:Requirer'] = item.key
        node = ("relation-" + str(node))
        relations.update({node: [container.copy()]})
        node = +1
    return relations
    

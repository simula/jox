#!/bin/bash
# Copyright 2016-2019 Eurecom and Mosaic5G Platforms Authors
# Licensed to the Mosaic5G under one or more contributor license
# agreements. See the NOTICE file distributed with this
# work for additional information regarding copyright ownership.
# The Mosaic5G licenses this file to You under the
# Apache License, Version 2.0  (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    	http://www.apache.org/licshiftenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# -------------------------------------------------------------------------------
#   For more information about the Mosaic5G:
#   	contact@mosaic-5g.io
#
#
################################################################################
# file
# brief Auto switch the RAN between the Monolithic and Functional Split based on the cpu usage
# author Osama Arouk

# Command line to increase the cpu usage: stress --cpu $NumberCpu --timeout $TimeInSeconds
#               For example: stress --cpu 6 --timeout 600
#               To install stress: sudo apt install stress
set -e

diss_aggregation="fs" # It is to tell what is the current mode of RAN. It can be either "mon", i.e. Monolithic, or "fs", i.e. Functional Split 
cpu_percent_to_switch_to_mon=50.0 # CPU usage above which, the RAN mode will be switched to Monolithic if the current mode is Functional Split
cpu_percent_to_switch_to_fs=40.0 # CPU usage below which, the RAN mode will be switched to Functional Split if the current mode is Monolithic 
threshold=10 # waiting time before switching from Monolithic to functional split, and vice versa

# change DIR_jox_config where the json file jox_config.json exists
DIR_jox_config=$HOME/mosaic5g/jox/jox/src/common/config

jox_ip=`jq -r '."flask-config"."flask-server"' $DIR_jox_config/jox_config.json`
jox_port=`jq -r '."flask-config"."flask-port"' $DIR_jox_config/jox_config.json`

if [ "$diss_aggregation" == "mon" ] ; then
    curl --silent --output /dev/null http://$jox_ip:$jox_port/config --data-binary "@mon_slice_initial_config.json"
elif [ "$diss_aggregation" == "fs" ] ; then
    curl --silent --output /dev/null http://$jox_ip:$jox_port/config --data-binary "@fs_slice_initial_config.json"
else
    echo $diss_aggregation 'is NOT supported, only "mon" and "fs" are supported '
    exit 0
fi
counter=0
while true; do
    #sleep 1
    cpu_usage=`awk '{u=$2+$4; t=$2+$4+$5; if (NR==1){u1=u; t1=t;} else print ($2+$4-u1) * 100 / (t-t1); }' <(grep 'cpu ' /proc/stat) <(sleep 1;grep 'cpu ' /proc/stat)`
    if [ "$diss_aggregation" == "mon" ] ; then
        if [ ${cpu_usage%.*} -le ${cpu_percent_to_switch_to_fs%.*} ] ; then
            if [ $counter -lt $threshold ] ; then
                counter=$((counter+1))
                echo 'Current RAN mode: Monolithic' $'\t' 'current cpu usage='$cpu_usage  $'\t' "Waiting for $((threshold-counter)) seconds to switch to functional split"
            else
                echo "switching to functional split mode"

                curl http://$jox_ip:$jox_port/config --data-binary "@fs_config_start.json"

                curl http://$jox_ip:$jox_port/relation -X DELETE --data-binary "@fs_rel_remove.json"
                sleep 25
                curl http://$jox_ip:$jox_port/relation -X POST --data-binary "@fs_rel_add_1.json"
                sleep 13
                curl http://$jox_ip:$jox_port/relation -X POST --data-binary "@fs_rel_add_2.json"
                sleep 20
                curl http://$jox_ip:$jox_port/relation -X POST --data-binary "@fs_rel_add_3.json"
                sleep 15
                curl http://$jox_ip:$jox_port/relation -X POST --data-binary "@fs_rel_add_4.json"
                sleep 10
                curl http://$jox_ip:$jox_port/config --data-binary "@fs_config_end.json"
                
                diss_aggregation="fs"
                echo "Current disaggregation is Monolithic"
                counter=0
            fi
        else
            counter=0
            echo 'Current RAN mode: Monolithic' $'\t' 'current cpu usage='$cpu_usage
        fi
    else
        if [ ${cpu_usage%.*} -ge  ${cpu_percent_to_switch_to_mon%.*} ] ; then
            if [ $counter -lt $threshold ] ; then
                counter=$((counter+1))
                echo 'Current RAN mode: Functiona Split' $'\t' 'current cpu usage='$cpu_usage  $'\t' "Waiting for $((threshold-counter)) seconds to switch to Monolithic"
            else
                echo "switching to monolithic mode"
                
                curl http://$jox_ip:$jox_port/config --data-binary "@mon_config_start.json"
                curl http://$jox_ip:$jox_port/relation -X DELETE --data-binary "@mon_rel_remove.json"
                sleep 30
                curl http://$jox_ip:$jox_port/relation -X POST --data-binary "@mon_rel_add.json"
                sleep 10

                diss_aggregation="mon"
                echo "Current disaggregation is Monolithic"
                counter=0
            fi
        else
            counter=0
            echo 'Current RAN mode: Functiona Split' $'\t' 'current cpu usage='$cpu_usage
        fi
    fi
    
done

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
#    	http://www.apache.org/licenses/LICENSE-2.0

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
# brief
# author

export DEBIAN_FRONTEND=noninteractive
###################################
# colorful echos
###################################
black='\E[30m'
red='\E[31m'
green='\E[32m'
yellow='\E[33m'
blue='\E[1;34m'
magenta='\E[35m'
cyan='\E[36m'
white='\E[37m'
reset_color='\E[00m'
COLORIZE=1

cecho()  {
    # Color-echo
    # arg1 = message
    # arg2 = color
    local default_msg="No Message."
    message=${1:-$default_msg}
    color=${2:-$green}
    [ "$COLORIZE" = "1" ] && message="$color$message$reset_color"
    echo -e "$message"
    return
}

echo_error()   { cecho "$*" $red          ;}
echo_fatal()   { cecho "$*" $red; exit -1 ;}
echo_warning() { cecho "$*" $yellow       ;}
echo_success() { cecho "$*" $green        ;}
echo_info()    { cecho "$*" $blue         ;}


#============================
#vars and default values
#===========================
SUDO='sudo -E'
base_dir=`pwd`
root_path=$(dirname $(readlink -f $0))

pkg_arx_dir="archives"
pkg_dst_dir=""
pkg_src_dir=""
pkg_vendor="Eurecom"
pkg_name="mosaic5g"
pkg_version="1.0"
pkg_type=""
pkg_ext=""
pkg_template="oai-epc"
num_subslices=2


machine_flavor="small"
os_flavor="ubuntu_16_64"

# package descriptor
pkg_desc_types=(nsi nssi)
pkg_desc_ext=(yml yaml)
pkg_dirs=(nsi nssi charms icon )
pkg_files=(README)
pkg_chksums="checksums.txt"


re='^[0-9]+$'
nsi_subslices=("[nssi_1]" "[nssi_1, nssi_2]" "[nssi_1, nssi_2, nssi_3]" "[nssi_1, nssi_2, nssi_3, nssi_4]" "[nssi_1, nssi_2, nssi_3, nssi_4, nssi_5]")

#=============================
# print help
#============================

function print_help() {
  echo_info '
Generates a JoX package describtor for onboarding from source diractory and

Options
-h
   print this help
-a | --pkg-description)
   Set the package short description. Default is set to: template for deploying oai-epc with two subslices.
-c | --create-pkg-template
   Create a package template"
-d | --dst-dir [dir]
   Directory to create a package template. Default is set to : $pkg_dst_dir in the current directory.
-m | --machine-flavor  [machine flavor]
    machine flavor to host services. Avaialble options: tiny(default), small.
-n | --num-subslices  [subslices]
    Set the number os subslices per slice. Avaialble options: 1, 2 (default), 3, 4, 5.
-p | --pkg-name [name]
    Name of the package to create. Default is set to : mosaic5g
-o | --os-flavor  [os flavor]
    machine flavor to host services. Avaialble options: ubuntu_14_64, ubuntu_16_64(default), ubuntu_18_64
-r | --pkg-version  [version]
   Package version. Default is 1.0.
-s | --src-dir [dir]
   Directory to use to create a package. Default is set to : current directory.
-t | --pkg-template)
   Set the template to generate the package. Available options: wordpress, oai-epc(default), oai-4g, oai-5g-cran, oai-nfv-rrh, oai-nfv-sim.
-v | --pkg-vendor [vendor]
   Package vendor name for descriptor. Default is set to: Eurecom

Usage: onboard_jox -s <src_directory> -p <dst_directory> -p m5g
Example:
- onboard -c               # to create a package template
- onboard -s mosaic5g      # to onboard a package into JoX
'
}
function print_set_vars(){

    echo_info "base dir:  $base_dir"
    echo_info "root path: $root_path"
    echo_info "src dir :  $pkg_src_dir"
    echo_info "dst dir :  $pkg_dst_dir"
    echo ""

    #resetting vars
    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"

}

function chksum() {
    echo_info  "Adding file $1 to $pkg_src_dir/$pkg_chksums"
    md5sum $1 >> $pkg_chksums
}

# Check if the array contains a specific value
# Taken from
# http://stackoverflow.com/questions/3685970/check-if-an-array-contains-a-value
function contains() {
    local n=$#
    local value=${!n}
    for ((i=1;i < $#;i++)); do
        if [ "${!i}" == "${value}" ]; then
            echo "y"
            return 0
        fi
    done
    echo "n"
    return 1
}

function check_pkg_type() {
    type=$1
    if [ $(contains "${pkg_desc_type[@]}" $type) == "y" ]; then
	pkg_type=$type
    else
	echo_error "Unknown descriptor type $type!" >&2
	pkg_type=""
    fi
}

function check_pkg_ext() {
    ext=$1
    if [ $(contains "${pkg_desc_ext[@]}" $ext) == "y" ]; then
	pkg_ext=$ext
    else
	echo_error "Unknown descriptor extension $ext!" >&2
	pkg_ext=""
    fi
}


function write_readme() {
    file=${1}/README
    date=$(date +%F)
    dir_tree=`tree $1`

    cat >$file <<EOF
Package Name:            $pkg_name
Package description:     $pkg_description
Package version:         $pkg_version
Package vendor:          $pkg_vendor
Package date:            $date
Package structure:       $dir_tree
EOF

}


###### wordpress
function write_nsi_wordpress_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
tosca_definitions_version: tosca_simple_yaml_1_0
imports: [nssi_1, nssi_2]
metadata:
  ID: wordpress
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date
relationships_template:
  connection_server_client:
    source:
      inputs: {name: eg1, node: wordpress, type: tosca.relationships.AttachesTo}
      node: nss_first
      parameters: nssi_1
    target:
      inputs: {name: ing1, node: mysql, type: tosca.relationships.DependsOn}
      node: nss_second
      parameters: nssi_2
    type: tosca.relationships.ConnectsTo

topology_template:
  node_templates:
    nss1:
      requirements:
        egress:
          eg1:
            node: wordpress
            relationship: {type: tosca.relationships.AttachesTo}
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss2:
      requirements:
        ingress:
          ing1:
            node: mysql
            relationship: {type: tosca.relationships.DependsOn}
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
EOF

}
function write_nssi_wordpress_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description ($2)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: "10.189.155.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_3: &data_network_3
    properties:
      network_name: "net3"
      ip_version: 4
      cidr: "192.168.12.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "192.168.12.254"
  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2
      - network3: *data_network_3
EOF


    if [ "$2" == "nssi_1" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_wordpress:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: wordpress_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.180.125.225"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    wordpress:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:trusty/wordpress-5'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_wordpress
          relationship: tosca.relationships.HostedOn

    wordpress_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_wordpress
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

EOF
	elif [ "$2" == "nssi_2" ] ; then
	cat >>$desc_file <<EOF

topology_template:
  node_templates:
    VDU_mysql:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: mysql_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.180.125.225"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    mysql:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:mysql-58'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_mysql
          relationship: tosca.relationships.HostedOn

    mysql_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_mysql
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF
    fi
}


###### oai-epc
function write_nsi_epc_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
tosca_definitions_version: tosca_simple_yaml_1_0
imports: [nssi_1, nssi_2]
metadata:
  ID: oai-epc
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date
relationships_template:
  connection_epc:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        type: tosca.relationships.AttachesTo
        name: eg1
        node: oai-hss
      node: nss_first
      parameters: nssi_1
    target:
      inputs:
        name: ing1
        node: oai-mme
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_2

topology_template:
  node_templates:
    nss_first:
      requirements:
        egress:
          eg1:
            node: oai-hss
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss_second:
      requirements:
        ingress:
          ing1:
            node: oai-mme
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
EOF

}
function write_nssi_epc_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description ($2)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: "10.189.155.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_3: &data_network_3
    properties:
      network_name: "net3"
      ip_version: 4
      cidr: "192.168.12.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "192.168.12.254"
  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2
      - network3: *data_network_3
EOF


    if [ "$2" == "nssi_1" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_mysql:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties:  "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: mysql_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.39.202.225"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_oai_hss:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: hss_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.122.34"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    mysql:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:mysql-58'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_mysql
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-hss
          relationship: tosca.relationships.AttachesTo

    oai-hss:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-hss-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai_hss
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    mysql_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_mysql
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    hss_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai_hss
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
	elif [ "$2" == "nssi_2" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-mme:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-mme_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.39.202.134"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_oai-spgw:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: hss_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.122.54"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    oai-mme:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-mme-18'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-mme
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-spgw:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm:  'cs:~navid-nikaein/xenial/oai-spgw-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-spgw
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-mme_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-mme
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    hss_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-spgw
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF
    fi
}


###### oai-4g
function write_nsi_oai4g_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
tosca_definitions_version: tosca_simple_yaml_1_0
imports: [nssi_1, nssi_2, nssi_3]
metadata:
  ID: oai-4g
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date

relationships_template:
  connection_epc:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        type: tosca.relationships.AttachesTo
        name: eg1
        node: oai-hss
      node: nss_first
      parameters: nssi_1
    target:
      inputs:
        name: ing1
        node: oai-mme
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_2

  connection_ran:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        name: eg1
        node: oai-mme
        type: tosca.relationships.AttachesTo
      node: nss_first
      parameters: nssi_2
    target:
      inputs:
        name: ing1
        node: oai-ran
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_3

topology_template:
  node_templates:
    nss1:
      requirements:
        egress:
          eg1:
            node: oai-hss
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss2:
      requirements:
        ingress:
          ing1:
            node: oai-mme
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI

    nss3:
      requirements:
        egress:
          eg1:
            node: oai-mme
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss4:
      requirements:
        ingress:
          ing1:
            node: oai-ran
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_3
      type: tosca.nodes.JOX.NSSI
EOF
}
function write_nssi_oai4g_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description ($2)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: "10.189.155.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_3: &data_network_3
    properties:
      network_name: "net3"
      ip_version: 4
      cidr: "192.168.12.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "192.168.12.254"
  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2
      - network3: *data_network_3
EOF


    if [ "$2" == "nssi_1" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_mysql:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: mysql_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.180.125.225"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_oai_hss:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: hss_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.1.2"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    mysql:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:mysql-58'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_mysql
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-hss
          relationship: tosca.relationships.AttachesTo

    oai-hss:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-hss-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai_hss
          relationship: tosca.relationships.HostedOn

    mysql_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_mysql
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    hss_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai_hss
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
	elif [ "$2" == "nssi_2" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-mme:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-mme_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.11.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_oai-spgw:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-spgw_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.11.2"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    oai-mme:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-mme-18'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-mme
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-spgw:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm:  'cs:~navid-nikaein/xenial/oai-spgw-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-spgw
          relationship: tosca.relationships.HostedOn

    oai-mme_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-mme
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    oai-spgw_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-spgw
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF
    elif [ "$2" == "nssi_3" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-ran:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-ran_port
#        tag_usrp:
#          type: tosca.capabilities.Endpoint
#          protocol:
#            - VRT # protocol for usrp
#            - CHDR # protocol for usrp
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.12.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    oai-ran:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-enb-33'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-ran
          relationship: tosca.relationships.HostedOn

    oai-ran_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-ran
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF

    fi
}


###### oai-5g-cran
function write_nsi_oai5gcran_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
tosca_definitions_version: tosca_simple_yaml_1_0
imports: [nssi_1, nssi_2, nssi_3]
metadata:
  ID: oai-5g-cran
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date

relationships_template:
  connection_epc:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        type: tosca.relationships.AttachesTo
        name: eg1
        node: oai-hss
      node: nss_first
      parameters: nssi_1
    target:
      inputs:
        name: ing1
        node: oai-mme
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_2
  connection_ran:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        name: eg1
        node: oai-mme
        type: tosca.relationships.AttachesTo
      node: nss_first
      parameters: nssi_2
    target:
      inputs:
        name: ing1
        node: oai-enb
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_3

topology_template:
  node_templates:
    nss1:
      requirements:
        egress:
          eg1:
            node: oai-hss
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss2:
      requirements:
        ingress:
          ing1:
            node: oai-mme
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss3:
      requirements:
        egress:
          eg1:
            node: oai-mme
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss4:
      requirements:
        ingress:
          ing1:
            node: oai-ran
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_3
      type: tosca.nodes.JOX.NSSI
EOF
}
function write_nssi_oai5gcran_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description ($2)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: "10.189.155.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_3: &data_network_3
    properties:
      network_name: "net3"
      ip_version: 4
      cidr: "192.168.12.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "192.168.12.254"
  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2
      - network3: *data_network_3
EOF


    if [ "$2" == "nssi_1" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_mysql:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: mysql_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.180.125.225"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_oai_hss:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: hss_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.1.2"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    mysql:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:mysql-58'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_mysql
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-hss
          relationship: tosca.relationships.AttachesTo

    oai-hss:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-hss-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai_hss
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    mysql_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_mysql
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    hss_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai_hss
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
	elif [ "$2" == "nssi_2" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-mme:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-mme_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.11.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_oai-spgw:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: spgw_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.11.2"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    oai-mme:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-mme-18'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-mme
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-spgw:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm:  'cs:~navid-nikaein/xenial/oai-spgw-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-spgw
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-mme_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-mme
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    spgw_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-spgw
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF
    elif [ "$2" == "nssi_3" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-enb:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-enb_port
#        tag_usrp:
#          type: tosca.capabilities.Endpoint
#          protocol:
#            - VRT # protocol for usrp
#            - CHDR # protocol for usrp
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.12.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1
    VDU_oai-rru:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: rru_port
      #      attributes:
      #        endpoint:
      #          type: tosca.capabilities.Endpoint
      #          ip_address: "172.24.11.2"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1
    oai-enb:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-enb-33'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-enb
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-rru
          relationship: tosca.relationships.AttachesTo
    oai-rru:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm:  'cs:~navid-nikaein/xenial/oai-rru-15'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-rru
          relationship: tosca.relationships.HostedOn

    oai-enb_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-enb
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
    rru_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-rru
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF

    fi
}

###### oai-nfv-rrh
function write_nsi_oainfvrrh_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
tosca_definitions_version: tosca_simple_yaml_1_0
imports: [nssi_1, nssi_2, nssi_3]
metadata:
  ID: oai-nfv-rrh
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date

relationships_template:
  connection_epc:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        type: tosca.relationships.AttachesTo
        name: eg1
        node: oai-hss
      node: nss_first
      parameters: nssi_1
    target:
      inputs:
        name: ing1
        node: oai-epc
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_2
  connection_ran:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        name: eg1
        node: oai-epc
        type: tosca.relationships.AttachesTo
      node: nss_first
      parameters: nssi_2
    target:
      inputs:
        name: ing1
        node: oai-enb
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_3

topology_template:
  node_templates:
    nss1:
      requirements:
        egress:
          eg1:
            node: oai-hss
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss2:
      requirements:
        ingress:
          ing1:
            node: oai-epc
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss3:
      requirements:
        egress:
          eg1:
            node: oai-epc
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss4:
      requirements:
        ingress:
          ing1:
            node: oai-enb
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_3
      type: tosca.nodes.JOX.NSSI
EOF
}
function write_nssi_oainfvrrh_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description ($2)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: "10.189.155.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_3: &data_network_3
    properties:
      network_name: "net3"
      ip_version: 4
      cidr: "192.168.12.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "192.168.12.254"
  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2
      - network3: *data_network_3
EOF


    if [ "$2" == "nssi_1" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_mysql:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: mysql_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.180.125.225"
      policies:
        policy1:
          type: tosca.policy.placement
          container_type: region
          container_number: 1

    VDU_oai_hss:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: hss_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.1.2"
      policies:
        policy1:
          type: tosca.policy.placement
          container_type: region
          container_number: 1

    mysql:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:mysql-58'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_mysql
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-hss
          relationship: tosca.relationships.AttachesTo

    oai-hss:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-hss-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai_hss
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    mysql_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_mysql
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    hss_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai_hss
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
	elif [ "$2" == "nssi_2" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-epc:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_14_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-epc_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.11.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    oai-epc:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/trusty/oai-epc-27'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-epc
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-epc_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-epc
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
    elif [ "$2" == "nssi_3" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-enb:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-enb_port
#        tag_usrp:
#          type: tosca.capabilities.Endpoint
#          protocol:
#            - VRT # protocol for usrp
#            - CHDR # protocol for usrp
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.12.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1
    VDU_oai-rrh:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_14_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: rru_port
      #      attributes:
      #        endpoint:
      #          type: tosca.capabilities.Endpoint
      #          ip_address: "172.24.11.2"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1
    oai-enb:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-enb-33'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-enb
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-rrh
          relationship: tosca.relationships.AttachesTo
    oai-rrh:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm:  'cs:~navid-nikaein/trusty/oai-rrh-10'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-rrh
          relationship: tosca.relationships.HostedOn

    oai-enb_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-enb
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
    rru_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-rrh
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF

    fi
}


###### oai-nfv-sim
function write_nsi_oainfvsim_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
tosca_definitions_version: tosca_simple_yaml_1_0
imports: [nssi_1, nssi_2, nssi_3]
metadata:
  ID: oai-nfv-sim
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date

relationships_template:
  connection_epc:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        type: tosca.relationships.AttachesTo
        name: eg1
        node: oai-hss
      node: nss_first
      parameters: nssi_1
    target:
      inputs:
        name: ing1
        node: oai-epc
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_2
  connection_ran:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        name: eg1
        node: oai-epc
        type: tosca.relationships.AttachesTo
      node: nss_first
      parameters: nssi_2
    target:
      inputs:
        name: ing1
        node: oai-enb
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_3

topology_template:
  node_templates:
    nss1:
      requirements:
        egress:
          eg1:
            node: oai-hss
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss2:
      requirements:
        ingress:
          ing1:
            node: oai-epc
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss3:
      requirements:
        egress:
          eg1:
            node: oai-epc
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
    nss4:
      requirements:
        ingress:
          ing1:
            node: oai-enb
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_3
      type: tosca.nodes.JOX.NSSI
EOF
}
function write_nssi_oainfvsim_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description ($2)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: "10.189.155.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_3: &data_network_3
    properties:
      network_name: "net3"
      ip_version: 4
      cidr: "192.168.12.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "192.168.12.254"
  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2
      - network3: *data_network_3
EOF


    if [ "$2" == "nssi_1" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_mysql:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: mysql_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.180.125.225"
      policies:
        policy1:
          type: tosca.policy.placement
          container_type: region
          container_number: 1

    VDU_oai_hss:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_16_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: hss_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.1.2"
      policies:
        policy1:
          type: tosca.policy.placement
          container_type: region
          container_number: 1

    mysql:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:mysql-58'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_mysql
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-hss
          relationship: tosca.relationships.AttachesTo

    oai-hss:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/xenial/oai-hss-16'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai_hss
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    mysql_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_mysql
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    hss_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai_hss
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
	elif [ "$2" == "nssi_2" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-epc:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_14_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-epc_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.11.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    oai-epc:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/trusty/oai-epc-27'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-epc
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    oai-epc_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-epc
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
    elif [ "$2" == "nssi_3" ] ; then
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-enb:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: kvm
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "ubuntu_14_64"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: oai-enb_port
#        tag_usrp:
#          type: tosca.capabilities.Endpoint
#          protocol:
#            - VRT # protocol for usrp
#            - CHDR # protocol for usrp
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "172.24.12.1"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1
    oai-enb:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:~navid-nikaein/trusty/oaisim-enb-ue-8'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_oai-enb
          relationship: tosca.relationships.HostedOn
    oai-enb_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_oai-enb
        link:
          node: *data_network_2
          type: tosca.nodes.network.Network
EOF

    fi
}



function write_nsi_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"

    cat >$desc_file <<EOF
description: $pkg_description
imports: ${nsi_subslices[$2-1]}
tosca_definitions_version: tosca_simple_yaml_1_0

metadata:
  ID: oai-epc
  author: $pkg_name
  vendor: $pkg_name
  version: $pkg_version
  date: $date
relationships_template:
  connection_nssi1_nssi2:
    type: tosca.relationships.ConnectsTo
    source:
      inputs:
        type: tosca.relationships.AttachesTo
        name: eg1
        node: node1
      node: nss_first
      parameters: nssi_1
    target:
      inputs:
        name: ing1
        node: node2
        type: tosca.relationships.DependsOn
      node: nss_second
      parameters: nssi_2

topology_template:
  node_templates:
    nss_first:
      requirements:
        egress:
          eg1:
            node: node1
            relationship:
              type: tosca.relationships.AttachesTo
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss_second:
      requirements:
        ingress:
          ing1:
            node: node2
            relationship:
              type: tosca.relationships.DependsOn
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
EOF

}

function write_nssi_template() {
    date=$(date +%F)
    name=$(basename $1)

    for i in `seq 1 $num_subslices`; do
	desc_file="${1}/nssi/nssi_${i}.yaml"

	cat >$desc_file <<EOF
description: $pkg_description (nssi_$i)
tosca_definitions_version: tosca_simple_yaml_1_0

imports: []
metadata:
  ID: $2
  author: $pkg_vendor
  vendor: $pkg_vendor
  version: $pkg_version
  date: $date

dsl_definitions:
  host_small: &host_small
    disk_size: 5
    mem_size: 1024
    num_cpus: 1
  host_tiny: &host_tiny
    disk_size: 5
    mem_size: 512
    num_cpus: 1
  os_linux_u_14_x64: &os_u14
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 14.04
  os_linux_u_16_x64: &os_u16
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 16.04
  os_linux_u_18_x64: &os_u18
    architecture: x86_64
    distribution: Ubuntu
    type: Linux
    version: 18.04
  data_network: &data_network_1
    properties:
      network_name: "net1"
      ip_version: 4
      cidr: '10.146.98.0/24'
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"
  data_network_2: &data_network_2
    properties:
      network_name: "net2"
      ip_version: 4
      cidr: "192.168.122.0/24"
      start_ip: ""
      end_ip: ""
      gateway_ip: "0.0.0.0"

  containers:
    region1:
      - network: *data_network_1
      - network2: *data_network_2

topology_template:
  node_templates:
    VDU_vnf1:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc

      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties:  "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: vnf1_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "10.39.202.225"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    VDU_vnf2:
      type: tosca.nodes.nfv.VDU.Compute
      artifacts:
        sw_image:
          type: tosca.artifacts.nfv.SwImage
          properties:
            supported_virtualisation_environments:
              entry_schema: default
              type: lxc
      capabilities:
        host:
          type: tosca.capabilities.Compute
          properties: "$machine_flavor"
        os:
          type: tosca.capabilities.OperatingSystem
          properties: "$os_flavor"
      properties:
        port_def:
          type: tosca.capabilities.Endpoint
          port_name: vnf2_port
#      attributes:
#        endpoint:
#          type: tosca.capabilities.Endpoint
#          ip_address: "192.168.122.34"
      policies:
        policy1:
          type: tosca.policy.placement  # New
          container_type: region
          container_number: 1

    vnf1:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:vnf1'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_vnf1
          relationship: tosca.relationships.HostedOn
        req2:
          node: vnf2
          relationship: tosca.relationships.AttachesTo

    vnf2:
      type: tosca.nodes.SoftwareComponent.JOX
      properties:
        charm: 'cs:vnf2'
        endpoint: localhost-gatto
        model: default
        vendor: $pkg_vendor
        version: $pkg_version
      requirements:
        req1:
          node: VDU_vnf2
          relationship: tosca.relationships.HostedOn
        req2:
          node: oai-spgw
          relationship: tosca.relationships.AttachesTo

    vnf1_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_vnf1
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network

    vnf2_port:
      type: tosca.nodes.network.Port
      requirements:
        binding:
          node: VDU_vnf2
        link:
          node: *data_network_1
          type: tosca.nodes.network.Network
EOF
    done
}


function main() {
    until [ -z "$1" ]; do

	case "$1" in

	    -a | --pkg-description)
		pkg_description=$2
		echo_info "Set the package description to $pkg_description"
		shift 2;;

	    -c | --create-pkg)
		CREATE_PKG=1
		echo_info "Will create a package template"
		shift ;;
	    -d | --dst-dir)
		pkg_dst_dir=$2
		if [ "$pkg_dst_dir" == "" ] ; then
		    pkg_dst_dir="./"
		fi
		echo_info "Set the package destination directory to $pkg_dst_dir"
		shift 2;;

	    -m | --machine-flavor)
		machine_flavor=$2
		if [ "$machine_flavor" == "" ] ; then
		    machine_flavor="tiny"
		fi
		echo_info "Set the machine flavorto $machine_flavor"
		shift 2;;

	    -n | --num-sublsices)
		if ! [[ $2 =~ $re ]] ; then
		    echo_error "Not a number" >&2;
		    exit 1
		fi
		num_subslices=$2
		if [ $num_subslices -gt 5 -o $num_subslices -lt 1 ] ; then
		    num_subslices=2
		fi
		echo_info "Set the number of subslices to $num_subslices"
		shift 2;;

	    -o | --os-flavor)
		os_flavor=$2
		if [ "$os_flavor" == "" ] ; then
		    os_flavor="ubuntu_16_64"
		fi
		echo_info "Set the OS flavor to $os_flavor"
		shift 2;;

	    -p | --pkg-name)
		pkg_name=$2
		if [ "$pkg_name" == "" ] ; then
		    pkg_name="mosaic5g"
		fi
		echo_info "Will create a package template with name=$pkg_name"
		shift 2;;

	    -s | --src-dir)
		pkg_src_dir=$2
		if [ "$pkg_src_dir" == "" ] ; then
		    pkg_src_dir="./"
		fi
		echo_info "Set the package source directory to $pkg_src_dir"
		shift 2;;

	    -v | --pkg-vendor)
		pkg_vendor=$2
		if [ "$pkg_vendor" == "" ] ; then
		    pkg_vendor="M5G"
		fi
		echo_info "Will create a package template with vendor=$pkg_vendor"
		shift 2;;

	    -r | --pkg-version)
		pkg_version=$2
		if [ "$pkg_version" == "" ] ; then
		    pkg_version="1.0"
		fi
		echo_info "Will create a package template with version=$pkg_version"
		shift 2;;

	    -t | --pkg-template)
		pkg_template=$2
		if [ "$pkg_template" != "wordpress" -a  "$pkg_template" != "oai-epc" -a  "$pkg_template" != "oai-4g" -a  "$pkg_template" != "oai-5g-cran" -a  "$pkg_template" != "oai-nfv-rrh" -a  "$pkg_template" != "oai-nfv-sim" ] ; then
		    echo_warning "Unsupported package template $pkg_template, Resetting to default template (oai-epc)"
		    pkg_template="oai-epc"
		else
		    echo_info "Set the package template=$pkg_template"
		fi
		pkg_name="mosaic5g-$pkg_template"
		shift 2;;


	    -h | --help)
		print_help
		exit 1;;

	    *)
		print_help
		if [ "$1" != "-h" -o "$1" != "--help" -o "$1" != "-help" ]; then
		    echo_fatal "Unknown option $1"
		fi
		break;;
	esac
    done

    if [ "$CREATE_PKG" = "1" ] ; then
	echo_info "Create the package template $pkg_name in $pkg_dst_dir"

	if [ -z "$pkg_dst_dir" ] ; then
	    pkg_dst_dir=$base_dir
	fi

	if [ -z "$pkg_src_dir" ] ; then
	    pkg_src_dir=$base_dir
	fi

	print_set_vars

	rm -rf "${pkg_dst_dir}/${pkg_name}"

	mkdir -p "${pkg_dst_dir}/${pkg_name}"

	for sub_dir in ${pkg_dirs[@]}; do
	    dir_path=${pkg_dst_dir}/${pkg_name}/${sub_dir}
	    mkdir -p ${dir_path}
	done
	if [ "$pkg_template" == "wordpress" ] ; then
	    num_subslices=2
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_wordpress_template $pkg_dst_dir/${pkg_name}
	    write_nssi_wordpress_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_wordpress_template $pkg_dst_dir/${pkg_name} nssi_2
    elif [ "$pkg_template" == "oai-epc" ] ; then
	    num_subslices=2
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_epc_template $pkg_dst_dir/${pkg_name}
	    write_nssi_epc_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_epc_template $pkg_dst_dir/${pkg_name} nssi_2
    elif [ "$pkg_template" == "oai-4g" ] ; then
        num_subslices=3
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_oai4g_template $pkg_dst_dir/${pkg_name}
	    write_nssi_oai4g_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_oai4g_template $pkg_dst_dir/${pkg_name} nssi_2
	    write_nssi_oai4g_template $pkg_dst_dir/${pkg_name} nssi_3
    elif [ "$pkg_template" == "oai-5g-cran" ] ; then
	    num_subslices=3
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_oai5gcran_template $pkg_dst_dir/${pkg_name}
	    write_nssi_oai5gcran_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_oai5gcran_template $pkg_dst_dir/${pkg_name} nssi_2
	    write_nssi_oai5gcran_template $pkg_dst_dir/${pkg_name} nssi_3
    elif [ "$pkg_template" == "oai-nfv-rrh" ] ; then
	    num_subslices=3
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_oainfvrrh_template $pkg_dst_dir/${pkg_name}
	    write_nssi_oainfvrrh_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_oainfvrrh_template $pkg_dst_dir/${pkg_name} nssi_2
	    write_nssi_oainfvrrh_template $pkg_dst_dir/${pkg_name} nssi_3
    elif [ "$pkg_template" == "oai-nfv-sim" ] ; then
	    num_subslices=3
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_oainfvsim_template $pkg_dst_dir/${pkg_name}
	    write_nssi_oainfvsim_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_oainfvsim_template $pkg_dst_dir/${pkg_name} nssi_2
	    write_nssi_oainfvsim_template $pkg_dst_dir/${pkg_name} nssi_3
	elif [ "$pkg_template" == "clean" ] ; then
	    num_subslices=3
	    pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"
	    write_nsi_template $pkg_dst_dir/${pkg_name} $num_subslices
	    write_nssi_template $pkg_dst_dir/${pkg_name}  $num_subslices
    else
	    echo_error "Unsupported template"
	    exit 1
	fi


	for file in ${pkg_files[@]}; do
	    file_path=${pkg_dst_dir}/${pkg_name}/${file}
	    touch ${file_path}
	done
	write_readme $pkg_dst_dir/${pkg_name}

	echo""
	cat $pkg_dst_dir/${pkg_name}/README
	echo_success "package template $pkg_name is generated in $pkg_dst_dir"

    else
	echo_info "Onboarding the package $pkg_name from source files into JoX"

	if [ ! -d "${pkg_src_dir}" ]; then
	    echo_error "Please specifiy package source directory"
	    exit 1
	fi

	# archive directory for the onboarded packages
	if [ ! -d "${pkg_arx_dir}" ]; then
	    mkdir -p "${pkg_arx_dir}"
	fi

	if [ ! -d "${pkg_dst_dir}" ]; then
	    pkg_dst_dir=$base_dir
	    echo_info "setting the package desitination directory to $pkg_dst_dir"
	fi

	pkg_name=$(basename $pkg_src_dir)
	cd $pkg_src_dir
	if [ $? -ne 0 ]; then
            echo_error "ERROR: changing directory to $pkg_dst_dir failed with error code $?" >&2
            exit $?
	fi

	# Remove checksum file, if present
	rm -f $pkg_chksums

	# Check the folders are supported ones
	dirs=$( find * -maxdepth 0 -type d )
	for d in ${dirs[@]}; do
	    find $d/* -type f  2>/dev/null|
		while read file; do
                    chksum $file
		done
	done

	cd $base_dir

       	tar zcvf ${pkg_name}.tar.gz "$pkg_src_dir" >/dev/null 2>&1

	if [ $? -ne 0 ]; then
            echo "ERROR: Creating archive for ${name} in $dest_dir" >&2
            exit 1
        fi

	# archive the package
	cp $pkg_name.tar.gz $pkg_arx_dir

	echo ""
	echo_success "onboarded package $pkg_name.tar.gz with the following structure:" >&2
	tree $pkg_src_dir
    fi

}

main "$@"
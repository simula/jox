#!/bin/bash
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
pkg_description="template for deploying package <$pkg_template> with $num_subslices subslices"

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
   Set the template to generate the package. Available options: clean, oai-epc(default).
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

function write_nsi_epc_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nsi/${pkg_name}.yaml"
 
    cat >$desc_file <<EOF
description: $pkg_description
imports: [nssi_1, nssi_2]
metadata: {ID: $pkg_name, author: $pkg_vendor, vendor: $pkg_vendor, version: $pkg_version, date: $date}
relationships_template:
  connection_server_client:
    source:
      inputs: {name: eg1, node: oai-hss, type: tosca.relationships.AttachesTo}
      node: nss_first
      parameters: nssi_1
    target:
      inputs: {name: ing1, node: oai-mme, type: tosca.relationships.DependsOn}
      node: nss_second
      parameters: nssi_2
    type: tosca.relationships.ConnectsTo
topology_template:
  node_templates:
    nss:
      requirements:
        egress:
          eg1:
            node: oai-hss
            relationship: {type: tosca.relationships.AttachesTo}
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss:
      requirements:
        ingress:
          ing1:
            node: oai-mme
            relationship: {type: tosca.relationships.DependsOn}
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
tosca_definitions_version: tosca_simple_yaml_1_0
EOF

}

function write_nssi_epc_template() {
    date=$(date +%F)
    name=$(basename $1)
    desc_file="${1}/nssi/${2}.yaml"
 
    cat >$desc_file <<EOF
description: $pkg_description ($2)
dsl_definitions:
  host_small: &id001 {disk_size: 5, mem_size: 1024, num_cpus: 1}
  host_tiny: {disk_size: 5, mem_size: 512, num_cpus: 1}
  os_linux_u_14_x64: {architecture: x86_64, distribution: Ubuntu, type: Linux, version: 14.04}
  os_linux_u_16_x64: &id002 {architecture: x86_64, distribution: Ubuntu, type: Linux,
    version: 16.04}
  os_linux_u_18_x64: {architecture: x86_64, distribution: Ubuntu, type: Linux, version: 18.04}
imports: [default_slice_nssi_1]
metadata: {ID: $2, author: $pkg_vendor, vendor: $pkg_vendor, version: $pkg_version, date: $date}
EOF


    if [ "$2" == "nssi_1" ] ; then 
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_mysql:
      artifacts:
        sw_image:
          properties:
            supported_virtualisation_environments: {entry_schema: local, type: lxc}
          type: tosca.artifacts.nfv.SwImage
      capabilities:
        host:
          properties: "$machine_flavor"
        os:
          properties: "$os_flavor"
      properties: null
      type: tosca.nodes.nfv.VDU.Compute
    VDU_oai-hss:
      artifacts:
        sw_image:
          properties:
            supported_virtualisation_environments: {entry_schema: local, type: lxc}
          type: tosca.artifacts.nfv.SwImage
      capabilities:
        host:
          properties: "$machine_flavor"
        os:
          properties: "$os_flavor"
      properties: null
      type: tosca.nodes.nfv.VDU.Compute
    mysql:
      properties: {charm: 'cs:mysql-58', endpoint: localhost, model: default-juju-model-1,
        vendor: $pkg_vendor, version: $pkg_version}
      requirements:
        req1: {node: VDU_mysql, relationship: tosca.relationships.HostedOn}
        req2: {node: oai-hss, relationship: tosca.relationships.AttachesTo}
      type: tosca.nodes.SoftwareComponent.JOX
    oai-hss:
      properties: {charm: 'cs:~navid-nikaein/xenial/oai-hss-16', endpoint: localhost,
        model: default-juju-model-1, vendor: $pkg_vendor, version: $pkg_version}
      requirements:
        req1: {node: VDU_oai-hss, relationship: tosca.relationships.HostedOn}
        req2: {node: oai-spgw, relationship: tosca.relationships.AttachesTo}
      type: tosca.nodes.SoftwareComponent.JOX
tosca_definitions_version: tosca_simple_yaml_1_0
EOF
	elif [ "$2" == "nssi_2" ] ; then 
	cat >>$desc_file <<EOF
topology_template:
  node_templates:
    VDU_oai-mme:
      artifacts:
        sw_image:
          properties:
            supported_virtualisation_environments: {entry_schema: local, type: lxc}
          type: tosca.artifacts.nfv.SwImage
      capabilities:
        host:
          properties: "$machine_flavor"
        os:
          properties: "$os_flavor"
      properties: null
      type: tosca.nodes.nfv.VDU.Compute
    VDU_oai-spgw:
      artifacts:
        sw_image:
          properties:
            supported_virtualisation_environments: {entry_schema: local, type: lxc}
          type: tosca.artifacts.nfv.SwImage
      capabilities:
        host:
          properties: "$machine_flavor"
        os:
          properties: "$os_flavor"
      properties: null
      type: tosca.nodes.nfv.VDU.Compute
    oai-mme:
      properties: {charm: 'cs:~navid-nikaein/xenial/oai-mme-18', endpoint: localhost,
        model: default-juju-model-1, vendor: $pkg_vendor, version: $pkg_version}
      requirements:
        req1: {node: VDU_oai-mme, relationship: tosca.relationships.HostedOn}
      type: tosca.nodes.SoftwareComponent.JOX
    oai-spgw:
      properties: {charm: 'cs:~navid-nikaein/xenial/oai-spgw-15', endpoint: localhost,
        model: default-juju-model-1, vendor: $pkg_vendor, version: $pkg_version}
      requirements:
        req1: {node: VDU_oai-spgw, relationship: tosca.relationships.HostedOn}
        req2: {node: oai-mme, relationship: tosca.relationships.AttachesTo}
      type: tosca.nodes.SoftwareComponent.JOX
tosca_definitions_version: tosca_simple_yaml_1_0
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
metadata: {ID: $pkg_name, author: $pkg_vendor, vendor: $pkg_vendor, version: $pkg_version, date: $date}
relationships_template:
  connection_server_client:
    source:
      inputs: {name: eg1, node: node1, type: tosca.relationships.AttachesTo}
      node: nss_1
      parameters: nssi_1
    target:
      inputs: {name: ing1, node: node2, type: tosca.relationships.DependsOn}
      node: nss_2
      parameters: nssi_2
    type: tosca.relationships.ConnectsTo
topology_template:
  node_templates:
    nss:
      requirements:
        egress:
          eg1:
            node: node1
            relationship: {type: tosca.relationships.AttachesTo}
        nssi: nssi_1
      type: tosca.nodes.JOX.NSSI
    nss:
      requirements:
        ingress:
          ing1:
            node: node2
            relationship: {type: tosca.relationships.DependsOn}
        nssi: nssi_2
      type: tosca.nodes.JOX.NSSI
tosca_definitions_version: tosca_simple_yaml_1_0
EOF

}

function write_nssi_template() {
    date=$(date +%F)
    name=$(basename $1)
    
    for i in `seq 1 $num_subslices`; do
	desc_file="${1}/nssi/nssi_${i}.yaml"
 
	cat >$desc_file <<EOF
description: $pkg_description (nssi_$i)
dsl_definitions:
  host_small: &id001 {disk_size: 5, mem_size: 1024, num_cpus: 1}
  host_tiny: {disk_size: 5, mem_size: 512, num_cpus: 1}
  os_linux_u_14_x64: {architecture: x86_64, distribution: Ubuntu, type: Linux, version: 14.04}
  os_linux_u_16_x64: &id002 {architecture: x86_64, distribution: Ubuntu, type: Linux,
    version: 16.04}
  os_linux_u_18_x64: {architecture: x86_64, distribution: Ubuntu, type: Linux, version: 18.04}
imports: [slice_nssi_$i]
metadata: {ID: nssi_$i, author: $pkg_vendor, vendor: $pkg_vendor, version: $pkg_version, date: $date}
topology_template:
  node_templates:
    VDU_vnf1:
      artifacts:
        sw_image:
          properties:
            supported_virtualisation_environments: {entry_schema: local, type: lxc}
          type: tosca.artifacts.nfv.SwImage
      capabilities:
        host:
          properties: "$machine_flavor"
        os:
          properties: "$os_flavor"
      properties: null
      type: tosca.nodes.nfv.VDU.Compute
    VDU_vnf2:
      artifacts:
        sw_image:
          properties:
            supported_virtualisation_environments: {entry_schema: local, type: lxc}
          type: tosca.artifacts.nfv.SwImage
      capabilities:
        host:
          properties: "$machine_flavor"
        os:
          properties: "$os_flavor"
      properties: null
      type: tosca.nodes.nfv.VDU.Compute
    vnf1:
      properties: {charm: 'cs:vnf1', endpoint: localhost, model: default-juju-model-1,
        vendor: $pkg_vendor, version: $pkg_version}
      requirements:
        req1: {node: VDU_vnf1, relationship: tosca.relationships.HostedOn}
        req2: {node: VDU_vnf2, relationship: tosca.relationships.AttachesTo}
      type: tosca.nodes.SoftwareComponent.JOX
    vnf2:
      properties: {charm: 'cs:vnf2', endpoint: localhost,
        model: default-juju-model-1, vendor: $pkg_vendor, version: $pkg_version}
      requirements:
        req1: {node: VDU_vnf1, relationship: tosca.relationships.HostedOn}
        req2: {node: VDU_vnf2, relationship: tosca.relationships.AttachesTo}
      type: tosca.nodes.SoftwareComponent.JOX
tosca_definitions_version: tosca_simple_yaml_1_0
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
		if [ "$pkg_template" != "clean" -a  "$pkg_template" != "oai-epc" ] ; then
		    echo_warning "Unsupported package template $pkg_template, Resetting to default template (oai-epc)"
		    pkg_template="oai-epc"
		else 
		    echo_info "Set the package template=$pkg_template"
		fi
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
	if [ "$pkg_template" == "oai-epc" ] ; then
	    write_nsi_epc_template $pkg_dst_dir/${pkg_name}
	    write_nssi_epc_template $pkg_dst_dir/${pkg_name} nssi_1
	    write_nssi_epc_template $pkg_dst_dir/${pkg_name} nssi_2
	elif [ "$pkg_template" == "clean" ] ; then
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

#!/bin/bash

#sudo service rabbitmq-server start
#if [ ! -f es_id ]; then
#    touch es_id
#fi
#if [ ! -s es_id ]; then
#    echo "elasticsearch is not running"
#    check_es_running=false
#else
#     check_es_running=$(docker inspect --format="{{.State.Running}}" $(cat es_id))
#fi

#if [ ! "$check_es_running" = true ]; then
#    echo $check_es_running
#    echo "running elasticsearch"
#    sudo rm es_id
#    sudo docker run -itd --cidfile es_id -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:6.6.2
#fi
###################################
# colorful echos
###################################

red=`tput setaf 1`
green=`tput setaf 2`
reset_color=`tput sgr0`

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
echo_info()    { cecho "$*" $blue         ;}
function print_help() {
  echo '
This program invokes the plugin microservice framework
-h                                  print help
-flexran | --run flexrAN plugin
-llmec   | --run llMEC plugin    
-es      | --run es plugin (Microservice framework not yet supported for es)   


'
  exit $1
}

run_flexran_plugin(){
python3 src/core/ro/plugins/flexran.py  
}

run_llmec_plugin(){
python3 src/core/ro/plugins/llmec.py  
}

run_es_plugin(){
echo "${red} Microservice framework not yet supported for es ${reset_color}"
#python3 src/core/ro/plugins/es.py  
}
function main() {
    until [ -z "$1" ]; do
        case "$1" in
            -flexran | --run-flexrAN-plugin)
            INSTALL_PKG=1
            echo_info "Running flexRAN plugin"
            shift;;
            -h | --help | -help )
            print_help 0
            shift;;
            -llmec | --run-llMEC-plugin)
            INSTALL_PKG=2
            echo_info "Running llMEC plugin"
            shift;;
            -es  | --run-es-plugin)
            INSTALL_PKG=3
            echo_info "Running es plugin"
            shift;;
            *)
            echo_error "Unknown option $1"
            print_help -1
            shift;;
        esac
    done

    if [ "$INSTALL_PKG" = "1" ] ; then
	    run_flexran_plugin
    fi
    if [ "$INSTALL_PKG" = "2" ] ; then
	    run_llmec_plugin
    fi
    if [ "$INSTALL_PKG" = "3" ] ; then
	    run_es_plugin
    fi
}

main  "$@"
#python3 src/core/ro/plugins/flexran.py  

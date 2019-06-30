#!/usr/bin/env bash

# juju models and juju controllers
juju_controller=nymphe-edu
juju_mode_1=default-1
juju_mode_2=default-2

# machines to be added to juju models
Machine_borer_ip=192.168.1.3
Machine_borer_user=borer
Machine_borer_pass=linux0

Machine_adalia_ip=192.168.1.2
Machine_adalia_user=adalia
Machine_adalia_pass=linux

Machine_psoque_ip=192.168.1.7
Machine_psoque_user=psoque
Machine_psoque_pass=linux

test_machine_user=root
test_machine_ip=192.168.1.12


ssh_key_private=~/.ssh/id_rsa

oai_cn=oai-cn
oai_ran=oai-ran

function clean_machine() {
    ## clean the machine
    sshpass -p $4 ssh -t  -i $3  $1@$2 "sudo rm /etc/systemd/system/jujud*"
    sshpass -p $4 ssh -t  -i $3  $1@$2 "sudo rm -rf /var/lib/juju"
    sshpass -p $4 ssh -t  -i $3  $1@$2 "sudo rm /usr/bin/juju-run"
     remove snap if any
    sshpass -p $4 ssh -t  -i $3  $1@$2 "sudo snap remove $oai_cn"
    sshpass -p $4 ssh -t  -i $3  $1@$2 "sudo snap remove $oai_ran"

    sshpass -p $4 ssh -t  -i $3  $1@$2 \
    "
    cat >/etc/hosts <<EOF
    echo 127.0.0.1 localhost
    echo 127.0.0.1 $1
    "

    sshpass -p $4 ssh -t  -i $3  $1@$2 \
    "
    cat >/etc/hostname <<EOF
    echo $1
    "
}

#clean_machine $Machine_adalia_user $Machine_adalia_ip $ssh_key_private $Machine_borer_pass
#clean_machine $Machine_borer_user $Machine_borer_ip $ssh_key_private $Machine_borer_pass
#clean_machine $Machine_psoque_user $Machine_psoque_ip $ssh_key_private $Machine_psoque_pass

function clean_machine_test() {
    ## clean the machine
    ssh -t  -i $3  $1@$2 "sudo rm /etc/systemd/system/jujud*"
    ssh -t  -i $3  $1@$2 "sudo rm -rf /var/lib/juju"
    ssh -t  -i $3  $1@$2 "sudo rm /usr/bin/juju-run"
#     remove snap if any
    ssh -t  -i $3  $1@$2 "sudo snap remove $oai_cn"
    ssh -t  -i $3  $1@$2 "sudo snap remove $oai_ran"

    ssh -t  -i $3  $1@$2 \
    "
    cat >/etc/hosts <<EOF
    127.0.0.1 localhost
    127.0.0.1 $1
    "

    ssh -t  -i $3  $1@$2 \
    "
    cat >/etc/hostname <<EOF
    $1
    "
}
clean_machine_test $test_machine_user $test_machine_ip $ssh_key_private


#add_machine_to_jujumodel(){
#juju add-machine -m $1:$2 ssh:$3@$4
#}
#
#### add machines to the first juju model
#add_machine_to_jujumodel $juju_controller  $juju_mode_1  $Machine_borer_user $Machine_borer_ip
#sleep 10
#add_machine_to_jujumodel $juju_controller  $juju_mode_1  $Machine_adalia_user $Machine_adalia_ip
#sleep 10
#
## add machines to the second juju model
#add_machine_to_jujumodel $juju_controller  $juju_mode_2  $Machine_psoque_user $Machine_psoque_user

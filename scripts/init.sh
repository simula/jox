#!/bin/bash
hss_ip=($juju status | grep hss/ | awk  {'print $5'})
mme_ip=($juju status | grep mme/ | awk  {'print $5'})
spgw_ip=($juju status | grep spgw/ | awk  {'print $5'})
ran_ip=$(juju status | grep oai-ran/ | awk  {'print $5'})
flexran_ip=$(juju status | grep flexran/ | awk  {'print $5'})

juju config oai-hss eth=ens3
hss=$(juju status | grep hss/ | awk -F "*" {'print $1'})
juju resolved $hss

juju config oai-mme eth=ens3
mme=$(juju status | grep mme/ | awk -F "*" {'print $1'})
juju resolved $mme

juju config oai-spgw pgw-eth=ens3 
juju config oai-spgw sgw-eth=ens3
spgw=$(juju status | grep spgw/ | awk -F "*" {'print $1'})
juju resolved $spgw

juju config oai-ran eth=enp0s31f6
juju config oai-ran flexran_if_name=enp0s31f6
#juju config oai-ran mme_ip_addr=$mme_ip
ran=$(juju status | grep ran/ | awk -F "*" {'print $1'})
juju resolved $ran

ran_conf_file=/var/snap/oai-ran/current/enb.band7.tm1.50PRB.usrpb210.conf
hss_conf_file=/var/snap/oai-hss/current/hss.conf

sed 's/#OPERRATOR_KEY=/OPERRATOR_KEY=/g' $hss_conf_file
sed 's/OPERRATOR_KEY=/#OPERRATOR_KEY=/g' $hss_conf_file

sed 's/mnc = 93/mnc = 95/g' $ran_conf_file

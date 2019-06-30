#!/usr/bin/env bash

#
### model 1
#juju config -m nymphe-edu:default-1 oai-spgw pgw-eth=wlp2s0 sgw-eth=wlp2s0
#juju config -m nymphe-edu:default-1 oai-enb eth=enp0s31f6
#juju config -m nymphe-edu:default-1  oai-enb eutra_band=17  downlink_frequency=737500000L uplink_frequency_offset=-30000000
#juju resolved -m nymphe-edu:default-1 --all
#
## model 1
#juju config -m nymphe-edu:default-2 oai-spgw pgw-eth=enp0s31f6 sgw-eth=enp0s31f6
#juju config oai-mme gummei_tai_mnc=94
#juju resolved -m nymphe-edu:default-2 --all


juju remove-relation  -m nymphe-edu:default-1 oai-enb oai-mme
sleep 2
juju remove-relation  -m nymphe-edu:default-1 oai-spgw oai-mme
sleep 2
juju remove-relation  -m nymphe-edu:default-1 oai-hss oai-mme
#juju remove-relation  -m nymphe-edu:default-1 oai-enb flexran
#sleep 2


#sleep 35
juju remove-relation  -m nymphe-edu:default-2 oai-enb oai-mme
sleep 2
juju remove-relation  -m nymphe-edu:default-2 oai-spgw oai-mme
sleep 2
juju remove-relation  -m nymphe-edu:default-2 oai-hss oai-mme



sleep 35

juju add-relation  -m nymphe-edu:default-1 oai-enb oai-mme
sleep 2
juju add-relation  -m nymphe-edu:default-1 oai-spgw oai-mme
sleep 2
juju add-relation  -m nymphe-edu:default-1 oai-hss oai-mme



juju add-relation  -m nymphe-edu:default-2 oai-mme admin/default-1.oai-enb
sleep 2
juju add-relation  -m nymphe-edu:default-2 oai-spgw oai-mme
sleep 2
juju add-relation  -m nymphe-edu:default-2 oai-hss oai-mme


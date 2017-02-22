#!/bin/bash
juju config oai-spgw sgw-eth=eth0
juju config oai-spgw  pgw-eth=eth0
juju config oai-spgw  DEFAULT_DNS_IPV4_ADDRESS=8.8.8.8
juju config oai-spgw  DEFAULT_DNS_SEC_IPV4_ADDRESS=2.2.2.2

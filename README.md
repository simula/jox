JOX is composed of the following directories: 

|-- charms
|   |-- bundle
|   |  |-- oai-nfv-rf
|   |  |-- oai-nfv-rrh 
|   |  |-- oai-nfv-sim
|   |-- trusty
|   |   |-- oai-enb
|   |   |-- oai-epc
|   |   |-- oai-hss
|   |   |-- oai-mme
|   |   |-- oai-rrh
|   |   |-- oaisim-enb-ue
|   |   |-- oai-spgw
|   |-- xenial
|-- README.md
|-- scripts
    |-- build_jox
    |-- tools
        |-- build_helper
        
        
To add:
- virt type of physical machines
- additional capabilities (tags)
 juju model-config enable-os-refresh-update=false enable-os-upgrade=false
- ES ubunut 16 
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
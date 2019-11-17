JOX is composed of the following directories: 

``` 
.
├── joxenv
├── jox.sh
├── nbi.sh
├── scripts
│   ├── build_jox_1.1
│   ├── build_jox_16.sh
│   ├── build_jox.sh
│   ├── deploy_template_1.1.sh
│   ├── pkg_gen.bash
│   └── tools
│       └── build_helper
├── src
│   ├── common
│   │   └── config
│   │       ├── gv.py
│   │       └── jox_config.json
│   ├── core
│   │   ├── nso
│   │   │   ├── nsi
│   │   │   │   ├── nsi_controller.py
│   │   │   │   └── slice.py
│   │   │   ├── nssi
│   │   │   │   ├── model.py
│   │   │   │   ├── nssi_controller.py
│   │   │   │   ├── service.py
│   │   │   │   └── subslice.py
│   │   │   ├── plugins
│   │   │   │   └── juju2_plugin.py
│   │   │   └── template_manager
│   │   │       └── template_manager.py
│   │   └── ro
│   │       ├── cloud.py
│   │       ├── monitor.py
│   │       ├── plugins
│   │       │   └── es.py
│   │       ├── resource_controller.py
│   │       └── vim_driver
│   │           └── vimdriver.py
│   ├── helpers
│   │   └── extract_info_juju_machine.py
│   ├── jox.py
│   └── nbi
│       ├── apidoc.json
│       ├── app.py
│       └── tasks.py
└── tests
    ├── add_macine.py
    ├── configs.py
    ├── jox_test_1.1.py
    └── settings.py
```
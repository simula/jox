#!/bin/bash

sudo service rabbitmq-server start
python3 src/nbi/app.py 

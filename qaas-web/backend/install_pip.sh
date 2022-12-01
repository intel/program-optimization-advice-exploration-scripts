#!/bin/bash

#FLASK_DIR=/nfs/site/proj/alac/members/yue/web-service
#TODO: Ability to use non-script directory
FLASK_DIR=$(pwd)
cd $FLASK_DIR
python3 -m venv ./venv
source ./venv/bin/activate
echo Using Proxy: $http_proxy
pip3 install --proxy $http_proxy -r requirements.txt
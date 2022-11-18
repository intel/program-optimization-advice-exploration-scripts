#!/bin/bash

FLASK_DIR=/nfs/site/proj/alac/members/yue/qaas/qaas/qaas-web/backend
cd $FLASK_DIR
python3 -m venv ./venv
source ./venv/bin/activate
echo Using Proxy: $http_proxy
pip3 install --proxy $http_proxy -r requirements.txt
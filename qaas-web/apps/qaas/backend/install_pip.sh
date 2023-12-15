#!/bin/bash

FLASK_DIR=$(pwd)
cd $FLASK_DIR
if [ -z "$http_proxy" ]; then
    sudo pip3 install -r ../../requirements.txt
else
    sudo pip3 install --proxy $http_proxy -r ../../requirements.txt
fi

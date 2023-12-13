#!/bin/bash

if [[ -z "$http_proxy" ]] || [[ ! "$http_proxy" =~ ^http://[a-zA-Z0-9.-]+(:[0-9]+)?$ ]]; then
    sudo pip3 install -r ./local_requirements.txt
else
    sudo pip3 install --proxy $http_proxy -r ./local_requirements.txt
fi

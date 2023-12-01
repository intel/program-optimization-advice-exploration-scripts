#!/bin/bash

if [ -z "$http_proxy" ]; then
    sudo pip3 install -r ./local_requirements.txt
else
    sudo pip3 install --proxy $http_proxy -r ./local_requirements.txt
fi

#!/bin/bash

#FLASK_DIR=/nfs/site/proj/alac/members/yue/web-service
#TODO: Ability to use non-script directory
FLASK_DIR=/nfs/site/proj/alac/members/yue/qaas/qaas/qaas-web/backend

QAAS_ROOT=/nfs/site/proj/alac/members/yue/qaas/qaas
BACKPLANE_DIR=${QAAS_ROOT}/qaas-backplane/src

source $FLASK_DIR/venv/bin/activate
echo PATYPATH: ${BACKPLANE_DIR}
PYTHONPATH=${BACKPLANE_DIR} python3 server.py

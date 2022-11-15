#!/bin/bash

FLASK_DIR=/nfs/site/proj/alac/members/yue/web-service
QAAS_ROOT=/nfs/site/proj/alac/members/yue/qaas/qaas
BACKPLANE_DIR=${QAAS_ROOT}/qaas-backplane/src

source $FLASK_DIR/venv/bin/activate
PYTHONPATH=${BACKPLANE_DIR} python3 server.py

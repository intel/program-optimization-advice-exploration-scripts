#!/bin/bash

FLASK_DIR=/nfs/site/proj/alac/members/yue/web-service
cd $FLASK_DIR
python3 -m venv ./venv
source ./venv/bin/activate
echo Using Proxy: $http_proxy
pip3 install --proxy $http_proxy Flask \
  Flask-Cors Flask-SocketIO Flask-SQLAlchemy \
  gevent gevent-websocket \
  mysqlclient numpy \
  pandas python-dateutil \
  python-socketio \
  SQLAlchemy Werkzeug 
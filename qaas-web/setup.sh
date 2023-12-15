#!/bin/bash

me=$(basename $(pwd))

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up $me"
  # Done, quit and not the execute code below.
else
  echo -n "Enter Qaas DB user password:"
  read -s QAAS_DB_PASSWORD
  echo "INSIDE container setting up $me"
  sed 's/#DB_USER_NAME#/qaas/g ; s/#DB_USER_PASSWD#/'${QAAS_DB_PASSWORD}'/g' ./config/qaas-web.conf.template > ./config/qaas-web.conf
  cd deployment
  python3 install.py
fi


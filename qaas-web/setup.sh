#!/bin/bash

me=$(basename $(pwd))
HTPASSWD_FILE="/etc/apache2/auth/.htpasswd"
USERNAME="qaas"

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up $me"
  # Done, quit and not the execute code below.
  echo -n "Enter Qaas DB user password:"
  read -s QAAS_DB_PASSWORD
  sed 's/#DB_USER_NAME#/qaas/g ; s/#DB_USER_PASSWD#/'${QAAS_DB_PASSWORD}'/g' ./apps/config/qaas-web.conf.template > ./apps/config/qaas-web.conf
else
  echo "INSIDE container setting up $me"
  echo "Setting up QaaS Web User Using Same Password As Database: " 
  # Getting back password from conf file
  QAAS_DB_PASSWORD=$(grep SQLALCHEMY_DATABASE_SERVER apps/config/qaas-web.conf |grep "mysql:"|cut -f1 -d@|cut -f3 -d:)
  echo Password is ${QAAS_DB_PASSWORD}
  echo -n $QAAS_DB_PASSWORD | htpasswd -i -c $HTPASSWD_FILE $USERNAME
  cd deployment
  python3 install.py  
fi




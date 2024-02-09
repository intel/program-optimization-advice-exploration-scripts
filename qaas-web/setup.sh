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
  sed 's/#DB_USER_NAME#/qaas/g ; s/#DB_USER_PASSWD#/'${QAAS_DB_PASSWORD}'/g' ./apps/config/alembic.ini.template > ./apps/config/alembic.ini
  echo "Starting persistent webdb container"
  ../container/run-container.sh -i local_image_qaas:latest -p -d -r ./deployment/entrypoint.sh
else
  echo "INSIDE ${QAAS_CONTAINER_NAME} container setting up $me"
  if [[ ${QAAS_CONTAINER_NAME} == "webdb" ]]; then
    echo "Setting up webdb in ${QAAS_CONTAINER_NAME} container"
    echo "Setting up QaaS Web User Using Same Password As Database: " 
    # Getting back password from conf file
    QAAS_DB_PASSWORD=$(grep SQLALCHEMY_DATABASE_SERVER apps/config/qaas-web.conf |grep "mysql:"|cut -f1 -d@|cut -f3 -d:)
    echo Password is ${QAAS_DB_PASSWORD}
    # Below few commands will update apache info in volumes (passwd and config)
    echo -n $QAAS_DB_PASSWORD | sudo htpasswd -i -c $HTPASSWD_FILE $USERNAME
    cat deployment/000-default.conf | sudo tee /etc/apache2/sites-available/000-default.conf
    sudo a2ensite 000-default.conf
    cd deployment
    sudo -E python3 install.py  
    sudo -E python3 start_server.py
  else 
    echo "Skipping webdb setup in ${QAAS_CONTAINER_NAME} container"
  fi
fi




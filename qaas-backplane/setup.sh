#!/bin/bash

me=$(basename $(pwd))

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up $me"
  # Done, quit and not the execute code below.
  echo "Starting persistent backplane container"
  ../container/run-container.sh -i local_image_qaas_backplane:latest -p -d -r /home/qaas/QAAS_SCRIPT_ROOT/scripts/backplane_entrypoint.sh
else
  echo "INSIDE ${QAAS_CONTAINER_NAME} container setting up $me"
  echo "Nothing to do"
fi




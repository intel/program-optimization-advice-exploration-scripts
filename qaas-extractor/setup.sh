#!/bin/bash

me=$(basename $(pwd))

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up $me"
  # Done, quit and not the execute code below.
  echo "Nothing to do"
else
  echo "INSIDE ${QAAS_CONTAINER_NAME} container setting up $me"
  if [[ ${QAAS_CONTAINER_NAME} == "backplane" ]]; then
    echo "Building extractor in ${QAAS_CONTAINER_NAME} container"
    script_root=$(grep QAAS_SCRIPT_ROOT ../qaas-backplane/config/qaas.conf |cut -f2 -d'=')
    extractor_path=${script_dir}/qaas-extractor

    # Build source code extractor
    make clean; make
    echo "Finished rest of setup inside the container for $me."
    echo "To use extractor, please run ../container/run-container.sh and try the extractCodelet.py script."
  else
    echo "Skipping extractor build in ${QAAS_CONTAINER_NAME} container"
  fi
fi

#!/bin/bash

# Run setup scripts for different components of qaas script.
run_component_setup() {
  # Currently under the directory of setup.sh
  for component in qaas-extractor qaas-web qaas-backplane; do
  # for component in qaas-web; do
    cd ${component}
    ./setup.sh
    cd ..
  done

}

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up local image"
  # Build local image

  echo -n "Customized dockerfile for backplane container (Press enter for none):"
  read custom_dockerfile

  pushd container
  if [ -z $custom_dockerfile ]; then
    ./build-local-image.sh
  else
    echo "Customized dockerfile: ${custom_dockerfile}"
    ./build-local-image.sh -f $custom_dockerfile
  fi
  popd

  # Setup components outside the container
  run_component_setup

  # Run this script again inside to set up the rest
  echo "Proceed rest of setup INSIDE WEBDB container"
  ./container/run-container.sh -i local_image_qaas:latest ./setup.sh
  echo "Proceed rest of setup INSIDE BACKPLANE container"
  ./container/run-container.sh -i local_image_qaas_backplane:latest ./setup.sh
  #don't put setup.sh next to run container, it thinks it is a parameter, instead just call setup in run container
  #./container/run-container.sh 
  # Done, quit and not the execute code below.
else
  echo "INSIDE ${QAAS_CONTAINER_NAME} container setting up TOPMOST script"
  run_component_setup
  #start server
  # SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
  # start_server_script_path=$SCRIPT_DIR/qaas-web/deployment/start_server.py
  # python3 ${start_server_script_path}

  # exec su qaas
fi

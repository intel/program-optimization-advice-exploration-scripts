#!/bin/bash

# Run setup scripts for different components of qaas script.
run_component_setup() {
  # Currently under the directory of setup.sh
  for component in qaas-extractor qaas-web; do
  # for component in qaas-web; do
    cd ${component}
    ./setup.sh
    cd ..
  done

}

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up local image"
  # Build local image
  pushd container
  ./build-local-image.sh
  popd

  # Setup components outside the container
  run_component_setup

  # Run this script again inside to set up the rest
  echo "Proceed rest of setup INSIDE container"
  # ./container/run-container.sh ./setup.sh
  #don't put setup.sh next to run container, it thinks it is a parameter, instead just call setup in run container
  ./container/run-container.sh 
  # Done, quit and not the execute code below.
else
  echo "INSIDE container setting up TOPMOST script"
  run_component_setup
  #start server
  SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
  start_server_script_path=$SCRIPT_DIR/qaas-web/deployment/start_server.py
  python3 ${start_server_script_path}

  exec su qaas
fi

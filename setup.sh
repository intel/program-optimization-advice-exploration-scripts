#!/bin/bash

# Run setup scripts for different components of qaas script.
run_component_setup() {
  # Currently under the directory of setup.sh
  for component in qaas-extractor qaas-web; do
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
  ./container/run-container.sh ./setup.sh
  # Done, quit and not the execute code below.
else
  echo "INSIDE container setting up TOPMOST script"
  run_component_setup
fi

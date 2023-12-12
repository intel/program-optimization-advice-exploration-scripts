#!/bin/bash

# Run setup scripts for different components of qaas script.

if [[ ${USER} != "qaas" ]]; then
  echo "Outside container setting up local image and then resume inside container"
  # Build local image
  pushd container
  ./build-local-image.sh

  # Run the script again inside to set up the rest
  popd
  ./container/run-container.sh ./setup.sh
  # Done, quit and not the execute code below.
  exit
fi

echo "Now setting up rest inside container"
# Currently under the directory of setup.sh

for component in qaas-extractor qaas-web; do
  cd ${component}
  ./setup.sh
  cd ..
done

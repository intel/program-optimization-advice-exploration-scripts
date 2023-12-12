#!/bin/bash

me=$(basename $(pwd))

if [[ ${USER} != "qaas" ]]; then
  echo "Outside container setting up $me"
  ../container/run-container.sh ./setup.sh
  # Done, quit and not the execute code below.
  exit
fi

echo "Now setting up rest inside container"
# Currently under the directory of setup.sh

# Build source code extractor
make clean; make

echo "Finished rest of setup inside the container for $me."
echo "To use extractor, please run ../container/run-container.sh and try the extractCodelet.py script."
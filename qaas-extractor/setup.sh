#!/bin/bash

me=$(basename $(pwd))

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up $me"
  # Done, quit and not the execute code below.
else
  echo "INSIDE container setting up $me"

  # Build source code extractor
  make clean; make
  echo "Finished rest of setup inside the container for $me."
  echo "To use extractor, please run ../container/run-container.sh and try the extractCodelet.py script."
fi

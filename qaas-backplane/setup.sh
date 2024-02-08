#!/bin/bash

me=$(basename $(pwd))

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up $me"
  # Done, quit and not the execute code below.
else
  echo "INSIDE container setting up $me"
  sudo -E pip3 install pytrie numpy py-cpuinfo
fi




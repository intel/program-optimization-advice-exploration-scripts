#!/bin/bash

# Stop a running qaas container
docker stop qaas_webdb
docker container rm qaas_webdb

docker stop qaas_backplane
docker container rm qaas_backplane

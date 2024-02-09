#!/bin/bash

# Stop a running qaas container
docker stop qaas_container
docker container rm qaas_container

docker stop qaas_backplane
docker container rm qaas_backplane

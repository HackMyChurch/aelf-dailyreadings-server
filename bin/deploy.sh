#!/bin/bash

set -e
set -x

# Get connection details
eval $(docker-machine env core2)

# Deploy
docker build -t aelf-api .
docker stop aelf-api
docker rm aelf-api
docker run --name aelf-api -d -p 4001:4000 --restart always aelf-api

# Follow
docker logs -f aelf-api


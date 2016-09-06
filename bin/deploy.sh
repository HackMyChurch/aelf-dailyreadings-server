#!/bin/bash

set -e
set -x

# Get connection details
eval $(docker-machine env aelf)

# Deploy
docker build -t aelf-api .

if docker ps | grep -q aelf-api
then
    docker stop aelf-api
    docker rm aelf-api
fi
docker run --name aelf-api -d -p 4001:4000 --restart always aelf-api

# Follow
docker logs -f aelf-api


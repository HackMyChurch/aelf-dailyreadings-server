#!/bin/bash

set -e

TAG=$(date +"%Y-%m-%d-%H-%M-%S")

# Build
for machine in $(docker-machine ls --quiet | grep 'prod\.epitre\.co$')
do
    (
        echo "[INFO] Starting build of 'aelf-api:$TAG' on $machine"
        eval $(docker-machine env $machine)
        docker build --quiet -t "aelf-api:$TAG" .
        echo "[INFO] Finished build of 'aelf-api:$TAG' on $machine"
    )&
done
wait

# Deploy
eval $(docker-machine env gra-01.prod.epitre.co)
if docker service inspect aelf-api &>/dev/null
then
    echo "[INFO] Updating service 'aelf-api:$TAG'"
    docker service update --image aelf-api:$TAG aelf-api
else
    echo "[INFO] Creating service 'aelf-api:$TAG'"
    docker service create --mode global --restart-condition any --name aelf-api -p 4001:4000 aelf-api:$TAG
fi

# Follow
echo "[INFO] All done!"


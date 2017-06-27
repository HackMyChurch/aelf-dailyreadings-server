#!/bin/bash

set -e

TAG=$(date +"%Y-%m-%d-%H-%M-%S")

# Determine environment
case $1 in
    prod)
        echo "[INFO] Will deploy in *prod* mode"
        DOCKER_NAME="aelf-api"
        DOCKER_PORT=4001
        ;;
    *)
        echo "[INFO] Will deploy in *BETA* mode (to deploy in prod, use --> $0 prod)"
        DOCKER_NAME="aelf-api-beta"
        DOCKER_PORT=4002
        ;;
esac

# Build
for machine in $(docker-machine ls --quiet | grep 'prod\.epitre\.co$')
do
    (
        echo "[INFO] Starting build of '${DOCKER_NAME}:${TAG}' on $machine"
        eval $(docker-machine env $machine)
        docker build --quiet -t "${DOCKER_NAME}:${TAG}" .
        echo "[INFO] Finished build of '${DOCKER_NAME}:${TAG}' on $machine"
    )&
done
wait

# Deploy
eval $(docker-machine env gra-01.prod.epitre.co)
if docker service inspect ${DOCKER_NAME} &>/dev/null
then
    echo "[INFO] Updating service '${DOCKER_NAME}:${TAG}:$TAG'"
    docker service update --image ${DOCKER_NAME}:${TAG} --publish-add ${DOCKER_PORT}:4000 ${DOCKER_NAME}
else
    echo "[INFO] Creating service '${DOCKER_NAME}:${TAG}:$TAG'"
    docker service create --mode global --restart-condition any --name ${DOCKER_NAME} -p ${DOCKER_PORT}:4000 ${DOCKER_NAME}:${TAG}
fi

# Follow
echo "[INFO] All done!"
docker service logs --tail 10 --follow ${DOCKER_NAME}


#!/bin/bash

set -e

# Make sure we have the dicts
DICT_VERSION="6.3"
DICT_ARCHIVE="hunspell-french-dictionaries-v${DICT_VERSION}.zip"
if ! [ -f "${DICT_ARCHIVE}" ]
then
    wget "http://www.dicollecte.org/download/fr/${DICT_ARCHIVE}"
fi

unzip -o "${DICT_ARCHIVE}" "fr-classique.aff" "fr-classique.dic"

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
TAG=$(date +"%Y-%m-%d-%H-%M-%S")
for machine in $(docker-machine ls --quiet | grep 'prod\.epitre\.co$' | grep -v '^mon')
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
    echo "[INFO] Updating service '${DOCKER_NAME}:${TAG}'"
    docker service update --image ${DOCKER_NAME}:${TAG} ${DOCKER_NAME}
else
    echo "[INFO] Creating service '${DOCKER_NAME}:${TAG}'"
    docker service create --mode global --restart-condition any --name ${DOCKER_NAME} --publish published=${DOCKER_PORT},target=4000,mode=host ${DOCKER_NAME}:${TAG}
fi

# Follow
echo "[INFO] All done!"
docker service logs --tail 10 --follow ${DOCKER_NAME}


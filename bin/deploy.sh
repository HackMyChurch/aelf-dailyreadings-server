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

# Build and deploy
TAG=$(date +"%Y-%m-%d-%H-%M-%S")
for machine in $(docker context ls --quiet | grep 'prod\.epitre\.co$' | grep -v '^mon')
do
    (
        echo "[INFO] Starting build of '${DOCKER_NAME}:${TAG}' on $machine"
        docker --context "${machine}" build --quiet -t "${DOCKER_NAME}:${TAG}" .

        if docker --context "${machine}" container inspect ${DOCKER_NAME} &>/dev/null
        then
            echo "[INFO] Removing container '${DOCKER_NAME}:${TAG}'"
            docker --context "${machine}" rm "${DOCKER_NAME}"
        fi

        echo "[INFO] Creating container '${DOCKER_NAME}:${TAG}'"
        docker --context "${machine}" run --detach --restart always --name ${DOCKER_NAME} --publish published=${DOCKER_PORT},target=4000,mode=host ${DOCKER_NAME}:${TAG}

        echo "[INFO] Garbage-collecting Docker"
        docker --context "${machine}" system prune --all --force

        echo "[INFO] Finished deploying '${DOCKER_NAME}:${TAG}' on $machine"
    )&
done

# Collect
wait
echo "[INFO] All done!"

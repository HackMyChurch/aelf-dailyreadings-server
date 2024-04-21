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
        HOSTS="prod.api.app.epitre.co"
        DOCKER_NAME="aelf-api"
        DOCKER_PORT=4001
        ;;
    *)
        echo "[INFO] Will deploy in *BETA* mode (to deploy in prod, use --> $0 prod)"
        HOSTS="beta.api.app.epitre.co"
        DOCKER_NAME="aelf-api-beta"
        DOCKER_PORT=4002
        ;;
esac

# Build and deploy
TAG=$(date +"%Y-%m-%d-%H-%M-%S")
for machine_ip in $(dig +short "${HOSTS}")
do
    machine="$(dig +short -x "${machine_ip}")"
    (
        echo "[INFO] Starting build of '${DOCKER_NAME}:${TAG}' on $machine (${machine_ip})"
        docker --host "ssh://root@${machine_ip}" build --quiet -t "${DOCKER_NAME}:${TAG}" .

        if docker --host "ssh://root@${machine_ip}" container inspect ${DOCKER_NAME} &>/dev/null
        then
            echo "[INFO] Removing container '${DOCKER_NAME}:${TAG}'"
            docker --host "ssh://root@${machine_ip}" rm --force "${DOCKER_NAME}"
        fi

        echo "[INFO] Creating container '${DOCKER_NAME}:${TAG}'"
        docker --host "ssh://root@${machine_ip}" run --detach --restart always --name ${DOCKER_NAME} --publish published=${DOCKER_PORT},target=4000,mode=host ${DOCKER_NAME}:${TAG}

        echo "[INFO] Garbage-collecting Docker"
        docker --host "ssh://root@${machine_ip}" system prune --force

        echo "[INFO] Finished deploying '${DOCKER_NAME}:${TAG}' on $machine"
    )&
done

# Collect
wait
echo "[INFO] All done!"

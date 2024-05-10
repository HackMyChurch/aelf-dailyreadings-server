#!/bin/bash

set -e

#
# Parse arguments
#

POSITIONAL_ARGS=()

LIMIT="*"
while [[ $# -gt 0 ]]
do
    case $1 in
        -l|--limit)
            LIMIT="$2"
            shift
            ;;
        -*)
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            ;;
    esac
    shift
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

APP_ENV=${1:-beta}

# Determine environment
case "${APP_ENV}" in
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

#
# Fetch the dictionnaries
#

# Make sure we have the dicts
DICT_VERSION="6.3"
DICT_ARCHIVE="hunspell-french-dictionaries-v${DICT_VERSION}.zip"
if ! [ -f "${DICT_ARCHIVE}" ]
then
    wget "http://www.dicollecte.org/download/fr/${DICT_ARCHIVE}"
fi

unzip -o "${DICT_ARCHIVE}" "fr-classique.aff" "fr-classique.dic"

#
# Build and start the application
#

# Build Docker run command
DOCKER_RUN_ARGS=""
DOCKER_RUN_ARGS="${DOCKER_RUN_ARGS} --detach --restart always"
DOCKER_RUN_ARGS="${DOCKER_RUN_ARGS} --publish published=${DOCKER_PORT},target=4000,mode=host"
DOCKER_RUN_ARGS="${DOCKER_RUN_ARGS} --env DD_PROFILING_ENABLED=true"
DOCKER_RUN_ARGS="${DOCKER_RUN_ARGS} --env DD_ENV=${APP_ENV}"
DOCKER_RUN_ARGS="${DOCKER_RUN_ARGS} --env DD_SERVICE=aelf-api"

function deploy_on() {
    local machine="$1"

    echo "[INFO] Starting build of '${DOCKER_NAME}:${TAG}' on $machine"
    docker --host "ssh://root@${machine}" build --quiet -t "${DOCKER_NAME}:${TAG}" .

    if docker --host "ssh://root@${machine}" container inspect ${DOCKER_NAME} &>/dev/null
    then
        echo "[INFO] Removing container '${DOCKER_NAME}:${TAG}'"
        docker --host "ssh://root@${machine}" rm --force "${DOCKER_NAME}"
    fi

    echo "[INFO] Creating container '${DOCKER_NAME}:${TAG}'"
    docker --host "ssh://root@${machine}" run ${DOCKER_RUN_ARGS} --name ${DOCKER_NAME} ${DOCKER_NAME}:${TAG}

    echo "[INFO] Garbage-collecting Docker"
    docker --host "ssh://root@${machine}" system prune --force

    echo "[INFO] Finished deploying '${DOCKER_NAME}:${TAG}' on $machine"
}

# Build and deploy
TAG=$(date +"%Y-%m-%d-%H-%M-%S")
for machine_ip in $(dig +short "${HOSTS}")
do
    machine="$(dig +short -x "${machine_ip}")"

    if [[ "${machine}" != ${LIMIT} ]]
    then
        echo "[INFO] Skipping ${machine} (not included by "${LIMIT}" pattern)"
        continue
    fi

    (
        # Attempt deployment up to 3 times
        for i in {1..3}
        do
            if deploy_on "${machine}"
            then
                exit 0
            fi
        done

        echo "[ERROR] Failed to deploy on ${machine}"
        exit 1
    )&
done

# Collect
wait
echo "[INFO] All done!"

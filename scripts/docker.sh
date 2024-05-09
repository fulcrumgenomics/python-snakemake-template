#!/usr/bin/env bash

###############################################################################
# Script that builds Docker images from targets in the Dockerfile. It is
# expected that there is a 1:1 correspondence between Mamba config files in
# dependencies/ and Docker images. Images are tagged with
# '<project>/<conf>:<version>', where <project> is the name of the project and
# defaults to .env/PROJECT if set, otherwise the root folder name; <conf> is the
# name of the Mamba config file without the .yml extension, and <version>
# defaults to .env/VERSION if set, otherwise 1.0. The project and version can
# be overriden by the -n and -v options, respectively.
###############################################################################

set -ex

usage() {
    cat <<EOF
Usage: $0 [options] [name...]

All images are built unless specific images are listed by name.

Optional:
    -n NAME     Project name to use when tagging images
    -v VERSION  Version to use when tagging images
    -f          Force Docker to rebuild all images
    -m          Build image to run on ARM Mac
EOF
    # shellcheck disable=SC2188
    >&2
    exit 1
}

parent=$(cd "$(dirname "$0")" && pwd -P)
root="$(dirname "${parent}")"
confs="${root}/dependencies"

# load default environment variables
# shellcheck source=../.env
source "${root}/.env"

project="$(basename "${root}")"
if [ -n "${PROJECT}" ]; then
    project="${PROJECT}"
fi
version="1.0"
if [ -n "${DOCKER_IMAGE_VERSION}" ]; then
    version="${DOCKER_IMAGE_VERSION}"
fi
rosetta_options=()
force_option=""
while getopts "n:v:mf" flag; do
    case "${flag}" in
    n) project=${OPTARG} ;;
    v) version=${OPTARG} ;;
    m) rosetta_options=(--platform linux/amd64 --load) ;;
    f) force_option="--no-cache" ;;
    *) usage ;;
    esac
done
shift $((OPTIND - 1))

docker_build() {
    docker build \
        --progress=plain \
        "${rosetta_options[@]}" \
        ${force_option} \
        --target "${1}" \
        -t "${project}/${1}:${version}" \
        -f "${root}/docker/Dockerfile" \
        "${root}"
}

if [ "$#" -eq 0 ]; then
    # build all images
    for conf_yml in "${confs}"/*.yml; do
        filename=$(basename -- "${conf_yml}")
        target="${filename%.yml}"
        # ignore dev.yml
        if [ "${target}" = "dev" ]; then
            continue
        fi
        docker_build "${target}"
    done
else
    for target in "$@"; do
        docker_build "${target}"
    done
fi

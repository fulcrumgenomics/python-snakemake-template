#!/usr/bin/env bash

###############################################################################
# Script that sets up the conda environment for development by installing all
# the dependencies into the same environment. By default, only the 'dev'
# dependencies are installed, but additional config files can be listed by name
# (without the .yml extension) as positional arguments, or all dependencies can
# be installed with the -a flag. The environment name defaults to .dependencies/PROJECT
# (or the root folder name if unset), but can be overridden with the -n flag.
###############################################################################

set -ex

usage() {
    cat <<EOF
Usage: $0 [options] [env...]

The 'dev' dependencies are installed by default. Additional config files can be listed 
by name (without the .yml extension).

Optional:
    -A  Activate the environment
    -R  Remove all packages from the environment before installing
    -m  Name/path of Mamba executable (defaults to 'mamba')
    -n  Specify the env name (defaults to the project name)
    -a  Install all dependencies
    -o  Only install the specified dependencies (i.e. do not install default dependencies)
EOF
    # shellcheck disable=SC2188
    >&2
    exit 1
}

parent=$(cd "$(dirname "$0")" && pwd -P)
root="$(dirname "${parent}")"
confs="${root}/dependencies"

# load defaults from .env
# shellcheck source=../.env
source "${root}/.env"

env="$(basename "${root}")"
if [ -n "${PROJECT}" ]; then
    env="${PROJECT}"
fi
activate=false
remove_all=false
mamba="mamba"
all=false
only=false
while getopts "ARaom:n:" flag; do
    case "${flag}" in
    A) activate=true ;;
    R) remove_all=true ;;
    m) mamba="${OPTARG}" ;;
    n) env="${OPTARG}" ;;
    a) all=true ;;
    o) only=true ;;
    *) usage ;;
    esac
done
shift $((OPTIND - 1))

is_micromamba=false
if [[ "${mamba}" =~ micro ]]; then
    is_micromamba=true
fi

env_exists() {
    ${mamba} env list | grep -F "${env} " >/dev/null
}

create_env() {
    if ${is_micromamba}; then
        command=("${mamba}" create --name "${env}" --no-dependencies)
    else
        command=("${mamba}" create --name "${env}" --no-default-packages)
    fi
    "${command[@]}"
}

remove_all() {
    if ${is_micromamba}; then
        command=("${mamba}" remove --name "${env}" --all)
    else
        command=("${mamba}" env remove --name "${env}" --all)
    fi
    "${command[@]}"
}

activate_env() {
    ${mamba} activate "${env}"
}

install_dependencies() {
    if ${is_micromamba}; then
        command=("${mamba}" update -y --name "${env}" --file "${confs}/${1}.yml")
    else
        command=("${mamba}" env update --name "${env}" --file "${confs}/${1}.yml")
    fi
    "${command[@]}"
}

clean_env() {
    ${mamba} clean --all --yes
}

if ! env_exists; then
    create_env
elif ${remove_all}; then
    remove_all
fi

if ${only}; then
    for conf in "$@"; do
        install_dependencies "${conf}"
    done
elif ${all}; then
    for conf_yml in "${confs}"/*.yml; do
        filename=$(basename -- "${conf_yml}")
        conf="${filename%.yml}"
        install_dependencies "${conf}"
    done
else
    install_dependencies dev
    for conf in "$@"; do
        install_dependencies "${conf}"
    done
fi

clean_env

if ${activate}; then
    activate_env
fi

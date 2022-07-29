#!/usr/bin/env bash

###############################################################################
# Script that should be run pre-commit after making any changes to the pyclient
# package / subdirectory.
#
# Runs:
#   Unit tests
#   Linting
#   Type checking
###############################################################################

set -e

failures=""

function banner() {
    echo
    echo "================================================================================"
    echo "$*"
    echo "================================================================================"
    echo
}

#####################################################################
# Takes two parameters, a "name" and a "command". 
# Runs the command and prints out whether it succeeded or failed, and
# also tracks a list of failed steps in $failures.
#####################################################################
function run() {
    local name=$1
    local cmd=$2

    banner "Running $name [$cmd]"
    set +e
    $cmd
    exit_code=$?
    set -e
    
    if [[ $exit_code == 0 ]]; then
        echo Passed $name 
    else
        echo Failed $name [$cmd]
        if [ -z "$failures" ]; then
            failures="$failures $name"
        else
            failures="$failures, $name"
        fi
    fi
}

parent=$(cd "$(dirname $0)" && pwd -P)
repo_root=$(dirname ${parent})
root=${repo_root}/src/python

if [[ -z ${CONDA_DEFAULT_ENV} ]]; then
    banner "Conda not active. pyclient conda environment must be active."
    exit 1
fi

pushd $root > /dev/null
banner "Executing in conda environment ${CONDA_DEFAULT_ENV} in directory ${root}"
run "Unit Tests"                "pytest -vv -r sx pyclient"
run "Style Checking"            "black --line-length 99 --check pyclient"
run "Linting"                   "flake8 --config=$parent/flake8.cfg pyclient"
run "Type Checking"             "mypy -p pyclient --config $parent/mypy.ini"
run "Shell Check (src/scripts)" "shellcheck ${repo_root}/src/scripts/*sh"
run "Shell Check (precommit)"   "shellcheck ${repo_root}/src/scripts/pypact/precommit.sh"
popd > /dev/null

if [ -z "$failures" ]; then
    banner "Precommit Passed"
else
    banner "Precommit Failed with failures in: $failures"
    exit 1
fi


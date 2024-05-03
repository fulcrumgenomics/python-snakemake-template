#!/usr/bin/env bash

###############################################################################
# Script that should be run pre-commit after making any changes to the toolkit
# package / subdirectory. By default, it performs checks on the python code and
# run unit tests, and fails if any of those steps fail. With the -f and -l
# options, it can automatically reformat and fix (some) lints, respetively. This
# script is also run by the CI action in github.
#
# Runs:
#   Unit tests
#   Linting
#   Type checking
#   Style checking (for both python and bash scripts)
###############################################################################

set -ex

failures=""

usage() {
    cat <<EOF
Usage: $0 [options] 

Optional:
    -f    Automatically fix formatting.
    -l    Automatically fix lints.
EOF
    # shellcheck disable=SC2188
    >&2
    exit 1
}

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
        echo "Passed $name"
    else
        echo "Failed $name [$cmd]"
        if [ -z "$failures" ]; then
            failures="$failures $name"
        else
            failures="$failures, $name"
        fi
    fi
}

parent=$(cd "$(dirname "$0")" && pwd -P)
repo_root="$(dirname "${parent}")"
root=${repo_root}/python

fix_format='false'
fix_lints='false'
while getopts "fl" flag; do
    case "${flag}" in
    f) fix_format='true' ;;
    l) fix_lints='true' ;;
    *) usage ;;
    esac
done
shift $((OPTIND - 1))

if [[ -z ${CONDA_DEFAULT_ENV} ]]; then
    banner "Conda environment must be active."
    exit 1
fi

if ${fix_format}; then
    pushd "$root" >/dev/null
    banner "Executing style fixes in conda environment ${CONDA_DEFAULT_ENV} in directory ${root}"
    run "Python Style Formatting" "ruff format"
    popd >/dev/null
fi

if ${fix_lints}; then
    pushd "$root" >/dev/null
    banner "Executing lint fixes in conda environment ${CONDA_DEFAULT_ENV} in directory ${root}"
    run "Python Lint Fixing" "ruff check --fix"
    popd >/dev/null
fi

pushd "$root" >/dev/null
banner "Executing checks in conda environment ${CONDA_DEFAULT_ENV} in directory ${root}"
run "Shell Check (scripts)" "shellcheck -x ${repo_root}/scripts/*sh"
run "Python Style Checking" "ruff format"
run "Python Linting" "ruff check"
run "Python Type Checking" "mypy ."
run "Python Unit Tests" "pytest -vv -r sx"
popd >/dev/null

if [ -z "$failures" ]; then
    banner "All checks Passed"
else
    banner "The following checks failed: $failures"
    exit 1
fi

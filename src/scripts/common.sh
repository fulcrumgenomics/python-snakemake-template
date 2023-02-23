#!/usr/bin/env bash

# Simplified logging function
function log() {
  >&2 printf "[%s] %b\n" "$(date +"%F %T %Z")" "$*"
}

# Determine how many cores to use by default
function find_core_limit() {
    if hash cgget 2>/dev/null; then
        cores=$(cgget -n --values-only --variable cpu.shares / | awk '{print int($1 / 1024.0)}')
    elif [[ -a /proc/cpuinfo ]]; then
        cores=$(grep -c ^processor /proc/cpuinfo)
    else
        cores=$(sysctl -n hw.ncpu)
    fi
    if [[ "$cores" -le "0" ]]; then
        log "Cores must be > 0: $cores"
        exit 1
    fi
    echo "$cores"
}

# Attempt to retrieve the amount of memory available for the pipeline.  If running in a
# docker container, then try to use `cgroups` to get the memory limit.  This fails if `--memory`
# is not set when running the docker container, so fall-back on the system resources otherwise.
# AWS should always be setting `--memory`, so this is only an issue when running manually.
function find_mem_limit_gb() {
    declare -a mem_limits
    if hash cgget 2>/dev/null; then
    # Source: https://stackoverflow.com/questions/42187085/check-mem-limit-within-a-docker-container
    # NB: convert from bytes to gigabytes
    # NB: Will correctly find the limit when set by `--memory` in a container. All other times returns a very large
    mem_limits=("${mem_limits[@]}" "$(cgget -n --values-only --variable memory.limit_in_bytes / | awk '{printf "%20.0f\n", int($1 / 1073741824.0)}')")
    fi
    if [[ -a /proc/meminfo ]]; then
    # NB: ignores `--memory` flag passed to a docker container
    # NB: convert from kilobytes to gigabytes
    mem_limits=("${mem_limits[@]}" "$(grep ^MemTotal /proc/meminfo | awk '{print int($2 / 1000000.0)}')")
    fi
    if hash sysctl 2>/dev/null && [[ "$OSTYPE" == "darwin"* ]]; then
    # NB: convert from bytes to gigabytes
    mem_limits=("${mem_limits[@]}" "$(sysctl -n hw.memsize | awk '{print int($1 / 1000000000.0)}')")
    fi

    # Check that we have at least one value
    if [[ "${#mem_limits[@]}" -le 0 ]]; then
        log "Could not determine available RAM."
        exit 1
    fi

    # Find min value
    mem_gb="${mem_limits[0]}"
    for lim in "${mem_limits[@]}"; do
        (( lim < mem_gb )) && mem_gb=$lim
    done

    if [[ "$mem_gb" -le "0" ]]; then
        log "Memory must be > 0: $mem_gb"
        exit 1
    fi
    echo "$mem_gb"
}

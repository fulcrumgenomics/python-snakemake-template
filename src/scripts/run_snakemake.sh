#!/usr/bin/env bash

usage() { 
    local err=${1:-""};
    cat <<EOF
Usage: $0 [options] 

Required:
    -s FILE   Input snakefile
    -o DIR    Output directory

Optional:
    -c FILE   Snakemake configuration file
    -n        Run snakemake in dry run mode
EOF
>&2;
    echo -e "\n$err" >&2;
    exit 1;
}

dry_run=""

while getopts "s:o:c:n" flag; do
    case "${flag}" in
        s) snakefile=${OPTARG};;
        o) out_dir=${OPTARG};;
        c) config_file=${OPTARG};;
        n) dry_run="-n";;
        *) usage;;
    esac
done
shift $((OPTIND-1))

extra_args=""
if [ -z "${snakefile}" ]; then
    usage "Missing required parameter -s";
fi
if [ -z "${out_dir}" ]; then
    usage "Missing required parameter -o";
fi
if [ ! -z "${config_file}" ]; then
    extra_args="--configfile $config_file";
fi


source $(dirname $0)/common.sh
cores=$(find_core_limit)
mem_gb=$(find_mem_limit_gb)
log "Number of cores: $cores"
log "Memory limit: $mem_gb GB"

# Run Snakemake pipeline
set -euo pipefail
snakemake \
  --printshellcmds \
  --reason \
  --nocolor \
  --keep-going \
  --rerun-incomplete \
  --jobs "$cores" \
  --resources "mem_gb=$mem_gb" \
  --snakefile $snakefile \
  --directory $out_dir \
  $dry_run \
  $extra_args;


log "All done!"

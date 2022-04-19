[![build](https://github.com/fulcrumgenomics/python-snakemake-skeleton/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/fulcrumgenomics/python-snakemake-skeleton/actions/workflows/pythonpackage.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/fulcrumgenomics/fgbio/blob/main/LICENSE)
[![Language](https://img.shields.io/badge/python-3.6.10-brightgreen)](https://www.python.org/downloads/release/python-3610/)

A skeleton repository for Snakemake pipepline(s) and a python command-line toolkit.

## Why this repo?

This the starting point for [Fulcrum Genomics][fulcrum-genomics-link] projects that contain Snakemake pipelines
and a python toolkit.

This repo contains the following, in no particular order:

- a hello world snakefile in `src/snakemake/hello_world.smk`
  - this uses the `onerror` directive to better display rule errors, in particular the last file
    lines of the rule's log
- a python toolkit (`clien-tools`) in `src/python/pyclient`
  - uses `defopt` for arg parsing
  - has custom logging in `core/logging.py`
  - has utility methods to support the above `onerror` snakemake directive in `pipeline/snakemake_utils.py`
  - has a unit test to ensure the above snakefile is runnable and generally executes the expected rules in `tests/test_hello_world.py`.
    This also includes a utility method to support running and verifying snakemake in `tests/util.py`
  - supports multiple sub-commands in `tools/__main__.py` with some nice logging when a tool fails
  - a little hello world tool in `tools/hello_world.py`

## Modifying this repo for a new client

This repo is a skeleton for Snakemake pipelines and a Python toolkit.

- [ ] Modify `setup.py`
- [ ] update `conda-requirements-minimal.txt` with minimal requirements for the `client-tools` toolkit
- [ ] update `conda-requirements-test.txt` with minimal requirements for the `client-tools` unit testing
- [ ] update `pip-requirements.txt` with minimal requirements for the `client-tools` (prefer conda)
- [ ] update `src/python/pyclient` source code (search for terms: `PYCLIENT`, `pyclient`, `client-tools`

## Install client-tools

- [Install conda][conda-link]


- Create the `pyclient` conda environment


```console
mamba create -n pyclient \
  --override-channels -y \
  -c bioconda -c conda-forge -c defaults \
  --file conda-requirements-minimal.txt \
  --file conda-requirements-test.txt
```

- Activate the `pyclient` conda environment

```bash
conda activate pyclient
```

- Install all non-conda dependencies via pip

```bash
pip install -r pip-requirements.txt
```

- Install `pyclient` (in developer mode)

```bash
python setup.py develop
```

- Validate the install via the help message

```bash
client-tools -h
```

- Validate the snakemake install

```bash
snakemake --snakefile src/snakemake/hello_world.smk -j 1
```

[fulcrum-genomics-link]: https://www.fulcrumgenomics.com
[conda-link]: https://docs.conda.io/projects/conda/en/latest/user-guide/install/


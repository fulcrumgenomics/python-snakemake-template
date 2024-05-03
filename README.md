# Workflow

This is a Snakemake workflow with a Python toolkit.

This project uses the following tools:

* Toolkit
  * Poetry for managing dependencies and for building/installing
  * Defopt for argument parsing
  * Pytest for testing the toolkit
  * Ruff for formatting and linting
  * Mypy for Python type checking
* Workflow
  * Snakemake for workflow execution
  * Mamba for package management
  * [Micromamba Docker](https://github.com/mamba-org/micromamba-docker) for containerization
  * [pytest-workflow](https://pytest-workflow.readthedocs.io/en/stable/) for testing the workflow

## Prerequisites

* [Poetry](https://python-poetry.org/docs/#installation): It is important that poetry is *not* installed in the same environment as your package dependencies. We recommend using the "official" installer:
```console
curl -sSL https://install.python-poetry.org | python3 -
```
* [Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)
* [Docker](https://docs.docker.com/engine/install/)

## Getting started

Set up your environment:

```console
bash scripts/mamba.sh [-A]
```

This will create a new environment with the same name as the project and will install the dependencies from [dependencies/dev.yml](dependencies/dev.yml).
You can specify a different environment name with the `-n` option.
The `-A` option causes the environment to be activated.

To activate the environment manually, run:

```console
mamba activate <project>
```

Each time you add dependencies to either of those files, re-run the script.

## Setting up the toolkit for development

The following command will install the toolkit in "editable" mode, which means it will use the source directory as the installation. This enables you to run tests on the code without having to re-install the package every time you make a change.

```console
cd python && poetry install
```

## Modifying the template

The [`.env`](.env) contains:
* A `PROJECT` variable that must be set to the name of the project. It defaults to "workflow", but that's probably not what you want.
* A `DOCKER_IMAGE_VERSION` variable that defaults to `1.0`.

After you finish reading this file, replace the contents with your project README.

## Adding a tool to the toolkit

The toolkit has a single entry point, `python/toolkit/tools/__main__.py`.
Each tool is a sub-command of the main entry point.
Some creative hacking of Defopt is done to enable common options to be defined for the top-level command.

`toolkit.Command` enumerates all the commands; each value is an instance of the `toolkit.tools.Tool` class, which wraps a `Callable` as well as some other metadata required by Defopt (the command name, short options, etc.).

The `run` function in `python/toolkit/tools/__main__.py` is the function that is called when the command is executed. It does the following:

* Parses any common options and returns the index of the first non-common option and a classl (`toolkit.tools.CommonOptions`) containing the parsed common options.
* Parses the sub-command and it's options.
* Executes the sub-command with the parsed options.

To use this framework:

* Add additional tools to `python/toolkit/tools/`, where each tool is a python file.
* Add a value to the `toolkit.Command` enum for each tool you create.
* Add any additional dependentices to `python/pyproject.toml`.

Note that DefOpt has the limitation that the same short name cannot be re-used for different parameters in different sub-commands. This is mostly a good thing as it encourages standardization between tools, but it does limit the pool of available short option names.

## Adding a rule to the workflow

If your new rule requires one or more tools that aren't available in one of the existing images, you'll need to add a new environment configuration file in [dependencies](dependencies/) with all of the packages required in your new image.
Next, modify [Dockerfile](Dockerfile) to add a build target for your new image, following the provided template.
Finally, to build your new image, run:

```console
bash scripts/docker.sh [-m] [-v VERSION] <target>
```

or to build all images run:

```console
bash scripts/docker.sh [-m] [-v VERSION] 
```

The `-m` option builds images that are compatible with an ARM Mac.
The `-v` option specifies the version with which to tag the images.


## Integration tests

Integration tests are defined in YAML files in the [tests](tests/) folder. See the [pytest-workflow docs](https://pytest-workflow.readthedocs.io/en/stable/) for details on how to write tests.

To run the integration tests:

```console
PROFILES=local,test[,rosetta|linux] pytest --git-aware tests/integration/
```

The `rosetta` profile is required on an ARM mac, and the `linux` profile is required on linux.
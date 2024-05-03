FROM mambaorg/micromamba:1.5.6 as base
# Install system-level dependencies as root
USER root
RUN apt-get update && apt-get install -y procps
USER $MAMBA_USER
# Set working directory
WORKDIR /workflow
# Uncomment this if lock files cause problems:
#RUN micromamba config set use_lockfiles False
# Uncomment these if downloads are too slow:
#RUN micromamba config set remote_connect_timeout_secs 300
#RUN micromamba config set remote_backoff_factor 10
#RUN micromamba config set remote_max_retries 5
# This completely disables timeouts due to slow downloads but it can result in a hung install:
#ENV MAMBA_NO_LOW_SPEED_LIMIT=1

# Build python toolkit
FROM base as toolkit-build
COPY --chown=$MAMBA_USER:$MAMBA_USER ./dependencies/dev.yml .
RUN micromamba install -y -n base -f dev.yml
RUN micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1
# TODO: add '--exclude=env' once that option becomes stable
COPY --chown=$MAMBA_USER:$MAMBA_USER ./python .
ADD --chown=$MAMBA_USER:$MAMBA_USER https://install.python-poetry.org install-poetry.py
RUN python3 install-poetry.py
ENV PATH="${PATH}:~/.local/bin"
# Build toolkit
RUN poetry build

# toolkit image
FROM base as toolkit
COPY --chown=$MAMBA_USER:$MAMBA_USER ./dependencies/toolkit.yml .
RUN micromamba install -y -n base -f toolkit.yml \
    && micromamba clean --all --yes \
    && rm -f toolkit.yml
ARG MAMBA_DOCKERFILE_ACTIVATE=1
COPY --from=toolkit-build --chown=$MAMBA_USER:$MAMBA_USER /workflow/dist/*.whl .
RUN pip install *.whl \
    && rm -f *.whl

# Additional images follow this general pattern. The target and the env .yml file
# must have the same name for scripts/docker.sh to work correctly.
#FROM base as <tool>
#COPY --chown=$MAMBA_USER:$MAMBA_USER ./dependencies/<tool>.yml .
#RUN micromamba install -y -n base -f <tool>.yml && rm <tool>.yml \
#   && micromamba clean --all --yes \
#   && rm -Rf <tool>.yml
#ARG MAMBA_DOCKERFILE_ACTIVATE=1

FROM quay.io/jupyter/scipy-notebook:2025-12-31

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
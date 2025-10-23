FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# Basic deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git python3 python3-pip python3-venv wget ca-certificates \
    libhdf5-dev liblapack-dev libblas-dev && \
    rm -rf /var/lib/apt/lists/*

# Python environment
RUN python3 -m pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Add scripts
WORKDIR /work
COPY scripts/ ./scripts/
COPY tools/ ./tools/
COPY params/ ./params/
COPY examples/ ./examples/

ENV PATH="/work/scripts:${PATH}"

ENTRYPOINT ["/bin/bash"]

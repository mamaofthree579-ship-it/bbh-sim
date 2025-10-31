# BBH-Sim Docker image
FROM ubuntu:22.04

LABEL maintainer="BBH-Sim Team"
LABEL description="Reproducible Binary Black Hole Simulation Environment"

# --- System setup ---
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git python3 python3-pip python3-venv \
    wget ca-certificates libhdf5-dev liblapack-dev libblas-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Python setup ---
RUN python3 -m pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# --- Copy project files ---
WORKDIR /work
COPY scripts/ ./scripts/
COPY tools/ ./tools/
COPY params/ ./params/
# COPY examples/ ./examples/

# --- Environment ---
ENV PATH="/work/scripts:${PATH}"

# --- Default entrypoint ---
CMD ["/bin/bash"]

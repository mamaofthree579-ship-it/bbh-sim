#!/usr/bin/env bash
set -euo pipefail
# This script prepares, runs, and postprocesses the toy example.
mkdir -p output
scripts/generate_initial_data.sh params/example_minimal.yaml output/initial_data
scripts/run_simulation.sh params/example_minimal.yaml output/run
scripts/postprocess.sh output/run output/post
echo DONE

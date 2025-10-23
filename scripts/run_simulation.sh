#!/usr/bin/env bash
set -euo pipefail
PARAMS=${1:-params/example_minimal.yaml}
OUTDIR=${2:-output/run}
mkdir -p "$OUTDIR"

echo "[run_simulation] Running toy evolution with params: $PARAMS"
# Placeholder: in a real pipeline this would invoke the NR evolution binary (MPI-enabled)
# For the toy example we create fake outputs that downstream scripts can read.
python3 - <<'PY'
import yaml, json, os
p=yaml.safe_load(open('$PARAMS'))
os.makedirs('$OUTDIR',exist_ok=True)
# fake waveform: simple damped sinusoid metadata
wf={'t':[0,10,20],'h_re':[0,0.1,0.05],'h_im':[0,0.0,-0.02]}
open(os.path.join('$OUTDIR','waveform.json'),'w').write(json.dumps(wf))
open(os.path.join('$OUTDIR','run_metadata.json'),'w').write(json.dumps({'params':p['simulation_name']}))
print('Wrote toy waveform and metadata to $OUTDIR')
PY

echo "Run complete (toy placeholder)."

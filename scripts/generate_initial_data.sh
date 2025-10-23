#!/usr/bin/env bash
set -euo pipefail

PARAMS=${1:-params/example_minimal.yaml}
OUTDIR=${2:-output/initial_data}
mkdir -p "$OUTDIR"

echo "[generate_initial_data] Reading params: $PARAMS"
# Placeholder: call TwoPunctures or other initial-data solver here.
# For the toy example we write a small metadata file.
python3 - <<'PY'
import yaml, json, sys, os
p=yaml.safe_load(open('$PARAMS'))
md={'initial_data':p['initial_data']}
os.makedirs('$OUTDIR', exist_ok=True)
open('$OUTDIR/initial_data.json','w').write(json.dumps(md,indent=2))
print('Wrote $OUTDIR/initial_data.json')
PY

echo "Initial data generation complete (toy placeholder)."

#!/usr/bin/env bash
set -euo pipefail
RUNDIR=${1:-output/run}
OUTDIR=${2:-output/post}
mkdir -p "$OUTDIR"

echo "[postprocess] Converting Psi4->h (toy) and packaging HDF5"
python3 - <<'PY'
import json, h5py, os
wf=json.load(open(os.path.join('$RUNDIR','waveform.json')))
os.makedirs('$OUTDIR',exist_ok=True)
with h5py.File(os.path.join('$OUTDIR','waveforms.h5'),'w') as f:
    grp=f.create_group('waveforms')
    import numpy as np
    grp.create_dataset('t',data=np.array(wf['t']))
    grp.create_dataset('h_re',data=np.array(wf['h_re']))
    grp.create_dataset('h_im',data=np.array(wf['h_im']))
    f.attrs['created_by']='BBH-Sim toy postprocess'
print('Wrote HDF5 to',os.path.join('$OUTDIR','waveforms.h5'))
PY

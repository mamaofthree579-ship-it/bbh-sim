#!/usr/bin/env python3
"""Minimal HDF5 validator for required groups/attributes."""
import h5py, sys

f=h5py.File(sys.argv[1],'r')
reqs=['metadata','initial','evolution','extraction','waveforms','diagnostics']
for r in reqs:
    if r not in f:
        print('MISSING',r)
        sys.exit(2)
print('Basic HDF5 layout OK')

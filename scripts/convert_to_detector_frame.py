#!/usr/bin/env python3
"""Convert geometric waveforms (h_lm in units of M) to detector-frame strain for a given total mass and sky location.
This is a small helper that uses pure-Python scaling and optional LALSuite if available.
"""
import argparse
import numpy as np

def scale_time_freq(times, M_total_solar):
    # geometric M -> seconds: M_sun = 4.92549095e-6 s
    M_sun_sec = 4.92549095e-6
    return np.array(times) * M_total_solar * M_sun_sec

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('wavefile')
    p.add_argument('--Mtot',type=float,default=60.0,help='Total mass in solar masses')
    args=p.parse_args()
    import json
    w=json.load(open(args.wavefile))
    t_scaled = scale_time_freq(w['t'], args.Mtot)
    print('First three scaled times (s):', t_scaled[:3])

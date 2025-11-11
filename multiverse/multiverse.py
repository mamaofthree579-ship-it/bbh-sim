# app_v4_research.py
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import json
import time
import math

st.set_page_config(page_title="Fractal Conscious Cosmos — Research v4", layout="wide")
st.title("Fractal Conscious Cosmos — Harmonic Simulation Environment")
st.markdown(
    "Interactive model of multiscale coherence, dark-matter diffusion, and fractal harmonic networks. "
    "Use sidebar controls to tune the simulation, Start to run continuously (if `streamlit-autorefresh` is installed), "
    "or Step to advance manually. Export logged metrics as CSV."
)

# ---------------------------
# Session initialization
# ---------------------------
def init_session():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        # Simulation parameters (defaults)
        st.session_state.N = 24               # nodes
        st.session_state.M = 5                # subnodes per node
        st.session_state.K = 0.25             # coupling
        st.session_state.freq_scale = 1.0
        st.session_state.dt = 0.02
        st.session_state.grid_size = 64
        st.session_state.D = 0.06
        st.session_state.alpha = 0.004
        st.session_state.steps_per_update = 6
        st.session_state.run = False
        st.session_state.last_step = time.time()
        # logs and storage
        st.session_state.time = 0.0
        st.session_state.log = pd.DataFrame(columns=["t","mean_amp","kuramoto_R","phase_var","dm_density"])
        st.session_state.metrics = []  # list of dicts for export
        # initialize sim state
        reset_sim(seed=42)

def reset_sim(seed=None):
    rng = np.random.default_rng(seed if seed is not None else int(time.time() % 1e9))
    N = st.session_state.N; M = st.session_state.M
    st.session_state.pos = rng.uniform(-1,1,(N,2))*40.0
    st.session_state.omegas = rng.uniform(0.2,2.0,(N,M)) * (2*np.pi) * st.session_state.freq_scale
    st.session_state.amps = rng.uniform(0.3,1.0,(N,M))
    st.session_state.phases = rng.uniform(0,2*np.pi,(N,M))
    # neighbor: k nearest
    k = min(6, max(1, N//6))
    d = np.linalg.norm(st.session_state.pos[:,None,:] - st.session_state.pos[None,:,:], axis=-1)
    neighbors = np.argsort(d, axis=1)[:,1:k+1]
    st.session_state.neighbors = neighbors
    st.session_state.grid = rng.uniform(0.05,1.0,(st.session_state.grid_size, st.session_state.grid_size))
    st.session_state.time = 0.0
    st.session_state.log = pd.DataFrame(columns=["t","mean_amp","kuramoto_R","phase_var","dm_density"])
    st.session_state.metrics = []

init_session()

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.header("Simulation Controls & Data")
    st.session_state.N = st.number_input("Nodes (N)", min_value=6, max_value=200, value=st.session_state.N, step=1)
    st.session_state.M = st.number_input("Subnodes per node (M)", min_value=1, max_value=20, value=st.session_state.M, step=1)
    st.session_state.K = st.slider("Global coupling K", 0.0, 2.0, float(st.session_state.K), 0.01)
    st.session_state.freq_scale = st.slider("Frequency scale", 0.1, 3.0, float(st.session_state.freq_scale), 0.01)
    st.session_state.dt = st.number_input("Time step dt", min_value=0.001, max_value=0.1, value=st.session_state.dt, step=0.001, format="%.4f")
    st.session_state.steps_per_update = st.number_input("Steps per update (per refresh)", min_value=1, max_value=200, value=st.session_state.steps_per_update, step=1)
    st.session_state.grid_size = st.number_input("Dark matter grid size", min_value=16, max_value=256, value=st.session_state.grid_size, step=1)
    st.session_state.D = st.slider("DM diffusion D", 0.0, 1.0, float(st.session_state.D), 0.01)
    st.session_state.alpha = st.slider("DM decay α", 0.0, 0.05, float(st.session_state.alpha), 0.0005)
    st.markdown("---")
    col1, col2 = st.columns(2)
    if col1.button("Step"):
        step_sim(steps=st.session_state.steps_per_update) if 'step_sim' in globals() else None
    if col2.button("Reset (random)"):
        reset_sim()
    st.markdown("---")
    run_toggle = st.checkbox("Start / Stop (continuous run)", value=st.session_state.run)
    st.session_state.run = run_toggle
    st.markdown("---")
    st.write("Data & Export")
    if st.button("Capture Snapshot (JSON)"):
        snap = create_snapshot()
        st.download_button("Download snapshot JSON", data=json.dumps(snap, indent=2), file_name=f"snapshot_t{st.session_state.time:.3f}.json", mime="application/json")
    if st.button("Export metrics CSV"):
        if st.session_state.metrics:
            df = pd.DataFrame(st.session_state.metrics)
            st.download_button("Download metrics CSV", data=df.to_csv(index=False), file_name="metrics.csv", mime="text/csv")
        else:
            st.warning("No metrics recorded yet.")

# The functions referenced above must exist before sidebar uses them.
# We'll define them now (ok to be below since Step button calls re-run).

# ---------------------------
# Core simulation functions
# ---------------------------
def compute_inst_amplitudes(t):
    omegas = st.session_state.omegas
    amps = st.session_state.amps
    phases = st.session_state.phases
    inst = amps * np.cos(omegas * t + phases)   # N x M
    node_amp = inst.mean(axis=1)
    complex_phase = np.exp(1j * (omegas * t + phases)).mean(axis=1)
    node_phase = np.angle(complex_phase)
    return node_amp, node_phase, inst

def kuramoto_step(dt):
    N, M = st.session_state.phases.shape
    neighbors = st.session_state.neighbors
    K = st.session_state.K
    _, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
    dph = np.zeros_like(st.session_state.phases)
    for i in range(N):
        neigh_idx = neighbors[i]
        if neigh_idx.size > 0:
            diffs = np.sin(node_phase[neigh_idx] - node_phase[i])
            mean_diff = diffs.mean()
        else:
            mean_diff = 0.0
        dph[i, :] = st.session_state.omegas[i, :] + K * mean_diff
    st.session_state.phases = (st.session_state.phases + dph * dt) % (2*np.pi)

def evolve_dark_matter(dt):
    g = st.session_state.grid
    D = st.session_state.D; alpha = st.session_state.alpha
    lap = (np.roll(g,1,axis=0) + np.roll(g,-1,axis=0) + np.roll(g,1,axis=1) + np.roll(g,-1,axis=1) - 4*g)
    newg = g + D * lap * dt - alpha * g * dt
    st.session_state.grid = np.clip(newg, 0.0, None)

def step_sim(steps=1):
    for _ in range(steps):
        kuramoto_step(st.session_state.dt)
        evolve_dark_matter(st.session_state.dt)
        st.session_state.time += st.session_state.dt
        amps, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
        z = np.mean(np.exp(1j * node_phase))
        R = float(np.abs(z))
        mean_amp = float(np.mean(np.abs(amps)))
        phase_var = float(np.var(node_phase))
        dm_density = float(np.mean(st.session_state.grid))
        # log
        st.session_state.log = st.session_state.log.append(
            {"t": st.session_state.time, "mean_amp": mean_amp, "kuramoto_R": R, "phase_var": phase_var, "dm_density": dm_density},
            ignore_index=True
        )
        # append to metrics list for export
        st.session_state.metrics.append({
            "t": float(st.session_state.time),
            "mean_amp": mean_amp,
            "kuramoto_R": R,
            "phase_var": phase_var,
            "dm_density": dm_density
        })

def create_snapshot():
    amps, node_phase, inst = compute_inst_amplitudes(st.session_state.time)
    snap = {
        "time": float(st.session_state.time),
        "N": int(st.session_state.N),
        "M": int(st.session_state.M),
        "pos": st.session_state.pos.tolist(),
        "node_amp": amps.tolist(),
        "node_phase": node_phase.tolist(),
        "sub_inst": inst.tolist(),
        "dm_grid": (st.session_state.grid / np.nanmax(st.session_state.grid)).tolist()
    }
    return snap

# ---------------------------
# Auto-refresh handling (optional) - use streamlit-autorefresh if available
# ---------------------------
use_autorefresh = False
try:
    from streamlit_autorefresh import st_autorefresh
    use_autorefresh = True
except Exception:
    use_autorefresh = False

if use_autorefresh:
    # refresh every 500ms; when refreshed, if run=True step the sim a bit
    refresh_count = st_autorefresh(interval=500, limit=None, key="auto_refresh")
    if st.session_state.run:
        step_sim(steps=st.session_state.steps_per_update)
else:
    # if not using autorefresh and run requested, show a note to press Step repeatedly
    if st.session_state.run:
        st.info("Auto-run requested but 'streamlit-autorefresh' not installed — press Step to advance, or install it (`pip install streamlit-autorefresh`) to run continuously.")

# ---------------------------
# Create snapshot and inject into HTML visualizer
# ---------------------------
snapshot = create_snapshot()
snapshot_json = json.dumps(snapshot)

# ---------------------------
# Build and display the Three.js visualizer (reads snapshot)
# ---------------------------
st.subheader("3D Visualizer — synchronized snapshot")
html = rf"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Visualizer</title>
<style>
  body {{ margin:0; background: linear-gradient(#00111a, #000); color:#fff; overflow:hidden; }}
  #overlay {{ position:absolute; left:10px; top:10px; color:#fff; font-family:sans-serif; z-index:10; }}
</style>
</head>
<body>
<div id="overlay">t = {snapshot['time']:.3f} s</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.js"></script>

<script>
const snapshot = {snapshot_json};
// --- your JavaScript below ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth*0.95, window.innerHeight*0.85);
document.body.appendChild(renderer.domElement);
// ... rest of script ...
</script>
</body>
</html>
"""
components.html(html, height=800, scrolling=True)

# ---------------------------
# Right column: metrics, log, charts
# ---------------------------
st.subheader("Research Metrics & Logs (Python authoritative)")
col1, col2 = st.columns([1,1])

with col1:
    st.write("Latest logged metrics (tail)")
    st.dataframe(st.session_state.log.tail(10).reset_index(drop=True))

with col2:
    st.write("Live derived metrics")
    # show latest computed metrics without heavy recompute
    if not st.session_state.log.empty:
        last = st.session_state.log.iloc[-1]
        st.metric("Time (s)", f"{last['t']:.3f}")
        st.metric("Mean Amp", f"{last['mean_amp']:.3f}")
        st.metric("Kuramoto R", f"{last['kuramoto_R']:.3f}")
        st.metric("Phase Var", f"{last['phase_var']:.5f}")
        st.metric("DM Density", f"{last['dm_density']:.3f}")
    else:
        st.info("Run Step(s) to populate metrics.")

st.markdown("---")
st.write("Amplitude history (last 200 samples)")
if "amp_history" not in st.session_state:
    st.session_state.amp_history = []
amps_now, _, _ = compute_inst_amplitudes(st.session_state.time)
st.session_state.amp_history.append(amps_now.tolist())
if len(st.session_state.amp_history) > 200:
    st.session_state.amp_history = st.session_state.amp_history[-200:]
df_amp = pd.DataFrame(st.session_state.amp_history, columns=[f"Node {i}" for i in range(st.session_state.N)])
st.line_chart(df_amp)

st.markdown("---")
st.caption("Notes: Python runs the authoritative simulation and logs metrics; the Three.js visualizer renders the injected snapshot so visuals match the numeric state.")

# End of file

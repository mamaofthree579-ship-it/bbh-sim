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
        st.session_state.N = 24
        st.session_state.M = 5
        st.session_state.K = 0.25
        st.session_state.freq_scale = 1.0
        st.session_state.dt = 0.02
        st.session_state.grid_size = 64
        st.session_state.D = 0.06
        st.session_state.alpha = 0.004
        st.session_state.steps_per_update = 6
        st.session_state.run = False
        st.session_state.last_step = time.time()
        st.session_state.time = 0.0
        st.session_state.log = pd.DataFrame(columns=["t","mean_amp","kuramoto_R","phase_var","dm_density"])
        st.session_state.metrics = []
        reset_sim(seed=42)

def reset_sim(seed=None):
    rng = np.random.default_rng(seed if seed is not None else int(time.time() % 1e9))
    N = st.session_state.N; M = st.session_state.M
    st.session_state.pos = rng.uniform(-1,1,(N,2))*40.0
    st.session_state.omegas = rng.uniform(0.2,2.0,(N,M)) * (2*np.pi) * st.session_state.freq_scale
    st.session_state.amps = rng.uniform(0.3,1.0,(N,M))
    st.session_state.phases = rng.uniform(0,2*np.pi,(N,M))
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
    st.session_state.N = st.number_input("Nodes (N)", 6, 200, st.session_state.N, 1)
    st.session_state.M = st.number_input("Subnodes per node (M)", 1, 20, st.session_state.M, 1)
    st.session_state.K = st.slider("Global coupling K", 0.0, 2.0, float(st.session_state.K), 0.01)
    st.session_state.freq_scale = st.slider("Frequency scale", 0.1, 3.0, float(st.session_state.freq_scale), 0.01)
    st.session_state.dt = st.number_input("Time step dt", 0.001, 0.1, st.session_state.dt, 0.001, format="%.4f")
    st.session_state.steps_per_update = st.number_input("Steps per update", 1, 200, st.session_state.steps_per_update, 1)
    st.session_state.grid_size = st.number_input("Dark matter grid size", 16, 256, st.session_state.grid_size, 1)
    st.session_state.D = st.slider("DM diffusion D", 0.0, 1.0, float(st.session_state.D), 0.01)
    st.session_state.alpha = st.slider("DM decay α", 0.0, 0.05, float(st.session_state.alpha), 0.0005)
    st.markdown("---")
    col1, col2 = st.columns(2)
    if col1.button("Step"):
        step_sim(st.session_state.steps_per_update) if 'step_sim' in globals() else None
    if col2.button("Reset (random)"):
        reset_sim()
    st.markdown("---")
    st.session_state.run = st.checkbox("Start / Stop (continuous run)", value=st.session_state.run)
    st.markdown("---")

# ---------------------------
# Core simulation
# ---------------------------
def compute_inst_amplitudes(t):
    omegas = st.session_state.omegas
    amps = st.session_state.amps
    phases = st.session_state.phases
    inst = amps * np.cos(omegas * t + phases)
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
        if len(neigh_idx) > 0:
            mean_diff = np.sin(node_phase[neigh_idx] - node_phase[i]).mean()
        else:
            mean_diff = 0.0
        dph[i, :] = st.session_state.omegas[i, :] + K * mean_diff
    st.session_state.phases = (st.session_state.phases + dph * dt) % (2*np.pi)

def evolve_dark_matter(dt):
    g = st.session_state.grid
    D = st.session_state.D; alpha = st.session_state.alpha
    lap = (np.roll(g,1,axis=0) + np.roll(g,-1,axis=0) + np.roll(g,1,axis=1) + np.roll(g,-1,axis=1) - 4*g)
    st.session_state.grid = np.clip(g + D * lap * dt - alpha * g * dt, 0.0, None)

def step_sim(steps=1):
    for _ in range(steps):
        kuramoto_step(st.session_state.dt)
        evolve_dark_matter(st.session_state.dt)
        st.session_state.time += st.session_state.dt
        amps, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
        R = float(np.abs(np.mean(np.exp(1j * node_phase))))
        st.session_state.metrics.append({
            "t": float(st.session_state.time),
            "mean_amp": float(np.mean(np.abs(amps))),
            "kuramoto_R": R,
            "phase_var": float(np.var(node_phase)),
            "dm_density": float(np.mean(st.session_state.grid))
        })
        st.session_state.log = pd.DataFrame(st.session_state.metrics)

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
# Auto-refresh (if installed)
# ---------------------------
use_autorefresh = False
try:
    from streamlit_autorefresh import st_autorefresh
    use_autorefresh = True
except Exception:
    use_autorefresh = False

if use_autorefresh:
    refresh_count = st_autorefresh(interval=800, limit=None, key="auto_refresh")
    if st.session_state.run:
        step_sim(st.session_state.steps_per_update)
elif st.session_state.run:
    st.info("Auto-run requested")
    
# --- 3D Visualizer (antialias fix, mobile safe) ---
st.subheader("3D Visualizer — Fixed Renderer (antialias defined)")

try:
    _ = snapshot
except NameError:
    import numpy as np, json
    N = 20
    snapshot = {
        "time": 0.0,
        "N": N,
        "node_amp": np.random.uniform(-1, 1, N).tolist(),
        "node_phase": np.random.uniform(-np.pi, np.pi, N).tolist(),
        "pos": np.random.uniform(-50, 50, (N, 2)).tolist(),
        "sub_inst": [[np.random.uniform(-1, 1) for _ in range(np.random.randint(2, 6))] for _ in range(N)],
        "dm_grid": (np.random.rand(64, 64) * 0.8).tolist()
    }
snapshot_json = json.dumps(snapshot)

html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Visualizer</title>
<style>
  body {{
    margin: 0;
    background: radial-gradient(circle at center, #000014 0%, #000 100%);
    overflow: hidden;
    color: #fff;
    font-family: sans-serif;
  }}
  #overlay {{
    position: absolute;
    left: 10px;
    top: 10px;
    color: #0ff;
    font-weight: bold;
    text-shadow: 0 0 6px #0ff;
    z-index: 10;
  }}
</style>
</head>
<body>
<div id="overlay">t = {snapshot['time']:.3f} s</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.min.js"></script>

<script>
const snapshot = {snapshot_json};

// --- Scene Setup ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 2000);
camera.position.z = window.innerWidth < 700 ? 60 : 100;

// ✅ Correctly define antialias option here:
const renderer = new // Source - https://stackoverflow.com/a
// Posted by Wilt, modified by community. See post 'Timeline' for change history
// Retrieved 2025-11-12, License - CC BY-SA 3.0

renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// --- Lighting ---
const ambient = new THREE.AmbientLight(0xffffff, 1.0);
scene.add(ambient);
const directional = new THREE.DirectionalLight(0x99ccff, 0.7);
directional.position.set(50, 50, 100);
scene.add(directional);

// --- Dark Matter Grid Plane ---
function drawDMGrid(dm) {{
  const size = dm.length;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(size, size);
  for (let y = 0; y < size; y++) {{
    for (let x = 0; x < size; x++) {{
      const v = Math.max(0, Math.min(1, dm[y][x]));
      const idx = (y*size + x)*4;
      img.data[idx] = Math.floor(20 + 220 * v);
      img.data[idx+1] = Math.floor(40 + 160 * v);
      img.data[idx+2] = Math.floor(100 + 120 * (1 - v));
      img.data[idx+3] = 200;
    }}
  }}
  ctx.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(canvas);
  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(200, 200),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0.7 })
  );
  plane.position.z = -25;
  scene.add(plane);
}}

// --- Nodes ---
const nodes = [];
(function createNodes(){{
  for (let i = 0; i < snapshot.N; i++) {{
    const amp = snapshot.node_amp[i];
    const phase = snapshot.node_phase[i];
    const hue = (phase + Math.PI) / (2*Math.PI);
    const color = new THREE.Color().setHSL(hue, 1.0, 0.55);
    const geometry = new THREE.SphereGeometry(1.5 + Math.abs(amp)*2.2, 24, 24);
    const material = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.7 });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.x = snapshot.pos[i][0];
    mesh.position.y = snapshot.pos[i][1];
    scene.add(mesh);
    const subs = [];
    for (let j = 0; j < snapshot.sub_inst[i].length; j++) {{
      const sAmp = snapshot.sub_inst[i][j];
      const sg = new THREE.SphereGeometry(0.4 + Math.abs(sAmp)*0.3, 12, 12);
      const sm = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.4 });
      const smesh = new THREE.Mesh(sg, sm);
      smesh.position.x = mesh.position.x + (Math.random() - 0.5)*4;
      smesh.position.y = mesh.position.y + (Math.random() - 0.5)*4;
      scene.add(smesh);
      subs.push(smesh);
    }}
    nodes.push({ mesh, subs });
  }}
}})();

drawDMGrid(snapshot.dm_grid);

// --- Controls ---
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.enablePan = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.7;

// --- Animation ---
let t = 0;
function animate() {{
  requestAnimationFrame(animate);
  t += 0.02;
  for (let i = 0; i < nodes.length; i++) {{
    const n = nodes[i];
    const glow = 1.0 + 0.2 * Math.sin(t * 2.0 + i);
    n.mesh.scale.set(glow, glow, glow);
    n.mesh.material.emissiveIntensity = 0.5 + 0.5 * Math.sin(t * 3.0 + i);
    for (let j = 0; j < n.subs.length; j++) {{
      const s = n.subs[j];
      const flick = 0.9 + 0.4 * Math.sin(t * 4.0 + i + j);
      s.scale.set(flick, flick, flick);
    }}
  }}
  controls.update();
  renderer.render(scene, camera);
}}
animate();

// --- Responsive Resize ---
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""
components.html(html, height=800, scrolling=False)
# ---------------------------
# Metrics + Charts
# ---------------------------
st.subheader("Research Metrics & Logs (Python authoritative)")
col1, col2 = st.columns([1,1])
with col1:
    st.write("Latest metrics:")
    st.dataframe(st.session_state.log.tail(10).reset_index(drop=True))
with col2:
    if not st.session_state.log.empty:
        last = st.session_state.log.iloc[-1]
        st.metric("Time (s)", f"{last['t']:.3f}")
        st.metric("Mean Amp", f"{last['mean_amp']:.3f}")
        st.metric("Kuramoto R", f"{last['kuramoto_R']:.3f}")
        st.metric("Phase Var", f"{last['phase_var']:.5f}")
        st.metric("DM Density", f"{last['dm_density']:.3f}")

st.markdown("---")
amps_now, _, _ = compute_inst_amplitudes(st.session_state.time)
if "amp_history" not in st.session_state:
    st.session_state.amp_history = []
st.session_state.amp_history.append(amps_now.tolist())
if len(st.session_state.amp_history) > 200:
    st.session_state.amp_history = st.session_state.amp_history[-200:]
df_amp = pd.DataFrame(st.session_state.amp_history, columns=[f"Node {i}" for i in range(st.session_state.N)])
st.line_chart(df_amp)

import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import json
import time
import io

st.set_page_config(layout="wide", page_title="Fractal Conscious Cosmos Simulator")

# -------------------------
# Utility / Session state
# -------------------------
def init_session():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        # simulation parameters
        st.session_state.N = 30                # nodes
        st.session_state.M = 5                 # subnodes per node
        st.session_state.K = 0.25              # coupling
        st.session_state.freq_scale = 1.0
        st.session_state.dt = 0.02
        st.session_state.grid_size = 48
        st.session_state.D = 0.06              # dark matter diffusion
        st.session_state.alpha = 0.004         # dark matter decay
        st.session_state.steps_per_update = 4
        st.session_state.run = False
        st.session_state.auto_export = False
        st.session_state.auto_export_interval = 30.0  # seconds
        # logs and time
        st.session_state.time = 0.0
        st.session_state.log = pd.DataFrame(columns=["t","mean_amp","kuramoto_R","energy_variance"])
        st.session_state.last_export_time = time.time()
        reset_sim(seed=12345)  # deterministic by default

def reset_sim(seed=None):
    rng = np.random.default_rng(seed if seed is not None else int(time.time() % 1e9))
    N = st.session_state.N; M = st.session_state.M
    st.session_state.pos = rng.uniform(-1,1,(N,2))*40.0
    st.session_state.omegas = rng.uniform(0.2,2.0,(N,M)) * (2*np.pi) * st.session_state.freq_scale
    st.session_state.amps = rng.uniform(0.3,1.0,(N,M))
    st.session_state.phases = rng.uniform(0,2*np.pi,(N,M))
    # simple neighbor assignment (k nearest by Euclidean)
    k = min(6, max(1, N//6))
    # compute pairwise dists and choose k nearest
    d = np.linalg.norm(st.session_state.pos[:,None,:] - st.session_state.pos[None,:,:], axis=-1)
    neighbors = np.argsort(d, axis=1)[:,1:k+1]
    st.session_state.neighbors = neighbors
    # dark matter grid
    st.session_state.grid = rng.uniform(0.05,1.0,(st.session_state.grid_size, st.session_state.grid_size))
    # reset time and log
    st.session_state.time = 0.0
    st.session_state.log = pd.DataFrame(columns=["t","mean_amp","kuramoto_R","energy_variance"])

init_session()

# -------------------------
# Sidebar controls
# -------------------------
with st.sidebar:
    st.header("Simulation Controls (data-first)")
    st.session_state.N = st.number_input("Nodes (N)", min_value=6, max_value=200, value=st.session_state.N, step=1)
    st.session_state.M = st.number_input("Subnodes per node (M)", min_value=1, max_value=20, value=st.session_state.M, step=1)
    st.session_state.K = st.slider("Global coupling K", 0.0, 2.0, float(st.session_state.K), 0.01)
    st.session_state.freq_scale = st.slider("Frequency scale", 0.1, 3.0, float(st.session_state.freq_scale), 0.01)
    st.session_state.dt = st.number_input("Time step dt", min_value=0.001, max_value=0.1, value=st.session_state.dt, step=0.001, format="%.4f")
    st.session_state.steps_per_update = st.number_input("Steps per update (per visual refresh)", min_value=1, max_value=200, value=st.session_state.steps_per_update, step=1)
    st.session_state.grid_size = st.number_input("Dark matter grid size", min_value=16, max_value=256, value=st.session_state.grid_size, step=1)
    st.session_state.D = st.slider("DM diffusion D", 0.0, 1.0, float(st.session_state.D), 0.01)
    st.session_state.alpha = st.slider("DM decay α", 0.0, 0.05, float(st.session_state.alpha), 0.0005)

    st.markdown("---")
    st.write("Run controls")
    run_col1, run_col2 = st.columns([1,1])
    if run_col1.button("Step"):
        step_sim(steps=st.session_state.steps_per_update)
    if run_col2.button("Reset (random)"):
        reset_sim()
    # toggle run/stop
    if st.button("Start / Stop (toggle)"):
        st.session_state.run = not st.session_state.run

    st.markdown("---")
    st.write("Export / Snapshot")
    if st.button("Capture Snapshot (save JSON)"):
        snap = create_snapshot()
        # start download
        st.download_button("Download snapshot JSON", data=json.dumps(snap, indent=2), file_name=f"snapshot_t{st.session_state.time:.3f}.json", mime="application/json")
    st.session_state.auto_export = st.checkbox("Auto-export CSV every N sec", value=st.session_state.auto_export)
    if st.session_state.auto_export:
        st.session_state.auto_export_interval = st.number_input("Auto-export interval (s)", min_value=5.0, max_value=3600.0, value=st.session_state.auto_export_interval, step=1.0)

    st.markdown("---")
    st.write("Data & Logs")
    if st.button("Export log CSV"):
        csv_bytes = st.session_state.log.to_csv(index=False).encode()
        st.download_button("Download simulation log CSV", data=csv_bytes, file_name="sim_log.csv", mime="text/csv")

# -------------------------
# Core simulation functions
# -------------------------
def compute_inst_amplitudes(time):
    """Compute instantaneous amplitudes and representative node phases."""
    omegas = st.session_state.omegas
    amps = st.session_state.amps
    phases = st.session_state.phases
    inst = amps * np.cos(omegas * time + phases)   # N x M
    node_amp = inst.mean(axis=1)
    complex_phase = np.exp(1j * (omegas * time + phases)).mean(axis=1)
    node_phase = np.angle(complex_phase)
    return node_amp, node_phase, inst

def kuramoto_step(dt):
    """
    Simple Euler-like Kuramoto-style step applied to subnode phases.
    It's stable enough for demonstration; replace with RK4 for higher fidelity.
    """
    N, M = st.session_state.phases.shape
    neighbors = st.session_state.neighbors
    K = st.session_state.K
    # representative node phases
    _, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
    # phase velocity: intrinsic + coupling via mean neighbor difference
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
    """Advance the simulation `steps` times and log aggregated metrics."""
    for _ in range(steps):
        kuramoto_step(st.session_state.dt)
        evolve_dark_matter(st.session_state.dt)
        st.session_state.time += st.session_state.dt
        # metrics & log
        amps, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
        z = np.mean(np.exp(1j * node_phase))
        R = float(np.abs(z))
        mean_amp = float(np.mean(np.abs(amps)))
        energy_var = float(np.var(amps))
        st.session_state.log = st.session_state.log.append(
            {"t": st.session_state.time, "mean_amp": mean_amp, "kuramoto_R": R, "energy_variance": energy_var},
            ignore_index=True
        )

def create_snapshot():
    """Create a JSON-serializable snapshot to inject into the JS visualizer."""
    amps, node_phase, inst = compute_inst_amplitudes(st.session_state.time)
    snap = {
        "time": float(st.session_state.time),
        "N": int(st.session_state.N),
        "M": int(st.session_state.M),
        "pos": st.session_state.pos.tolist(),
        "node_amp": amps.tolist(),
        "node_phase": node_phase.tolist(),
        "sub_inst": inst.tolist(),   # N x M matrix
        "dm_grid": (st.session_state.grid / np.nanmax(st.session_state.grid)).tolist()  # normalized
    }
    return snap

# -------------------------
# Auto-run logic (polling)
# -------------------------
# If run is True, perform a small batch of steps, update snapshot, and rerun to refresh the UI.
if st.session_state.run:
    # run batch
    step_sim(steps=st.session_state.steps_per_update)
    # auto-export if enabled
    if st.session_state.auto_export and (time.time() - st.session_state.last_export_time) >= st.session_state.auto_export_interval:
        csv_bytes = st.session_state.log.to_csv(index=False).encode()
        # provide a download button via st.download_button (imperative) — show ephemeral message
        st.session_state.last_export_time = time.time()
        st.success("Auto-exported logs (download available below).")
        st.download_button("Download auto-exported log CSV", data=csv_bytes, file_name=f"sim_log_t{int(time.time())}.csv", mime="text/csv")
    # re-render by letting the script continue to the components.html which gets a fresh snapshot
    # small sleep to avoid tight loop on rerun
    time.sleep(0.01)
    st.experimental_rerun()

# -------------------------
# Page main layout — left: visualizer, right: metrics + live chart
# -------------------------
col1, col2 = st.columns([3, 1])

# The visualizer will receive a snapshot JSON injected into the HTML.
snapshot = create_snapshot()
snapshot_json = json.dumps(snapshot)

with col1:
    st.subheader("3D Visualizer (synchronized snapshot)")
    # The HTML/JS reads `const snapshot = ...` and renders it.
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Visualizer</title>
<style>body{{margin:0;background:#000}}#overlay{{position:absolute;left:10px;top:10px;color:#fff;font-family:sans-serif;z-index:10}}</style>
</head>
<body>
<div id="overlay">t = {snapshot['time']:.3f} s</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>
const snapshot = {snapshot_json};  // injected snapshot from Python

// Basic Three.js scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 90;
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth*0.95, window.innerHeight*0.85);
document.body.appendChild(renderer.domElement);

// ambient light for visibility
const amb = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(amb);
const dir = new THREE.DirectionalLight(0xffffff, 0.6); dir.position.set(50,50,100); scene.add(dir);

// draw DM grid as a translucent plane texture
function drawDMGrid(dm) {
    const size = dm.length;
    const canvas = document.createElement('canvas');
    canvas.width = size; canvas.height = size;
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(size, size);
    for (let y=0;y<size;y++){
        for (let x=0;x<size;x++){
            const v = Math.max(0, Math.min(1, dm[y][x]));
            const idx = (y*size + x)*4;
            // magma-ish map tweak
            img.data[idx] = Math.floor(255*v);
            img.data[idx+1] = Math.floor(60*v);
            img.data[idx+2] = Math.floor(140*(1-v));
            img.data[idx+3] = 200;
        }
    }
    ctx.putImageData(img, 0, 0);
    const tex = new THREE.CanvasTexture(canvas);
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(90,90), new THREE.MeshBasicMaterial({map:tex, transparent:true, opacity:0.55}));
    plane.position.set(0,0,-10);
    scene.add(plane);
}

// create node meshes based on snapshot
const nodes = [];
(function createNodes(){
    const N = snapshot.N;
    const pos = snapshot.pos;
    for (let i=0;i<N;i++){
        const amp = snapshot.node_amp[i];
        const h = (snapshot.node_phase[i] + Math.PI) / (2*Math.PI);
        const color = new THREE.Color().setHSL(h, 1, 0.5);
        const geo = new THREE.SphereGeometry(1.5 + Math.abs(amp)*2.5, 16, 16);
        const mat = new THREE.MeshStandardMaterial({color: color});
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.x = pos[i][0];
        mesh.position.y = pos[i][1];
        mesh.userData = {id: i};
        scene.add(mesh);
        // small satellites for subnodes (use instanced or simple small spheres)
        const subMeshes = [];
        const sub_inst = snapshot.sub_inst[i];
        for (let j=0;j<sub_inst.length;j++){
            const subAmp = sub_inst[j];
            const sg = new THREE.SphereGeometry(0.5 + Math.abs(subAmp)*0.8, 8, 8);
            const sh = (snapshot.node_phase[i]+Math.PI)/(2*Math.PI);
            const smat = new THREE.MeshBasicMaterial({color: new THREE.Color().setHSL(sh,1,0.5)});
            const sMesh = new THREE.Mesh(sg, smat);
            sMesh.position.x = mesh.position.x + (Math.random()-0.5)*3;
            sMesh.position.y = mesh.position.y + (Math.random()-0.5)*3;
            scene.add(sMesh);
            subMeshes.push(sMesh);
        }
        nodes.push({mesh:mesh, subs: subMeshes});
    }
})();

// draw DM background
drawDMGrid(snapshot.dm_grid);

// animate small twinkle effect for subs and nodes using snapshot amplitudes for scale/color
let t = 0;
function animate(){
    requestAnimationFrame(animate);
    for (let i=0;i<nodes.length;i++){
        const baseAmp = snapshot.node_amp[i];
        const s = 1.0 + 0.12*Math.sin(t*3 + i);
        nodes[i].mesh.scale.set(s*(1+Math.abs(baseAmp)), s*(1+Math.abs(baseAmp)), s*(1+Math.abs(baseAmp)));
        // subnodes twinkle
        for (let j=0;j<nodes[i].subs.length;j++){
            const k = nodes[i].subs[j];
            const flick = 0.8 + 0.4*Math.sin(t*6 + i + j);
            k.scale.set(flick, flick, flick);
        }
    }
    t += 0.02;
    renderer.render(scene, camera);
}
animate();

// responsive resize
window.addEventListener('resize', ()=> {
    renderer.setSize(window.innerWidth*0.95, window.innerHeight*0.85);
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
});
</script>
</body>
</html>
"""
    # Render the visualizer
    components.html(html, height=800, scrolling=True)

with col2:
    st.subheader("Live metrics & amplitude chart")
    # show most recent log table
    if len(st.session_state.log) > 0:
        st.write("Recent metrics (last 10):")
        st.dataframe(st.session_state.log.tail(10).reset_index(drop=True))
    else:
        st.info("Run simulation steps to populate metrics.")

    # live amplitude chart sampled from Python simulation (authoritative)
    st.write("Live node amplitude history (last 200 samples)")
    if "amp_history" not in st.session_state:
        st.session_state.amp_history = []
    # append current amplitudes
    amps_now, _, _ = compute_inst_amplitudes(st.session_state.time)
    st.session_state.amp_history.append(amps_now.tolist())
    if len(st.session_state.amp_history) > 200:
        st.session_state.amp_history = st.session_state.amp_history[-200:]
    df_amp = pd.DataFrame(st.session_state.amp_history, columns=[f"Node {i}" for i in range(st.session_state.N)])
    st.line_chart(df_amp)

    # quick download options
    st.markdown("---")
    st.write("Download current snapshot / logs")
    if st.button("Download current snapshot JSON"):
        snap = create_snapshot()
        st.download_button("Download snapshot JSON", data=json.dumps(snap, indent=2), file_name=f"snapshot_t{st.session_state.time:.3f}.json", mime="application/json")
    if st.button("Download logs CSV (full)"):
        csv_bytes = st.session_state.log.to_csv(index=False).encode()
        st.download_button("Download logs CSV", data=csv_bytes, file_name="sim_log_full.csv", mime="text/csv")

# End of app
st.markdown("---")
st.caption("Note: This app uses Python-driven simulation and injects a snapshot into the Three.js visualizer on each update. "
           "If you want continuous, high-frequency, bidirectional streaming, we can add a websocket bridge in a follow-up.")

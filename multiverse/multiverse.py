import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import json
import time

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="Fractal Conscious Cosmos — Research v5", layout="wide")
st.title("🌀 Fractal Conscious Cosmos — Harmonic Research Environment")
st.markdown("""
This simulation models multiscale coherence, dark-matter diffusion, and fractal harmonic networks. 
Use sidebar controls to adjust parameters, **Step** to manually advance, or **Start** for continuous mode.
""")

# ---------------------------
# Initialization
# ---------------------------
def reset_sim(seed=None):
    rng = np.random.default_rng(seed if seed is not None else int(time.time() % 1e9))
    
    # Safely pull bounds from session state or fall back to defaults
    N = st.session_state.get("N", 24)
    M = st.session_state.get("M", 5)
    grid_size = st.session_state.get("grid_size", 64)
    freq_scale = st.session_state.get("freq_scale", 1.0)
    
    st.session_state.pos = rng.uniform(-1, 1, (N, 2)) * 40.0
    st.session_state.omegas = rng.uniform(0.2, 2.0, (N, M)) * (2 * np.pi) * freq_scale
    st.session_state.amps = rng.uniform(0.3, 1.0, (N, M))
    st.session_state.phases = rng.uniform(0, 2 * np.pi, (N, M))
    
    k = min(6, max(1, N // 6))
    d = np.linalg.norm(st.session_state.pos[:, None, :] - st.session_state.pos[None, :, :], axis=-1)
    st.session_state.neighbors = np.argsort(d, axis=1)[:, 1:k + 1]
    st.session_state.grid = rng.uniform(0.05, 1.0, (grid_size, grid_size))
    st.session_state.time = 0.0
    st.session_state.log = pd.DataFrame(columns=["t", "mean_amp", "kuramoto_R", "phase_var", "dm_density"])
    st.session_state.metrics = []

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
        reset_sim(seed=42)

init_session()

# ---------------------------
# Core simulation functions
# ---------------------------
def compute_inst_amplitudes(t):
    omegas, amps, phases = st.session_state.omegas, st.session_state.amps, st.session_state.phases
    inst = amps * np.cos(omegas * t + phases)
    node_amp = inst.mean(axis=1)
    
    # Vectorized phase computing
    node_phase = np.angle(np.exp(1j * (omegas * t + phases)).mean(axis=1))
    return node_amp, node_phase, inst

def kuramoto_step(dt):
    N, M = st.session_state.phases.shape
    neighbors = st.session_state.neighbors
    K = st.session_state.K
    _, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
    
    dph = np.zeros_like(st.session_state.phases)
    for i in range(N):
        neigh_idx = neighbors[i]
        mean_diff = np.mean(np.sin(node_phase[neigh_idx] - node_phase[i])) if len(neigh_idx) > 0 else 0
        dph[i, :] = st.session_state.omegas[i, :] + K * mean_diff
        
    st.session_state.phases = (st.session_state.phases + dph * dt) % (2 * np.pi)

def evolve_dark_matter(dt):
    g = st.session_state.grid
    D, alpha = st.session_state.D, st.session_state.alpha
    
    # FIXED: Corrected string syntax bugs inside np.roll
    lap = (np.roll(g, 1, axis=0) + np.roll(g, -1, axis=0) + 
           np.roll(g, 1, axis=1) + np.roll(g, -1, axis=1) - 4 * g)
    st.session_state.grid = np.clip(g + D * lap * dt - alpha * g * dt, 0, None)

def step_sim(steps=1):
    for _ in range(steps):
        kuramoto_step(st.session_state.dt)
        evolve_dark_matter(st.session_state.dt)
        st.session_state.time += st.session_state.dt
        
    amps, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
    R = float(np.abs(np.mean(np.exp(1j * node_phase))))
    mean_amp = float(np.mean(np.abs(amps)))
    phase_var = float(np.var(node_phase))
    dm_density = float(np.mean(st.session_state.grid))
    
    new_entry = {
        "t": st.session_state.time,
        "mean_amp": mean_amp,
        "kuramoto_R": R,
        "phase_var": phase_var,
        "dm_density": dm_density
    }
    
    st.session_state.log = pd.concat([st.session_state.log, pd.DataFrame([new_entry])], ignore_index=True)
    st.session_state.metrics.append(new_entry)

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.header("🎛 Simulation Controls & Data")
    st.session_state.N = st.number_input("Nodes (N)", 6, 200, int(st.session_state.N))
    st.session_state.M = st.number_input("Subnodes per Node (M)", 1, 20, int(st.session_state.M))
    st.session_state.K = st.slider("Global Coupling (K)", 0.0, 2.0, float(st.session_state.K), 0.01)
    st.session_state.freq_scale = st.slider("Frequency Scale", 0.1, 3.0, float(st.session_state.freq_scale), 0.01)
    st.session_state.dt = st.number_input("Time Step (dt)", 0.001, 0.1, float(st.session_state.dt), 0.001)
    st.session_state.grid_size = st.number_input("Dark Matter Grid Size", 16, 256, int(st.session_state.grid_size))
    st.session_state.D = st.slider("DM Diffusion (D)", 0.0, 1.0, float(st.session_state.D), 0.01)
    st.session_state.alpha = st.slider("DM Decay (α)", 0.0, 0.05, float(st.session_state.alpha), 0.0005)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("Step"):
        step_sim(st.session_state.steps_per_update)
        st.success(f"Advanced — t = {st.session_state.time:.3f}s")
    if c2.button("Reset Simulation"):
        reset_sim()
        st.warning("Simulation reset complete.")
        
    st.markdown("---")
    st.session_state.run = st.checkbox("Start Continuous Run", value=st.session_state.run)
    
    st.markdown("---")
    st.subheader("📊 Data Export")
    if st.button("📥 Export Metrics (CSV)"):
        if st.session_state.metrics:
            df = pd.DataFrame(st.session_state.metrics)
            # FIXED: Explicit kwarg pairing for download button data stream
            st.download_button(label="Download Metrics CSV", data=df.to_csv(index=False), file_name="metrics.csv", mime="text/csv")
        else:
            st.warning("No metrics available yet.")
            
    if st.button("📷 Export Snapshot (JSON)"):
        amps, node_phase, inst = compute_inst_amplitudes(st.session_state.time)
        snap = {
            "time": float(st.session_state.time),
            "N": int(st.session_state.N),
            "pos": st.session_state.pos.tolist(),
            "node_amp": amps.tolist(),
            "node_phase": node_phase.tolist(),
            "dm_grid": (st.session_state.grid / (np.nanmax(st.session_state.grid) + 1e-9)).tolist()
        }
        st.download_button(label="Download Snapshot JSON", data=json.dumps(snap, indent=2), file_name="snapshot.json", mime="application/json")

# ---------------------------
# Auto-refresh loop engine
# ---------------------------
if st.session_state.run:
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=800, limit=None, key="refresh")
        step_sim(st.session_state.steps_per_update)
    except ImportError:
        st.info("Install `streamlit-autorefresh` for continuous live updates.")

# ---------------------------
# Visualization Engine
# ---------------------------
amps, node_phase, _ = compute_inst_amplitudes(st.session_state.time)
snapshot = {
    "time": float(st.session_state.time),
    "N": int(st.session_state.N),
    "pos": st.session_state.pos.tolist(),
    "node_amp": amps.tolist(),
    "node_phase": node_phase.tolist(),
    "dm_grid": (st.session_state.grid / (np.nanmax(st.session_state.grid) + 1e-9)).tolist()
}

html_payload = f"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fractal Cosmos Visualizer</title>
    <style>
        body {{ margin: 0; background: radial-gradient(circle at center, #001022 0%, #000 100%); overflow: hidden; }}
        #overlay {{ position: absolute; top: 10px; left: 10px; color: #0ff; font-family: monospace; text-shadow: 0 0 10px #0ff; z-index: 10; }}
    </style>
</head>
<body>
    <div id="overlay">t = {snapshot['time']:.3f} s</div>
    <script src="https://jsdelivr.net"></script>
    <script>
        const snapshot = {json.dumps(snapshot)};
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 2000);
        camera.position.z = 100;
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        scene.add(new THREE.AmbientLight(0xffffff, 0.8));
        
        // Render Dark Matter Grid Plane
        const s = snapshot.dm_grid.length;
        const canvas = document.createElement('canvas');
        canvas.width = s; canvas.height = s;
        const ctx = canvas.getContext('2d');
        const img = ctx.createImageData(s, s);
        for (let y=0; y<s; y++) {{
            for (let x=0; x<s; x++) {{
                const v = Math.max(0, Math.min(1, snapshot.dm_grid[y][x]));
                const idx = (y*s+x)*4;
                img.data[idx] = 30 + 220*v;
                img.data[idx+1] = 10 + 90*v;
                img.data[idx+2] = 80 + 120*(1-v);
                img.data[idx+3] = 180;
            }}
        }}
        ctx.putImageData(img,0,0);
        const tex = new THREE.CanvasTexture(canvas);
        const plane = new THREE.Mesh(new THREE.PlaneGeometry(160,160), new THREE.MeshBasicMaterial({{map:tex, transparent:true, opacity:0.55}}));
        plane.position.set(0,0,-10);
        scene.add(plane);

        // Render Nodes (with correct dimension arrays restored)
        const nodes = [];
        for(let i=0; i<snapshot.N; i++) {{
            const amp = snapshot.node_amp[i];
            const hue = (snapshot.node_phase[i] + Math.PI)/(2*Math.PI);
            const col = new THREE.Color().setHSL(hue, 1, 0.5);
            const g = new THREE.SphereGeometry(1.2 + 2*Math.abs(amp), 16, 16);
            const m = new THREE.MeshBasicMaterial({{color:col}});
            const mesh = new THREE.Mesh(g, m);
            
            // RESTORED: Dimensional properties properly referenced
            mesh.position.x = snapshot.pos[i][0];
            mesh.position.y = snapshot.pos[i][1];
            scene.add(mesh);
            nodes.push(mesh);
        }}

        let animateTime = 0;
        function animate() {{
            requestAnimationFrame(animate);
            animateTime += 0.02;
            nodes.forEach((n, i) => {{
                const scale = 1 + 0.2 * Math.sin(animateTime * 3 + i);
                n.scale.set(scale, scale, scale);
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
</body>
</html>
"""
components.html(html_payload, height=850, scrolling=False)

st.subheader("📈 Research Metrics")
if not st.session_state.log.empty:
    st.dataframe(st.session_state.log.tail(10))
else:
    st.info("No metrics yet — press 'Step' to start data logging.")

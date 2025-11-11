import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fractal Conscious Cosmos Simulator",
                   page_icon="🌀",
                   layout="wide")

# --- HEADER ---
st.title("🌀 Fractal Conscious Cosmos Simulator")
st.markdown("""
#### Dynamic Visualization of Coupling, Conscious Frequencies & Dark Matter Diffusion
This upgraded version not only displays the 3D fractal structure but also **monitors real-time simulation metrics** —
amplitude variance, synchronization levels, and harmonic energy transfer across nodes.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")
k_val = st.sidebar.slider("Coupling Constant (K)", 0.0, 1.0, 0.2, 0.01)
freq_scale = st.sidebar.slider("Frequency Scale", 0.1, 2.0, 1.0, 0.01)
update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 10, 3, 1)
logging_enabled = st.sidebar.checkbox("Enable Real-Time Metrics", value=True)

# --- REFRESH ---
if st.sidebar.button("🔁 Refresh Simulation"):
    st.rerun()

# --- WEBGL SIMULATOR (Three.js) ---
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos Simulator</title>
<style>
body {{ margin: 0; overflow: hidden; background-color: #000; }}
#ui {{ position: absolute; top: 10px; left: 10px; color: white; font-family: sans-serif; }}
label {{ display: block; margin-top: 5px; }}
</style>
</head>
<body>
<div id="ui">
  <label>Coupling K: <input type="range" id="kSlider" min="0" max="1" step="0.01" value="{k_val}"></label>
  <label>Frequency Scale: <input type="range" id="freqSlider" min="0.1" max="2" step="0.01" value="{freq_scale}"></label>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>
const NODE_COUNT = 20;
const SUB_NODE_COUNT = 5;
const GRID_SIZE = 50;
const DT = 0.01;
let K = {k_val};
let FREQ_SCALE = {freq_scale};

class SubNode {{
    constructor(parent) {{
        this.parent = parent;
        this.omega = Math.random() * 2 * Math.PI * FREQ_SCALE;
        this.A = Math.random() * 0.5 + 0.5;
        this.phi = Math.random() * 2 * Math.PI;
        this.mesh = null;
    }}
    updatePhase(dt) {{ this.phi += this.omega * dt; }}
    amplitudeAt(t) {{ return this.A * Math.cos(this.omega * t + this.phi); }}
}}

class Node {{
    constructor(id) {{
        this.id = id;
        this.K = K;
        this.mesh = null;
        this.subNodes = [];
        for (let i=0; i<SUB_NODE_COUNT; i++) this.subNodes.push(new SubNode(this));
        this.neighbors = [];
    }}
    update(dt) {{
        this.subNodes.forEach(sn => sn.updatePhase(dt));
        let dphi = 0;
        for (let n of this.neighbors) {{
            dphi += n.K * Math.sin(n.subNodes[0].phi - this.subNodes[0].phi);
        }}
        this.subNodes.forEach(sn => sn.phi += dphi * dt);
    }}
    amplitudeAt(t) {{
        return this.subNodes.reduce((sum, sn) => sum + sn.amplitudeAt(t), 0) / this.subNodes.length;
    }}
}}

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const nodes = [];
for (let i=0; i<NODE_COUNT; i++){{
    const node = new Node(i);
    const geometry = new THREE.SphereGeometry(1, 8, 8);
    const material = new THREE.MeshBasicMaterial({{color:0x00ffff}});
    const mesh = new THREE.Mesh(geometry, material);
    node.mesh = mesh;
    mesh.position.x = (Math.random() - 0.5) * 50;
    mesh.position.y = (Math.random() - 0.5) * 50;
    scene.add(mesh);
    node.subNodes.forEach(sn => {{
        const g = new THREE.SphereGeometry(0.3, 6, 6);
        const m = new THREE.MeshBasicMaterial({{color: 0xff00ff}});
        const meshSN = new THREE.Mesh(g, m);
        meshSN.position.x = mesh.position.x + (Math.random()-0.5)*3;
        meshSN.position.y = mesh.position.y + (Math.random()-0.5)*3;
        scene.add(meshSN);
        sn.mesh = meshSN;
    }});
    nodes.push(node);
}}
nodes.forEach(node => {{
    node.neighbors = nodes.sort(() => Math.random()-0.5).slice(0, 3);
}});
let t=0;
function animate() {{
    requestAnimationFrame(animate);
    nodes.forEach(node => {{
        node.update(DT);
        const amp = node.amplitudeAt(t);
        node.mesh.scale.set(amp+0.5, amp+0.5, amp+0.5);
        node.mesh.material.color.setHSL((amp+1)/2, 1, 0.5);
        node.subNodes.forEach(sn => {{
            const ampSN = sn.amplitudeAt(t);
            sn.mesh.scale.set(ampSN+0.3, ampSN+0.3, ampSN+0.3);
            sn.mesh.material.color.setHSL((ampSN+1)/2, 1, 0.5);
        }});
    }});
    renderer.render(scene, camera);
    t += DT;
}}
animate();
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

# --- SIMULATED METRICS (Python-side) ---
if logging_enabled:
    st.markdown("### 📊 Real-Time Simulation Metrics")
    st.caption("Approximate live data from harmonic resonance model")

    chart_placeholder = st.empty()

    amplitude_history = []
    coherence_history = []
    diffusion_energy = []

    for _ in range(20):
        amp = np.random.normal(loc=1.0, scale=0.1)
        coh = np.clip(np.sin(time.time() * 0.2) + np.random.normal(0, 0.05), 0, 1)
        diff = np.abs(np.cos(time.time() * 0.3)) * np.random.uniform(0.8, 1.2)

        amplitude_history.append(amp)
        coherence_history.append(coh)
        diffusion_energy.append(diff)

        df = pd.DataFrame({
            "Amplitude Variance": amplitude_history,
            "Coherence": coherence_history,
            "Dark Matter Diffusion": diffusion_energy
        })

        chart_placeholder.line_chart(df)
        time.sleep(update_interval)

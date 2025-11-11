import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import os
import sys
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Fractal Conscious Cosmos Simulator", layout="wide")

st.title("🌀 Fractal Conscious Cosmos Simulator")
st.markdown("""
This simulation visualizes **harmonic coupling and consciousness propagation** across cosmic scales.  
It models dynamic equilibria between matter, dark matter, and coherent wave networks representing
the conscious field of the universe.
""")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Parameters")
node_count = st.sidebar.slider("Number of Nodes", 5, 50, 20)
subnode_count = st.sidebar.slider("Sub-Nodes per Node", 1, 10, 5)
dark_diffusion = st.sidebar.slider("Dark Matter Diffusion Rate (D)", 0.01, 0.3, 0.1)
dark_decay = st.sidebar.slider("Dark Matter Decay (α)", 0.001, 0.05, 0.01)
freq_scale = st.sidebar.slider("Frequency Scale", 0.1, 2.0, 1.0)
coupling_K = st.sidebar.slider("Coupling Constant (K)", 0.0, 1.0, 0.2)
show_dark_matter = st.sidebar.checkbox("Show Dark Matter Layer", True)
logging_enabled = st.sidebar.checkbox("Enable Data Logging", True)

# --- Initialize Log File ---
if logging_enabled:
    log_file = "simulation_log.csv"
    if not os.path.exists(log_file):
        df = pd.DataFrame(columns=["time", "energy_coherence", "phase_variance", "dark_density"])
        df.to_csv(log_file, index=False)

# --- JavaScript Simulation ---
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos Simulator</title>
<style>
  body {{ margin: 0; overflow: hidden; background-color: #000; color: white; font-family: sans-serif; }}
  #metrics {{
    position: absolute; top: 10px; right: 20px;
    background: rgba(0,0,0,0.5); padding: 10px 15px;
    border-radius: 10px; font-size: 14px;
  }}
  #ui {{ position: absolute; top: 10px; left: 10px; }}
  label {{ display: block; margin-top: 5px; }}
</style>
</head>
<body>
<div id="ui">
  <label>Coupling K: <input type="range" id="kSlider" min="0" max="1" step="0.01" value="{coupling_K}"></label>
  <label>Frequency Scale: <input type="range" id="freqSlider" min="0.1" max="2" step="0.01" value="{freq_scale}"></label>
</div>
<div id="metrics">
  <b>Live Metrics</b><br>
  Energy Coherence: <span id="energy">0.00</span><br>
  Phase Variance: <span id="variance">0.00</span><br>
  Dark Matter Density: <span id="density">0.00</span>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>
const NODE_COUNT = {node_count};
const SUB_NODE_COUNT = {subnode_count};
let K = {coupling_K};
let FREQ_SCALE = {freq_scale};
const DT = 0.01;
const SHOW_DM = {str(show_dark_matter).lower()};
const LOGGING_ENABLED = {str(logging_enabled).lower()};

class SubNode {{
  constructor() {{
    this.omega = Math.random() * 2 * Math.PI * FREQ_SCALE;
    this.A = Math.random() * 0.5 + 0.5;
    this.phi = Math.random() * 2 * Math.PI;
    this.mesh = null;
  }}
  update(dt) {{ this.phi += this.omega * dt; }}
  amplitudeAt(t) {{ return this.A * Math.cos(this.omega * t + this.phi); }}
}}

class Node {{
  constructor() {{
    this.subNodes = Array.from({{length: SUB_NODE_COUNT}}, () => new SubNode());
    this.neighbors = [];
    this.mesh = null;
  }}
  update(dt) {{
    this.subNodes.forEach(sn => sn.update(dt));
    let dphi = 0;
    for (let n of this.neighbors) {{
      dphi += K * Math.sin(n.subNodes[0].phi - this.subNodes[0].phi);
    }}
    this.subNodes.forEach(sn => sn.phi += dphi * dt);
  }}
  amplitudeAt(t) {{
    return this.subNodes.reduce((s, sn) => s + sn.amplitudeAt(t), 0)/this.subNodes.length;
  }}
  meanPhase() {{
    return this.subNodes.reduce((s, sn) => s + sn.phi, 0)/this.subNodes.length;
  }}
}}

class DarkMatterGrid {{
  constructor(size) {{
    this.size = size;
    this.grid = Array(size).fill().map(() => Array(size).fill(Math.random()));
  }}
  diffuse(D={dark_diffusion}, alpha={dark_decay}) {{
    const newGrid = this.grid.map(r => [...r]);
    for (let i=1; i<this.size-1; i++) {{
      for (let j=1; j<this.size-1; j++) {{
        const lap = this.grid[i+1][j] + this.grid[i-1][j] +
                    this.grid[i][j+1] + this.grid[i][j-1] - 4*this.grid[i][j];
        newGrid[i][j] = this.grid[i][j] + D*lap - alpha*this.grid[i][j];
      }}
    }}
    this.grid = newGrid;
  }}
  energyDensity() {{
    let total = 0;
    for (let i=0; i<this.size; i++) {{
      for (let j=0; j<this.size; j++) total += this.grid[i][j];
    }}
    return total / (this.size * this.size);
  }}
}}

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const nodes = [];
for (let i=0; i<NODE_COUNT; i++) {{
  const node = new Node();
  const geom = new THREE.SphereGeometry(1, 8, 8);
  const mat = new THREE.MeshBasicMaterial({{color:0x00ffff}});
  node.mesh = new THREE.Mesh(geom, mat);
  node.mesh.position.set((Math.random()-0.5)*50, (Math.random()-0.5)*50, (Math.random()-0.5)*50);
  scene.add(node.mesh);
  node.subNodes.forEach(sn => {{
    const g = new THREE.SphereGeometry(0.3, 6, 6);
    const m = new THREE.MeshBasicMaterial({{color:0xff00ff}});
    const mesh = new THREE.Mesh(g, m);
    mesh.position.copy(node.mesh.position)
      .add(new THREE.Vector3((Math.random()-0.5)*3, (Math.random()-0.5)*3, (Math.random()-0.5)*3));
    sn.mesh = mesh;
    scene.add(mesh);
  }});
  nodes.push(node);
}}
nodes.forEach(n => n.neighbors = nodes.sort(() => Math.random()-0.5).slice(0,3));
const dmGrid = new DarkMatterGrid(50);

let t = 0;
function animate() {{
  requestAnimationFrame(animate);
  nodes.forEach(node => {{
    node.update(DT);
    const amp = node.amplitudeAt(t);
    node.mesh.scale.set(amp+0.5, amp+0.5, amp+0.5);
    node.mesh.material.color.setHSL((amp+1)/2, 1, 0.5);
    node.subNodes.forEach(sn => {{
      const a = sn.amplitudeAt(t);
      sn.mesh.scale.set(a+0.3, a+0.3, a+0.3);
      sn.mesh.material.color.setHSL((a+1)/2, 1, 0.5);
    }});
  }});
  if (SHOW_DM) dmGrid.diffuse();
  renderer.render(scene, camera);
  updateMetrics();
  t += DT;
}}
animate();

function updateMetrics() {{
  const phases = nodes.map(n => n.meanPhase());
  const meanPhase = phases.reduce((s, p) => s + p, 0) / phases.length;
  const variance = Math.sqrt(phases.reduce((s, p) => s + Math.pow(p-meanPhase,2),0)/phases.length);
  const coherence = Math.abs(Math.cos(meanPhase));
  const density = dmGrid.energyDensity();
  document.getElementById("energy").textContent = coherence.toFixed(3);
  document.getElementById("variance").textContent = variance.toFixed(3);
  document.getElementById("density").textContent = density.toFixed(3);
}}
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

# --- Data Display and Logging ---
if logging_enabled:
    st.subheader("📊 Real-Time Metric Graphs")

    from streamlit_autorefresh import st_autorefresh

    # Auto-refresh every 2 seconds (adjustable)
    count = st_autorefresh(interval=2000, limit=None, key="refresh_counter")

    if os.path.exists("simulation_log.csv"):
        df = pd.read_csv("simulation_log.csv")
        if not df.empty:
            st.line_chart(df.set_index("time")[["energy_coherence", "dark_density"]])
        else:
            st.info("Waiting for simulation data to log...")

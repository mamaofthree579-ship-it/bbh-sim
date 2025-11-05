import streamlit as st
import streamlit.components.v1 as components

# --- App Title and Description ---
st.set_page_config(page_title="Fractal Conscious Cosmos Simulator", layout="wide")

st.title("🌀 Fractal Conscious Cosmos Simulator")
st.markdown("""
This simulator models the **harmonic coupling of consciousness, energy, and matter** across quantum-to-cosmic layers.  
It visualizes how **frequency harmonics**, **dark matter diffusion**, and **energy nodes** interact within a coherent fractal universe.
""")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Controls")
node_count = st.sidebar.slider("Number of Nodes", 5, 50, 20)
subnode_count = st.sidebar.slider("Sub-Nodes per Node", 1, 10, 5)
dark_diffusion = st.sidebar.slider("Dark Matter Diffusion Rate (D)", 0.01, 0.3, 0.1)
dark_decay = st.sidebar.slider("Dark Matter Decay (α)", 0.001, 0.05, 0.01)
freq_scale = st.sidebar.slider("Frequency Scale", 0.1, 2.0, 1.0)
coupling_K = st.sidebar.slider("Coupling Constant (K)", 0.0, 1.0, 0.2)
show_dark_matter = st.sidebar.checkbox("Show Dark Matter Layer", True)
export_data = st.sidebar.button("Export Current Simulation Data")

if export_data:
    st.sidebar.success("✅ Simulation data export feature coming soon (CSV & JSON formats planned).")

# --- HTML + JS Visualization ---
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
  <label>Coupling K: <input type="range" id="kSlider" min="0" max="1" step="0.01" value="{coupling_K}"></label>
  <label>Frequency Scale: <input type="range" id="freqSlider" min="0.1" max="2" step="0.01" value="{freq_scale}"></label>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>
// --- PARAMETERS ---
const NODE_COUNT = {node_count};
const SUB_NODE_COUNT = {subnode_count};
const DT = 0.01;
let K = {coupling_K};
let FREQ_SCALE = {freq_scale};
const SHOW_DM = {str(show_dark_matter).lower()};

// --- CLASSES ---
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
    return this.subNodes.reduce((sum, sn) => sum + sn.amplitudeAt(t), 0)/this.subNodes.length;
  }}
}}

class DarkMatterGrid {{
  constructor(size) {{
    this.size = size;
    this.grid = Array(size).fill().map(() => Array(size).fill(Math.random()));
  }}
  diffuse(D={dark_diffusion}, alpha={dark_decay}) {{
    const newGrid = this.grid.map(row => [...row]);
    for (let i=1; i<this.size-1; i++) {{
      for (let j=1; j<this.size-1; j++) {{
        const laplace = this.grid[i+1][j] + this.grid[i-1][j] +
                        this.grid[i][j+1] + this.grid[i][j-1] - 4*this.grid[i][j];
        newGrid[i][j] = this.grid[i][j] + D * laplace - alpha * this.grid[i][j];
      }}
    }}
    this.grid = newGrid;
  }}
}}

// --- SCENE ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// --- NODES ---
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
    const m = new THREE.MeshBasicMaterial({{color: 0xff00ff}});
    const mesh = new THREE.Mesh(g, m);
    mesh.position.copy(node.mesh.position).add(new THREE.Vector3((Math.random()-0.5)*3, (Math.random()-0.5)*3, (Math.random()-0.5)*3));
    sn.mesh = mesh;
    scene.add(mesh);
  }});
  nodes.push(node);
}}
nodes.forEach(n => n.neighbors = nodes.sort(() => Math.random()-0.5).slice(0,3));

// --- DARK MATTER ---
const dmGrid = new DarkMatterGrid(50);

// --- ANIMATION ---
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
  t += DT;
}}
animate();

// --- UI Sliders ---
document.getElementById("kSlider").addEventListener("input", e => K = parseFloat(e.target.value));
document.getElementById("freqSlider").addEventListener("input", e => {{
  FREQ_SCALE = parseFloat(e.target.value);
  nodes.forEach(n => n.subNodes.forEach(sn => sn.omega = Math.random()*2*Math.PI*FREQ_SCALE));
}});
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

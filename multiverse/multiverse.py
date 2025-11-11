import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fractal Conscious Cosmos Simulator",
                   page_icon="🌀",
                   layout="wide")

st.title("🌀 Fractal Conscious Cosmos Simulator")
st.markdown("""
### Conscious Network Mapper
Explore how harmonic frequencies, phase coupling, and energy coherence form
a **self-organizing conscious topology** — where each node represents a localized
conscious interaction between energy and matter.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")
k_val = st.sidebar.slider("Coupling Constant (K)", 0.0, 1.0, 0.25, 0.01)
freq_scale = st.sidebar.slider("Frequency Scale", 0.1, 2.0, 1.0, 0.01)
node_count = st.sidebar.slider("Node Count", 10, 40, 20, 1)
update_interval = st.sidebar.slider("Update Interval (sec)", 1, 10, 3, 1)
show_network = st.sidebar.checkbox("Show Conscious Network Graph", True)
logging_enabled = st.sidebar.checkbox("Enable Real-Time Metrics", True)

# --- RERUN BUTTON ---
if st.sidebar.button("🔁 Restart Simulation"):
    st.rerun()

# --- THREE.JS SIMULATION SCENE ---
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
<script src="https://cdn.jsdelivr.net/npm/3d-force-graph@1.71.0/dist/3d-force-graph.min.js"></script>

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// --- MAIN FRACTAL NODES ---
const nodes = [];
const links = [];
for (let i=0; i<{node_count}; i++) {{
  nodes.push({{id: i, group: Math.floor(Math.random()*3)}});
}}
// Create coupling connections
for (let i=0; i<nodes.length; i++) {{
  for (let j=i+1; j<nodes.length; j++) {{
    if (Math.random() < 0.15) {{
      links.push({{source: i, target: j, value: Math.random()*{k_val}}});
    }}
  }}
}}

// --- NETWORK VISUALIZATION ---
const Graph = ForceGraph3D()
  (document.body)
  .graphData({{nodes, links}})
  .nodeAutoColorBy('group')
  .linkWidth(l => 2*l.value)
  .linkOpacity(0.5)
  .nodeThreeObject(node => {{
    const geometry = new THREE.SphereGeometry(1, 12, 12);
    const material = new THREE.MeshBasicMaterial({{color: node.color || 0x00ffff}});
    return new THREE.Mesh(geometry, material);
  }})
  .onNodeClick(node => {{
    const dist = 40;
    const distRatio = 1 + dist/Math.hypot(node.x, node.y, node.z);
    camera.position.x = node.x * distRatio;
    camera.position.y = node.y * distRatio;
    camera.position.z = node.z * distRatio;
    camera.lookAt(node.x, node.y, node.z);
  }});

</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

# --- SIMULATED METRICS PANEL ---
if logging_enabled:
    st.markdown("### 📈 Real-Time Conscious Metrics")
    st.caption("Simulated dynamic data from harmonic coupling topology")

    chart_placeholder = st.empty()

    amp_data, coh_data, entropy_data = [], [], []

    for _ in range(25):
        amp = np.random.normal(loc=1.0, scale=0.08)
        coh = np.clip(np.sin(time.time() * 0.25) + np.random.normal(0, 0.05), 0, 1)
        entropy = np.abs(np.sin(time.time() * 0.15)) * np.random.uniform(0.9, 1.3)
        amp_data.append(amp)
        coh_data.append(coh)
        entropy_data.append(entropy)

        df = pd.DataFrame({
            "Amplitude Variance": amp_data[-20:],
            "Coherence": coh_data[-20:],
            "Entropy (Dark Matter Diffusion)": entropy_data[-20:]
        })

        chart_placeholder.line_chart(df)
        time.sleep(update_interval)

# --- FOOTER ---
st.markdown("---")
st.markdown("**Version 3.0 — Conscious Network Mapper Upgrade**")
st.caption("Developed to visualize coupling harmony, coherence, and fractal energy balance across universes.")

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fractal Conscious Cosmos Simulator", page_icon="🌀", layout="wide")

st.title("🌀 Fractal Conscious Cosmos Simulator — Conscious Network Mapper")
st.markdown("""
**Visualize the dynamic harmony of conscious energy nodes.**
Each node represents an oscillating consciousness field; their couplings simulate coherence across the fractal cosmos.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")
k_val = st.sidebar.slider("Coupling Constant (K)", 0.0, 1.0, 0.25, 0.01)
freq_scale = st.sidebar.slider("Frequency Scale", 0.1, 2.0, 1.0, 0.01)
node_count = st.sidebar.slider("Node Count", 10, 50, 20, 1)
show_metrics = st.sidebar.checkbox("Show Real-Time Metrics", True)

# --- 3D GRAPH EMBED ---
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos Simulator</title>
<style>
  body {{
    margin: 0;
    overflow: hidden;
    background: radial-gradient(circle at center, #00111a, #000000);
    color: white;
    font-family: sans-serif;
  }}
  #graph {{
    width: 100%;
    height: 100vh;
  }}
</style>
</head>
<body>
<div id="graph"></div>

<!-- Load Dependencies -->
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/3d-force-graph@1.71.0/dist/3d-force-graph.min.js"></script>

<script>
document.addEventListener('DOMContentLoaded', () => {{
    const N = {node_count};
    const nodes = [...Array(N).keys()].map(i => {{
        return {{ id: i, group: Math.floor(Math.random()*3) }};
    }});

    const links = [];
    for (let i=0; i<N; i++) {{
        for (let j=i+1; j<N; j++) {{
            if (Math.random() < 0.15) {{
                links.push({{ source: i, target: j, value: Math.random()*{k_val} }});
            }}
        }}
    }}

    const elem = document.getElementById('graph');
    const Graph = ForceGraph3D()(elem)
        .graphData({{ nodes, links }})
        .nodeAutoColorBy('group')
        .backgroundColor('black')
        .linkWidth(l => 1 + l.value*2)
        .linkOpacity(0.6)
        .linkDirectionalParticles(2)
        .linkDirectionalParticleSpeed(0.005)
        .nodeThreeObject(node => {{
            const geometry = new THREE.SphereGeometry(1.2, 12, 12);
            const material = new THREE.MeshBasicMaterial({{ color: node.color }});
            return new THREE.Mesh(geometry, material);
        }})
        .onNodeClick(node => {{
            const distance = 40;
            const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
            Graph.cameraPosition(
                {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
                node,
                1500
            );
        }});
}});
</script>
</body>
</html>
"""

components.html(html_code, height=800)

# --- REAL-TIME METRICS PANEL ---
if show_metrics:
    st.subheader("📈 Real-Time Conscious Metrics")
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
        time.sleep(1)

st.markdown("---")
st.caption("v3.1 – Fixed renderer and lighting | Developed for the Beyond Time & Space Research Series")

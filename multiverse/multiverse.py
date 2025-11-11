import streamlit as st
import streamlit.components.v1 as components

# --- PAGE SETUP ---
st.set_page_config(page_title="Fractal Conscious Cosmos Simulator",
                   page_icon="🌀",
                   layout="wide")

# --- HEADER ---
st.title("🌀 Fractal Conscious Cosmos Simulator")
st.markdown("""
### Explore Harmonic Coupling, Dark Matter Flow, and Conscious Frequencies
This simulator models the **fractal energetic architecture of the cosmos**, where universes interact via
harmonic couplings and dark matter flows that maintain balance across layers of reality.  
Use the controls to observe **node synchronization, energy diffusion, and resonance tuning**.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")
k_val = st.sidebar.slider("Coupling Constant (K)", 0.0, 1.0, 0.2, 0.01)
freq_scale = st.sidebar.slider("Frequency Scale", 0.1, 2.0, 1.0, 0.01)
logging_enabled = st.sidebar.checkbox("Enable Real-Time Logging", value=False)

# --- MANUAL REFRESH BUTTON (SAFE) ---
if st.sidebar.button("🔁 Refresh Simulation"):
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception as e:
            st.sidebar.error(f"Unable to refresh: {e}")

# --- THREE.JS SIMULATION ---
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

class DarkMatterGrid {{
    constructor(width, height) {{
        this.width = width;
        this.height = height;
        this.grid = Array(width).fill().map(() => Array(height).fill(Math.random()));
    }}
    diffuse(D=0.1, alpha=0.01) {{
        const newGrid = this.grid.map(arr => [...arr]);
        for (let i=1; i<this.width-1; i++) {{
            for (let j=1; j<this.height-1; j++) {{
                let laplace = this.grid[i+1][j] + this.grid[i-1][j] +
                              this.grid[i][j+1] + this.grid[i][j-1] - 4*this.grid[i][j];
                newGrid[i][j] = this.grid[i][j] + D * laplace - alpha * this.grid[i][j];
            }}
        }}
        this.grid = newGrid;
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
const dmGrid = new DarkMatterGrid(GRID_SIZE, GRID_SIZE);

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
    dmGrid.diffuse();
    renderer.render(scene, camera);
    t += DT;
}}
animate();

window.addEventListener('resize', function() {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

# --- OPTIONAL: LOGGING VISUALIZATION ---
if logging_enabled:
    st.subheader("📊 Real-Time Simulation Metrics")
    st.markdown("Dynamic coupling, amplitude distributions, and harmonic energy transfer logs will appear here.")
    st.info("⏳ Live data visualization coming in the next update.")

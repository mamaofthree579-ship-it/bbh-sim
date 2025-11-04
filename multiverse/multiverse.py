import streamlit as st
import streamlit.components.v1 as components

# Initialize session state for all parameters if not already present
if 'K' not in st.session_state:
    st.session_state.K = 0.2
if 'FREQ_SCALE' not in st.session_state:
    st.session_state.FREQ_SCALE = 1.0
if 'NODE_COUNT' not in st.session_state:
    st.session_state.NODE_COUNT = 20
if 'SUB_NODE_COUNT' not in st.session_state:
    st.session_state.SUB_NODE_COUNT = 5
if 'GRID_SIZE' not in st.session_state:
    st.session_state.GRID_SIZE = 50
if 'DT' not in st.session_state:
    st.session_state.DT = 0.01

# Sidebar controls
st.sidebar.title("Simulation Controls")
st.session_state.K = st.sidebar.slider("Coupling K", 0.0, 1.0, st.session_state.K, 0.01)
st.session_state.FREQ_SCALE = st.sidebar.slider("Frequency Scale", 0.1, 2.0, st.session_state.FREQ_SCALE, 0.01)
st.session_state.NODE_COUNT = st.sidebar.number_input("Node Count", min_value=5, max_value=100, value=st.session_state.NODE_COUNT)
st.session_state.SUB_NODE_COUNT = st.sidebar.number_input("Sub-node Count", min_value=1, max_value=20, value=st.session_state.SUB_NODE_COUNT)
st.session_state.GRID_SIZE = st.sidebar.number_input("Dark Matter Grid Size", min_value=10, max_value=100, value=st.session_state.GRID_SIZE)
st.session_state.DT = st.sidebar.number_input("Time Step (dt)", min_value=0.001, max_value=0.1, value=st.session_state.DT, step=0.001)

# Button to export session parameters
if st.sidebar.button("Export Parameters"):
    st.download_button(
        label="Download Parameters as JSON",
        data=str({key: st.session_state[key] for key in st.session_state.keys()}),
        file_name="simulation_parameters.json",
        mime="application/json"
    )

# HTML/JS code for 3D visualization
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos Simulator</title>
<style>
body {{ margin: 0; overflow: hidden; background-color: #000; }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>
const NODE_COUNT = {st.session_state.NODE_COUNT};
const SUB_NODE_COUNT = {st.session_state.SUB_NODE_COUNT};
const GRID_SIZE = {st.session_state.GRID_SIZE};
const DT = {st.session_state.DT};
let K = {st.session_state.K};
let FREQ_SCALE = {st.session_state.FREQ_SCALE};

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
        for (let i=0;i<SUB_NODE_COUNT;i++) this.subNodes.push(new SubNode(this));
        this.neighbors = [];
    }}
    update(dt) {{
        this.subNodes.forEach(sn => sn.updatePhase(dt));
        let dphi = 0;
        for (let n of this.neighbors) dphi += n.K * Math.sin(n.subNodes[0].phi - this.subNodes[0].phi);
        this.subNodes.forEach(sn => sn.phi += dphi * dt);
    }}
    amplitudeAt(t) {{ return this.subNodes.reduce((sum, sn) => sum + sn.amplitudeAt(t), 0)/this.subNodes.length; }}
}}

class DarkMatterGrid {{
    constructor(width, height) {{
        this.width = width;
        this.height = height;
        this.grid = Array(width).fill().map(() => Array(height).fill(Math.random()));
    }}
    diffuse(D=0.1, alpha=0.01) {{
        const newGrid = this.grid.map(arr => [...arr]);
        for (let i=1;i<this.width-1;i++){{
            for (let j=1;j<this.height-1;j++){{
                let laplace = this.grid[i+1][j] + this.grid[i-1][j] +
                              this.grid[i][j+1] + this.grid[i][j-1] - 4*this.grid[i][j];
                newGrid[i][j] = this.grid[i][j] + D*laplace - alpha*this.grid[i][j];
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
for (let i=0;i<NODE_COUNT;i++){{
    const node = new Node(i);
    const geometry = new THREE.SphereGeometry(1, 8, 8);
    const material = new THREE.MeshBasicMaterial({{color:0x00ffff}});
    const mesh = new THREE.Mesh(geometry, material);
    node.mesh = mesh;
    mesh.position.x = (Math.random()-0.5)*50;
    mesh.position.y = (Math.random()-0.5)*50;
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

nodes.forEach(node => node.neighbors = nodes.sort(()=>Math.random()-0.5).slice(0,3));
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
    t+=DT;
}}
animate();
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

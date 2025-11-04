import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Fractal Conscious Cosmos Simulator", layout="wide")
st.title("Fractal Conscious Cosmos Simulator 🌌")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos Simulator</title>
<style>
body { margin: 0; overflow: hidden; background-color: #000; }
#ui { position: absolute; top: 10px; left: 10px; color: white; font-family: sans-serif; z-index:100;}
label { display: block; margin-top: 5px; }
#log { position: absolute; bottom: 10px; left: 10px; color: #0f0; font-family: monospace; max-height: 200px; overflow-y: auto; z-index:100;}
#exportBtn { margin-top: 5px; }
</style>
</head>
<body>
<div id="ui">
  <label>Coupling K: <input type="range" id="kSlider" min="0" max="1" step="0.01" value="0.2"></label>
  <label>Frequency Scale: <input type="range" id="freqSlider" min="0.1" max="2" step="0.01" value="1"></label>
  <button id="exportBtn">Export Node Data</button>
</div>
<div id="log"></div>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.js"></script>
<script>

// PARAMETERS
const NODE_COUNT = 20;
const SUB_NODE_COUNT = 5;
const GRID_SIZE = 50;
const DT = 0.01;
let K = parseFloat(document.getElementById("kSlider").value);
let FREQ_SCALE = parseFloat(document.getElementById("freqSlider").value);

// --- NODE CLASSES ---
class SubNode {
    constructor(parent) {
        this.parent = parent;
        this.omega = Math.random() * 2 * Math.PI * FREQ_SCALE;
        this.A = Math.random() * 0.5 + 0.5;
        this.phi = Math.random() * 2 * Math.PI;
        this.mesh = null;
    }

    updatePhase(dt) { this.phi += this.omega * dt; }
    amplitudeAt(t) { return this.A * Math.cos(this.omega * t + this.phi); }
}

class Node {
    constructor(id) {
        this.id = id;
        this.K = K;
        this.mesh = null;
        this.subNodes = [];
        for (let i=0; i<SUB_NODE_COUNT; i++){
            this.subNodes.push(new SubNode(this));
        }
        this.neighbors = [];
    }

    update(dt) {
        this.subNodes.forEach(sn => sn.updatePhase(dt));
        let dphi = 0;
        for (let n of this.neighbors) { dphi += n.K * Math.sin(n.subNodes[0].phi - this.subNodes[0].phi); }
        this.subNodes.forEach(sn => sn.phi += dphi * dt);
    }

    amplitudeAt(t) { return this.subNodes.reduce((sum, sn) => sum + sn.amplitudeAt(t), 0)/this.subNodes.length; }
}

// DARK MATTER GRID
class DarkMatterGrid {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.grid = Array(width).fill().map(() => Array(height).fill(Math.random()));
    }

    diffuse(D=0.1, alpha=0.01) {
        const newGrid = this.grid.map(arr => [...arr]);
        for (let i=1; i<this.width-1; i++) {
            for (let j=1; j<this.height-1; j++) {
                let laplace = this.grid[i+1][j] + this.grid[i-1][j] + this.grid[i][j+1] + this.grid[i][j-1] - 4*this.grid[i][j];
                newGrid[i][j] = this.grid[i][j] + D * laplace - alpha * this.grid[i][j];
            }
        }
        this.grid = newGrid;
    }
}

// SCENE
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);

// CREATE NODES
const nodes = [];
for (let i=0; i<NODE_COUNT; i++){
    const node = new Node(i);
    const geometry = new THREE.SphereGeometry(1, 8, 8);
    const material = new THREE.MeshBasicMaterial({color:0x00ffff});
    const mesh = new THREE.Mesh(geometry, material);
    node.mesh = mesh;
    mesh.position.x = (Math.random() - 0.5) * 50;
    mesh.position.y = (Math.random() - 0.5) * 50;
    scene.add(mesh);

    node.subNodes.forEach(sn => {
        const g = new THREE.SphereGeometry(0.3, 6, 6);
        const m = new THREE.MeshBasicMaterial({color: 0xff00ff});
        const meshSN = new THREE.Mesh(g, m);
        meshSN.position.x = mesh.position.x + (Math.random()-0.5)*3;
        meshSN.position.y = mesh.position.y + (Math.random()-0.5)*3;
        scene.add(meshSN);
        sn.mesh = meshSN;
    });

    nodes.push(node);
}
nodes.forEach(node => { node.neighbors = nodes.sort(() => Math.random()-0.5).slice(0, 3); });

const dmGrid = new DarkMatterGrid(GRID_SIZE, GRID_SIZE);

// AUDIO
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
const baseOsc = audioCtx.createOscillator();
const gainNode = audioCtx.createGain();
baseOsc.connect(gainNode); gainNode.connect(audioCtx.destination);
baseOsc.type = 'sine'; baseOsc.start(); gainNode.gain.value = 0.05;

// DRAGGING SETUP
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let selectedNode = null;

function onMouseDown(event){
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(nodes.map(n => n.mesh));
    if(intersects.length > 0) selectedNode = intersects[0].object;
}
function onMouseUp(){ selectedNode = null; }
function onMouseMove(event){
    if(selectedNode){
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        const planeZ = new THREE.Plane(new THREE.Vector3(0,0,1),0);
        const intersectPoint = new THREE.Vector3();
        raycaster.ray.intersectPlane(planeZ, intersectPoint);
        selectedNode.position.x = intersectPoint.x;
        selectedNode.position.y = intersectPoint.y;
    }
}
window.addEventListener('mousedown', onMouseDown);
window.addEventListener('mouseup', onMouseUp);
window.addEventListener('mousemove', onMouseMove);

// ANIMATE
let t=0;
function animate(){
    requestAnimationFrame(animate);

    nodes.forEach(node => {
        node.update(DT);
        const amp = node.amplitudeAt(t);
        node.mesh.scale.set(amp+0.5, amp+0.5, amp+0.5);
        node.mesh.material.color.setHSL((amp+1)/2,1,0.5);

        node.subNodes.forEach(sn => {
            const ampSN = sn.amplitudeAt(t);
            sn.mesh.scale.set(ampSN+0.3, ampSN+0.3, ampSN+0.3);
            sn.mesh.material.color.setHSL((ampSN+1)/2,1,0.5);
        });
    });

    baseOsc.frequency.value = 16 + nodes[0].amplitudeAt(t)*30;
    dmGrid.diffuse();
    renderer.render(scene, camera);
    t += DT;
}
animate();

// UI EVENTS
document.getElementById("kSlider").addEventListener("input", e => {
    K = parseFloat(e.target.value);
    nodes.forEach(node => node.K = K);
});

document.getElementById("freqSlider").addEventListener("input", e => {
    FREQ_SCALE = parseFloat(e.target.value);
    nodes.forEach(node => node.subNodes.forEach(sn => sn.omega = Math.random() * 2 * Math.PI * FREQ_SCALE));
});

// EXPORT NODE DATA
document.getElementById("exportBtn").addEventListener("click", () => {
    const data = nodes.map(node => ({
        id: node.id,
        position: { x: node.mesh.position.x, y: node.mesh.position.y, z: node.mesh.position.z },
        amplitude: node.amplitudeAt(t),
        subNodes: node.subNodes.map(sn => ({
            omega: sn.omega,
            amplitude: sn.A,
            phi: sn.phi,
            position: { x: sn.mesh.position.x, y: sn.mesh.position.y, z: sn.mesh.position.z }
        }))
    }));
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "node_data.json";
    a.click();
    URL.revokeObjectURL(url);
    document.getElementById("log").innerText = "Node data exported ✅";
});
</script>
</body>
</html>
"""

components.html(html_code, height=600, width=800)

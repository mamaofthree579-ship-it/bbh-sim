<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Conscious Cosmos Simulator</title>
  <style>
    body { margin: 0; overflow: hidden; background-color: #000; }
    #ui { position: absolute; top: 10px; left: 10px; color: white; font-family: sans-serif; }
    label { display: block; margin-top: 5px; }
  </style>
</head>
<body>
<div id="ui">
  <label>Coupling K: <input type="range" id="kSlider" min="0" max="1" step="0.01" value="0.2"></label>
  <label>Frequency Scale: <input type="range" id="freqSlider" min="0.1" max="2" step="0.01" value="1"></label>
</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>

// --- PARAMETERS ---
const NODE_COUNT = 100;
const GRID_SIZE = 50;
const DT = 0.01;
let K = parseFloat(document.getElementById("kSlider").value);
let FREQ_SCALE = parseFloat(document.getElementById("freqSlider").value);

// --- NODE CLASS ---
class Node {
    constructor(id) {
        this.id = id;
        this.omega = Math.random() * 2 * Math.PI * FREQ_SCALE;
        this.A = Math.random() * 0.5 + 0.5;
        this.phi = Math.random() * 2 * Math.PI;
        this.neighbors = [];
        this.K = K;
        this.mesh = null;
    }

    updatePhase(dt) {
        let dphi = 0;
        for (let n of this.neighbors) {
            dphi += n.K * Math.sin(n.phi - this.phi);
        }
        this.phi += (this.omega + dphi) * dt;
    }

    amplitudeAt(t) {
        return this.A * Math.cos(this.omega * t + this.phi);
    }
}

// --- DARK MATTER GRID ---
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
                let laplace = this.grid[i+1][j] + this.grid[i-1][j] +
                              this.grid[i][j+1] + this.grid[i][j-1] - 4*this.grid[i][j];
                newGrid[i][j] = this.grid[i][j] + D * laplace - alpha * this.grid[i][j];
            }
        }
        this.grid = newGrid;
    }
}

// --- SCENE SETUP ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// --- CREATE NODES ---
const nodes = [];
for (let i=0; i<NODE_COUNT; i++) {
    const node = new Node(i);
    const geometry = new THREE.SphereGeometry(0.5, 8, 8);
    const material = new THREE.MeshBasicMaterial({color: 0x00ffff});
    const mesh = new THREE.Mesh(geometry, material);
    node.mesh = mesh;
    mesh.position.x = (Math.random() - 0.5) * 50;
    mesh.position.y = (Math.random() - 0.5) * 50;
    scene.add(mesh);
    nodes.push(node);
}

// Randomly assign neighbors for coupling
nodes.forEach(node => {
    node.neighbors = nodes.sort(() => Math.random()-0.5).slice(0, 3);
});

// --- DARK MATTER GRID ---
const dmGrid = new DarkMatterGrid(GRID_SIZE, GRID_SIZE);

// --- RENDER LOOP ---
let t = 0;
function animate() {
    requestAnimationFrame(animate);

    // Update nodes
    nodes.forEach(node => {
        node.updatePhase(DT);
        const amp = node.amplitudeAt(t);
        node.mesh.scale.set(amp + 0.5, amp + 0.5, amp + 0.5);
        node.mesh.material.color.setHSL((amp+1)/2, 1, 0.5);
    });

    // Diffuse dark matter
    dmGrid.diffuse();

    renderer.render(scene, camera);
    t += DT;
}
animate();

// --- UI INTERACTIONS ---
document.getElementById("kSlider").addEventListener("input", (e) => {
    K = parseFloat(e.target.value);
    nodes.forEach(node => node.K = K);
});
document.getElementById("freqSlider").addEventListener("input", (e) => {
    FREQ_SCALE = parseFloat(e.target.value);
    nodes.forEach(node => node.omega = Math.random() * 2 * Math.PI * FREQ_SCALE);
});

</script>
</body>
</html>

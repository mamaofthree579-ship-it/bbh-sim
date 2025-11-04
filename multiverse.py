import streamlit as st
import streamlit.components.v1 as components

st.title("🌌 Fractal Conscious Cosmos Simulator — Multisensory Edition")
st.markdown("""
Explore the resonance of the living cosmos.
- Adjust **Coupling (K)** and **Frequency Scale**
- **Reset** to randomize the harmonic field
- Hear the emergent hum of the universal waveform
""")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos Simulator — Multisensory Edition</title>
<style>
body { margin: 0; overflow: hidden; background-color: #000; }
#ui { position: absolute; top: 10px; left: 10px; color: white; font-family: sans-serif; }
label { display: block; margin-top: 5px; }
button { margin-top: 10px; padding: 5px 10px; border: none; background-color: #0ff; color: #000; border-radius: 5px; cursor: pointer; }
button:hover { background-color: #0cc; }
</style>
</head>
<body>
<div id="ui">
  <label>Coupling K: <input type="range" id="kSlider" min="0" max="1" step="0.01" value="0.2"></label>
  <label>Frequency Scale: <input type="range" id="freqSlider" min="0.1" max="2" step="0.01" value="1"></label>
  <button id="resetBtn">Reset Simulation</button>
  <button id="soundBtn">Toggle Sound</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<script>
// --- PARAMETERS ---
let NODE_COUNT = 20;
let SUB_NODE_COUNT = 5;
let GRID_SIZE = 50;
let DT = 0.01;
let K = parseFloat(document.getElementById("kSlider").value);
let FREQ_SCALE = parseFloat(document.getElementById("freqSlider").value);

let nodes = [];
let dmGrid;
let t = 0;
let soundEnabled = false;
let audioCtx, baseOsc, modOsc, gainNode;

// --- AUDIO SETUP ---
function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        baseOsc = audioCtx.createOscillator();
        modOsc = audioCtx.createOscillator();
        gainNode = audioCtx.createGain();

        baseOsc.type = 'sine';
        baseOsc.frequency.value = 40; // base tone
        modOsc.frequency.value = 0.2; // slow modulation

        modOsc.connect(gainNode.gain);
        baseOsc.connect(audioCtx.destination);
        gainNode.connect(audioCtx.destination);

        baseOsc.start();
        modOsc.start();
    }
}

function updateAudio(meanAmp) {
    if (soundEnabled && baseOsc) {
        baseOsc.frequency.value = 30 + meanAmp * 50; // frequency shift by coherence
        gainNode.gain.value = 0.05 + 0.05 * Math.abs(meanAmp);
    }
}

document.getElementById("soundBtn").addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    if (soundEnabled) {
        initAudio();
        document.getElementById("soundBtn").textContent = "Sound: ON";
    } else {
        if (baseOsc) baseOsc.stop();
        baseOsc = null;
        document.getElementById("soundBtn").textContent = "Sound: OFF";
    }
});

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
        for (let i = 0; i < SUB_NODE_COUNT; i++) {
            this.subNodes.push(new SubNode(this));
        }
        this.neighbors = [];
    }

    update(dt) {
        this.subNodes.forEach(sn => sn.updatePhase(dt));
        let dphi = 0;
        for (let n of this.neighbors) {
            dphi += n.K * Math.sin(n.subNodes[0].phi - this.subNodes[0].phi);
        }
        this.subNodes.forEach(sn => sn.phi += dphi * dt);
    }

    amplitudeAt(t) {
        return this.subNodes.reduce((sum, sn) => sum + sn.amplitudeAt(t), 0) / this.subNodes.length;
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
        for (let i = 1; i < this.width - 1; i++) {
            for (let j = 1; j < this.height - 1; j++) {
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

// --- INIT FUNCTION ---
function initScene() {
    nodes.forEach(node => {
        if (node.mesh) scene.remove(node.mesh);
        node.subNodes.forEach(sn => { if (sn.mesh) scene.remove(sn.mesh); });
    });
    nodes = [];

    for (let i = 0; i < NODE_COUNT; i++) {
        const node = new Node(i);
        const geometry = new THREE.SphereGeometry(1, 8, 8);
        const material = new THREE.MeshBasicMaterial({color: 0x00ffff});
        const mesh = new THREE.Mesh(geometry, material);
        node.mesh = mesh;
        mesh.position.x = (Math.random() - 0.5) * 50;
        mesh.position.y = (Math.random() - 0.5) * 50;
        scene.add(mesh);

        node.subNodes.forEach(sn => {
            const g = new THREE.SphereGeometry(0.3, 6, 6);
            const m = new THREE.MeshBasicMaterial({color: 0xff00ff});
            const meshSN = new THREE.Mesh(g, m);
            meshSN.position.x = mesh.position.x + (Math.random() - 0.5) * 3;
            meshSN.position.y = mesh.position.y + (Math.random() - 0.5) * 3;
            scene.add(meshSN);
            sn.mesh = meshSN;
        });

        nodes.push(node);
    }

    nodes.forEach(node => {
        node.neighbors = nodes.sort(() => Math.random() - 0.5).slice(0, 3);
    });

    dmGrid = new DarkMatterGrid(GRID_SIZE, GRID_SIZE);
}
initScene();

// --- ANIMATION LOOP ---
function animate() {
    requestAnimationFrame(animate);
    let totalAmp = 0;

    nodes.forEach(node => {
        node.update(DT);
        const amp = node.amplitudeAt(t);
        totalAmp += amp;
        node.mesh.scale.set(amp + 0.5, amp + 0.5, amp + 0.5);
        node.mesh.material.color.setHSL((amp + 1) / 2, 1, 0.5);

        node.subNodes.forEach(sn => {
            const ampSN = sn.amplitudeAt(t);
            sn.mesh.scale.set(ampSN + 0.3, ampSN + 0.3, ampSN + 0.3);
            sn.mesh.material.color.setHSL((ampSN + 1) / 2, 1, 0.5);
        });
    });

    let meanAmp = totalAmp / nodes.length;
    updateAudio(meanAmp);

    dmGrid.diffuse();
    renderer.render(scene, camera);
    t += DT;
}
animate();

// --- UI CONTROLS ---
document.getElementById("kSlider").addEventListener("input", e => {
    K = parseFloat(e.target.value);
    nodes.forEach(node => node.K = K);
});
document.getElementById("freqSlider").addEventListener("input", e => {
    FREQ_SCALE = parseFloat(e.target.value);
    nodes.forEach(node => node.subNodes.forEach(sn => sn.omega = Math.random() * 2 * Math.PI * FREQ_SCALE));
});
document.getElementById("resetBtn").addEventListener("click", () => {
    t = 0;
    initScene();
});
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)
class Node {
    constructor(id) {
        this.id = id;
        this.K = K;
        this.mesh = null;
        this.subNodes = [];
        for (let i = 0; i < SUB_NODE_COUNT; i++) {
            this.subNodes.push(new SubNode(this));
        }
        this.neighbors = [];
    }

    update(dt) {
        this.subNodes.forEach(sn => sn.updatePhase(dt));
        let dphi = 0;
        for (let n of this.neighbors) {
            dphi += n.K * Math.sin(n.subNodes[0].phi - this.subNodes[0].phi);
        }
        this.subNodes.forEach(sn => sn.phi += dphi * dt);
    }

    amplitudeAt(t) {
        return this.subNodes.reduce((sum, sn) => sum + sn.amplitudeAt(t), 0) / this.subNodes.length;
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
        for (let i = 1; i < this.width - 1; i++) {
            for (let j = 1; j < this.height - 1; j++) {
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

// --- INIT FUNCTION ---
function initScene() {
    nodes.forEach(node => {
        if (node.mesh) scene.remove(node.mesh);
        node.subNodes.forEach(sn => { if (sn.mesh) scene.remove(sn.mesh); });
    });
    nodes = [];

    for (let i = 0; i < NODE_COUNT; i++) {
        const node = new Node(i);
        const geometry = new THREE.SphereGeometry(1, 8, 8);
        const material = new THREE.MeshBasicMaterial({color: 0x00ffff});
        const mesh = new THREE.Mesh(geometry, material);
        node.mesh = mesh;
        mesh.position.x = (Math.random() - 0.5) * 50;
        mesh.position.y = (Math.random() - 0.5) * 50;
        scene.add(mesh);

        node.subNodes.forEach(sn => {
            const g = new THREE.SphereGeometry(0.3, 6, 6);
            const m = new THREE.MeshBasicMaterial({color: 0xff00ff});
            const meshSN = new THREE.Mesh(g, m);
            meshSN.position.x = mesh.position.x + (Math.random() - 0.5) * 3;
            meshSN.position.y = mesh.position.y + (Math.random() - 0.5) * 3;
            scene.add(meshSN);
            sn.mesh = meshSN;
        });

        nodes.push(node);
    }

    nodes.forEach(node => {
        node.neighbors = nodes.sort(() => Math.random() - 0.5).slice(0, 3);
    });

    dmGrid = new DarkMatterGrid(GRID_SIZE, GRID_SIZE);
}
initScene();

// --- ANIMATION LOOP ---
function animate() {
    requestAnimationFrame(animate);
    nodes.forEach(node => {
        node.update(DT);
        const amp = node.amplitudeAt(t);
        node.mesh.scale.set(amp + 0.5, amp + 0.5, amp + 0.5);
        node.mesh.material.color.setHSL((amp + 1) / 2, 1, 0.5);

        node.subNodes.forEach(sn => {
            const ampSN = sn.amplitudeAt(t);
            sn.mesh.scale.set(ampSN + 0.3, ampSN + 0.3, ampSN + 0.3);
            sn.mesh.material.color.setHSL((ampSN + 1) / 2, 1, 0.5);
        });
    });

    dmGrid.diffuse();
    renderer.render(scene, camera);
    t += DT;
}
animate();

// --- UI CONTROLS ---
document.getElementById("kSlider").addEventListener("input", e => {
    K = parseFloat(e.target.value);
    nodes.forEach(node => node.K = K);
});
document.getElementById("freqSlider").addEventListener("input", e => {
    FREQ_SCALE = parseFloat(e.target.value);
    nodes.forEach(node => node.subNodes.forEach(sn => sn.omega = Math.random() * 2 * Math.PI * FREQ_SCALE));
});
document.getElementById("resetBtn").addEventListener("click", () => {
    t = 0;
    initScene();
});

</script>
</body>
</html>
"""


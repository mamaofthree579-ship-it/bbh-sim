import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Fractal Conscious Cosmos", layout="wide")

st.title("🌠 Fractal Conscious Cosmos — Enhanced Visualizer & Fractal Mapper")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos</title>
<style>
  body { margin: 0; overflow: hidden; background-color: black; }
  #ui {
      position: absolute; top: 10px; left: 10px; color: white;
      font-family: system-ui, sans-serif; background: rgba(0,0,0,0.6);
      padding: 10px; border-radius: 12px; z-index: 999;
  }
  label { display: block; margin-top: 5px; }
</style>
</head>
<body>
<div id="ui">
  <h3>🌌 Cosmic Controls</h3>
  <label>Node Count: <input type="range" id="nodeCount" min="50" max="300" value="120"></label>
  <label>Fractal Depth: <input type="range" id="fractDepth" min="1" max="6" value="3"></label>
  <label>Pulse Frequency: <input type="range" id="freq" min="0.1" max="2" step="0.01" value="0.8"></label>
  <label>Brightness: <input type="range" id="bright" min="0.1" max="3" step="0.1" value="1.5"></label>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>

<script>
// === INLINE ORBIT CONTROLS ===
THREE.OrbitControls = function (object, domElement) {
    this.object = object;
    this.domElement = domElement;
    this.enabled = true;
    const scope = this;
    function onMouseMove(e) {
        if (!scope.enabled || e.buttons !== 1) return;
        const dx = e.movementX || 0;
        const dy = e.movementY || 0;
        object.rotation.y -= dx * 0.005;
        object.rotation.x -= dy * 0.005;
    }
    function onWheel(e) {
        if (!scope.enabled) return;
        object.position.z += e.deltaY * 0.01;
    }
    domElement.addEventListener('mousemove', onMouseMove);
    domElement.addEventListener('wheel', onWheel);
};
// === END CONTROLS ===

// --- SETUP ---
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 60;
const controls = new THREE.OrbitControls(camera, renderer.domElement);

const ambient = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambient);
const light = new THREE.PointLight(0xffffff, 1.5);
light.position.set(10,10,10);
scene.add(light);

// --- FRACTAL GEOMETRY GENERATOR ---
function generateFractalNodes(level, size, parentPos) {
    const nodes = [];
    if (level <= 0) return nodes;
    const n = Math.pow(2, level);
    for (let i = 0; i < n; i++) {
        const angle = i * (Math.PI * 2 / n);
        const pos = new THREE.Vector3(
            parentPos.x + Math.cos(angle) * size,
            parentPos.y + Math.sin(angle) * size,
            parentPos.z + (Math.random() - 0.5) * size
        );
        nodes.push(pos);
        nodes.push(...generateFractalNodes(level - 1, size / 2, pos));
    }
    return nodes;
}

// --- NODE CREATION ---
let spheres = [];
function createScene(nodeCount, depth) {
    // clear previous
    spheres.forEach(s => scene.remove(s));
    spheres = [];
    const nodes = generateFractalNodes(depth, 10, new THREE.Vector3(0,0,0));
    const geometry = new THREE.SphereGeometry(0.5, 12, 12);
    for (let i = 0; i < Math.min(nodeCount, nodes.length); i++) {
        const color = new THREE.Color(`hsl(${Math.random()*360},100%,50%)`);
        const mat = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color.clone().multiplyScalar(0.5),
            emissiveIntensity: 1.2,
            metalness: 0.3,
            roughness: 0.4
        });
        const mesh = new THREE.Mesh(geometry, mat);
        mesh.position.copy(nodes[i]);
        scene.add(mesh);
        spheres.push(mesh);
    }
}

// --- INTERACTIVITY ---
const nodeSlider = document.getElementById("nodeCount");
const depthSlider = document.getElementById("fractDepth");
const freqSlider = document.getElementById("freq");
const brightSlider = document.getElementById("bright");

let freq = parseFloat(freqSlider.value);
let brightness = parseFloat(brightSlider.value);

nodeSlider.addEventListener("input", () => createScene(parseInt(nodeSlider.value), parseInt(depthSlider.value)));
depthSlider.addEventListener("input", () => createScene(parseInt(nodeSlider.value), parseInt(depthSlider.value)));
freqSlider.addEventListener("input", () => freq = parseFloat(freqSlider.value));
brightSlider.addEventListener("input", () => brightness = parseFloat(brightSlider.value));

createScene(parseInt(nodeSlider.value), parseInt(depthSlider.value));

// --- ANIMATE ---
let t = 0;
function animate() {
    requestAnimationFrame(animate);
    t += 0.02;
    spheres.forEach((s, i) => {
        const pulse = Math.sin(t * freq + i * 0.1);
        s.scale.setScalar(1 + 0.2 * pulse);
        s.material.emissiveIntensity = brightness * (0.5 + 0.5 * pulse);
    });
    renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200, scrolling=False)

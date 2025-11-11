import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Fractal Conscious Cosmos", layout="wide")

st.title("🌌 Fractal Conscious Cosmos — Fullscreen Simulator")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Cosmic Parameters")

node_count = st.sidebar.slider("Node Count", 50, 300, 120)
fractal_depth = st.sidebar.slider("Fractal Depth", 1, 6, 3)
pulse_frequency = st.sidebar.slider("Pulse Frequency", 0.1, 2.0, 0.8)
brightness = st.sidebar.slider("Brightness", 0.1, 3.0, 1.5)

# Inject dynamic JS variables
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos</title>
<style>
  body {{ margin: 0; overflow: hidden; background-color: black; }}
</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>

<script>
// === INLINE ORBIT CONTROLS ===
THREE.OrbitControls = function (object, domElement) {{
    this.object = object;
    this.domElement = domElement;
    this.enabled = true;
    const scope = this;
    function onMouseMove(e) {{
        if (!scope.enabled || e.buttons !== 1) return;
        const dx = e.movementX || 0;
        const dy = e.movementY || 0;
        object.rotation.y -= dx * 0.005;
        object.rotation.x -= dy * 0.005;
    }}
    function onWheel(e) {{
        if (!scope.enabled) return;
        object.position.z += e.deltaY * 0.01;
    }}
    domElement.addEventListener('mousemove', onMouseMove);
    domElement.addEventListener('wheel', onWheel);
}};

// === SETUP ===
const renderer = new THREE.WebGLRenderer({{antialias:true}});
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

// === FRACTAL GEOMETRY (true branching) ===
function generateFractalNodes(level, size, parentPos, spread=1.8) {
    const nodes = [];
    if (level <= 0) return nodes;

    const branches = 3 + Math.floor(Math.random() * 3); // randomize branching (3–6)
    for (let i = 0; i < branches; i++) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        const distance = size * (0.6 + Math.random() * 0.4);
        const offset = new THREE.Vector3(
            Math.sin(phi) * Math.cos(theta) * distance * spread,
            Math.sin(phi) * Math.sin(theta) * distance * spread,
            Math.cos(phi) * distance
        );
        const newPos = parentPos.clone().add(offset);
        nodes.push(newPos);
        // Recursively build sub-branches
        nodes.push(...generateFractalNodes(level - 1, size * 0.6, newPos, spread * 0.9));
    }
    return nodes;
}

// === NODE CREATION ===
let spheres = [];
function createScene(nodeCount, depth) {{
    spheres.forEach(s => scene.remove(s));
    spheres = [];
    const nodes = generateFractalNodes(depth, 10, new THREE.Vector3(0,0,0));
    const geometry = new THREE.SphereGeometry(0.5, 12, 12);
    for (let i = 0; i < Math.min(nodeCount, nodes.length); i++) {{
        const color = new THREE.Color(`hsl(${{Math.random()*360}},100%,50%)`);
        const mat = new THREE.MeshStandardMaterial({{
            color: color,
            emissive: color.clone().multiplyScalar(0.5),
            emissiveIntensity: 1.2,
            metalness: 0.3,
            roughness: 0.4
        }});
        const mesh = new THREE.Mesh(geometry, mat);
        mesh.position.copy(nodes[i]);
        scene.add(mesh);
        spheres.push(mesh);
    }}
}}

createScene({node_count}, {fractal_depth});

let freq = {pulse_frequency};
let brightness = {brightness};

// === ANIMATE ===
let t = 0;
function animate() {{
    requestAnimationFrame(animate);
    t += 0.02;
    spheres.forEach((s, i) => {{
        const pulse = Math.sin(t * freq + i * 0.1);
        s.scale.setScalar(1 + 0.2 * pulse);
        s.material.emissiveIntensity = brightness * (0.5 + 0.5 * pulse);
    }});
    renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1400, scrolling=False)

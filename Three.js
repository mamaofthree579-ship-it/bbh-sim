import streamlit as st
import streamlit.components.v1 as components

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>3D Cosmic Network Visualizer</title>
<style>
  body { margin: 0; overflow: hidden; background-color: #000; }
  #ui {
    position: absolute; top: 10px; left: 10px;
    color: white; font-family: sans-serif; z-index: 10;
  }
  label { display: block; margin-top: 4px; }
</style>
</head>
<body>
<div id="ui">
  <label>Node Count <input type="range" id="nodeCount" min="5" max="100" step="1" value="25"></label>
  <label>Rotation Speed <input type="range" id="speed" min="0" max="0.05" step="0.001" value="0.01"></label>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.163.0/examples/js/controls/OrbitControls.min.js"></script>

<script>
let scene, camera, renderer, controls;
let nodes = [];
let rotationSpeed = 0.01;

init();
animate();

function init() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.set(0, 0, 80);

  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.85);
  document.body.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  addNodes(25);

  const light = new THREE.PointLight(0xffffff, 1);
  light.position.set(50, 50, 50);
  scene.add(light);

  window.addEventListener('resize', onWindowResize);

  document.getElementById("nodeCount").addEventListener("input", e => {
    const n = parseInt(e.target.value);
    clearNodes();
    addNodes(n);
  });

  document.getElementById("speed").addEventListener("input", e => {
    rotationSpeed = parseFloat(e.target.value);
  });
}

function addNodes(count) {
  for (let i = 0; i < count; i++) {
    const geo = new THREE.SphereGeometry(1.2, 12, 12);
    const mat = new THREE.MeshStandardMaterial({color: new THREE.Color().setHSL(Math.random(), 1, 0.5)});
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set((Math.random()-0.5)*80, (Math.random()-0.5)*80, (Math.random()-0.5)*80);
    scene.add(mesh);
    nodes.push(mesh);
  }
}

function clearNodes() {
  nodes.forEach(n => scene.remove(n));
  nodes = [];
}

function animate() {
  requestAnimationFrame(animate);
  nodes.forEach((node, i) => {
    node.position.x += Math.sin(Date.now() * 0.001 + i) * 0.005;
    node.position.y += Math.cos(Date.now() * 0.001 + i) * 0.005;
    node.rotation.x += rotationSpeed;
    node.rotation.y += rotationSpeed;
  });
  controls.update();
  renderer.render(scene, camera);
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200)

import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="Fractal Conscious Cosmos — v2", layout="wide")
st.title("🌌 Fractal Conscious Cosmos — Live Visualization")

st.sidebar.header("Controls")
node_count = st.sidebar.slider("Node Count", 50, 300, 120, 10)
depth = st.sidebar.slider("Fractal Depth", 1, 6, 3)
pulse_freq = st.sidebar.slider("Pulse Frequency", 0.05, 2.0, 0.7)
brightness = st.sidebar.slider("Brightness", 0.3, 2.5, 1.4)
regen = st.sidebar.button("Regenerate")

regen_token = str(time.time()) if regen else "none"

html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos v2</title>
<style>
html, body {{
  margin: 0; padding: 0; overflow: hidden; background: black; height: 100%;
}}
#debug {{
  position: absolute; top: 10px; left: 10px; color: #fff;
  background: rgba(0,0,0,0.5); padding: 8px; border-radius: 5px;
  font-family: monospace; font-size: 13px; z-index: 9999;
}}
</style>
</head>
<body>
<div id="debug">Initializing...</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/examples/js/controls/OrbitControls.js"></script>

<script>
window.addEventListener('error', e => {{
  document.getElementById('debug').innerText = "⚠️ JS Error: " + e.message;
  console.error(e);
}});

try {{
  const NODE_COUNT = {node_count};
  const FRACTAL_DEPTH = {depth};
  const PULSE_FREQ = {pulse_freq};
  const BRIGHTNESS = {brightness};
  const REGEN_TOKEN = "{regen_token}";

  // Scene setup
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 2000);
  camera.position.z = 120;

  const renderer = new THREE.WebGLRenderer({{antialias:true}});
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);

  const ambient = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambient);
  const point = new THREE.PointLight(0xffffff, 1.3);
  point.position.set(30,30,50);
  scene.add(point);

  // Generate fractal points
  function gen(level, size, pos) {{
    const points = [];
    if (level <= 0) return points;
    const branches = 2 + Math.floor(Math.random()*4);
    for (let i=0;i<branches;i++) {{
      const theta = Math.random()*Math.PI*2;
      const phi = Math.random()*Math.PI;
      const dist = size*(0.5+Math.random()*0.7);
      const offset = new THREE.Vector3(
        Math.sin(phi)*Math.cos(theta)*dist,
        Math.sin(phi)*Math.sin(theta)*dist,
        Math.cos(phi)*dist
      );
      const newPos = pos.clone().add(offset);
      points.push(newPos);
      points.push(...gen(level-1, size*0.6, newPos));
    }}
    return points;
  }}

  const root = new THREE.Vector3(0,0,0);
  const nodes = gen(FRACTAL_DEPTH, 10, root);
  while (nodes.length < NODE_COUNT) {{
    nodes.push(new THREE.Vector3((Math.random()-0.5)*40, (Math.random()-0.5)*40, (Math.random()-0.5)*40));
  }}

  const positions = new Float32Array(nodes.length*3);
  for (let i=0;i<nodes.length;i++) {{
    positions[i*3]=nodes[i].x;
    positions[i*3+1]=nodes[i].y;
    positions[i*3+2]=nodes[i].z;
  }}

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(positions,3));

  const colors = new Float32Array(nodes.length*3);
  for (let i=0;i<nodes.length;i++) {{
    const h = i/nodes.length;
    const color = new THREE.Color().setHSL(h,0.7,0.5);
    colors[i*3]=color.r; colors[i*3+1]=color.g; colors[i*3+2]=color.b;
  }}
  geom.setAttribute('color', new THREE.BufferAttribute(colors,3));

  const mat = new THREE.PointsMaterial({{
    size: 1.0,
    vertexColors: true,
    transparent: true,
    opacity: 0.9
  }});
  const pointsObj = new THREE.Points(geom, mat);
  scene.add(pointsObj);

  // Animation
  let t = 0;
  function animate() {{
    requestAnimationFrame(animate);
    t += 0.016;
    const pulse = 0.5 + 0.5*Math.sin(t * PULSE_FREQ);
    mat.size = 0.5 + 0.8*pulse*BRIGHTNESS;
    mat.opacity = 0.7 + 0.3*pulse;
    pointsObj.rotation.y += 0.001;
    renderer.render(scene, camera);
  }}
  animate();

  document.getElementById('debug').innerText = "✅ WebGL Ready — Nodes: "+NODE_COUNT+", Depth: "+FRACTAL_DEPTH;

  window.addEventListener('resize', ()=>{
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
  });

}} catch(err) {{
  document.getElementById('debug').innerText = "❌ Error: " + err.message;
  console.error(err);
}}
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200, scrolling=False)

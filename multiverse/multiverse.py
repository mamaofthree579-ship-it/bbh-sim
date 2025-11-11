# multiverse_orbit_inline.py
import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="Fractal Conscious Cosmos — Inline Controls", layout="wide")
st.title("🌌 Fractal Conscious Cosmos — Inline Camera Controls (Stable)")

# Sidebar controls
st.sidebar.header("Visualization Controls")
node_count = st.sidebar.slider("Node Count", 50, 400, 140, step=10)
fractal_depth = st.sidebar.slider("Fractal Depth", 1, 6, 3)
pulse_frequency = st.sidebar.slider("Pulse Frequency", 0.05, 2.0, 0.8, step=0.01)
brightness = st.sidebar.slider("Brightness", 0.2, 3.0, 1.6, step=0.1)
if st.sidebar.button("Regenerate (new seed)"):
    regen_token = str(time.time())
else:
    regen_token = "none"

# HTML template using placeholders (safe)
html_template = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Fractal Conscious Cosmos</title>
  <style>
    html, body {{ height:100%; margin:0; background:#000; overflow:hidden; }}
    #debug {{ position:absolute; left:12px; top:12px; z-index:9999;
      background:rgba(0,0,0,0.7); color:#fff; padding:6px 10px; border-radius:6px;
      font-family:monospace; font-size:13px; }}
    canvas {{ display:block; }}
  </style>
</head>
<body>
  <div id="debug">⏳ Initializing...</div>

  <script>
  const NODE_COUNT = %%NODE_COUNT%%;
  const FRACTAL_DEPTH = %%FRACTAL_DEPTH%%;
  const PULSE_FREQ = %%PULSE_FREQ%%;
  const BRIGHTNESS = %%BRIGHTNESS%%;
  const REGEN_TOKEN = "%%REGEN_TOKEN%%";

  function startWhenReady() {{
    if (typeof THREE === 'undefined') {{
      document.getElementById('debug').innerText = '⏳ Waiting for Three.js...';
      setTimeout(startWhenReady, 200);
      return;
    }}
    initFractalUniverse();
  }}

  function loadThree() {{
    const s = document.createElement('script');
    s.src = "https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js";
    s.onload = startWhenReady;
    s.onerror = () => document.getElementById('debug').innerText = "❌ Failed to load three.js";
    document.head.appendChild(s);
  }}

  function initFractalUniverse() {{
    try {{
      document.getElementById('debug').innerText = '✅ WebGL Ready — Building Scene...';
      const renderer = new THREE.WebGLRenderer({{antialias:true}});
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 3000);
      camera.position.z = 150;

      const ambient = new THREE.AmbientLight(0xffffff, 0.8);
      scene.add(ambient);
      const light = new THREE.PointLight(0xffffff, 1.2);
      light.position.set(50,50,80);
      scene.add(light);

      // simple fractal node generator
      function gen(depth, size, parent) {{
        const pts = [];
        if (depth <= 0) return pts;
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
          const newP = parent.clone().add(offset);
          pts.push(newP);
          pts.push(...gen(depth-1, size*0.6, newP));
        }}
        return pts;
      }}

      const nodes = gen(FRACTAL_DEPTH, 12, new THREE.Vector3(0,0,0));
      while (nodes.length < NODE_COUNT) {{
        nodes.push(new THREE.Vector3((Math.random()-0.5)*80,(Math.random()-0.5)*80,(Math.random()-0.5)*80));
      }}
      const pos = new Float32Array(nodes.length*3);
      for (let i=0;i<nodes.length;i++) {{
        pos[i*3]=nodes[i].x; pos[i*3+1]=nodes[i].y; pos[i*3+2]=nodes[i].z;
      }}
      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.BufferAttribute(pos,3));
      const mat = new THREE.PointsMaterial({{color:0x44ccff,size:1.5}});
      const cloud = new THREE.Points(geom, mat);
      scene.add(cloud);

      let t=0;
      function animate() {{
        requestAnimationFrame(animate);
        t+=0.02;
        cloud.rotation.y+=0.0015;
        const pulse=0.5+0.5*Math.sin(t*PULSE_FREQ);
        mat.size=0.8+1.2*pulse*BRIGHTNESS;
        renderer.render(scene, camera);
      }}
      animate();

      window.addEventListener('resize', ()=>{
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect=window.innerWidth/window.innerHeight;
        camera.updateProjectionMatrix();
      });
    }} catch(e) {{
      document.getElementById('debug').innerText = '❌ JS Error: '+e.message;
      console.error(e);
    }}
  }}

  loadThree();
  </script>
</body>
</html>
"""

# replace placeholders safely
html = html_template.replace("%%NODE_COUNT%%", str(node_count)) \
                    .replace("%%FRACTAL_DEPTH%%", str(fractal_depth)) \
                    .replace("%%PULSE_FREQ%%", str(pulse_frequency)) \
                    .replace("%%BRIGHTNESS%%", str(brightness)) \
                    .replace("%%REGEN_TOKEN%%", regen_token)

components.html(html, height=820, width=1400, scrolling=False)

st.markdown("---")
st.write("If the debug box shows an error, open the browser console (F12 → Console) and paste the error here so I can inspect it.")

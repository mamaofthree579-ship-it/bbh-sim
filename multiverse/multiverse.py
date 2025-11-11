# multiverse_fixed.py
import streamlit as st
import streamlit.components.v1 as components
import json
import time

st.set_page_config(page_title="Fractal Conscious Cosmos — Fixed", layout="wide")
st.title("🌌 Fractal Conscious Cosmos — Fixed Visualizer")

# Sidebar controls (Python-side)
st.sidebar.header("Visualization Controls")
node_count = st.sidebar.slider("Node Count", 50, 400, 140, step=10)
fractal_depth = st.sidebar.slider("Fractal Depth", 1, 6, 3)
pulse_frequency = st.sidebar.slider("Pulse Frequency", 0.05, 2.0, 0.8, step=0.01)
brightness = st.sidebar.slider("Brightness", 0.2, 3.0, 1.6, step=0.1)
reset_button = st.sidebar.button("Regenerate (random seed)")

# If user presses regenerate, we can toggle a timestamp to force new run
regen_token = str(time.time()) if reset_button else ""

# HTML/JS template with placeholders (no Python f-strings, safe braces)
html_template = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Fractal Conscious Cosmos — Fixed</title>
  <style>
    html, body {{height:100%; margin:0; background:#000; overflow:hidden;}}
    #debug {{ position: absolute; left: 12px; top: 12px; z-index:9999;
             background: rgba(0,0,0,0.5); color:#fff; padding:8px 10px; border-radius:6px;
             font-family: monospace; font-size:13px; }}
  </style>
</head>
<body>
  <div id="debug">Initializing...</div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.min.js"></script>

  <script>
  // Safety: inline OrbitControls minimal version (mouse drag rotates, wheel zooms)
  THREE.OrbitControls = function(object, domElement) {{
    this.object = object;
    this.domElement = domElement;
    this.enabled = true;
    const scope = this;
    function onMouseMove(e) {{
      if (!scope.enabled || (e.buttons !== 1 && e.buttons !== 3)) return;
      const dx = e.movementX || 0;
      const dy = e.movementY || 0;
      object.rotation.y -= dx * 0.005;
      object.rotation.x -= dy * 0.005;
    }}
    function onWheel(e) {{
      if (!scope.enabled) return;
      object.position.z += e.deltaY * 0.01;
      if (object.position.z < 5) object.position.z = 5;
      if (object.position.z > 200) object.position.z = 200;
    }}
    domElement.addEventListener('mousemove', onMouseMove, false);
    domElement.addEventListener('wheel', onWheel, false);
  }};

  (function(){{
    try {{
      // WebGL check
      if (!window.WebGLRenderingContext) {{
        document.getElementById('debug').innerText = "❌ WebGL not supported in this browser/environment.";
        return;
      }}

      // PARAMETERS injected from Python
      const NODE_COUNT = %%NODE_COUNT%%;
      const FRACTAL_DEPTH = %%FRACTAL_DEPTH%%;
      const PULSE_FREQ = %%PULSE_FREQ%%;
      const BRIGHTNESS = %%BRIGHTNESS%%;
      const REGEN_TOKEN = "%%REGEN_TOKEN%%";

      // Basic THREE setup
      const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(window.devicePixelRatio ? window.devicePixelRatio : 1);
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
      camera.position.z = 90;

      // Controls
      const controls = new THREE.OrbitControls(camera, renderer.domElement);

      // Lighting (increase ambient to make emissive visible)
      const ambient = new THREE.AmbientLight(0xffffff, 0.9);
      scene.add(ambient);
      const point = new THREE.PointLight(0xffffff, 1.2);
      point.position.set(20, 30, 40);
      scene.add(point);

      // True branching fractal generator
      function generateFractalNodes(level, size, parentPos, spread=1.6) {{
        const nodes = [];
        if (level <= 0) return nodes;
        const branches = 2 + Math.floor(Math.random() * 4); // 2..5
        for (let i=0;i<branches;i++) {{
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.random() * Math.PI;
          const distance = size * (0.5 + Math.random() * 0.7);
          const offset = new THREE.Vector3(
            Math.sin(phi) * Math.cos(theta) * distance * spread,
            Math.sin(phi) * Math.sin(theta) * distance * spread,
            Math.cos(phi) * distance
          );
          const newPos = parentPos.clone().add(offset);
          nodes.push(newPos);
          nodes.push(...generateFractalNodes(level - 1, size * 0.62, newPos, spread * 0.9));
        }}
        return nodes;
      }}

      // Create particle cloud from positions
      function buildCloud(nodeCount, depth) {{
        // clear previous
        if (window._fractalPoints) {{
          scene.remove(window._fractalPoints);
          window._fractalPoints.geometry.dispose();
          window._fractalPoints.material.dispose();
          window._fractalPoints = null;
        }}

        const root = new THREE.Vector3(0,0,0);
        const positions = [];
        const nodes = generateFractalNodes(depth, 12, root);
        // if generator produced fewer than requested, replicate with jitter
        while (nodes.length < nodeCount) {{
          // add jittered nodes
          nodes.push(new THREE.Vector3((Math.random()-0.5)*40, (Math.random()-0.5)*40, (Math.random()-0.5)*40));
        }}
        for (let i=0;i<Math.min(nodeCount, nodes.length); i++) {{
          positions.push(nodes[i].x, nodes[i].y, nodes[i].z);
        }}
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        // color per vertex via HSL gradient
        const colors = new Float32Array((positions.length/3)*3);
        for (let i=0;i<positions.length/3;i++) {{
          const h = (i / (positions.length/3)) * 0.7 + Math.random()*0.1;
          const col = new THREE.Color().setHSL(h, 0.8, 0.55);
          colors[i*3] = col.r; colors[i*3+1] = col.g; colors[i*3+2] = col.b;
        }}
        geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        const mat = new THREE.PointsMaterial({{ size: 0.9, vertexColors: true, transparent: true, opacity: 0.95 }});
        const points = new THREE.Points(geom, mat);
        scene.add(points);
        window._fractalPoints = points;
        window._fractalParams = {{ nodeCount: nodeCount, depth: depth }};
      }}

      // initial seed determines randomness; include regen token to force different run
      Math.seedrandom && Math.seedrandom(REGEN_TOKEN); // if seedrandom loaded, optional

      buildCloud(NODE_COUNT, FRACTAL_DEPTH);

      // animation + pulsing via shader-like emissive simulation
      let t = 0;
      function animate() {{
        requestAnimationFrame(animate);
        t += 0.016;
        if (window._fractalPoints) {{
          const positions = window._fractalPoints.geometry.attributes.position.array;
          const pc = window._fractalPoints.material;
          // simple slow rotation
          window._fractalPoints.rotation.y += 0.0008;
          // modulate size/opacity for pulse
          const pulse = 0.5 + 0.5 * Math.sin(t * PULSE_FREQ * 2.0);
          pc.size = 0.6 + 0.9 * pulse;
          pc.opacity = 0.6 + 0.35 * pulse * (BRIGHTNESS/1.6);
          window._fractalPoints.material.needsUpdate = true;
        }}
        controls && controls.update && controls.update();
        renderer.render(scene, camera);
      }}

      animate();
      document.getElementById('debug').innerText = "✅ WebGL Ready — Nodes: " + NODE_COUNT + " depth:" + FRACTAL_DEPTH;

      // Resize handler
      window.addEventListener('resize', function() {{
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
      }});

      // Expose rebuild function (for debugging/testing)
      window.rebuildFractal = function(nc, d, freq, bright) {{
        buildCloud(nc, d);
        // update pulse and brightness
        // (we'll just keep the constants from initial injection for simplicity)
      }};
    }} catch (err) {{
      document.getElementById('debug').innerText = "⚠️ Error initializing: " + err.message;
      console.error(err);
    }}
  }})()
  </script>
</body>
</html>
"""

# Safely replace placeholders with numeric/string values
html = html_template.replace("%%NODE_COUNT%%", str(node_count)) \
                    .replace("%%FRACTAL_DEPTH%%", str(fractal_depth)) \
                    .replace("%%PULSE_FREQ%%", str(pulse_frequency)) \
                    .replace("%%BRIGHTNESS%%", str(brightness)) \
                    .replace("%%REGEN_TOKEN%%", regen_token)

# Render the component (fullscreen-like)
components.html(html, height=800, width=1400, scrolling=False)

st.markdown("---")
st.write("If the scene appears too dim or too bright, tweak Brightness and Pulse Frequency in the sidebar.")
st.write("If nothing appears, check the debug banner (top-left) for WebGL / error info.")

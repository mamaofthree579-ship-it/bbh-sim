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
  <title>Fractal Conscious Cosmos (inline controls)</title>
  <style>
    html, body {{ height:100%; margin:0; background:#000; overflow:hidden; }}
    #debug {{ position: absolute; left:12px; top:12px; z-index:9999;
      background: rgba(0,0,0,0.6); color: #fff; padding:8px 10px; border-radius:6px;
      font-family: monospace; font-size:13px; }}
    canvas {{ display:block; }}
  </style>
</head>
<body>
  <div id="debug">Initializing...</div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>

  <script>
  // placeholders (will be replaced by Python)
  const NODE_COUNT = %%NODE_COUNT%%;
  const FRACTAL_DEPTH = %%FRACTAL_DEPTH%%;
  const PULSE_FREQ = %%PULSE_FREQ%%;
  const BRIGHTNESS = %%BRIGHTNESS%%;
  const REGEN_TOKEN = "%%REGEN_TOKEN%%";

  // Basic safety/error logging
  window.addEventListener('error', function(e) {{
    const dbg = document.getElementById('debug');
    dbg.innerText = "JS ERROR: " + e.message;
    console.error(e);
  }});

  (function(){{
    try {{
      if (!window.WebGLRenderingContext) {{
        document.getElementById('debug').innerText = "❌ WebGL not supported in this browser.";
        return;
      }}

      // Renderer + scene + camera
      const renderer = new THREE.WebGLRenderer({{ antialias: true }});
      renderer.setPixelRatio(window.devicePixelRatio || 1);
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 3000);
      camera.position.set(0, 0, 110);

      // Inline minimal controls (rotate / zoom / pan)
      const controls = {{
        enabled: true,
        isDragging: false,
        lastX: 0,
        lastY: 0,
        buttons: {{ LEFT: 0, MIDDLE: 1, RIGHT: 2 }},
        sensitivity: 0.005,
        zoomSpeed: 0.02,
        panSpeed: 0.5,
        onMouseDown: function(e) {{
          this.isDragging = true; this.lastX = e.clientX; this.lastY = e.clientY; this.button = e.button;
        }},
        onMouseUp: function(e) {{ this.isDragging = false; }},
        onMouseMove: function(e) {{
          if (!this.isDragging) return;
          const dx = e.clientX - this.lastX;
          const dy = e.clientY - this.lastY;
          this.lastX = e.clientX; this.lastY = e.clientY;
          if (this.button === this.buttons.LEFT) {{
            // rotate camera around origin
            const rotY = dx * this.sensitivity;
            const rotX = dy * this.sensitivity;
            const q = new THREE.Quaternion();
            q.setFromEuler(new THREE.Euler(rotX, rotY, 0, 'XYZ'));
            camera.position.applyQuaternion(q);
            camera.lookAt(0,0,0);
          }} else if (this.button === this.buttons.RIGHT) {{
            // pan camera (translate)
            const pan = new THREE.Vector3(-dx * this.panSpeed * 0.01, dy * this.panSpeed * 0.01, 0);
            camera.position.add(pan);
          }}
        }},
        onWheel: function(e) {{
          const delta = e.deltaY;
          camera.position.z += delta * this.zoomSpeed;
          if (camera.position.z < 10) camera.position.z = 10;
          if (camera.position.z > 1000) camera.position.z = 1000;
        }}
      }};
      // attach listeners
      renderer.domElement.addEventListener('mousedown', function(e) {{ controls.onMouseDown(e); }}, false);
      window.addEventListener('mouseup', function(e) {{ controls.onMouseUp(e); }}, false);
      window.addEventListener('mousemove', function(e) {{ controls.onMouseMove(e); }}, false);
      window.addEventListener('wheel', function(e) {{ controls.onWheel(e); }}, {passive:true});

      // Lighting
      const ambient = new THREE.AmbientLight(0xffffff, 0.85);
      scene.add(ambient);
      const pl = new THREE.PointLight(0xffffff, 1.2);
      pl.position.set(40,40,60);
      scene.add(pl);

      // True branching fractal generator
      function generateFractalNodes(level, size, parentPos, spread=1.6) {{
        const out = [];
        if (level <= 0) return out;
        const branches = 2 + Math.floor(Math.random() * 4); // 2..5
        for (let i=0;i<branches;i++) {{
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.random() * Math.PI;
          const dist = size * (0.5 + Math.random()*0.7);
          const offset = new THREE.Vector3(
            Math.sin(phi) * Math.cos(theta) * dist * spread,
            Math.sin(phi) * Math.sin(theta) * dist * spread,
            Math.cos(phi) * dist
          );
          const newPos = parentPos.clone().add(offset);
          out.push(newPos);
          out.push(...generateFractalNodes(level - 1, size * 0.62, newPos, spread * 0.9));
        }}
        return out;
      }}

      // Build points cloud
      function buildCloud(nCount, depth) {{
        if (window._points) {{
          scene.remove(window._points);
          window._points.geometry.dispose();
          window._points.material.dispose();
          window._points = null;
        }}
        const root = new THREE.Vector3(0,0,0);
        const nodes = generateFractalNodes(depth, 12, root);
        while (nodes.length < nCount) {{
          nodes.push(new THREE.Vector3((Math.random()-0.5)*60, (Math.random()-0.5)*60, (Math.random()-0.5)*60));
        }}
        const used = nodes.slice(0, nCount);
        const positions = new Float32Array(used.length * 3);
        const colors = new Float32Array(used.length * 3);
        for (let i=0;i<used.length;i++) {{
          positions[i*3] = used[i].x;
          positions[i*3+1] = used[i].y;
          positions[i*3+2] = used[i].z;
          const h = (i / used.length) * 0.75 + Math.random()*0.05;
          const col = new THREE.Color().setHSL(h, 0.85, 0.55);
          colors[i*3] = col.r; colors[i*3+1] = col.g; colors[i*3+2] = col.b;
        }}
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        const mat = new THREE.PointsMaterial({{ size: 1.2, vertexColors: true, transparent: true, opacity: 0.95 }});
        const points = new THREE.Points(geom, mat);
        scene.add(points);
        window._points = points;
      }}

      // seed regen token used only to vary randomness across runs if provided
      if (REGEN_TOKEN && REGEN_TOKEN !== "none") {{
        // Try to use Math.seedrandom if available; otherwise random change occurs naturally
        if (typeof Math.seedrandom === 'function') {{
          Math.seedrandom(REGEN_TOKEN);
        }}
      }}

      buildCloud(NODE_COUNT, FRACTAL_DEPTH);

      // Animation loop (pulse)
      let tt = 0;
      function animate() {{
        requestAnimationFrame(animate);
        tt += 0.02;
        if (window._points) {{
          const mat = window._points.material;
          const pulse = 0.5 + 0.5 * Math.sin(tt * PULSE_FREQ * 2.0);
          mat.size = 0.6 + 1.0 * pulse * BRIGHTNESS;
          mat.opacity = 0.6 + 0.35 * pulse * (BRIGHTNESS / 1.6);
          window._points.rotation.y += 0.0012;
        }}
        renderer.render(scene, camera);
      }}
      animate();

      // success message
      document.getElementById('debug').innerText = "✅ WebGL Ready — nodes: " + NODE_COUNT + ", depth: " + FRACTAL_DEPTH;

      // handle resize
      window.addEventListener('resize', function() {{
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
      }});
    }} catch (err) {{
      document.getElementById('debug').innerText = "❌ Initialization error: " + err.message;
      console.error(err);
    }}
  }})();
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

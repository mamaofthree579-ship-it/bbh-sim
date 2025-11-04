import streamlit as st
import numpy as np
import plotly.graph_objects as go
from streamlit.components.v1 import html as components_html

st.set_page_config(page_title="Quantum Black Hole Simulator", layout="wide")
st.title("Quantum Black Hole Simulator — Embedded Interactive")

st.markdown(
    "This app embeds a Plotly 3D visualization + WebAudio synth inside a single iframe so the buttons and animation work reliably."
)

# ----- Build Plotly geometry -----
def sphere_mesh(radius=1.0, res_u=48, res_v=24):
    u = np.linspace(0, 2 * np.pi, res_u)
    v = np.linspace(0, np.pi, res_v)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones_like(u), np.cos(v))
    return x.tolist(), y.tolist(), z.tolist()

x_h, y_h, z_h = sphere_mesh(1.0)
x_p, y_p, z_p = sphere_mesh(1.3)
x_q, y_q, z_q = sphere_mesh(0.6)

fig = go.Figure()
fig.add_surface(x=x_h, y=y_h, z=z_h, colorscale=[[0, "#2b0055"], [1, "#8a3fff"]],
                showscale=False, opacity=0.95, name="EventHorizon")
fig.add_surface(x=x_p, y=y_p, z=z_p, colorscale=[[0, "#fca311"], [1, "#ffd56b"]],
                showscale=False, opacity=0.28, name="PhotonSphere")
fig.add_surface(x=x_q, y=y_q, z=z_q, colorscale=[[0, "#ff6ad5"], [1, "#ffffff"]],
                showscale=False, opacity=0.85, name="QuantumCore")

fig.update_layout(
    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'),
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="black",
)

plotly_div = fig.to_html(include_plotlyjs='cdn', full_html=False)

# ---------- HTML/JS for iframe ----------
PAGE_HTML = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>BBH Embedded</title>
  <style>
    body {{ margin:0; font-family:Inter, Arial, sans-serif; background:#05000a; color:#eae6ff; }}
    .container {{ padding:12px; max-width:1200px; margin:auto; }}
    .controls {{ display:flex; gap:10px; align-items:center; margin-top:8px; flex-wrap:wrap; }}
    .btn {{ background:#8000ff; color:white; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; }}
    .btn.secondary {{ background:#444; }}
    label {{ font-size:0.95rem; margin-right:8px; color:#d6c7ff; }}
    .info {{ margin-top:8px; color:#ffd; font-size:0.95rem; }}
    .small {{ color:#cfc3ff; font-size:0.9rem; }}
    input[type=range] {{ width:200px; }}
    .row {{ display:flex; gap:12px; align-items:center; }}
  </style>
</head>
<body>
  <div class="container">
    <h3 style="margin:6px 0 4px 0;">Embedded Black Hole — Live 3D</h3>
    <div id="plotly-area">{plotly_div}</div>

    <div class="controls">
      <div class="row">
        <label>Mass (M☉)</label>
        <input id="massSlider" type="range" min="1e5" max="1e8" step="1e5" value="4300000">
        <span id="massLabel" class="small">4,300,000</span>
      </div>

      <div class="row">
        <label>Hotspot speed</label>
        <input id="speedSlider" type="range" min="0.002" max="0.08" step="0.002" value="0.026">
        <span id="speedLabel" class="small">0.026</span>
      </div>

      <button class="btn" id="playBtn">🎧 Play Rumble</button>
      <button class="btn secondary" id="stopBtn">⏹ Stop</button>
      <button class="btn" id="animBtn">🌠 Start Orbit</button>
      <button class="btn secondary" id="stopAnimBtn">⏹ Stop Orbit</button>
    </div>

    <div class="info" id="physInfo">
      <div>Schwarzschild radius rₛ (computed): <strong id="rsVal">—</strong> m</div>
      <div>Photon sphere ≈ 1.5 rₛ: <strong id="psVal">—</strong> m</div>
      <div class="small">Note: normalized visual scale used for clarity.</div>
    </div>
  </div>

<script>
  const G = 6.67430e-11;
  const c = 2.99792458e8;
  const M_sun = 1.98847e30;
  let currentMass = Number(document.getElementById('massSlider').value);
  let hotspotSpeed = Number(document.getElementById('speedSlider').value);

  const massLabel = document.getElementById('massLabel');
  const speedLabel = document.getElementById('speedLabel');
  const rsVal = document.getElementById('rsVal');
  const psVal = document.getElementById('psVal');

  function computeRadii(M_solar) {{{{
    const M = M_solar * M_sun;
    const rs = 2 * G * M / (c*c);
    const rph = 1.5 * rs;
    return {{{{ rs, rph }}}};
  }}}}

  function updatePhysicalDisplay() {{{{
    const r = computeRadii(currentMass);
    rsVal.textContent = r.rs.toExponential(6);
    psVal.textContent = r.rph.toExponential(6);
  }}}}

  massLabel.textContent = Number(currentMass).toLocaleString();
  speedLabel.textContent = hotspotSpeed.toFixed(3);
  updatePhysicalDisplay();

  document.getElementById('massSlider').addEventListener('input', (e)=>{{{{ 
    currentMass = Number(e.target.value);
    massLabel.textContent = Number(currentMass).toLocaleString();
    updatePhysicalDisplay();
  }}}});
  document.getElementById('speedSlider').addEventListener('input', (e)=>{{{{ 
    hotspotSpeed = Number(e.target.value);
    speedLabel.textContent = hotspotSpeed.toFixed(3);
  }}}});

  function getPlotlyDiv() {{{{
    return document.querySelector('.js-plotly-plot');
  }}}}
  const plotlyDiv = getPlotlyDiv();

  let animHandle = null;
  let animRunning = false;
  let angle = 0;

  function startOrbit() {{{{
    if (!plotlyDiv || animRunning) return;
    animRunning = true;
    function step() {{{{
      const radius = 2.2;
      const eye = {{{{x: Math.cos(angle)*radius, y: Math.sin(angle)*radius, z: 0.6}}}};
      Plotly.relayout(plotlyDiv, {{{{'scene.camera.eye': eye}}}});
      angle += hotspotSpeed;
      animHandle = requestAnimationFrame(step);
    }}}}
    animHandle = requestAnimationFrame(step);
  }}}}
  function stopOrbit() {{{{
    animRunning = false;
    if (animHandle) cancelAnimationFrame(animHandle);
  }}}}

  document.getElementById('animBtn').addEventListener('click', ()=> startOrbit());
  document.getElementById('stopAnimBtn').addEventListener('click', ()=> stopOrbit());

  // WebAudio rumble
  let audioCtx=null, osc1=null, osc2=null, g1=null, g2=null;

  function startRumble() {{{{
    if (audioCtx && audioCtx.state!=='closed') return;
    audioCtx = new (window.AudioContext||window.webkitAudioContext)();
    osc1=audioCtx.createOscillator(); osc2=audioCtx.createOscillator();
    g1=audioCtx.createGain(); g2=audioCtx.createGain();

    osc1.type='sine'; osc2.type='sawtooth';
    osc1.frequency.value=30+(Math.log10(currentMass)-5)*6;
    osc2.frequency.value=osc1.frequency.value*2;
    osc1.connect(g1); g1.connect(audioCtx.destination);
    osc2.connect(g2); g2.connect(audioCtx.destination);

    const now=audioCtx.currentTime;
    g1.gain.setValueAtTime(0.0001,now);
    g1.gain.linearRampToValueAtTime(0.28,now+0.05);
    g1.gain.exponentialRampToValueAtTime(0.0001,now+6.0);
    g2.gain.setValueAtTime(0.0001,now);
    g2.gain.linearRampToValueAtTime(0.06,now+0.05);
    g2.gain.exponentialRampToValueAtTime(0.0001,now+6.0);

    osc1.start(now); osc2.start(now);
    osc1.stop(now+6.05); osc2.stop(now+6.05);
    setTimeout(()=>{{{{audioCtx.close(); audioCtx=null;}}}},6200);
  }}}}
  function stopRumble() {{{{
    if (!audioCtx) return;
    try{{{{osc1&&osc1.stop();osc2&&osc2.stop();audioCtx.close();}}}}catch(e){{{{}}}} 
    audioCtx=null;
  }}}}

  document.getElementById('playBtn').addEventListener('click', ()=> startRumble());
  document.getElementById('stopBtn').addEventListener('click', ()=> stopRumble());
</script>
</body>
</html>
"""

components_html(PAGE_HTML, height=820, scrolling=True)

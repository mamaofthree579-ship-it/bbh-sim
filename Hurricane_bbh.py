import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io, base64, soundfile as sf

# ----------------------------------------
# App setup
# ----------------------------------------
st.set_page_config(page_title="Quantum Black Hole — Lensed Overview", layout="wide")
st.title("🔭 Quantum Black Hole — Fractal Core + Lensing")

# ----------------------------------------
# Controls (sidebar)
# ----------------------------------------
st.sidebar.header("Simulation Controls")
mass_scale = st.sidebar.slider(
    "Mass (visual scale, M☉)", min_value=1000, max_value=100000000,
    value=4300000, step=1000, format="%d"
)
spin = st.sidebar.slider("Spin (visual)", 0.0, 5.0, 1.0, 0.1)
trail_length = st.sidebar.slider("Hotspot Trail Length", 1, 13, 8, 1)
enable_sound = st.sidebar.checkbox("Enable Sound", value=True)
lensing_strength = st.sidebar.slider("Lensing strength", 0.0, 1.0, 0.18, 0.01)

# ----------------------------------------
# Build 3D "fractal" singularity core + accretion disk (Plotly)
# ----------------------------------------
theta, phi = np.mgrid[0:2*np.pi:90j, 0:np.pi:45j]
r_base = 1 + 0.28 * np.sin(3 * theta) * np.cos(2 * phi)
r = r_base * (1 + 0.18 * np.sin(spin))
x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

fig = go.Figure()

# Singularity core (slightly purple so hotspot doesn't disappear behind pure black)
fig.add_surface(
    x=x, y=y, z=z,
    colorscale=[[0, 'rgb(30,6,40)'], [1, 'rgb(150,90,200)']],
    showscale=False, opacity=0.96, name="Singularity Core",
)

# Accretion disk (thin, slightly perturbed)
disk_r = np.linspace(0.5, 3, 200)
disk_theta = np.linspace(0, 2*np.pi, 200)
R, T = np.meshgrid(disk_r, disk_theta)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = 0.04 * np.sin(8 * T)  # small wave perturbation
fig.add_surface(
    x=X, y=Y, z=Z,
    colorscale='YlOrBr', opacity=0.82, showscale=False, name="Accretion Disk"
)

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='auto',
        bgcolor="black"
    ),
    margin=dict(l=0, r=0, b=0, t=0),
)

# ----------------------------------------
# Audio generation (hurricane + whirlpool inspired)
# ----------------------------------------
def generate_whirlpool_sound(duration=4.0, fs=44100, intensity=1.0):
    t = np.linspace(0, duration, int(fs*duration), endpoint=False)
    # Low, slowly modulated swirl (whirlpool-like)
    low = np.sin(2*np.pi*18 * t * (1 + 0.25*np.sin(2*np.pi*0.2*t)))
    # Mid turbulent band (hurricane-like)
    mid = 0.5 * np.sin(2*np.pi*70 * t * (1 + 0.5*np.cos(2*np.pi*0.12*t)))
    # Noise / airflow texture
    noise = 0.12 * np.random.normal(scale=1.0, size=t.shape)
    env = np.exp(-t / (0.9 + 0.3 * (1-intensity)))  # mild decay
    wave = (low + mid + noise) * env * (0.6 + 0.7 * intensity)
    # normalize to safe range
    wave = wave / np.max(np.abs(wave) + 1e-9) * 0.6
    return np.float32(wave)

sound_wave = generate_whirlpool_sound(intensity=min(1.0, spin*0.22))
sound_buf = io.BytesIO()
sf.write(sound_buf, sound_wave, 44100, format='WAV')
sound_buf.seek(0)

# ----------------------------------------
# Display Plotly 3D figure
# ----------------------------------------
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ----------------------------------------
# Orbit + Lensing Overlay (HTML canvas with JS)
# - Draws orbiting hotspots + subtle radial lensing warp
# - Kept separate so Plotly figure remains stable
# ----------------------------------------
overlay_html = f"""
<div style="width:100%;max-width:1120px;margin:8px auto;">
<canvas id="lenseOrbit" width="1120" height="340" 
  style="display:block;margin:0 auto;border-radius:10px;
         background:radial-gradient(circle at 50% 45%, rgba(20,4,30,0.9) 0%, rgba(0,0,0,1) 70%);"></canvas>
<script>
  const canvas = document.getElementById('lenseOrbit');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const cx = W/2, cy = H/2;
  let angle = 0;
  const spin = {spin:.2f};
  const trailLen = {trail_length};
  const lensStrength = {lensing_strength:.3f};

  // Hotspot trail buffer
  let trail = [];

  function drawLensingBackground() {{
    // subtle warped grid — simulates light bending
    ctx.save();
    ctx.translate(cx, cy);
    for(let r=60; r<420; r+=28){{
      ctx.beginPath();
      const wobble = Math.sin(r*0.08 + angle*0.6)*6*lensStrength;
      for(let a=0; a<=Math.PI*2; a+=0.06){{
        const rr = r + Math.sin(a*3 + angle*0.5)*wobble;
        const x = Math.cos(a)*rr, y = Math.sin(a)*rr*0.42; // elliptical warp
        if(a === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }}
      ctx.closePath();
      ctx.strokeStyle = 'rgba(180,120,255,' + (0.02 + 0.02*(1 - (r/420))) + ')';
      ctx.lineWidth = 1;
      ctx.stroke();
    }}
    ctx.restore();
  }}

  function draw() {{
    ctx.clearRect(0,0,W,H);

    // Lensing lines (background)
    drawLensingBackground();

    // orbit radii
    const rA = 80, rB = 160;
    const xA = cx + Math.cos(angle) * rA;
    const yA = cy + Math.sin(angle) * rA;
    const xB = cx - Math.cos(angle) * rB;
    const yB = cy - Math.sin(angle) * rB;

    // push to trail
    trail.unshift({{x:xA, y:yA}});
    if(trail.length > trailLen) trail.pop();

    // draw trail fading
    for(let i=0;i<trail.length;i++){{
      const a = 1 - i/trail.length;
      ctx.beginPath();
      ctx.arc(trail[i].x, trail[i].y, Math.max(1.2, 6*a), 0, Math.PI*2);
      ctx.fillStyle = 'rgba(255,230,190,' + (0.08 + 0.6*a*0.6) + ')';
      ctx.fill();
    }}

    // draw bodies
    ctx.beginPath(); ctx.arc(xA,yA,12,0,Math.PI*2); ctx.fillStyle='rgba(166,77,255,0.95)'; ctx.fill();
    ctx.beginPath(); ctx.arc(xB,yB,18,0,Math.PI*2); ctx.fillStyle='rgba(50,200,255,0.9)'; ctx.fill();

    // central glow (horizon)
    const grad = ctx.createRadialGradient(cx, cy, 8, cx, cy, 140);
    grad.addColorStop(0, 'rgba(180,100,240,0.12)');
    grad.addColorStop(0.4, 'rgba(140,50,200,0.06)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(cx-420, cy-200, 840, 400);

    angle += 0.02 + spin*0.015;
    requestAnimationFrame(draw);
  }}

  draw();
</script>
</div>
"""

st.components.v1.html(overlay_html, height=380, scrolling=False)

# ----------------------------------------
# Sound control
# ----------------------------------------
if enable_sound:
    st.audio(sound_buf, format="audio/wav")
else:
    st.write("Sound is disabled via sidebar toggle.")

# ----------------------------------------
# Small status / info panel
# ----------------------------------------
with st.expander("Event Summary (concise)", expanded=True):
    st.write(f"Mass (visual): **{int(mass_scale):,} M☉**  •  Spin (visual): **{spin:.2f}**")
    st.write("Lensing: subtle radial warp around the visual; adjust 'Lensing strength' to taste.")
    st.write("Notes: visuals are pedagogical/illustrative rather than full GR ray-tracing.")

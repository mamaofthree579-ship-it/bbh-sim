import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io, base64, soundfile as sf

# ==============================================
# 🔭 App Setup
# ==============================================
st.set_page_config(page_title="Quantum Black Hole Simulator", layout="wide")
st.title("🌀 Quantum Black Hole Dynamics — Fractal Singularity Core")

# ==============================================
# 🌌 Parameters
# ==============================================
st.sidebar.header("Simulation Parameters")
mass_scale = st.sidebar.slider(
    "Mass (visual scale, M☉)", min_value=1000, max_value=100000000,
    value=4300000, step=1000, format="%d"
)
spin = st.sidebar.slider("Spin Rate", 0.0, 5.0, 1.0, 0.1)
trail_length = st.sidebar.slider("Hotspot Trail Length", 1, 13, 8, 1)

# ==============================================
# 🌪️ Generate Fractal Core Visualization
# ==============================================
theta, phi = np.mgrid[0:2*np.pi:90j, 0:np.pi:45j]
r_base = 1 + 0.3 * np.sin(3 * theta) * np.cos(2 * phi)
r = r_base * (1 + 0.2 * np.sin(spin))
x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

# ==============================================
# 🌀 Plotly 3D Figure
# ==============================================
fig = go.Figure()

# Black hole core
fig.add_surface(
    x=x, y=y, z=z, colorscale="Viridis", showscale=False,
    opacity=0.98, name="Singularity Core"
)

# Accretion disk
disk_r = np.linspace(0.5, 3, 200)
disk_theta = np.linspace(0, 2*np.pi, 200)
R, T = np.meshgrid(disk_r, disk_theta)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = 0.05 * np.sin(10*T)  # wave-like distortion
fig.add_surface(
    x=X, y=Y, z=Z,
    colorscale="Inferno", opacity=0.8, showscale=False, name="Accretion Disk"
)

fig.update_layout(
    scene=dict(
        xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        aspectmode='cube', bgcolor="black"
    ),
    margin=dict(l=0, r=0, b=0, t=0),
)

# ==============================================
# 🎵 Generate "Hurricane/Whirlpool" Audio
# ==============================================
def generate_whirlpool_sound(duration=4.0, fs=44100, intensity=1.0):
    t = np.linspace(0, duration, int(fs*duration))
    low_band = np.sin(2*np.pi*20*t*(1+0.3*np.sin(2*np.pi*0.5*t)))
    mid_band = np.sin(2*np.pi*80*t*(1+0.5*np.cos(2*np.pi*0.25*t)))
    high_band = np.random.normal(0, 0.1, len(t))
    combined = (low_band + 0.4*mid_band + 0.3*high_band)
    combined *= np.exp(-t/duration*1.5)
    combined *= intensity
    return np.float32(combined)

sound_data = generate_whirlpool_sound(intensity=spin*0.2)
sound_bytes = io.BytesIO()
sf.write(sound_bytes, sound_data, 44100, format='WAV')
sound_bytes.seek(0)

# ==============================================
# 🖼️ Display 3D Visualization
# ==============================================
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ==============================================
# 🌌 Dynamic Orbit Overlay (subtle holographic effect)
# ==============================================
color = "#a64dff"

orbit_html_template = """
<canvas id="orbit" width="880" height="320"
        style="border-radius:8px;
               background:radial-gradient(circle at center,#120014,#010006);
               display:block;margin:10px auto"></canvas>
<script>
  const canvas = document.getElementById('orbit'), ctx = canvas.getContext('2d');
  const cx = canvas.width/2, cy = canvas.height/2;
  let angle = 0;
  const rA = 80, rB = 160;
  const cA = "{color}";
  const cB = "#33ccff";
  function draw(){{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    // subtle background circles
    for(let i=0;i<4;i++){{
      ctx.beginPath();
      ctx.arc(cx,cy,80+i*40,0,Math.PI*2);
      ctx.strokeStyle = 'rgba(160,0,255,0.03)';
      ctx.stroke();
    }}
    const xA = cx + Math.cos(angle)*rA, yA = cy + Math.sin(angle)*rA;
    const xB = cx - Math.cos(angle)*rB, yB = cy - Math.sin(angle)*rB;
    ctx.beginPath(); ctx.arc(xA,yA,12,0,Math.PI*2); ctx.fillStyle = cA; ctx.fill();
    ctx.beginPath(); ctx.arc(xB,yB,16,0,Math.PI*2); ctx.fillStyle = cB; ctx.fill();
    angle += 0.02 + ({spin}*0.01);
    requestAnimationFrame(draw);
  }}
  draw();
</script>
""".format(color=color, spin=spin)

# Display the overlay animation
st.components.v1.html(orbit_html_template, height=360, scrolling=False)

# ==============================================
# 🔊 Sound Toggle
# ==============================================
if st.checkbox("Enable Sound", value=True):
    st.audio(sound_bytes, format="audio/wav")
else:
    st.info("Sound disabled.")

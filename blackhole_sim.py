import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.io.wavfile import write
import tempfile
import io

# --- Constants ---
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

st.set_page_config(page_title="Black Hole Anatomy — Step 3", layout="wide")

st.title("🌌 Black Hole Anatomy — Step 3: Relativistic Disk & Chirp")

st.markdown("""
Now we add **relativistic Doppler effects** and an **optional audio chirp**.  
The disk brightens on the approaching side (blueshift) and dims on the receding side (redshift).  
Use the time slider to watch the motion and optionally listen to a chirp tone.
""")

# --- Mass selection ---
mass_solar = st.slider("Black-hole mass (solar masses)", 1, 10000000, 4300000, step=10000)
mass = mass_solar * M_sun

# --- Physical radii ---
r_s = 2 * G * mass / c**2
r_isco = 3 * r_s
scale = 1.0
r_s_vis = scale
r_disk_inner = (r_isco / r_s) * scale
r_disk_outer = 6 * scale

# --- Hotspot and Doppler ---
st.sidebar.header("🌀 Hotspot & Disk Controls")
speed_factor = st.sidebar.slider("Orbital speed (fraction of c)", 0.01, 0.5, 0.1)
t = st.slider("Orbital phase", 0.0, 1.0, 0.0, step=0.01)

# Orbital position
theta = 2 * np.pi * t
x_hot = 1.2 * r_disk_inner * np.cos(theta)
y_hot = 1.2 * r_disk_inner * np.sin(theta)
z_hot = 0

# --- Doppler intensity map ---
theta_disk = np.linspace(0, 2*np.pi, 300)
radii = np.linspace(r_disk_inner, r_disk_outer, 2)
R, T = np.meshgrid(radii, theta_disk)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = np.zeros_like(X)

# Relativistic beaming intensity
v_over_c = speed_factor * np.cos(T - theta)
doppler_intensity = (1 + v_over_c) / (1 - v_over_c + 1e-8)
doppler_intensity = np.clip(doppler_intensity, 0.5, 2.0)
colorscale = [[0, "darkred"], [0.5, "orangered"], [1, "gold"]]

# --- Plot surfaces ---
disk = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=doppler_intensity,
    colorscale=colorscale,
    cmin=0.5, cmax=2.0,
    showscale=False,
    opacity=0.85,
    name="Accretion Disk"
)

# Horizon
u = np.linspace(0, 2*np.pi, 60)
v = np.linspace(0, np.pi, 30)
xh = r_s_vis * np.outer(np.cos(u), np.sin(v))
yh = r_s_vis * np.outer(np.sin(u), np.sin(v))
zh = r_s_vis * np.outer(np.ones_like(u), np.cos(v))
horizon = go.Surface(
    x=xh, y=yh, z=zh,
    colorscale=[[0, "#8e2de2"], [1, "#8e2de2"]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# Hotspot
hotspot = go.Scatter3d(
    x=[x_hot], y=[y_hot], z=[z_hot],
    mode="markers",
    marker=dict(size=8, color="yellow", opacity=0.95),
    name="Hotspot"
)

# --- Layout ---
fig = go.Figure(data=[disk, horizon, hotspot])
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.9))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# --- Optional chirp sound ---
st.sidebar.header("🎵 Chirp Audio Generator")
if st.sidebar.checkbox("Generate chirp audio"):
    duration = 2.0  # seconds
    fs = 44100
    t_audio = np.linspace(0, duration, int(fs * duration))
    freq_start = 200
    freq_end = 800
    freq = freq_start + (freq_end - freq_start) * (t_audio / duration)
    waveform = 0.2 * np.sin(2 * np.pi * freq * t_audio)
    waveform = np.int16(waveform / np.max(np.abs(waveform)) * 32767)

    temp_wav = io.BytesIO()
    write(temp_wav, fs, waveform)
    st.audio(temp_wav, format="audio/wav")

# --- Info box ---
st.markdown(f"""
### ⚙️ Physical parameters

**Mass:** {mass_solar:,.0f} M☉  
**Schwarzschild radius (rₛ):** {r_s:.3e} m  
**ISCO (3 rₛ):** {r_isco:.3e} m  
**Hotspot speed:** {speed_factor:.2f} c  

---

🟣 **Event Horizon** — boundary of no return  
🟠 **Accretion Disk** — Doppler brightened on approach  
✨ **Hotspot** — simulated plasma knot, orbital phase = {t:.2f}  
🎧 **Audio Chirp** — simplified inspiral tone (optional)
""")

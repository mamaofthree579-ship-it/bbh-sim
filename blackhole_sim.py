import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.io.wavfile import write
import io, base64

st.set_page_config(page_title="3D Black Hole Simulator", layout="wide", page_icon="🌌")

st.title("🌌 Black Hole Anatomy & Chirp Visualization")
st.markdown(
    """
Explore the **structure of a black hole** and the **gravitational wave chirp** from merging binaries.  
Use the controls below to animate and play the chirp sound while viewing the accretion disk, photon ring, and event horizon.
"""
)

# --- Constants ---
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

# --- Controls ---
col1, col2, col3 = st.columns(3)
with col1:
    M = st.slider("Black Hole Mass (Solar Masses)", 1e6, 1e9, 4.3e6, step=1e6, format="%.1e")
with col2:
    live_mode = st.checkbox("Enable Live Animation", True)
with col3:
    play_chirp = st.button("🎧 Play Chirp")

# --- Physics Calculations ---
r_s = 2 * G * (M * M_sun) / c**2
r_ph = 1.5 * r_s

st.markdown(
    f"""
**Mass:** {M:,.0f} M☉  
**Schwarzschild radius:** {r_s:.3e} m  
**Photon sphere:** {r_ph:.3e} m  
"""
)

# --- Build 3D geometry ---
theta = np.linspace(0, 2 * np.pi, 80)
phi = np.linspace(0, np.pi, 80)
theta, phi = np.meshgrid(theta, phi)

# Event horizon
x_bh = np.sin(phi) * np.cos(theta)
y_bh = np.sin(phi) * np.sin(theta)
z_bh = np.cos(phi)

# Photon ring (bright ring)
ring_theta = np.linspace(0, 2*np.pi, 200)
x_ring = 1.5 * np.cos(ring_theta)
y_ring = 1.5 * np.sin(ring_theta)
z_ring = np.zeros_like(ring_theta)

# Accretion disk
disk_r = np.linspace(1.5, 3, 100)
disk_t = np.linspace(0, 2*np.pi, 100)
disk_r, disk_t = np.meshgrid(disk_r, disk_t)
x_disk = disk_r * np.cos(disk_t)
y_disk = disk_r * np.sin(disk_t)
z_disk = np.zeros_like(x_disk)

# --- Traces ---
fig = go.Figure()

# Event Horizon
fig.add_trace(go.Surface(
    x=x_bh, y=y_bh, z=z_bh,
    surfacecolor=np.zeros_like(z_bh),
    colorscale=[[0, "rgb(60,0,90)"], [1, "rgb(30,0,40)"]],
    showscale=False, name="Event Horizon", opacity=1.0
))

# Photon Ring
fig.add_trace(go.Scatter3d(
    x=x_ring, y=y_ring, z=z_ring,
    mode="lines", line=dict(color="gold", width=6),
    name="Photon Ring"
))

# Accretion Disk
fig.add_trace(go.Surface(
    x=x_disk, y=y_disk, z=z_disk,
    surfacecolor=disk_r,
    colorscale=[[0, "rgb(80,0,120)"], [1, "rgb(220,160,30)"]],
    opacity=0.85, showscale=False, name="Accretion Disk"
))

# --- Labels (floating in 3D space) ---
labels = [
    dict(text="Event Horizon", x=0, y=0, z=1.2, showarrow=False, font=dict(color="white", size=12)),
    dict(text="Photon Ring", x=1.8, y=0, z=0.1, showarrow=False, font=dict(color="gold", size=12)),
    dict(text="Accretion Disk", x=2.3, y=0.2, z=-0.1, showarrow=False, font=dict(color="orange", size=12))
]

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False),
        yaxis=dict(showbackground=False, showticklabels=False),
        zaxis=dict(showbackground=False, showticklabels=False),
        annotations=labels,
        aspectmode="data"
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Chirp simulation ---
def generate_chirp(duration=4.0, f_start=30, f_end=400, fs=44100):
    t = np.linspace(0, duration, int(fs * duration))
    k = (f_end - f_start) / duration
    f_t = f_start + k * t
    phase = 2 * np.pi * np.cumsum(f_t) / fs
    chirp_wave = np.sin(phase) * np.hanning(len(phase))
    audio = (chirp_wave * 32767).astype(np.int16)
    return fs, audio

if play_chirp:
    fs, audio = generate_chirp()
    buf = io.BytesIO()
    write(buf, fs, audio)
    st.audio(buf, format="audio/wav")

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Optional download ---
chirp_fs, chirp_audio = generate_chirp()
wav_buf = io.BytesIO()
write(wav_buf, chirp_fs, chirp_audio)
wav_b64 = base64.b64encode(wav_buf.getvalue()).decode()
st.download_button("⬇️ Download Chirp (WAV)", data=wav_buf.getvalue(), file_name="chirp.wav")

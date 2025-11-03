import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.io.wavfile import write
import io

# --- Constants ---
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

st.set_page_config(page_title="Black Hole & Chirp Simulator", layout="wide")

st.title("🌌 Black Hole Simulator — 3D Horizon, Disk & Chirp")

st.markdown("""
Explore a **3D black hole** and listen to the corresponding **gravitational-wave chirp**.  
The chirp pitch and amplitude dynamically react to the orbital motion of the plasma hotspot.
""")

# --- Fixed mass reference (Sagittarius A*) ---
mass_solar = 4_300_000
mass = mass_solar * M_sun
r_s = 2 * G * mass / c**2

# --- Sidebar controls ---
st.sidebar.header("🎛️ Controls")
speed_factor = st.sidebar.slider("Hotspot orbital speed (fraction of c)", 0.01, 0.5, 0.1)
t_phase = st.sidebar.slider("Orbital phase", 0.0, 1.0, 0.0, step=0.01)
tilt_angle = st.sidebar.slider("View tilt (degrees)", 0, 80, 25)
trail_length = st.sidebar.slider("Trail length", 0.1, 1.0, 0.5)
chirp_duration = st.sidebar.slider("Chirp duration (seconds)", 2.0, 10.0, 5.0)
audio_volume = st.sidebar.slider("Audio volume", 0.2, 1.0, 0.7)

# --- Visual scales ---
r_s_vis = 0.5
r_disk_inner = 1.5 * r_s_vis
r_disk_outer = 6 * r_s_vis

# --- Orbital math ---
theta = 2 * np.pi * t_phase
x_hot = 1.2 * r_disk_inner * np.cos(theta)
y_hot = 1.2 * r_disk_inner * np.sin(theta)
z_hot = 0

# --- Disk Doppler shading ---
theta_disk = np.linspace(0, 2*np.pi, 300)
radii = np.linspace(r_disk_inner, r_disk_outer, 2)
R, T = np.meshgrid(radii, theta_disk)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = np.zeros_like(X)

v_over_c = speed_factor * np.cos(T - theta)
doppler_intensity = np.clip((1 + v_over_c) / (1 - v_over_c + 1e-6), 0.5, 2.0)

# --- Disk surface ---
disk = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=doppler_intensity,
    colorscale=[[0, "darkred"], [0.5, "orangered"], [1, "gold"]],
    cmin=0.5, cmax=2.0,
    showscale=False,
    opacity=0.9,
    name="Accretion Disk"
)

# --- Event horizon (purple sphere) ---
u = np.linspace(0, 2*np.pi, 60)
v = np.linspace(0, np.pi, 30)
xh = r_s_vis * np.outer(np.cos(u), np.sin(v))
yh = r_s_vis * np.outer(np.sin(u), np.sin(v))
zh = r_s_vis * np.outer(np.ones_like(u), np.cos(v))
horizon = go.Surface(
    x=xh, y=yh, z=zh,
    colorscale=[[0, "#b300ff"], [1, "#8e2de2"]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# --- Hotspot + trail ---
trail_thetas = np.linspace(theta - 2*np.pi*trail_length, theta, 50)
x_trail = 1.2 * r_disk_inner * np.cos(trail_thetas)
y_trail = 1.2 * r_disk_inner * np.sin(trail_thetas)
z_trail = np.zeros_like(x_trail)

hotspot = go.Scatter3d(
    x=[x_hot], y=[y_hot], z=[z_hot],
    mode="markers",
    marker=dict(size=8, color="yellow", opacity=0.95),
    name="Hotspot"
)

trail = go.Scatter3d(
    x=x_trail, y=y_trail, z=z_trail,
    mode="lines",
    line=dict(color="yellow", width=3),
    name="Trail"
)

# --- Combine 3D scene ---
fig3d = go.Figure(data=[disk, horizon, trail, hotspot])
fig3d.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(
            x=1.5*np.cos(np.radians(tilt_angle)),
            y=1.5*np.sin(np.radians(tilt_angle)),
            z=0.9
        )),
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig3d, use_container_width=True)

# --- Gravitational Wave Chirp ---
st.markdown("### 🌊 Gravitational Wave Chirp")

# Chirp parameters — dynamic with hotspot speed and phase
t_chirp = np.linspace(0, 1, 2000)
base_freq = 30 + 20 * np.sin(2 * np.pi * t_phase)
freq = base_freq * (1 + 15 * t_chirp**3) * (1 + speed_factor)
amp = t_chirp**2 * (0.6 + 0.4 * np.sin(2 * np.pi * t_phase))
chirp_signal = amp * np.sin(2 * np.pi * freq * t_chirp)

# --- Plot chirp ---
fig_chirp = go.Figure()
fig_chirp.add_trace(go.Scatter(
    x=t_chirp, y=chirp_signal,
    mode="lines", line=dict(width=2, color="aqua"),
    fill="tozeroy", name="GW Chirp"
))
fig_chirp.update_layout(
    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="white"),
    xaxis=dict(title="Time (normalized)", showgrid=False),
    yaxis=dict(title="Strain (a.u.)", showgrid=False),
    margin=dict(l=30, r=30, t=30, b=30)
)
st.plotly_chart(fig_chirp, use_container_width=True)

# --- Generate chirp audio ---
sample_rate = 44100
time_audio = np.linspace(0, chirp_duration, int(sample_rate * chirp_duration))
audio_freq = np.interp(time_audio, np.linspace(0, chirp_duration, len(freq)), freq)
audio_amp = np.interp(time_audio, np.linspace(0, chirp_duration, len(amp)), amp)
audio_wave = np.sin(2 * np.pi * audio_freq * time_audio) * audio_amp
audio_wave = (audio_wave / np.max(np.abs(audio_wave))) * audio_volume

# Convert to 16-bit PCM
audio_int16 = np.int16(audio_wave * 32767)
wav_bytes = io.BytesIO()
write(wav_bytes, sample_rate, audio_int16)
st.audio(wav_bytes.getvalue(), format="audio/wav")

# --- Info box ---
st.markdown(f"""
### ⚙️ Parameters
**Black Hole Mass:** {mass_solar:,.0f} M☉  
**Schwarzschild radius (rₛ):** {r_s:.3e} m  
**Hotspot speed:** {speed_factor:.2f} c  
**Tilt angle:** {tilt_angle}°  
**Chirp duration:** {chirp_duration:.1f} s  
**Audio volume:** {audio_volume:.2f}

---

💜 **Event Horizon:** purple visualization  
🔥 **Accretion Disk:** Doppler brightened  
💫 **Hotspot:** plasma trail orbiting near ISCO  
🎵 **Chirp:** GW strain growing with orbital frequency
""")

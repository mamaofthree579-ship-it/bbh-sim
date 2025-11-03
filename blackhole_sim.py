import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.io.wavfile import write
import io

# --- Constants ---
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

st.set_page_config(page_title="Black Hole Simulator — Smooth Live Mode", layout="wide")

st.title("🌌 Black Hole Simulator — Smooth Live Mode & Chirp")

st.markdown("""
This interactive 3D visualization shows the **anatomy of a Schwarzschild black hole**, including:
- A purple **event horizon**
- A Doppler-shifted **accretion disk**
- A rotating **hotspot with trail**
- An evolving **gravitational-wave chirp**

> Tip: Use *Live Mode* for continuous smooth animation.
""")

# --- Sidebar controls ---
st.sidebar.header("🎛️ Controls")
speed_factor = st.sidebar.slider("Hotspot orbital speed (fraction of c)", 0.01, 0.5, 0.1)
tilt_angle = st.sidebar.slider("View tilt (degrees)", 0, 80, 25)
trail_length = st.sidebar.slider("Trail length", 0.1, 1.0, 0.5)
chirp_duration = st.sidebar.slider("Chirp duration (seconds)", 2.0, 10.0, 5.0)
audio_volume = st.sidebar.slider("Audio volume", 0.2, 1.0, 0.7)
live_mode = st.sidebar.checkbox("🔄 Live Mode (smooth animation)", value=True)

# --- Black hole geometry ---
r_s_vis = 0.5
r_disk_inner = 1.5 * r_s_vis
r_disk_outer = 6 * r_s_vis

# --- Static geometry ---
u = np.linspace(0, 2*np.pi, 60)
v = np.linspace(0, np.pi, 30)
xh = r_s_vis * np.outer(np.cos(u), np.sin(v))
yh = r_s_vis * np.outer(np.sin(u), np.sin(v))
zh = r_s_vis * np.outer(np.ones_like(u), np.cos(v))
horizon = go.Surface(
    x=xh, y=yh, z=zh,
    colorscale=[[0, "#b300ff"], [1, "#8e2de2"]],
    showscale=False, opacity=1.0,
    name="Event Horizon"
)

theta_disk = np.linspace(0, 2*np.pi, 300)
radii = np.linspace(r_disk_inner, r_disk_outer, 2)
R, T = np.meshgrid(radii, theta_disk)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = np.zeros_like(X)

# --- Frames for animation ---
frames = []
n_frames = 60
for i in range(n_frames):
    theta = 2 * np.pi * i / n_frames
    v_over_c = speed_factor * np.cos(T - theta)
    doppler_intensity = np.clip((1 + v_over_c) / (1 - v_over_c + 1e-6), 0.5, 2.0)
    disk = go.Surface(
        x=X, y=Y, z=Z,
        surfacecolor=doppler_intensity,
        colorscale=[[0, "darkred"], [0.5, "orangered"], [1, "gold"]],
        cmin=0.5, cmax=2.0,
        showscale=False, opacity=0.9
    )
    x_hot = 1.2 * r_disk_inner * np.cos(theta)
    y_hot = 1.2 * r_disk_inner * np.sin(theta)
    z_hot = 0
    trail_thetas = np.linspace(theta - 2*np.pi*trail_length, theta, 40)
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

    frames.append(go.Frame(data=[disk, horizon, trail, hotspot], name=str(i)))

# --- Base figure ---
fig = go.Figure(
    data=[horizon],
    frames=frames
)

# --- Layout ---
fig.update_layout(
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
    updatemenus=[{
        "buttons": [
            {"args": [None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}],
             "label": "▶️ Play", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
             "label": "⏸ Pause", "method": "animate"}
        ],
        "direction": "left", "pad": {"r": 10, "t": 10}, "type": "buttons", "x": 0.1, "y": 0, "xanchor": "right", "yanchor": "top"
    }]
)

# --- Chirp ---
t = np.linspace(0, 1, 2000)
freq = 30 * (1 + 15 * t**3) * (1 + speed_factor)
amp = t**2
signal = amp * np.sin(2 * np.pi * freq * t)
fig_chirp = go.Figure()
fig_chirp.add_trace(go.Scatter(x=t, y=signal, mode="lines", line=dict(color="aqua", width=2)))
fig_chirp.update_layout(
    paper_bgcolor="black", plot_bgcolor="black",
    xaxis=dict(title="Time (normalized)"),
    yaxis=dict(title="Strain (a.u.)"),
    font=dict(color="white"),
    margin=dict(l=30, r=30, t=30, b=30)
)

# --- Display ---
st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig_chirp, use_container_width=True)

# --- Chirp sound ---
sample_rate = 44100
time_audio = np.linspace(0, chirp_duration, int(sample_rate * chirp_duration))
audio_freq = np.interp(time_audio, np.linspace(0, chirp_duration, len(freq)), freq)
audio_amp = np.interp(time_audio, np.linspace(0, chirp_duration, len(amp)), amp)
audio_wave = np.sin(2 * np.pi * audio_freq * time_audio) * audio_amp
audio_wave = (audio_wave / np.max(np.abs(audio_wave))) * audio_volume
audio_int16 = np.int16(audio_wave * 32767)
wav_bytes = io.BytesIO()
write(wav_bytes, sample_rate, audio_int16)
st.audio(wav_bytes.getvalue(), format="audio/wav")

# Streamlit + Plotly app: Black hole horizon + accretion disk + hotspot + chirp + audio
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.io.wavfile import write
import io

st.set_page_config(page_title="Black Hole Simulator (fixed animation)", layout="wide")

st.title("🌌 Black Hole — Horizon, Disk, Hotspot & Chirp (fixed)")

st.markdown("Play/Pause the animation below. The chirp (audio + waveform) is shown under the 3D view.")

# -------------------------
# UI Controls
# -------------------------
col1, col2 = st.columns([1, 0.35])
with col1:
    speed_factor = st.slider("Hotspot angular speed (relative)", 0.02, 0.5, 0.12)
    trail_length = st.slider("Trail length (revolutions)", 0.05, 1.2, 0.35)
    n_frames = st.slider("Animation frames (quality)", 24, 120, 60)
with col2:
    chirp_duration = st.slider("Chirp duration (s)", 1.0, 8.0, 3.2)
    audio_volume = st.slider("Audio volume", 0.05, 1.0, 0.35)

# -------------------------
# Visual geometry (normalized)
# -------------------------
r_s_vis = 1.0                          # visual radius of event horizon
r_disk_inner = 1.5 * r_s_vis
r_disk_outer = 5.5 * r_s_vis

# build horizon surface (static)
u = np.linspace(0, 2*np.pi, 48)
v = np.linspace(0, np.pi, 24)
xh = r_s_vis * np.outer(np.cos(u), np.sin(v))
yh = r_s_vis * np.outer(np.sin(u), np.sin(v))
zh = r_s_vis * np.outer(np.ones_like(u), np.cos(v))

# disk param grid (fixed mesh - surfacecolor will vary per frame)
theta_disk = np.linspace(0, 2*np.pi, 240)
radii = np.linspace(r_disk_inner, r_disk_outer, 3)
R, T = np.meshgrid(radii, theta_disk)
Xdisk = R * np.cos(T)
Ydisk = R * np.sin(T)
Zdisk = np.zeros_like(Xdisk)

# helper for colors
def hex_rgba(h, a=1.0):
    h = h.lstrip('#')
    r = int(h[0:2], 16); g = int(h[2:4], 16); b = int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"

# -------------------------
# Build initial traces (the figure must have the same number of base traces as frames expect)
# Order: disk, horizon, trail, hotspot
# -------------------------

# initial disk (frame 0)
initial_doppler = np.ones_like(Xdisk)
disk_base = go.Surface(
    x=Xdisk, y=Ydisk, z=Zdisk,
    surfacecolor=initial_doppler,
    colorscale=[[0, "darkred"], [0.5, "orangered"], [1, "gold"]],
    cmin=0.5, cmax=2.0,
    showscale=False,
    opacity=0.95,
    name="Accretion Disk"
)

# horizon surface (static purple-ish)
horizon = go.Surface(
    x=xh, y=yh, z=zh,
    colorscale=[[0, "#aa66ff"], [1, "#6b2bd1"]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# initial trail (few points)
trail_base = go.Scatter3d(
    x=[r_disk_inner * 1.2], y=[0.0], z=[0.0],
    mode="lines",
    line=dict(color="yellow", width=4),
    name="Trail",
    hoverinfo="skip"
)

# initial hotspot
hotspot_base = go.Scatter3d(
    x=[r_disk_inner * 1.2], y=[0.0], z=[0.0],
    mode="markers",
    marker=dict(size=6, color="yellow", opacity=0.95),
    name="Hotspot",
    hoverinfo="skip"
)

fig = go.Figure(data=[disk_base, horizon, trail_base, hotspot_base], frames=[])

# -------------------------
# Create frames (must produce data arrays matching base trace order)
# -------------------------
frames = []
for i in range(n_frames):
    theta = 2 * np.pi * (i / n_frames) * (1 + speed_factor)  # angular param
    # Doppler-like intensity map: very simple toy model based on local azimuthal velocity projection
    v_over_c = speed_factor * np.cos(T - theta)
    doppler = np.clip((1 + v_over_c) / (1 - v_over_c + 1e-6), 0.4, 2.0)

    # hotspot position and trail
    hot_r = 1.2 * r_disk_inner
    x_hot = hot_r * np.cos(theta)
    y_hot = hot_r * np.sin(theta)
    z_hot = 0.0

    # trail thetas (backwards)
    trail_thetas = np.linspace(theta - 2*np.pi*trail_length, theta, max(10, int(20*trail_length*n_frames/60)))
    x_trail = hot_r * np.cos(trail_thetas)
    y_trail = hot_r * np.sin(trail_thetas)
    z_trail = np.zeros_like(x_trail)

    # Build the three dynamic traces (disk, trail, hotspot) plus the static horizon (we include it for frame consistency)
    disk_frame = go.Surface(
        x=Xdisk, y=Ydisk, z=Zdisk,
        surfacecolor=doppler,
        colorscale=[[0, "darkred"], [0.5, "orangered"], [1, "gold"]],
        cmin=0.4, cmax=2.0,
        showscale=False,
        opacity=0.95
    )
    horizon_frame = go.Surface(x=xh, y=yh, z=zh,
                               colorscale=[[0, "#aa66ff"], [1, "#6b2bd1"]],
                               showscale=False, opacity=1.0)
    trail_frame = go.Scatter3d(x=x_trail, y=y_trail, z=z_trail, mode="lines",
                               line=dict(color="rgba(255,220,120,0.9)", width=3))
    hotspot_frame = go.Scatter3d(x=[x_hot], y=[y_hot], z=[z_hot], mode="markers",
                                 marker=dict(size=6, color="rgba(255,220,120,0.98)"))
    frames.append(go.Frame(data=[disk_frame, horizon_frame, trail_frame, hotspot_frame], name=f"f{i}"))

fig.frames = frames

# -------------------------
# Layout + animation controls
# -------------------------
frame_duration_ms = int(max(20, 1000 / (n_frames / 3)))  # heuristic so faster frames -> shorter duration
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.8, y=0.6, z=0.8))
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    margin=dict(l=0, r=0, t=30, b=0),
    updatemenus=[{
        "buttons": [
            {"args": [None, {"frame": {"duration": frame_duration_ms, "redraw": True}, "fromcurrent": True}],
             "label": "▶ Play", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
             "label": "⏸ Pause", "method": "animate"}
        ],
        "direction": "left", "pad": {"r": 10, "t": 10}, "type": "buttons", "x": 0.02, "y": 0.0
    }],
    showlegend=False
)

# Add a small title inside the plot for clarity
fig.update_layout(title_text="Event Horizon (purple) + Disk (Doppler) + Hotspot (yellow)")

# -------------------------
# Chirp waveform & audio (simple PN-like toy chirp)
# -------------------------
# Generate a normalized chirp waveform (strain-like)
Nw = 2000
t_norm = np.linspace(0, 1, Nw)
# toy instantaneous freq rising with t
freq0 = 24.0 + speed_factor * 40.0
freq1 = 420.0 + speed_factor * 60.0
inst_freq = freq0 + (freq1 - freq0) * (t_norm ** 1.6)
env = (t_norm ** 2) * np.exp(-1.3 * (1 - t_norm))
wave = env * np.sin(2 * np.pi * inst_freq * (t_norm * 1.0))

chirp_fig = go.Figure()
chirp_fig.add_trace(go.Scatter(x=t_norm * chirp_duration, y=wave, mode="lines", line=dict(color="aqua", width=2)))
chirp_fig.update_layout(paper_bgcolor="black", plot_bgcolor="black",
                        xaxis=dict(title="Time (s)", color="white"),
                        yaxis=dict(title="Relative amplitude", color="white"),
                        margin=dict(l=40, r=20, t=30, b=40),
                        font=dict(color="white"))

# Audio generation: map t_norm -> real time array of chirp_duration
sr = 44100
t_audio = np.linspace(0, chirp_duration, int(sr * chirp_duration), endpoint=False)
# interpolate instantaneous frequency & envelope to audio times
inst_freq_audio = np.interp(t_audio / chirp_duration, t_norm, inst_freq)
env_audio = np.interp(t_audio / chirp_duration, t_norm, env)
audio_wave = np.sin(2 * np.pi * inst_freq_audio * t_audio) * env_audio
# scale & volume
audio_wave /= np.max(np.abs(audio_wave)) + 1e-12
audio_wave *= audio_volume
audio_int16 = np.int16(audio_wave * 32767)
wav_buf = io.BytesIO()
write(wav_buf, sr, audio_int16)
wav_bytes = wav_buf.getvalue()

# -------------------------
# Display: 3D and chirp + audio
# -------------------------
st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(chirp_fig, use_container_width=True)
st.audio(wav_bytes, format="audio/wav")

st.markdown("""
**Notes**
- This is a toy, pedagogical visualization (not a GR ray-tracer). The disk color is a simplified Doppler proxy.
- Use Play to animate. If you prefer continuous loop, press Play and leave it playing.
""")

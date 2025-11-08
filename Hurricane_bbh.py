import io
import time
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import wave
import struct

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")
st.title("🌀 Black Hole Anatomy — Hurricane Dynamics Simulator")
st.markdown(
    """
Interactive black-hole anatomy visual with a synthesized hurricane/whirlpool rumble.
This version uses browser audio (`st.audio`) so it works reliably in cloud and local Streamlit.
"""
)

# --- UI parameters ---
mass = st.slider("Black Hole Mass (M☉, visual scale)", min_value=1_000, max_value=10_000_000, value=4_300_000, step=1_000)
spin = st.slider("Spin Intensity", 0.1, 1.0, 0.6, 0.05)
st.write("Visualizing for mass:", f"{mass:,} M☉")

# --- Build 3D visual (singularity + accretion spiral) ---
theta = np.linspace(0, 2 * np.pi, 150)
phi = np.linspace(0, np.pi, 75)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones(np.size(theta)), np.cos(phi))

core_radius = 0.30  # visual scale; keep small so disk is visible

fig = go.Figure(
    data=[
        go.Surface(
            x=core_radius * x,
            y=core_radius * y,
            z=core_radius * z,
            surfacecolor=z,
            colorscale="Electric",
            opacity=0.92,
            name="Singularity Core",
            showscale=False,
        )
    ]
)

# Accretion Disk — spiral arms (particle line)
r = np.linspace(core_radius * 1.5, 1.2, 300)
theta_disk = np.linspace(0, 50 * np.pi, 300)
x_disk = r * np.cos(theta_disk)
y_disk = r * np.sin(theta_disk)
z_disk = 0.05 * np.sin(3 * theta_disk)

fig.add_trace(
    go.Scatter3d(
        x=x_disk,
        y=y_disk,
        z=z_disk,
        mode="lines",
        line=dict(color="orange", width=3),
        name="Accretion Disk",
    )
)

# Layout
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="cube",
    ),
    paper_bgcolor="black",
    scene_camera=dict(eye=dict(x=1.8, y=1.8, z=0.45)),
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Sound synthesis helpers (create WAV bytes for browser playback) ---
def generate_blackhole_rumble(duration=3.0, base_freq=60.0, rate=44100):
    """
    Create a float32 waveform representing a hurricane-whirlpool rumble.
    Returned array is in range [-1.0, +1.0].
    """
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    # layered components: low gravity pulse + turbulent sidebands + slow modulation
    signal = (
        0.50 * np.sin(2 * np.pi * base_freq * t)  # main low pulse
        + 0.28 * np.sin(2 * np.pi * (base_freq * 2.3) * t + 0.9 * np.sin(2 * np.pi * 0.34 * t))
        + 0.18 * np.sin(2 * np.pi * (base_freq * 0.7) * t + 1.2 * np.sin(2 * np.pi * 0.12 * t))
    )
    # slow amplitude modulation (hurricane envelope)
    mod = 0.6 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t))
    out = (signal * mod)
    # gentle band-limited noise to give "whirlpool" texture
    rng = np.random.default_rng(1234)
    noise = 0.02 * rng.standard_normal(len(t))
    out = out + noise
    # normalize (avoid clipping)
    max_abs = np.max(np.abs(out))
    if max_abs > 0:
        out = out / (max_abs * 1.02)
    return out.astype(np.float32)

def wav_bytes_from_float32(signal, rate=44100):
    """
    Convert float32 waveform (-1..1) to 16-bit PCM WAV bytes in-memory.
    Returns bytes object suitable for st.audio(..., format='audio/wav').
    """
    # convert to int16
    int16 = np.int16(signal * 32767)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(rate)
        # pack data as little-endian signed 16-bit
        wf.writeframes(int16.tobytes())
    bio.seek(0)
    return bio.read()

# --- UI layout: plot + controls on right column ---
col1, col2 = st.columns([2, 1])
plot_area = col1.empty()

# Buttons & controls
if col2.button("▶️ Live Motion (rotate camera)"):
    # animate camera for a short demonstration loop (non-blocking-ish)
    # Note: in Streamlit each update re-renders — keep short to remain responsive
    frames = 120
    for f in range(frames):
        angle_deg = f * (360.0 / frames)
        camera = dict(eye=dict(x=2.0 * np.sin(np.radians(angle_deg)), y=2.0 * np.cos(np.radians(angle_deg)), z=0.45))
        fig.update_layout(scene_camera=camera)
        plot_area.plotly_chart(fig, use_container_width=True)
        time.sleep(0.03)
else:
    plot_area.plotly_chart(fig, use_container_width=True)

col2.markdown("### Audio")
dur = col2.slider("Duration (s)", min_value=1.0, max_value=8.0, value=3.0, step=0.5)
base_freq = col2.slider("Base frequency (Hz)", min_value=20.0, max_value=150.0, value=60.0, step=1.0)

if col2.button("🎧 Generate & Play Rumble (browser)"):
    # generate WAV and hand to browser audio player
    with st.spinner("Synthesizing rumble..."):
        signal = generate_blackhole_rumble(duration=dur, base_freq=base_freq, rate=44100)
        wav_bytes = wav_bytes_from_float32(signal, rate=44100)
    col2.audio(wav_bytes, format="audio/wav")
    st.success("Audio ready — use the player above to play.")

# --- Informational footer ---
st.markdown(
    """
**Notes**
- This app synthesizes an immersive rumble as a pedagogical / aesthetic representation (not a literal physical audio emission).
- Browser audio via `st.audio` is used to ensure the app runs in server/cloud environments without native audio devices.
"""
)

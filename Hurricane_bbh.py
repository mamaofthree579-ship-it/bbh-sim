import io
import time
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import wave

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")
st.title("🌀 Black Hole Anatomy — Hurricane Dynamics Simulator")
st.markdown(
    """
An interactive black hole anatomy visual with a synthesized hurricane–whirlpool rumble.  
Now with smooth rotation toggle and downloadable audio.
"""
)

# --- UI parameters ---
mass = st.slider("Black Hole Mass (M☉, visual scale)", 1_000, 10_000_000, 4_300_000, step=1_000)
spin = st.slider("Spin Intensity", 0.1, 1.0, 0.6, 0.05)
st.write(f"Visualizing for mass: {mass:,} M☉")

# --- Build 3D visual (singularity + accretion spiral) ---
theta = np.linspace(0, 2 * np.pi, 150)
phi = np.linspace(0, np.pi, 75)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones(np.size(theta)), np.cos(phi))
core_radius = 0.30

fig = go.Figure(
    data=[
        go.Surface(
            x=core_radius * x,
            y=core_radius * y,
            z=core_radius * z,
            surfacecolor=z,
            colorscale="Electric",
            opacity=0.9,
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

# --- Audio synthesis ---
def generate_blackhole_rumble(duration=3.0, base_freq=60.0, rate=44100):
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    signal = (
        0.5 * np.sin(2 * np.pi * base_freq * t)
        + 0.28 * np.sin(2 * np.pi * (base_freq * 2.3) * t + 0.9 * np.sin(2 * np.pi * 0.34 * t))
        + 0.18 * np.sin(2 * np.pi * (base_freq * 0.7) * t + 1.2 * np.sin(2 * np.pi * 0.12 * t))
    )
    mod = 0.6 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t))
    out = signal * mod + 0.02 * np.random.default_rng(1234).standard_normal(len(t))
    out /= np.max(np.abs(out)) * 1.02
    return out.astype(np.float32)

def wav_bytes_from_float32(signal, rate=44100):
    int16 = np.int16(signal * 32767)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(int16.tobytes())
    bio.seek(0)
    return bio.read()

# --- Layout ---
col1, col2 = st.columns([2, 1])
plot_area = col1.empty()

# --- Rotation controls using session_state ---
if "rotating" not in st.session_state:
    st.session_state.rotating = False
if "angle" not in st.session_state:
    st.session_state.angle = 0.0

def toggle_rotation():
    st.session_state.rotating = not st.session_state.rotating

col2.markdown("### Visual Controls")
col2.button("⏯ Start / Stop Live Rotation", on_click=toggle_rotation)
plot_area.plotly_chart(fig, use_container_width=True)

# --- Update rotation if active ---
if st.session_state.rotating:
    placeholder = st.empty()
    for _ in range(150):
        if not st.session_state.rotating:
            break
        st.session_state.angle += 2
        camera = dict(
            eye=dict(
                x=2.0 * np.sin(np.radians(st.session_state.angle)),
                y=2.0 * np.cos(np.radians(st.session_state.angle)),
                z=0.45,
            )
        )
        fig.update_layout(scene_camera=camera)
        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(0.03)
    placeholder.empty()

# --- Audio section ---
col2.markdown("### Audio Rumble")
dur = col2.slider("Duration (s)", 1.0, 8.0, 3.0, 0.5)
base_freq = col2.slider("Base frequency (Hz)", 20.0, 150.0, 60.0, 1.0)

if col2.button("🎧 Generate & Play Rumble"):
    with st.spinner("Synthesizing rumble..."):
        signal = generate_blackhole_rumble(dur, base_freq)
        wav_bytes = wav_bytes_from_float32(signal)
    col2.audio(wav_bytes, format="audio/wav")
    st.download_button("⬇️ Download WAV", data=wav_bytes, file_name="blackhole_rumble.wav", mime="audio/wav")

# --- Footer ---
st.markdown(
    """
**Notes**
- Rotation toggle runs smoothly without full-frame flashing.  
- Audio is generated in memory and playable via browser or downloadable as WAV.  
- Sound is a simulated hurricane–whirlpool rumble inspired by gravitational turbulence.
"""
)

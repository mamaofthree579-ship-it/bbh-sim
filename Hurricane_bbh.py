import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import sounddevice as sd

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")

st.title("🌀 Black Hole Anatomy — Hurricane Dynamics Simulator")
st.markdown(
    """
This interactive simulator visualizes a black hole’s anatomy with an accretion disk and a dynamic singularity core.  
It also includes a synthesized sound representing a *hurricane–whirlpool-like rumble* in extreme gravitational conditions.
"""
)

# --- Parameters ---
mass = st.slider("Black Hole Mass (M☉, visual scale)", min_value=1_000, max_value=10_000_000, value=4_300_000, step=1_000)
spin = st.slider("Spin Intensity", 0.1, 1.0, 0.6, 0.05)
st.write("Visualizing for mass:", mass, "solar masses")

# --- 3D Grid for Accretion Disk and Singularity ---
theta = np.linspace(0, 2 * np.pi, 150)
phi = np.linspace(0, np.pi, 75)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones(np.size(theta)), np.cos(phi))

# Singularity core (purple fractal crystal-like)
core_radius = 0.3
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

# Accretion Disk (spiraling plasma)
r = np.linspace(core_radius * 1.5, 1.2, 400)
theta_disk = np.linspace(0, 50 * np.pi, 400)
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

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="cube",
    ),
    paper_bgcolor="black",
    scene_camera=dict(eye=dict(x=1.8, y=1.8, z=0.4)),
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Sound Generation (whirlpool-hurricane hybrid rumble) ---
def generate_blackhole_rumble(duration=3.0, base_freq=60.0, rate=44100):
    t = np.linspace(0, duration, int(rate * duration))
    # Low frequency gravity “pulse” + turbulence
    signal = (
        0.5 * np.sin(2 * np.pi * base_freq * t)
        + 0.3 * np.sin(2 * np.pi * (base_freq * 2.3) * t + 0.7 * np.sin(2 * np.pi * 0.3 * t))
        + 0.2 * np.sin(2 * np.pi * (base_freq * 0.7) * t + 1.2 * np.sin(2 * np.pi * 0.1 * t))
    )
    # Add a slow hurricane-like amplitude modulation
    mod = 0.5 * (1 + np.sin(2 * np.pi * 0.1 * t))
    return (signal * mod).astype(np.float32)

col1, col2 = st.columns(2)
plot_container = col1.empty()

# --- Buttons ---
if col2.button("🎧 Play Rumble Sound"):
    st.write("Generating gravitational hurricane rumble...")
    rumble = generate_blackhole_rumble()
    sd.play(rumble, samplerate=44100)
    sd.wait()
    st.success("Playback complete.")

# --- Live Motion Animation ---
if col2.button("▶️ Live Motion"):
    st.write("Animating black hole rotation...")
    for frame in range(240):
        angle = frame * 1.5
        camera = dict(
            eye=dict(
                x=2.0 * np.sin(np.radians(angle)),
                y=2.0 * np.cos(np.radians(angle)),
                z=0.3
            )
        )
        fig.update_layout(scene_camera=camera)
        plot_container.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)
else:
    plot_container.plotly_chart(fig, use_container_width=True)

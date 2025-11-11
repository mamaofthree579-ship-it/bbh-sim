import numpy as np
import plotly.graph_objects as go
import streamlit as st
import io
import base64
import soundfile as sf

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")
st.title("🌀 Black Hole Anatomy — Hurricane Dynamics Simulator")

st.markdown("""
Experience the **quantum hurricane** — a theoretical black hole modeled as a spinning vortex of plasma and energy.  
The **sound** evolves with spin intensity, blending the deep rumble of gravity with the turbulence of a hurricane and the pull of a cosmic whirlpool.
""")

# --- Parameters ---
mass = st.slider("Black Hole Mass (M☉, visual scale)", 1_000, 10_000_000, 4_300_000, step=1_000)
spin = st.slider("Spin Intensity", 0.1, 1.0, 0.6, 0.05)
sound_duration = st.slider("Sound Duration (seconds)", 2, 20, 8)
st.write(f"Visualizing for mass: {mass:,} M☉ — Spin factor: {spin:.2f}")

# --- Generate the black hole visual ---
theta = np.linspace(0, 2 * np.pi, 150)
phi = np.linspace(0, np.pi, 75)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones(np.size(theta)), np.cos(phi))
core_radius = 0.3

fig = go.Figure()

# Singularity Core
fig.add_surface(
    x=core_radius * x,
    y=core_radius * y,
    z=core_radius * z,
    surfacecolor=z,
    colorscale="Electric",
    opacity=0.9,
    showscale=False,
    name="Singularity Core",
)

# Accretion Disk Spiral
r = np.linspace(core_radius * 1.5, 1.2, 400)
theta_disk = np.linspace(0, 60 * np.pi, 400)
x_disk = r * np.cos(theta_disk)
y_disk = r * np.sin(theta_disk)
z_disk = 0.06 * np.sin(3 * theta_disk)

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

# --- Camera rotation frames ---
frames = []
for angle in np.linspace(0, 360, 180):
    camera = dict(
        eye=dict(
            x=2.0 * np.sin(np.radians(angle)),
            y=2.0 * np.cos(np.radians(angle)),
            z=0.45,
        )
    )
    frames.append(go.Frame(layout=dict(scene_camera=camera)))

fig.frames = frames

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="cube",
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
    updatemenus=[
        {
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "▶️ Rotate",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "mode": "immediate"}],
                },
                {
                    "label": "⏸ Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                },
            ],
        }
    ],
)

# --- Display 3D visualization ---
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Dynamic Quantum Hurricane Sound ---
st.markdown("### 🌪️ Generate Black Hole Rumble (Spin-Responsive Sound)")

sample_rate = 44100
t = np.linspace(0, sound_duration, int(sample_rate * sound_duration))

# Dynamic frequencies tied to spin
base_freq = 20 + 30 * spin           # deeper rumbles at low spin, higher at high spin
vortex_freq = 5 + 60 * spin          # faster whirlpool modulation with spin
noise_amp = 0.3 + 0.7 * spin         # turbulence intensity increases with spin

# Generate sound layers
base = np.sin(2 * np.pi * base_freq * t)
vortex = np.sin(2 * np.pi * (vortex_freq + 15 * np.sin(2 * np.pi * 0.2 * t)) * t)
noise = noise_amp * np.random.randn(len(t))

# Composite and dampen
sound = (0.5 * base + 0.4 * vortex + 0.3 * noise) * np.exp(-0.0003 * t * sample_rate)
sound /= np.max(np.abs(sound))

# Convert to playable WAV
buffer = io.BytesIO()
sf.write(buffer, sound, sample_rate, format="WAV")
b64_audio = base64.b64encode(buffer.getvalue()).decode()

st.audio(f"data:audio/wav;base64,{b64_audio}", format="audio/wav")
st.caption("Sound spectrum adapts to spin — low spin = deep rumble, high spin = chaotic plasma turbulence.")

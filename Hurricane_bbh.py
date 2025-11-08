import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")
st.title("🌀 Black Hole Anatomy — Hurricane Dynamics Simulator")
st.markdown(
    """
Interactive 3D visualization of a black hole’s anatomy, showing the singularity and swirling accretion disk.  
The rotation is now handled **natively by Plotly**, eliminating frame flashing.
"""
)

# --- Parameters ---
mass = st.slider("Black Hole Mass (M☉, visual scale)", 1_000, 10_000_000, 4_300_000, step=1_000)
spin = st.slider("Spin Intensity", 0.1, 1.0, 0.6, 0.05)
st.write(f"Visualizing for mass: {mass:,} M☉")

# --- Core geometry ---
theta = np.linspace(0, 2 * np.pi, 150)
phi = np.linspace(0, np.pi, 75)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones(np.size(theta)), np.cos(phi))
core_radius = 0.30

# --- Figure setup ---
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

# --- Camera animation frames ---
frames = []
for angle in np.linspace(0, 360, 120):
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

# --- Display ---
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

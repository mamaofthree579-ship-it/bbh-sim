import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy — Quantum Singularity Simulation")
st.caption("Visual simulation of the fractal singularity core and rotating accretion disk")

# ------------------------------------------------------------
# Parameters
# ------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    mass = st.number_input("Mass (solar masses)", value=4.3e6, format="%.1e")
with col2:
    live_motion = st.checkbox("Live rotation", value=True)

# Constants
rotation_speed = 0.05  # radians per frame

# ------------------------------------------------------------
# Geometry grids
# ------------------------------------------------------------
theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 50)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones_like(theta), np.cos(phi))

# ------------------------------------------------------------
# Create 3D figure
# ------------------------------------------------------------
fig = go.Figure()

# Singularity core — fractal crystal representation
fig.add_surface(
    x=0.5 * x,
    y=0.5 * y,
    z=0.5 * z,
    colorscale=[[0, "rgb(130,70,220)"], [1, "rgb(220,200,255)"]],
    showscale=False,
    opacity=0.95,
    name="Singularity Core",
)

# Event horizon shell
fig.add_surface(
    x=x,
    y=y,
    z=z,
    colorscale=[[0, "rgb(20,0,40)"], [1, "rgb(100,0,160)"]],
    showscale=False,
    opacity=0.85,
    name="Event Horizon",
)

# Accretion disk (thin ring with mild vertical turbulence)
r_disk = np.linspace(0.8, 10, 100)
theta_disk = np.linspace(0, 2 * np.pi, 200)
R, T = np.meshgrid(r_disk, theta_disk)
Xdisk = R * np.cos(T)
Ydisk = R * np.sin(T)
Zdisk = 0.05 * np.sin(6 * T) * np.exp(-R / 10)

fig.add_surface(
    x=Xdisk,
    y=Ydisk,
    z=Zdisk,
    colorscale=[[0, "rgba(255,180,60,0.3)"], [1, "rgba(255,80,0,0.8)"]],
    showscale=False,
    opacity=0.9,
    name="Accretion Disk",
)

# ------------------------------------------------------------
# Animation — rotate black hole only (camera stays fixed)
# ------------------------------------------------------------
if live_motion:
    frames = []
    for i in range(60):
        angle = i * rotation_speed
        cos_a, sin_a = np.cos(angle), np.sin(angle)

        # Rotate core + horizon + disk
        x_rot = cos_a * x - sin_a * y
        y_rot = sin_a * x + cos_a * y
        Xdisk_rot = cos_a * Xdisk - sin_a * Ydisk
        Ydisk_rot = sin_a * Xdisk + cos_a * Ydisk

        frame = go.Frame(
            data=[
                go.Surface(
                    x=x_rot, y=y_rot, z=z,
                    colorscale=[[0, "rgb(20,0,40)"], [1, "rgb(100,0,160)"]],
                    showscale=False, opacity=0.85
                ),
                go.Surface(
                    x=0.5*x_rot, y=0.5*y_rot, z=0.5*z,
                    colorscale=[[0, "rgb(130,70,220)"], [1, "rgb(220,200,255)"]],
                    showscale=False, opacity=0.95
                ),
                go.Surface(
                    x=Xdisk_rot, y=Ydisk_rot, z=Zdisk,
                    colorscale=[[0, "rgba(255,180,60,0.3)"], [1, "rgba(255,80,0,0.8)"]],
                    showscale=False, opacity=0.9
                ),
            ]
        )
        frames.append(frame)

    fig.frames = frames
    fig.update_layout(
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "▶️ Rotate",
                "method": "animate",
                "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True}]
            }]
        }]
    )

# ------------------------------------------------------------
# Layout
# ------------------------------------------------------------
fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False),
        yaxis=dict(showbackground=False, showticklabels=False),
        zaxis=dict(showbackground=False, showticklabels=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.4, y=1.4, z=1.1)),
        bgcolor="black",
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

# ------------------------------------------------------------
# Display
# ------------------------------------------------------------
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    """
    ### Visual Components
    - **Violet Core:** quantum fractal singularity.  
    - **Dark Shell:** event horizon boundary.  
    - **Orange Disk:** accretion plasma torus.  
    - Background removed for optimal clarity.
    """
)

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy — Realistic Visualization")
st.caption("Dynamic 3D view of a singularity, accretion disk, and starfield environment")

# ------------------------------------------------------------
# Parameters
# ------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    mass = st.number_input("Mass (solar masses)", value=4.3e6, format="%.1e")
with col2:
    live_motion = st.checkbox("Live rotation", value=True)

# Scale parameters
nebula_spread = 10
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
# Scene setup
# ------------------------------------------------------------
fig = go.Figure()

# Singularity core
fig.add_surface(
    x=0.5 * x,
    y=0.5 * y,
    z=0.5 * z,
    colorscale=[[0, "rgb(120,60,200)"], [1, "rgb(220,180,255)"]],
    showscale=False,
    opacity=0.9,
    name="Singularity Core",
)

# Event horizon
fig.add_surface(
    x=x,
    y=y,
    z=z,
    colorscale=[[0, "rgb(30,0,60)"], [1, "rgb(100,0,160)"]],
    showscale=False,
    opacity=0.85,
    name="Event Horizon",
)

# Accretion Disk (rotating ring)
r_disk = np.linspace(0.8, nebula_spread, 100)
theta_disk = np.linspace(0, 2 * np.pi, 200)
R, T = np.meshgrid(r_disk, theta_disk)
Xdisk = R * np.cos(T)
Ydisk = R * np.sin(T)
Zdisk = 0.05 * np.sin(5 * T) * np.exp(-R / nebula_spread)

fig.add_surface(
    x=Xdisk,
    y=Ydisk,
    z=Zdisk,
    colorscale=[[0, "rgba(255,180,60,0.3)"], [1, "rgba(255,80,0,0.8)"]],
    showscale=False,
    opacity=0.9,
    name="Accretion Disk",
)

# Distant static starfield
Nstars = 1500
r_starfield = 80
phi_s = np.random.uniform(0, np.pi, Nstars)
theta_s = np.random.uniform(0, 2 * np.pi, Nstars)
x_stars = r_starfield * np.sin(phi_s) * np.cos(theta_s)
y_stars = r_starfield * np.sin(phi_s) * np.sin(theta_s)
z_stars = r_starfield * np.cos(phi_s)

fig.add_trace(
    go.Scatter3d(
        x=x_stars,
        y=y_stars,
        z=z_stars,
        mode="markers",
        marker=dict(size=1.5, color="white", opacity=0.8),
        name="Background Stars",
    )
)

# ------------------------------------------------------------
# Animation — rotate black hole, not camera
# ------------------------------------------------------------
if live_motion:
    frames = []
    for i in range(60):
        angle = i * rotation_speed
        cos_a, sin_a = np.cos(angle), np.sin(angle)

        # rotate black hole + disk about z-axis
        x_rot = cos_a * x - sin_a * y
        y_rot = sin_a * x + cos_a * y
        Xdisk_rot = cos_a * Xdisk - sin_a * Ydisk
        Ydisk_rot = sin_a * Xdisk + cos_a * Ydisk

        frame = go.Frame(
            data=[
                go.Surface(x=x_rot, y=y_rot, z=z, colorscale=[[0, "rgb(30,0,60)"], [1, "rgb(100,0,160)"]], showscale=False, opacity=0.85),
                go.Surface(x=0.5*x_rot, y=0.5*y_rot, z=0.5*z, colorscale=[[0, "rgb(120,60,200)"], [1, "rgb(220,180,255)"]], showscale=False, opacity=0.9),
                go.Surface(x=Xdisk_rot, y=Ydisk_rot, z=Zdisk, colorscale=[[0, "rgba(255,180,60,0.3)"], [1, "rgba(255,80,0,0.8)"]], showscale=False, opacity=0.9)
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
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),
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
    ### Visual Structure
    - **Purple core:** the quantum crystalline singularity.  
    - **Dark violet shell:** the event horizon boundary.  
    - **Orange band:** the accretion disk.  
    - **Static stars:** background environment (fixed, not rotating).  
    """
)

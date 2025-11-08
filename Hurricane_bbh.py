import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy — Realistic Visualization")
st.caption("Dynamic visualization of a singularity, accretion disk, and starfield environment")

# ------------------------------------------------------------
# Adjustable parameters
# ------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    mass = st.number_input("Mass (solar masses)", value=4.3e6, format="%.1e")
with col2:
    live_motion = st.checkbox("Live rotation", value=True)

# Scale factors
r_s = 2.95 * mass / 1e6  # scaled Schwarzschild radius (arbitrary visual scale)
nebula_spread = 10

# ------------------------------------------------------------
# Generate black hole + singularity
# ------------------------------------------------------------
theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 50)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones_like(theta), np.cos(phi))

# Singularity core (small fractal-like sphere)
fig = go.Figure()

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
    colorscale=[[0, "rgb(40,0,60)"], [1, "rgb(140,0,200)"]],
    showscale=False,
    opacity=0.8,
    name="Event Horizon",
)

# ------------------------------------------------------------
# Accretion Disk (new surface)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Distant starfield (far background only)
# ------------------------------------------------------------
Nstars = 1000
r_starfield = 100  # big radius so they’re far away
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
        marker=dict(size=2, color="white", opacity=0.8),
        name="Background Stars",
    )
)

# ------------------------------------------------------------
# Camera & animation
# ------------------------------------------------------------
camera = dict(eye=dict(x=1.6, y=1.6, z=0.9))

if live_motion:
    frames = []
    for i in range(60):
        angle = i * (2 * np.pi / 60)
        cam = dict(eye=dict(x=1.6 * np.cos(angle), y=1.6 * np.sin(angle), z=0.9))
        frames.append(go.Frame(layout=dict(scene_camera=cam)))
    fig.frames = frames
    fig.update_layout(updatemenus=[{
        "type": "buttons",
        "showactive": False,
        "buttons": [{
            "label": "▶️",
            "method": "animate",
            "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True}]
        }]
    }])

# ------------------------------------------------------------
# Scene settings
# ------------------------------------------------------------
fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False),
        yaxis=dict(showbackground=False, showticklabels=False),
        zaxis=dict(showbackground=False, showticklabels=False),
        aspectmode="data",
        camera=camera,
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
    ### Description
    This simulator shows a **black hole with a quantum-style singularity**,  
    an **accretion disk**, and a **distant starfield**.

    - The singularity appears as a glowing crystalline core.  
    - The accretion disk is a turbulent surface around it.  
    - Stars are drawn far enough away to give a sense of cosmic scale.
    """
)

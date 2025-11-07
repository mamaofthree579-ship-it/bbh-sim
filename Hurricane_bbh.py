import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy Visualizer")
st.markdown("""
Explore the structure of a **black hole** based on the fractal singularity hypothesis:
- **Crystalline Singularity Core** – condensed quantum graviton field  
- **Accretion Nebula** – hot plasma disk emitting radiation  
- **Distant Starfield** – static cosmic background  
""")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Controls")
motion = st.sidebar.checkbox("Live Motion", value=False)
mass_scale = st.sidebar.slider("Singularity Scale", 0.5, 3.0, 1.0, 0.1)
nebula_density = st.sidebar.slider("Nebula Density", 500, 3000, 1000, 100)
nebula_spread = st.sidebar.slider("Nebula Spread", 5.0, 20.0, 10.0, 0.5)
star_density = st.sidebar.slider("Starfield Density", 1000, 8000, 4000, 200)

# --- Create Figure ---
fig = go.Figure()

# =======================================================
# STARFIELD: Far background, not a 3D globe
# =======================================================
Nstars = star_density
# Place stars randomly on a large spherical shell (radius ~200)
phi = np.random.uniform(0, 2 * np.pi, Nstars)
theta = np.random.uniform(0, np.pi, Nstars)
R_bg = 200

x_star = R_bg * np.sin(theta) * np.cos(phi)
y_star = R_bg * np.sin(theta) * np.sin(phi)
z_star = R_bg * np.cos(theta)

fig.add_trace(go.Scatter3d(
    x=x_star, y=y_star, z=z_star,
    mode="markers",
    marker=dict(size=0.8, color="rgba(255,255,255,0.45)"),
    name="Distant Starfield"
))

# =======================================================
# ACCRETION NEBULA (glowing disk)
# =======================================================
Nneb = nebula_density
theta = np.random.uniform(0, 2 * np.pi, Nneb)
r = nebula_spread * np.sqrt(np.random.rand(Nneb))
x_neb = r * np.cos(theta)
y_neb = r * np.sin(theta)
z_neb = np.random.normal(0, 0.3, Nneb)

fig.add_trace(go.Scatter3d(
    x=x_neb, y=y_neb, z=z_neb,
    mode="markers",
    marker=dict(size=2, color="rgba(255,150,50,0.25)"),
    name="Accretion Nebula"
))

# =======================================================
# SINGULARITY CORE (quantum crystalline graviton core)
# =======================================================
u = np.linspace(0, 2 * np.pi, 80)
v = np.linspace(0, np.pi, 80)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))

fig.add_surface(
    x=mass_scale*0.8*x,
    y=mass_scale*0.8*y,
    z=mass_scale*0.8*z,
    colorscale=[[0, "black"], [0.5, "purple"], [1, "violet"]],
    opacity=1.0,
    showscale=False,
    name="Singularity Core"
)

# =======================================================
# LAYOUT CONFIGURATION
# =======================================================
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="cube",
        bgcolor="black",
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    showlegend=False
)

# =======================================================
# LIVE ROTATION (smooth motion)
# =======================================================
if motion:
    plot_area = st.empty()
    for frame in range(240):
        angle = frame * 0.02
        fig.update_layout(scene_camera=dict(
            eye=dict(x=2.2*np.cos(angle), y=2.2*np.sin(angle), z=0.4)
        ))
        plot_area.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.03)
else:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.caption("Based on the fractal crystalline singularity model — visualized as a gravitational core emitting plasma through quantum energy curvature.")

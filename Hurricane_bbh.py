import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Anatomy — Visibility Fixed", layout="wide")

st.title("🌀 Black Hole Anatomy — Distant Starfield Edition")
st.markdown("""
A 3D model showing a black hole with a visible singularity core and accretion disk,  
set against a **realistic distant starfield**.  
""")

# Sidebar controls
st.sidebar.header("Simulation Controls")
motion = st.sidebar.checkbox("Live Motion", value=False)
mass_scale = st.sidebar.slider("Singularity Scale", 0.5, 3.0, 1.0, 0.1)
nebula_density = st.sidebar.slider("Nebula Density", 500, 3000, 1000, 100)
nebula_spread = st.sidebar.slider("Nebula Spread", 5.0, 20.0, 10.0, 0.5)
star_density = st.sidebar.slider("Starfield Density", 1000, 6000, 2000, 100)
star_distance = st.sidebar.slider("Star Distance (Background Radius)", 200, 800, 500, 50)

# =======================================================
# Create figure
# =======================================================
fig = go.Figure()

# =======================================================
# SINGULARITY CORE
# =======================================================
u = np.linspace(0, 2 * np.pi, 80)
v = np.linspace(0, np.pi, 80)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))

fig.add_surface(
    x=mass_scale * 0.8 * x,
    y=mass_scale * 0.8 * y,
    z=mass_scale * 0.8 * z,
    colorscale=[[0, "black"], [0.5, "purple"], [1, "violet"]],
    opacity=1.0,
    showscale=False,
    name="Singularity Core"
)

# =======================================================
# ACCRETION DISK
# =======================================================
Nneb = nebula_density
theta = np.random.uniform(0, 2 * np.pi, Nneb)
r = nebula_spread * np.sqrt(np.random.rand(Nneb))
x_neb = r * np.cos(theta)
y_neb = r * np.sin(theta)
z_neb = np.random.normal(0, 0.2, Nneb)

fig.add_trace(go.Scatter3d(
    x=x_neb, y=y_neb, z=z_neb,
    mode="markers",
    marker=dict(size=2.2, color="rgba(255,160,60,0.3)"),
    name="Accretion Nebula"
))

# =======================================================
# STARFIELD (FAR BACKGROUND ONLY)
# =======================================================
Nstars = star_density
phi = np.random.uniform(0, 2 * np.pi, Nstars)
theta = np.random.uniform(0, np.pi, Nstars)
r_stars = np.random.uniform(star_distance * 0.8, star_distance, Nstars)

x_star = r_stars * np.sin(theta) * np.cos(phi)
y_star = r_stars * np.sin(theta) * np.sin(phi)
z_star = r_stars * np.cos(theta)

fig.add_trace(go.Scatter3d(
    x=x_star, y=y_star, z=z_star,
    mode="markers",
    marker=dict(size=1.2, color="rgba(255,255,255,0.4)"),
    name="Distant Stars"
))

# =======================================================
# Layout
# =======================================================
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor="black",
        aspectmode="cube"
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, b=0, t=0),
    showlegend=False
)

# =======================================================
# Animation Loop
# =======================================================
if motion:
    plot_area = st.empty()
    for frame in range(300):
        angle = frame * 0.02
        fig.update_layout(scene_camera=dict(
            eye=dict(x=10 * np.sin(angle), y=10 * np.cos(angle), z=3 * np.sin(angle / 2))
        ))
        plot_area.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.03)
else:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.caption("You are viewing the black hole and accretion disk against a distant starfield.")

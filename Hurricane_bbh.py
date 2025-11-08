import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Realistic Black Hole Anatomy — Cosmic Cavity Edition")
st.markdown("""
This simulation places you *inside the cosmos*, showing a black hole surrounded by a realistic starfield.
Nearby space is cleared by gravitational scattering, letting you clearly view the singularity and accretion disk.
""")

# Sidebar controls
st.sidebar.header("Simulation Controls")
motion = st.sidebar.checkbox("Live Motion", value=False)
mass_scale = st.sidebar.slider("Singularity Scale", 0.5, 3.0, 1.0, 0.1)
nebula_density = st.sidebar.slider("Nebula Density", 500, 3000, 1000, 100)
nebula_spread = st.sidebar.slider("Nebula Spread", 5.0, 20.0, 10.0, 0.5)
star_density = st.sidebar.slider("Starfield Density", 1000, 8000, 4000, 200)
inner_clear = st.sidebar.slider("Cavity Radius", 20.0, 80.0, 45.0, 1.0)
outer_space = st.sidebar.slider("Starfield Radius", 100.0, 300.0, 200.0, 10.0)

# Create figure
fig = go.Figure()

# =======================================================
# STARFIELD — stars only *beyond* the cavity radius
# =======================================================
Nstars = star_density
phi = np.random.uniform(0, 2 * np.pi, Nstars)
theta = np.random.uniform(0, np.pi, Nstars)

# Distance from center — stars appear farther away
r_stars = np.random.uniform(inner_clear, outer_space, Nstars)

# Apply slight repulsion gradient (denser at large r)
weights = (r_stars - inner_clear) / (outer_space - inner_clear)
r_stars = r_stars * (0.8 + 0.4 * weights)

# Convert to Cartesian coordinates
x_star = r_stars * np.sin(theta) * np.cos(phi)
y_star = r_stars * np.sin(theta) * np.sin(phi)
z_star = r_stars * np.cos(theta)

fig.add_trace(go.Scatter3d(
    x=x_star, y=y_star, z=z_star,
    mode="markers",
    marker=dict(size=1.5, color="rgba(255,255,255,0.5)"),
    name="Starfield Background"
))

# =======================================================
# ACCRETION NEBULA — glowing plasma disk
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
    marker=dict(size=2, color="rgba(255,180,80,0.25)"),
    name="Accretion Nebula"
))

# =======================================================
# SINGULARITY CORE — crystalline fractal center
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
# Layout and Camera
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
# Live motion: orbit the camera gently
# =======================================================
if motion:
    plot_area = st.empty()
    for frame in range(300):
        angle = frame * 0.02
        fig.update_layout(scene_camera=dict(
            eye=dict(x=5 * np.sin(angle), y=5 * np.cos(angle), z=2.5 * np.sin(angle / 3))
        ))
        plot_area.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.03)
else:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.caption("You are within the cleared cavity of the black hole’s gravity well, surrounded by distant stars and the glowing accretion plasma.")

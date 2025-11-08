import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Quantum Black Hole Anatomy", layout="wide")

st.title("🌀 Quantum Black Hole Anatomy — Fractal Core Model")
st.markdown("""
A 3D model focusing on the **singularity structure** and **accretion dynamics**.  
This simplified version removes the background starfield for clarity and realism.
""")

# Sidebar controls
st.sidebar.header("Simulation Controls")
motion = st.sidebar.checkbox("Live Motion", value=False)
mass_scale = st.sidebar.slider("Singularity Scale", 0.5, 3.0, 1.0, 0.1)
nebula_density = st.sidebar.slider("Accretion Particle Density", 500, 3000, 1500, 100)
nebula_spread = st.sidebar.slider("Accretion Disk Radius", 4.0, 15.0, 8.0, 0.5)
core_texture = st.sidebar.selectbox("Core Color Scheme", ["Violet Plasma", "Blue Plasma", "Amber Core"])

# =======================================================
# Choose colors
# =======================================================
if core_texture == "Violet Plasma":
    core_colors = [[0, "black"], [0.4, "purple"], [1, "violet"]]
elif core_texture == "Blue Plasma":
    core_colors = [[0, "black"], [0.4, "navy"], [1, "cyan"]]
else:
    core_colors = [[0, "black"], [0.4, "darkorange"], [1, "gold"]]

# =======================================================
# Create figure
# =======================================================
fig = go.Figure()

# --- Singularity core ---
u = np.linspace(0, 2 * np.pi, 80)
v = np.linspace(0, np.pi, 80)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))

fig.add_surface(
    x=mass_scale * 0.8 * x,
    y=mass_scale * 0.8 * y,
    z=mass_scale * 0.8 * z,
    colorscale=core_colors,
    opacity=1.0,
    showscale=False,
    name="Singularity Core"
)

# --- Accretion disk surface instead of particle cloud ---
r_disk = np.linspace(0.5, nebula_spread, 100)
theta_disk = np.linspace(0, 2*np.pi, 200)
R, T = np.meshgrid(r_disk, theta_disk)
Xdisk = R * np.cos(T)
Ydisk = R * np.sin(T)
Zdisk = 0.2 * np.sin(3 * T) * np.exp(-R/nebula_spread)  # small turbulence waves

fig.add_surface(
    x=Xdisk, y=Ydisk, z=Zdisk,
    colorscale=[[0, "rgba(255,160,60,0.2)"], [1, "rgba(255,80,0,0.6)"]],
    showscale=False,
    opacity=0.8,
    name="Accretion Disk Surface"
)
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
# Live motion (rotating camera)
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

st.caption("This model focuses on the singularity core and accretion flow, without background interference.")

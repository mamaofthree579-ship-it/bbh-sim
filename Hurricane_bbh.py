import numpy as np
import plotly.graph_objects as go
import streamlit as st
import time

st.set_page_config(page_title="Black Hole Anatomy Explorer", layout="wide")

st.title("🌀 Black Hole Anatomy — Realistic Visualization")

st.markdown("""
Explore the anatomy of a black hole and its surrounding structures.
Use the sliders and toggle options below to adjust parameters.
""")

# --- Sidebar controls
st.sidebar.header("Simulation Controls")

mass = st.sidebar.slider("Mass (visual scale, M☉)", 1e3, 1e8, 4.3e6, step=1e3, format="%.0f")
spin = st.sidebar.slider("Spin parameter (a*)", 0.0, 0.99, 0.7, step=0.01)
disk_temp = st.sidebar.slider("Disk intensity (brightness)", 0.1, 2.0, 1.0, step=0.1)
live_mode = st.sidebar.checkbox("Enable Live Rotation", value=False)
show_labels = st.sidebar.checkbox("Show Labels", value=True)

# --- Base coordinate grid
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 100)
TH, PH = np.meshgrid(theta, phi)
x = np.sin(TH) * np.cos(PH)
y = np.sin(TH) * np.sin(PH)
z = np.cos(TH)

# --- Black hole parameters
r_s = 1.0  # Schwarzschild radius (normalized)
r_inner = r_s * 0.98
r_outer = r_s * 3.0

# --- Event horizon (dark sphere)
horizon = go.Surface(
    x=r_inner*x, y=r_inner*y, z=r_inner*z,
    colorscale=[[0, "black"], [1, "rgb(60,0,60)"]],
    showscale=False,
    name="Event Horizon",
    opacity=1
)

# --- Accretion disk
r = np.linspace(r_outer, 10*r_outer, 200)
phi_disk = np.linspace(0, 2*np.pi, 200)
R, PHI = np.meshgrid(r, phi_disk)
X = R * np.cos(PHI)
Y = R * np.sin(PHI)
Z = 0.05 * np.sin(5*PHI)  # slight warping
color_intensity = np.clip(np.exp(-0.2 * (R - r_outer)) * disk_temp, 0, 1)
disk = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=color_intensity,
    colorscale="Inferno",
    showscale=False,
    opacity=0.9,
    name="Accretion Disk"
)

# --- Photon sphere (light ring)
r_photon = 1.5 * r_s
ring_phi = np.linspace(0, 2*np.pi, 200)
ring_x = r_photon * np.cos(ring_phi)
ring_y = r_photon * np.sin(ring_phi)
ring_z = np.zeros_like(ring_phi)
ring = go.Scatter3d(
    x=ring_x, y=ring_y, z=ring_z,
    mode="lines",
    line=dict(color="violet", width=5),
    name="Photon Sphere"
)

# --- Fractal Singularity Core
r_core = 0.3 * r_s
fractal_phi = np.linspace(0, 2*np.pi, 80)
fractal_theta = np.linspace(0, np.pi, 40)
FPH, FTH = np.meshgrid(fractal_phi, fractal_theta)
core_x = r_core * np.sin(FTH) * np.cos(FPH)
core_y = r_core * np.sin(FTH) * np.sin(FPH)
core_z = r_core * np.cos(FTH)
core = go.Surface(
    x=core_x, y=core_y, z=core_z,
    colorscale=[[0, "rgb(80,0,100)"], [1, "rgb(180,0,255)"]],
    showscale=False,
    opacity=0.8,
    name="Singularity Core"
)

# --- Scene layout
scene = dict(
    xaxis=dict(showbackground=False, showgrid=False, visible=False),
    yaxis=dict(showbackground=False, showgrid=False, visible=False),
    zaxis=dict(showbackground=False, showgrid=False, visible=False),
    aspectmode="cube"
)

# --- Initialize figure
fig = go.Figure(data=[disk, horizon, ring, core])
fig.update_layout(
    paper_bgcolor="black",
    scene=scene,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=show_labels
)

# --- Live rotation or static view
plot_area = st.empty()
if live_mode:
    for angle in range(0, 360, 2):
        fig.update_layout(scene_camera=dict(eye=dict(x=np.cos(np.radians(angle))*1.5, y=np.sin(np.radians(angle))*1.5, z=0.6)))
        plot_area.plotly_chart(fig, use_container_width=True)
        time.sleep(0.03)
else:
    fig.update_layout(scene_camera=dict(eye=dict(x=1.5, y=1.5, z=0.6)))
    plot_area.plotly_chart(fig, use_container_width=True)

st.caption("Visualization inspired by realistic GRMHD simulations — simplified for educational study.")

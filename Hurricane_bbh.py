import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- App Setup ---
st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")
st.title("🌀 Black Hole Anatomy Simulator")
st.caption("A realistic 3D visualization exploring the structure and dynamics of a single black hole")

# --- Parameters ---
mass = st.sidebar.slider("Black Hole Mass (M☉)", 1e3, 1e8, 4.3e6, step=1e5, format="%.0f")
r_s = 2 * 6.674e-11 * mass * 1.988e30 / (3e8)**2  # Schwarzschild radius
r_outer = 3 * r_s  # accretion disk outer boundary
r_inner = r_s      # inner disk radius

# --- Meshgrid for Disk ---
theta = np.linspace(0, 2*np.pi, 200)
r = np.linspace(r_inner, r_outer, 100)
R, T = np.meshgrid(r, theta)
x = R * np.cos(T)
y = R * np.sin(T)
z = np.zeros_like(x)

# --- Accretion Disk Coloring (hot inner, cooler outer) ---
colors = np.exp(-((R - r_inner) / (r_outer - r_inner)))
colors = (colors - colors.min()) / (colors.max() - colors.min())

# --- Plotly Figure ---
fig = go.Figure()

# --- Singularity Core (purple fractal sphere) ---
phi, theta = np.mgrid[0:np.pi:60j, 0:2*np.pi:60j]
x_core = 0.5 * r_s * np.sin(phi) * np.cos(theta)
y_core = 0.5 * r_s * np.sin(phi) * np.sin(theta)
z_core = 0.5 * r_s * np.cos(phi)

fig.add_surface(
    x=x_core, y=y_core, z=z_core,
    colorscale=[[0, 'rgb(80,0,120)'], [1, 'rgb(200,120,255)']],
    opacity=0.9,
    showscale=False,
    name="Singularity Core"
)

# --- Accretion Disk ---
fig.add_surface(
    x=x, y=y, z=z,
    surfacecolor=colors,
    colorscale="Inferno",
    opacity=0.8,
    showscale=False,
    name="Accretion Disk"
)

# --- Star Field (distant, not in black hole cube) ---
Nstars = 1200
np.random.seed(42)
r_starfield = 50 * r_outer
theta_s = np.random.uniform(0, np.pi, Nstars)
phi_s = np.random.uniform(0, 2*np.pi, Nstars)

star_x = r_starfield * np.sin(theta_s) * np.cos(phi_s)
star_y = r_starfield * np.sin(theta_s) * np.sin(phi_s)
star_z = r_starfield * np.cos(theta_s)

fig.add_trace(go.Scatter3d(
    x=star_x, y=star_y, z=star_z,
    mode="markers",
    marker=dict(size=2, color="white", opacity=0.6),
    name="Stars"
))

# --- Layout (full-screen use, realistic space) ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-r_starfield, r_starfield]),
        yaxis=dict(visible=False, range=[-r_starfield, r_starfield]),
        zaxis=dict(visible=False, range=[-r_starfield, r_starfield]),
        aspectmode="data",
        bgcolor="black"
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Camera + View Options ---
st.sidebar.markdown("### View Options")
view = st.sidebar.radio("Camera Angle", ["Isometric", "Above Disk", "Edge View"])

camera_dict = {
    "Isometric": dict(eye=dict(x=1.5, y=1.5, z=1)),
    "Above Disk": dict(eye=dict(x=0, y=0, z=2.5)),
    "Edge View": dict(eye=dict(x=2.5, y=0, z=0.1)),
}
fig.update_layout(scene_camera=camera_dict[view])

# --- Display Visualization ---
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Information Sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Simulation Notes:**")
st.sidebar.info(
    "The singularity core represents a hypothesized fractal structure of quantum-compressed matter.\n\n"
    "The accretion disk emits energy in multiple spectra as matter orbits and heats from gravitational shear.\n\n"
    "The background stars are distant—forming a realistic skybox for depth."
)

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Quantum Singularity & Black Hole Anatomy Simulator")

# Sidebar controls
with st.sidebar:
    st.header("Simulation Controls")
    mode = st.selectbox("Mode", ["Classical Anatomy", "Quantum Fractal Core"])
    rotation_speed = st.slider("Rotation Speed", 0.0, 2.0, 0.3, 0.05)
    accretion_intensity = st.slider("Accretion Intensity", 0.1, 1.0, 0.6, 0.05)
    core_luminosity = st.slider("Core Luminosity", 0.0, 1.0, 0.7, 0.05)
    fractal_detail = st.slider("Fractal Core Complexity", 1, 5, 3, 1)
    show_labels = st.checkbox("Show Labels", True)

# Generate base mesh
theta, phi = np.mgrid[0:np.pi:100j, 0:2*np.pi:100j]
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# Core (fractal luminous)
core_radius = 0.25
core_color = "rgb(180,100,255)" if mode == "Quantum Fractal Core" else "rgb(100,0,150)"

core_x = core_radius * x
core_y = core_radius * y
core_z = core_radius * z

# Apply simple fractal perturbation to simulate “quantum crystalline” texture
if mode == "Quantum Fractal Core":
    for _ in range(fractal_detail):
        perturb = 0.04 * np.sin(6 * phi + 3 * np.pi * np.random.rand())
        core_x += perturb * np.cos(phi)
        core_y += perturb * np.sin(phi)

# Event horizon
r_event = 0.6
horizon_color = "rgba(50,0,80,0.95)"
horizon_x, horizon_y, horizon_z = r_event * x, r_event * y, r_event * z

# Accretion disk
r_disk = np.linspace(0.6, 1.6, 60)
phi_disk = np.linspace(0, 2 * np.pi, 120)
R, Phi = np.meshgrid(r_disk, phi_disk)
disk_x = R * np.cos(Phi)
disk_y = R * np.sin(Phi)
disk_z = 0.05 * np.sin(Phi * 8) * accretion_intensity

# Create Plotly figure
fig = go.Figure()

# Add event horizon
fig.add_surface(
    x=horizon_x,
    y=horizon_y,
    z=horizon_z,
    colorscale=[[0, horizon_color], [1, horizon_color]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# Add fractal core
fig.add_surface(
    x=core_x,
    y=core_y,
    z=core_z,
    colorscale=[[0, core_color], [1, core_color]],
    showscale=False,
    opacity=core_luminosity,
    name="Fractal Core"
)

# Add accretion disk
fig.add_surface(
    x=disk_x,
    y=disk_y,
    z=disk_z,
    colorscale=[[0, "rgb(255,120,60)"], [1, "rgb(255,220,180)"]],
    showscale=False,
    opacity=accretion_intensity,
    name="Accretion Disk"
)

# Layout and camera motion
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
)

# Add labels
if show_labels:
    fig.add_trace(go.Scatter3d(
        x=[0, 0, 1.3],
        y=[0, 0, 0],
        z=[0.6, -0.6, 0],
        mode="text",
        text=["Singularity Core", "Event Horizon", "Accretion Disk"],
        textposition="top center",
        textfont=dict(color="white", size=14)
    ))

# Animate rotation
angle = st.session_state.get("angle", 0.0)
angle += rotation_speed
st.session_state.angle = angle

camera = dict(
    eye=dict(x=2*np.cos(angle), y=2*np.sin(angle), z=0.7)
)
fig.update_layout(scene_camera=camera)

st.plotly_chart(fig, use_container_width=True)

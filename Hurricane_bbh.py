import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Quantum Singularity Field Simulator", layout="wide")

st.title("🌀 Quantum Singularity & Field Flow Simulator")

# Sidebar controls
with st.sidebar:
    st.header("Simulation Controls")
    mode = st.selectbox("Visualization Mode", ["Classical Anatomy", "Quantum Fractal Core"])
    field_mode = st.selectbox("Field Flow", ["Collapse (Inward)", "Emergence (Outward)"])
    rotation_speed = st.slider("Rotation Speed", 0.0, 2.0, 0.3, 0.05)
    accretion_intensity = st.slider("Accretion Intensity", 0.1, 1.0, 0.6, 0.05)
    core_luminosity = st.slider("Core Luminosity", 0.0, 1.0, 0.7, 0.05)
    fractal_detail = st.slider("Fractal Core Complexity", 1, 5, 3, 1)
    field_strength = st.slider("Quantum Field Intensity", 0.2, 1.0, 0.6, 0.05)
    show_labels = st.checkbox("Show Labels", True)

# --- Core geometry
theta, phi = np.mgrid[0:np.pi:100j, 0:2*np.pi:100j]
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

core_radius = 0.25
core_color = "rgb(180,100,255)" if mode == "Quantum Fractal Core" else "rgb(100,0,150)"
core_x, core_y, core_z = core_radius * x, core_radius * y, core_radius * z

# --- Fractal texture for the singularity
if mode == "Quantum Fractal Core":
    for _ in range(fractal_detail):
        perturb = 0.04 * np.sin(6 * phi + 3 * np.pi * np.random.rand())
        core_x += perturb * np.cos(phi)
        core_y += perturb * np.sin(phi)

# --- Event horizon
r_event = 0.6
horizon_color = "rgba(40,0,80,0.95)"
hx, hy, hz = r_event * x, r_event * y, r_event * z

# --- Accretion disk
r_disk = np.linspace(0.6, 1.6, 60)
phi_disk = np.linspace(0, 2*np.pi, 120)
R, Phi = np.meshgrid(r_disk, phi_disk)
disk_x = R * np.cos(Phi)
disk_y = R * np.sin(Phi)
disk_z = 0.05 * np.sin(Phi * 8) * accretion_intensity

# --- Build figure
fig = go.Figure()

# Event horizon
fig.add_surface(
    x=hx, y=hy, z=hz,
    colorscale=[[0, horizon_color], [1, horizon_color]],
    showscale=False, opacity=1.0, name="Event Horizon"
)

# Core
fig.add_surface(
    x=core_x, y=core_y, z=core_z,
    colorscale=[[0, core_color], [1, core_color]],
    showscale=False, opacity=core_luminosity, name="Singularity Core"
)

# Accretion disk
fig.add_surface(
    x=disk_x, y=disk_y, z=disk_z,
    colorscale=[[0, "rgb(255,120,60)"], [1, "rgb(255,220,180)"]],
    showscale=False, opacity=accretion_intensity, name="Accretion Disk"
)

# --- Quantum field lines
def generate_field_lines(n_lines=20, steps=100, outward=False):
    lines = []
    for i in range(n_lines):
        angle = i * (2 * np.pi / n_lines)
        r = np.linspace(0.2, 1.8, steps)
        spiral = 0.3 * np.sin(4 * np.pi * r)
        x = r * np.cos(angle + spiral)
        y = r * np.sin(angle + spiral)
        z = np.sign(np.sin(angle)) * 0.5 * np.sin(2 * np.pi * r)
        if not outward:
            x, y, z = -x, -y, -z
        lines.append((x, y, z))
    return lines

outward = field_mode == "Emergence (Outward)"
lines = generate_field_lines(outward=outward)

for x, y, z in lines:
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="lines",
        line=dict(width=2, color=f"rgba(150, 80, 255, {field_strength})"),
        showlegend=False
    ))

# --- Labels
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

# --- Camera animation
angle = st.session_state.get("angle", 0.0)
angle += rotation_speed
st.session_state.angle = angle

camera = dict(eye=dict(x=2*np.cos(angle), y=2*np.sin(angle), z=0.6))
fig.update_layout(scene_camera=camera)

# --- Final layout
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

st.plotly_chart(fig, use_container_width=True)

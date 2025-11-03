import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="Singularity Visualizer", layout="wide", page_icon="🌌")

st.title("🌌 Crystalline Singularity — 3D Visualization")

st.markdown("""
This simulation presents a **non-rotating black hole** with a crystalline singularity core.  
Use the controls to explore the geometry and brightness of the system.
""")

# === Controls ===
st.sidebar.header("🧭 Visualization Controls")
horizon_radius = st.sidebar.slider("Event Horizon Radius", 5, 50, 20)
disk_radius = st.sidebar.slider("Accretion Disk Radius", 30, 120, 60)
disk_thickness = st.sidebar.slider("Disk Thickness", 0.5, 5.0, 1.5)
brightness = st.sidebar.slider("Singularity Brightness", 0.1, 2.0, 1.0)
rotation_speed = st.sidebar.slider("Disk Rotation Speed", 0.1, 3.0, 1.0)

# === 3D coordinates ===
theta = np.linspace(0, 2*np.pi, 100)
phi = np.linspace(0, np.pi, 100)
x = horizon_radius * np.outer(np.cos(theta), np.sin(phi))
y = horizon_radius * np.outer(np.sin(theta), np.sin(phi))
z = horizon_radius * np.outer(np.ones(np.size(theta)), np.cos(phi))

# === Load singularity texture ===
def load_image_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

texture_b64 = load_image_as_base64("/mount/bbh/bbh-sim/singularity/singularity.png")

# === Create figure ===
fig = go.Figure()

# --- Singularity core (textured sphere) ---
fig.add_trace(go.Surface(
    x=x * 0.5,
    y=y * 0.5,
    z=z * 0.5,
    surfacecolor=np.zeros_like(x),
    colorscale=[[0, "rgba(255,255,255,0)"], [1, "rgba(255,255,255,0)"]],
    showscale=False,
    hoverinfo='skip',
    opacity=brightness
))

# --- Event horizon ---
fig.add_trace(go.Surface(
    x=x,
    y=y,
    z=z,
    colorscale=[[0, "rgb(120,0,180)"], [1, "rgb(60,0,100)"]],
    opacity=0.4,
    showscale=False,
    hoverinfo="skip"
))

# --- Accretion disk ---
disk_t = np.linspace(0, 2*np.pi, 200)
disk_r = np.linspace(horizon_radius * 1.2, disk_radius, 50)
T, R = np.meshgrid(disk_t, disk_r)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = disk_thickness * np.sin(T * rotation_speed)  # gives motion effect

fig.add_trace(go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale="Inferno",
    opacity=0.7,
    showscale=False,
    hoverinfo="skip"
))

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
)

# === Display ===
st.plotly_chart(fig, use_container_width=True)

# === Chirp sound toggle ===
st.sidebar.markdown("---")
st.sidebar.subheader("🎧 Sound Options")

if st.sidebar.button("Play Chirp Sound"):
    chirp_file = "chirp.mp3"  # must exist in your project root
    st.audio(chirp_file, format="audio/mp3")
else:
    st.sidebar.caption("Press the button to hear the gravitational chirp")

st.caption("Visualization © 2025 • Interactive Crystalline Singularity Simulator")

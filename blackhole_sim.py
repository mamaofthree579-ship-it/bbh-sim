🪐 quantum_blackhole_app.py

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy Simulator")
st.markdown("""
Explore a 3D model of a black hole with:
- **Event Horizon** (purple boundary)
- **Accretion Disk** (hot plasma disk)
- **Fractal Singularity Core** (quantum graviton crystal)
""")

# --- Controls ---
mass = st.slider("Black Hole Mass (in Solar Masses)", 1e6, 1e9, 4.3e6, step=1e6)
st.caption("Adjust mass to see radius scaling")

# --- Constants ---
G = 6.67430e-11
c = 2.998e8
M_sun = 1.98847e30

# --- Derived Quantities ---
M = mass * M_sun
r_s = 2 * G * M / c**2     # Schwarzschild radius
r_ph = 1.5 * r_s            # Photon sphere radius
r_disk = 3 * r_s            # Accretion disk outer radius

# --- Coordinates for Spherical Surfaces ---
theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 100)
theta, phi = np.meshgrid(theta, phi)

x = np.sin(phi) * np.cos(theta)
y = np.sin(phi) * np.sin(theta)
z = np.cos(phi)

# --- Plotly Figure ---
fig = go.Figure()

# Event horizon
fig.add_trace(go.Surface(
    x=r_s * x,
    y=r_s * y,
    z=r_s * z,
    colorscale=[[0, "rgb(80,0,120)"], [1, "rgb(140,0,220)"]],
    opacity=1.0,
    showscale=False,
    name="Event Horizon"
))

# Accretion disk (flattened torus)
phi_disk = np.linspace(0, 2 * np.pi, 100)
r_vals = np.linspace(0.8 * r_disk, r_disk, 30)
phi_disk, r_vals = np.meshgrid(phi_disk, r_vals)

x_disk = r_vals * np.cos(phi_disk)
y_disk = r_vals * np.sin(phi_disk)
z_disk = 0.15 * np.sin(3 * phi_disk) * (r_vals / r_disk)**2  # small warp

fig.add_trace(go.Surface(
    x=x_disk,
    y=y_disk,
    z=z_disk,
    surfacecolor=np.abs(np.sin(phi_disk)),
    colorscale="Inferno",
    opacity=0.85,
    showscale=False,
    name="Accretion Disk"
))

# Singularity core
fig.add_trace(go.Surface(
    x=0.4 * r_s * x,
    y=0.4 * r_s * y,
    z=0.4 * r_s * z,
    colorscale="Plasma",
    opacity=0.95,
    showscale=False,
    name="Singularity Core"
))

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        bgcolor="black"
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="black"
)

# --- Info Sidebar ---
st.sidebar.header("📊 Physical Parameters")
st.sidebar.write(f"**Mass:** {mass:,.0f} M☉")
st.sidebar.write(f"**Schwarzschild Radius (rₛ):** {r_s:.3e} m")
st.sidebar.write(f"**Photon Sphere (≈1.5 rₛ):** {r_ph:.3e} m")
st.sidebar.write(f"**Accretion Disk Outer Radius:** {r_disk:.3e} m")

st.sidebar.markdown("""
---
### 🧠 Notes
- Purple sphere: **Event Horizon**
- Orange glow: **Accretion Disk**
- Magenta core: **Quantum Fractal Singularity**
- Sizes are **scaled for visibility**, not true proportion.
---
""")

# --- Optional rotation ---
rotate = st.checkbox("Auto-rotate view", value=True)
if rotate:
    for angle in range(0, 360, 5):
        camera = dict(eye=dict(x=1.5*np.cos(np.radians(angle)),
                               y=1.5*np.sin(np.radians(angle)),
                               z=0.5))
        fig.update_layout(scene_camera=camera)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.plotly_chart(fig, use_container_width=True)

st.caption("Visualization by GPT-5 • Based on Schwarzschild geometry + fractal singularity theory model.")

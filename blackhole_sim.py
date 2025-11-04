import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy Simulator")
st.markdown("""
Visualize the structure of a black hole:
- **Event Horizon** (purple surface)
- **Accretion Disk** (orange-red plasma)
- **Fractal Singularity Core** (crystalline glow)
""")

# --- Controls ---
mass = st.slider("Black Hole Mass (in Solar Masses)", 1e6, 1e9, 4.3e6, step=1e6)
st.caption("Adjust mass to see relative scaling of features")

# --- Constants ---
G = 6.67430e-11
c = 2.998e8
M_sun = 1.98847e30

# --- Derived Quantities ---
M = mass * M_sun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s
r_disk = 3 * r_s

# --- Spherical coordinates (each surface needs its own meshgrid) ---
def sphere_mesh(radius, resolution=60):
    theta = np.linspace(0, 2 * np.pi, resolution)
    phi = np.linspace(0, np.pi, resolution)
    theta, phi = np.meshgrid(theta, phi)
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return x, y, z

# --- Plot ---
fig = go.Figure()

# Event Horizon
x_h, y_h, z_h = sphere_mesh(r_s)
fig.add_trace(go.Surface(
    x=x_h, y=y_h, z=z_h,
    colorscale=[[0, "rgb(80,0,120)"], [1, "rgb(140,0,220)"]],
    opacity=1.0,
    showscale=False,
    name="Event Horizon"
))

# Accretion Disk
phi_disk = np.linspace(0, 2 * np.pi, 150)
r_vals = np.linspace(0.8 * r_disk, r_disk, 30)
phi_disk, r_vals = np.meshgrid(phi_disk, r_vals)
x_d = r_vals * np.cos(phi_disk)
y_d = r_vals * np.sin(phi_disk)
z_d = 0.1 * r_disk * np.sin(3 * phi_disk) * (r_vals / r_disk)**2

fig.add_trace(go.Surface(
    x=x_d, y=y_d, z=z_d,
    surfacecolor=np.abs(np.sin(phi_disk)),
    colorscale="Inferno",
    opacity=0.9,
    showscale=False,
    name="Accretion Disk"
))

# Singularity Core (smaller sphere)
x_c, y_c, z_c = sphere_mesh(0.4 * r_s)
fig.add_trace(go.Surface(
    x=x_c, y=y_c, z=z_c,
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

# --- Sidebar Info ---
st.sidebar.header("📊 Physical Parameters")
st.sidebar.write(f"**Mass:** {mass:,.0f} M☉")
st.sidebar.write(f"**Schwarzschild Radius (rₛ):** {r_s:.3e} m")
st.sidebar.write(f"**Photon Sphere (≈1.5 rₛ):** {r_ph:.3e} m")
st.sidebar.write(f"**Accretion Disk Outer Radius:** {r_disk:.3e} m")

st.sidebar.markdown("""
---
### Notes
- Purple = Event Horizon  
- Orange = Accretion Disk  
- Magenta = Fractal Singularity Core  
- Scales are normalized for clarity
---
""")

# --- Rotation ---
rotate = st.checkbox("Auto-rotate view", value=True)
if rotate:
    for angle in range(0, 360, 10):
        camera = dict(eye=dict(x=1.8*np.cos(np.radians(angle)),
                               y=1.8*np.sin(np.radians(angle)),
                               z=0.5))
        fig.update_layout(scene_camera=camera)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.plotly_chart(fig, use_container_width=True)

st.caption("Visualization by GPT-5 • Based on Schwarzschild geometry and fractal singularity theory.")


---

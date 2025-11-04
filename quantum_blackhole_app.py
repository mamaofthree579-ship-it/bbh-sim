import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Fractal Singularity Black Hole", layout="wide")

st.title("🌀 Quantum Black Hole Anatomy — Fractal Core with Gravitational Ripples")

st.markdown("""
An interactive 3D visualization of black hole anatomy based on the **Fractal Singularity Theory**:

- **Event Horizon** — Boundary of spacetime collapse  
- **Accretion Disk** — Rotating plasma ring  
- **Fractal Core** — Pulsing crystalline singularity formed by compiled quantum gravitons  
- **Ripples** — Quantum-gravity wavefronts representing spacetime response to singularity oscillations
""")

# --- Constants ---
G = 6.67430e-11
c = 2.998e8
M_sun = 1.98847e30

# --- Parameters ---
mass = st.slider("Black Hole Mass (in Solar Masses)", 1e6, 1e9, 4.3e6, step=1e6)
pulse_speed = st.slider("Core Pulse Speed", 0.5, 3.0, 1.5, step=0.1)
animate = st.checkbox("Activate Fractal Pulse", True)

# --- Derived Radii ---
M = mass * M_sun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s
r_disk = 3 * r_s

# --- Sphere Mesh Helper ---
def sphere_mesh(radius, resolution=60):
    theta = np.linspace(0, 2 * np.pi, resolution)
    phi = np.linspace(0, np.pi, resolution)
    theta, phi = np.meshgrid(theta, phi)
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return x, y, z

# --- Base Spheres ---
x_h, y_h, z_h = sphere_mesh(r_s)
phi_disk = np.linspace(0, 2 * np.pi, 150)
r_vals = np.linspace(0.8 * r_disk, r_disk, 30)
phi_disk, r_vals = np.meshgrid(phi_disk, r_vals)
x_d = r_vals * np.cos(phi_disk)
y_d = r_vals * np.sin(phi_disk)
z_d = 0.1 * r_disk * np.sin(3 * phi_disk) * (r_vals / r_disk)**2

# --- Figure Setup ---
fig = go.Figure()

# Event Horizon
fig.add_surface(
    x=x_h, y=y_h, z=z_h,
    colorscale=[[0, "rgb(40,0,80)"], [1, "rgb(160,0,220)"]],
    opacity=1.0,
    showscale=False,
    name="Event Horizon"
)

# Accretion Disk
fig.add_surface(
    x=x_d, y=y_d, z=z_d,
    surfacecolor=np.abs(np.sin(phi_disk)),
    colorscale="Inferno",
    opacity=0.85,
    showscale=False,
    name="Accretion Disk"
)

# Fractal Core (dynamic)
x_c, y_c, z_c = sphere_mesh(0.4 * r_s)
fractal_intensity = np.abs(np.sin(4 * np.sqrt(x_c**2 + y_c**2 + z_c**2) / r_s))
core_surface = go.Surface(
    x=x_c, y=y_c, z=z_c,
    surfacecolor=fractal_intensity,
    colorscale="Plasma",
    opacity=0.95,
    showscale=False,
    name="Fractal Core"
)
fig.add_trace(core_surface)

# Initial Ripple Placeholder
x_r, y_r, z_r = sphere_mesh(1.1 * r_s)
ripple_surface = go.Surface(
    x=x_r, y=y_r, z=z_r,
    surfacecolor=np.zeros_like(x_r),
    colorscale="Viridis",
    opacity=0.1,
    showscale=False,
    name="Quantum Ripple"
)
fig.add_trace(ripple_surface)

# Scene Layout
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

# Sidebar info
st.sidebar.header("📊 Physical Parameters")
st.sidebar.write(f"**Mass:** {mass:,.0f} M☉")
st.sidebar.write(f"**Schwarzschild radius (rₛ):** {r_s:.3e} m")
st.sidebar.write(f"**Photon sphere (≈1.5 rₛ):** {r_ph:.3e} m")
st.sidebar.write(f"**Accretion Disk Radius:** {r_disk:.3e} m")

st.sidebar.markdown("""
---
**Legend**
- Violet → Event Horizon  
- Orange → Accretion Disk  
- Magenta → Fractal Core  
- Green → Quantum Ripple  
---
""")

# --- Display Logic ---
if not animate:
    st.plotly_chart(fig, use_container_width=True)
else:
    placeholder = st.empty()
    base_x, base_y, base_z = x_c, y_c, z_c

    for t in np.linspace(0, 4*np.pi, 120):
        # Core pulse expansion
        pulse = 0.25 * np.sin(t * pulse_speed) + 1.0
        x_c = base_x * pulse
        y_c = base_y * pulse
        z_c = base_z * pulse

        fractal_intensity = np.abs(np.sin(4 * np.sqrt(x_c**2 + y_c**2 + z_c**2) / (r_s * pulse)))
        fig.data[2].update(
            x=x_c, y=y_c, z=z_c,
            surfacecolor=fractal_intensity
        )

        # Ripple expansion
        ripple_radius = (1.1 + 0.4 * np.sin(t * pulse_speed)) * r_s
        x_r, y_r, z_r = sphere_mesh(ripple_radius)
        ripple_intensity = np.exp(-3 * np.abs(np.sin(t * pulse_speed)))
        fig.data[3].update(
            x=x_r, y=y_r, z=z_r,
            opacity=0.15 + 0.05 * np.sin(t * 2)
        )

        placeholder.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.05)

st.caption("Visualization by GPT-5 • Incorporating quantum-graviton crystalline core with spacetime ripple dynamics.")

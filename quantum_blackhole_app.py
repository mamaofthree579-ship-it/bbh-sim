import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Quantum Black Hole Anatomy", layout="wide")

st.title("🌀 Quantum Black Hole Anatomy — Stable Fractal Core Pulse")

st.markdown("""
Explore the **fractal crystalline singularity** — a quantum-graviton core pulsing within the event horizon.  
This version keeps the camera and layout stable while the **core and ripples animate in place**.
""")

# --- Constants ---
G = 6.67430e-11
c = 2.998e8
M_sun = 1.98847e30

# --- Parameters ---
mass = st.slider("Black Hole Mass (in Solar Masses)", 1e6, 1e9, 4.3e6, step=1e6)
pulse_speed = st.slider("Pulse Frequency", 0.5, 3.0, 1.5, step=0.1)

# --- Derived Radii ---
M = mass * M_sun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s
r_disk = 3 * r_s

# --- Helper for sphere ---
def sphere_mesh(radius, res=60):
    theta = np.linspace(0, 2 * np.pi, res)
    phi = np.linspace(0, np.pi, res)
    theta, phi = np.meshgrid(theta, phi)
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return x, y, z

# --- Static structures ---
x_h, y_h, z_h = sphere_mesh(r_s)
phi_disk = np.linspace(0, 2 * np.pi, 150)
r_vals = np.linspace(0.8 * r_disk, r_disk, 30)
phi_disk, r_vals = np.meshgrid(phi_disk, r_vals)
x_d = r_vals * np.cos(phi_disk)
y_d = r_vals * np.sin(phi_disk)
z_d = 0.1 * r_disk * np.sin(3 * phi_disk) * (r_vals / r_disk)**2

# --- Base figure setup ---
fig = go.Figure()

# Event Horizon
fig.add_surface(
    x=x_h, y=y_h, z=z_h,
    colorscale=[[0, "rgb(40,0,80)"], [1, "rgb(160,0,220)"]],
    opacity=1.0, showscale=False, name="Event Horizon"
)

# Accretion Disk
fig.add_surface(
    x=x_d, y=y_d, z=z_d,
    surfacecolor=np.abs(np.sin(phi_disk)),
    colorscale="Inferno", opacity=0.85, showscale=False, name="Accretion Disk"
)

# --- Animation frames ---
frames = []
for t in np.linspace(0, 2*np.pi, 40):
    pulse = 0.4 * (1 + 0.2 * np.sin(t * pulse_speed))
    ripple_radius = 1.2 * r_s + 0.2 * r_s * np.sin(t * pulse_speed)

    # Core
    x_c, y_c, z_c = sphere_mesh(pulse * r_s)
    fractal_intensity = np.abs(np.sin(4 * np.sqrt(x_c**2 + y_c**2 + z_c**2) / (r_s * pulse)))

    # Ripple
    x_r, y_r, z_r = sphere_mesh(ripple_radius)
    ripple_opacity = 0.1 + 0.05 * np.sin(t * 2 * pulse_speed)

    frame = go.Frame(
        data=[
            go.Surface(
                x=x_c, y=y_c, z=z_c,
                surfacecolor=fractal_intensity,
                colorscale="Plasma", showscale=False, opacity=0.9, name="Core"
            ),
            go.Surface(
                x=x_r, y=y_r, z=z_r,
                surfacecolor=np.ones_like(x_r)*0.3,
                colorscale="Viridis", showscale=False, opacity=ripple_opacity, name="Ripple"
            )
        ],
        name=f"frame{t}"
    )
    frames.append(frame)

# Add initial frame surfaces
fig.add_surface(
    x=sphere_mesh(0.4 * r_s)[0],
    y=sphere_mesh(0.4 * r_s)[1],
    z=sphere_mesh(0.4 * r_s)[2],
    colorscale="Plasma",
    opacity=0.9,
    showscale=False,
    name="Fractal Core"
)
fig.add_surface(
    x=sphere_mesh(1.2 * r_s)[0],
    y=sphere_mesh(1.2 * r_s)[1],
    z=sphere_mesh(1.2 * r_s)[2],
    colorscale="Viridis",
    opacity=0.1,
    showscale=False,
    name="Quantum Ripple"
)

# Layout configuration
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        bgcolor="black"
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
    updatemenus=[{
        "type": "buttons",
        "showactive": False,
        "buttons": [{
            "label": "▶ Play Pulse",
            "method": "animate",
            "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True}]
        }]
    }]
)

fig.frames = frames
st.plotly_chart(fig, use_container_width=True)

st.caption("Visualization by GPT-5 • Stable fractal singularity with localized quantum-ripple dynamics.")

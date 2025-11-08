import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Anatomy — Accretion Disk Microstars", layout="wide")

st.title("🌀 Black Hole Anatomy — Accretion Disk Plasma Simulation")

# --- Parameters ---
G = 6.67430e-11
c = 3.0e8
M_sun = 1.989e30

mass = st.slider("Black Hole Mass (solar masses)", 1e5, 1e9, 4.3e6, step=1e5, format="%.0f")
M = mass * M_sun
r_s = 2 * G * M / c**2  # Schwarzschild radius (m)

st.markdown(f"**Schwarzschild radius (rₛ):** {r_s/1000:.2e} km")

# --- Core geometry ---
theta = np.linspace(0, 2*np.pi, 100)
phi = np.linspace(0, np.pi, 100)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones_like(theta), np.cos(phi))

# --- Base figure ---
fig = go.Figure()

# Event horizon
fig.add_surface(
    x=r_s*x, y=r_s*y, z=r_s*z,
    colorscale=[[0, "black"], [1, "black"]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# Accretion disk (static)
r_disk_inner, r_disk_outer = 1.2*r_s, 2.0*r_s
disk_r = np.linspace(r_disk_inner, r_disk_outer, 50)
disk_t = np.linspace(0, 2*np.pi, 200)
R, T = np.meshgrid(disk_r, disk_t)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = 0.03 * np.sin(6*T) * r_s / 10  # subtle wave pattern

fig.add_surface(
    x=X, y=Y, z=Z,
    colorscale="inferno",
    opacity=0.8,
    showscale=False,
    name="Accretion Disk"
)

# --- Plasma microstars (orbiting particles) ---
N = 300
r_particles = np.random.uniform(r_disk_inner, r_disk_outer, N)
phi_particles = np.random.uniform(0, 2*np.pi, N)
z_particles = np.random.uniform(-0.02*r_s, 0.02*r_s, N)

# Button control
col1, col2 = st.columns(2)
animate = col1.button("▶️ Animate Accretion Disk")
reset = col2.button("⏹️ Reset View")

# --- Animation loop ---
frames = []
if animate:
    for t in np.linspace(0, 2*np.pi, 100):
        x_p = r_particles * np.cos(phi_particles + t)
        y_p = r_particles * np.sin(phi_particles + t)
        glow = 0.5 + 0.5 * np.sin(10*(phi_particles + t))
        frame = go.Scatter3d(
            x=x_p, y=y_p, z=z_particles,
            mode="markers",
            marker=dict(
                size=3,
                color=glow,
                colorscale="YlOrRd",
                opacity=0.9
            ),
            name="Microstars"
        )
        frames.append(frame)
    # show last frame (simple motion illusion)
    fig.add_trace(frames[-1])
else:
    fig.add_trace(go.Scatter3d(
        x=r_particles*np.cos(phi_particles),
        y=r_particles*np.sin(phi_particles),
        z=z_particles,
        mode="markers",
        marker=dict(size=3, color="gold", opacity=0.8),
        name="Microstars"
    ))

# --- Scene layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        bgcolor="black",
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

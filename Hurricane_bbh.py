import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Fractal Singularity — Quantum Black Hole Anatomy", layout="wide")
st.title("🌀 Fractal Singularity: Quantum Black Hole Anatomy Explorer")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Controls")
core_scale = st.sidebar.slider("Base Core Size", 0.3, 1.0, 0.6, 0.05)
disk_radius = st.sidebar.slider("Accretion Disk Radius", 1.2, 3.0, 2.0, 0.1)
rotation_speed = st.sidebar.slider("Rotation Speed", 10, 80, 40, 5)
pulse_strength = st.sidebar.slider("Core Pulsation Strength", 0.0, 0.3, 0.1, 0.01)
frames_count = 100

# === 1. Geometry ===
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 100)
x = np.outer(np.sin(theta), np.cos(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.cos(theta), np.ones_like(phi))

# === 2. Base Surfaces ===
def make_core(scale, temperature_factor=0.0):
    """Fractal-like singularity core with temperature-sensitive color."""
    color_scales = [
        [[0, "#2b004d"], [0.5, "#8a2be2"], [1, "#ffccff"]],
        [[0, "#4b0082"], [0.5, "#9400d3"], [1, "#ffffff"]],
        [[0, "#5f00ff"], [0.5, "#a020f0"], [1, "#87cefa"]]
    ]
    idx = int(np.clip(temperature_factor * (len(color_scales) - 1), 0, len(color_scales)-1))
    return go.Surface(
        x=scale * x,
        y=scale * y,
        z=scale * z,
        surfacecolor=np.cos(6 * x * y * z),
        colorscale=color_scales[idx],
        showscale=False,
        opacity=0.95,
        name="Fractal Core"
    )

# Event Horizon
horizon_surface = go.Surface(
    x=1.0 * x, y=1.0 * y, z=1.0 * z,
    surfacecolor=np.zeros_like(x),
    colorscale=[[0, "black"], [1, "purple"]],
    showscale=False,
    opacity=0.4,
    name="Event Horizon"
)

# Accretion Disk
phi_disk = np.linspace(0, 2*np.pi, 200)
r_disk = np.linspace(1.0, disk_radius, 2)
R, P = np.meshgrid(r_disk, phi_disk)
x_disk = R * np.cos(P)
y_disk = R * np.sin(P)
z_disk = 0.05 * np.sin(10 * P)
disk_surface = go.Surface(
    x=x_disk, y=y_disk, z=z_disk,
    surfacecolor=np.cos(P),
    colorscale="Inferno",
    showscale=False,
    opacity=0.9,
    name="Accretion Disk"
)

# Plasma Corona
phi_corona = np.linspace(0, 2*np.pi, 120)
r_corona = np.linspace(disk_radius * 0.8, disk_radius * 1.3, 2)
R_c, P_c = np.meshgrid(r_corona, phi_corona)
x_corona = R_c * np.cos(P_c)
y_corona = R_c * np.sin(P_c)
z_corona = 0.2 * np.sin(6 * P_c) + 0.3
corona_surface = go.Surface(
    x=x_corona, y=y_corona, z=z_corona,
    surfacecolor=np.sin(P_c),
    colorscale=[[0, "rgba(120,0,255,0.0)"], [0.5, "rgba(200,100,255,0.3)"], [1, "rgba(255,255,255,0.6)"]],
    showscale=False,
    opacity=0.5,
    name="Plasma Corona"
)

# === 3. Animation Frames ===
frames = []
for i, angle in enumerate(np.linspace(0, 2*np.pi, frames_count)):
    pulse = 1.0 + pulse_strength * np.sin(2 * angle)
    temp_factor = (np.sin(2 * angle) + 1) / 2

    # Disk & corona rotation
    rot_x_disk = np.cos(angle) * x_disk - np.sin(angle) * y_disk
    rot_y_disk = np.sin(angle) * x_disk + np.cos(angle) * y_disk
    rot_x_corona = np.cos(angle) * x_corona - np.sin(angle) * y_corona
    rot_y_corona = np.sin(angle) * x_corona + np.cos(angle) * y_corona

    frames.append(
        go.Frame(
            name=f"frame{i}",
            data=[
                make_core(core_scale * pulse, temperature_factor=temp_factor),
                horizon_surface,
                go.Surface(x=rot_x_disk, y=rot_y_disk, z=z_disk, surfacecolor=np.cos(P),
                           colorscale="Inferno", showscale=False, opacity=0.9),
                go.Surface(x=rot_x_corona, y=rot_y_corona, z=z_corona, surfacecolor=np.sin(P_c),
                           colorscale=[[0, "rgba(120,0,255,0.0)"],
                                       [0.5, "rgba(200,100,255,0.3)"],
                                       [1, "rgba(255,255,255,0.6)"]],
                           showscale=False, opacity=0.5)
            ],
        )
    )

# === 4. Figure ===
fig = go.Figure(
    data=[make_core(core_scale), horizon_surface, disk_surface, corona_surface],
    frames=frames,
    layout=go.Layout(
        title="Fractal Singularity — Event Horizon, Accretion Disk, and Plasma Corona",
        paper_bgcolor="black",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            bgcolor="black"
        ),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.05, y=0.05,
            buttons=[
                dict(label="▶️ Play", method="animate",
                     args=[None, {"frame": {"duration": 1000/rotation_speed, "redraw": True},
                                  "fromcurrent": True, "mode": "immediate"}]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
            ]
        )],
    ),
)

# === 5. Display in Streamlit ===
st.plotly_chart(fig, use_container_width=True)

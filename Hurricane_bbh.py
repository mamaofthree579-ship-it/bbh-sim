import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Fractal Singularity — Quantum Black Hole Anatomy", layout="wide")
st.title("🌀 Fractal Singularity: Quantum Black Hole Anatomy Explorer")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Controls")
disk_radius = st.sidebar.slider("Accretion Disk Radius", 1.2, 3.0, 2.0, 0.1)
core_scale = st.sidebar.slider("Base Core Size", 0.3, 1.0, 0.6, 0.05)
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
    """
    Create the fractal-like singularity core.
    Temperature factor modulates the color gradient — hotter when compressed.
    """
    # Shift the colormap according to temperature (more white/blue at high T)
    color_scales = [
        [[0, "#2b004d"], [0.5, "#8a2be2"], [1, "#ffccff"]],  # cool → violet → warm pink
        [[0, "#4b0082"], [0.5, "#9400d3"], [1, "#ffffff"]],  # violet → bright → white
        [[0, "#5f00ff"], [0.5, "#a020f0"], [1, "#87cefa"]]   # hot → lavender → sky blue
    ]
    idx = int(np.clip(temperature_factor * (len(color_scales) - 1), 0, len(color_scales)-1))
    colorscale = color_scales[idx]

    return go.Surface(
        x=scale * x,
        y=scale * y,
        z=scale * z,
        surfacecolor=np.cos(6 * x * y * z),
        colorscale=colorscale,
        showscale=False,
        opacity=0.95,
        name="Fractal Singularity Core"
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

# === 3. Animation Frames ===
frames = []
for i, angle in enumerate(np.linspace(0, 2*np.pi, frames_count)):
    # Core pulsation
    pulse = 1.0 + pulse_strength * np.sin(2 * angle)
    temp_factor = (np.sin(2 * angle) + 1) / 2  # normalized [0,1]

    # Disk rotation
    rot_x = np.cos(angle) * x_disk - np.sin(angle) * y_disk
    rot_y = np.sin(angle) * x_disk + np.cos(angle) * y_disk

    frames.append(
        go.Frame(
            name=f"frame{i}",
            data=[
                make_core(core_scale * pulse, temperature_factor=temp_factor),
                horizon_surface,
                go.Surface(
                    x=rot_x,
                    y=rot_y,
                    z=z_disk,
                    surfacecolor=np.cos(P),
                    colorscale="Inferno",
                    showscale=False,
                    opacity=0.9,
                ),
            ],
        )
    )

# === 4. Main Figure ===
fig = go.Figure(
    data=[make_core(core_scale), horizon_surface, disk_surface],
    frames=frames,
    layout=go.Layout(
        title="Fractal Singularity — Quantum Energy Pulsation & Horizon Dynamics",
        paper_bgcolor="black",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            bgcolor="black"
        ),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.05, y=0.05,
                buttons=[
                    dict(
                        label="▶️ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 1000/rotation_speed, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
    ),
)

# === 5. Display in Streamlit ===
st.plotly_chart(fig, use_container_width=True)

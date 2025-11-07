import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Fractal Singularity – Black Hole Anatomy", layout="wide")
st.title("🌀 Fractal Singularity: Black Hole Anatomy Explorer")

# Parameters
disk_radius = st.slider("Accretion Disk Radius", 1.2, 3.0, 2.0, 0.1)
core_scale = st.slider("Core Size", 0.2, 1.0, 0.6, 0.05)
rotation_speed = st.slider("Rotation Speed", 10, 80, 40, 5)
frames_count = 60

# === 1. Build geometry grids ===
theta = np.linspace(0, np.pi, 80)
phi = np.linspace(0, 2*np.pi, 80)
x = np.outer(np.sin(theta), np.cos(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.cos(theta), np.ones_like(phi))

# === 2. Core, horizon, and accretion disk surfaces ===
core_surface = go.Surface(
    x=core_scale * x, y=core_scale * y, z=core_scale * z,
    surfacecolor=np.cos(6 * x * y * z), colorscale="Viridis",
    showscale=False, opacity=0.95, name="Fractal Singularity Core"
)

horizon_surface = go.Surface(
    x=1.0 * x, y=1.0 * y, z=1.0 * z,
    surfacecolor=np.zeros_like(x), colorscale=[[0, "black"], [1, "purple"]],
    showscale=False, opacity=0.4, name="Event Horizon"
)

# Disk mesh
phi_disk = np.linspace(0, 2*np.pi, 200)
r_disk = np.linspace(1.0, disk_radius, 2)
R, P = np.meshgrid(r_disk, phi_disk)
x_disk = R * np.cos(P)
y_disk = R * np.sin(P)
z_disk = 0.05 * np.sin(10 * P)

disk_surface = go.Surface(
    x=x_disk, y=y_disk, z=z_disk,
    surfacecolor=np.cos(P), colorscale="Inferno",
    showscale=False, opacity=0.9, name="Accretion Disk"
)

# === 3. Animation frames ===
frames = []
for i, angle in enumerate(np.linspace(0, 2*np.pi, frames_count)):
    # Rotate the disk around z
    rot_x = np.cos(angle) * x_disk - np.sin(angle) * y_disk
    rot_y = np.sin(angle) * x_disk + np.cos(angle) * y_disk
    frames.append(
        go.Frame(
            name=f"frame{i}",
            data=[
                core_surface,
                horizon_surface,
                go.Surface(
                    x=rot_x, y=rot_y, z=z_disk,
                    surfacecolor=np.cos(P), colorscale="Inferno",
                    showscale=False, opacity=0.9
                )
            ]
        )
    )

# === 4. Combine figure ===
fig = go.Figure(
    data=[core_surface, horizon_surface, disk_surface],
    frames=frames,
    layout=go.Layout(
        title="Black Hole Anatomy – Fractal Singularity Model",
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
                            {"frame": {"duration": 1000/rotation_speed, "redraw": True},
                             "fromcurrent": True, "mode": "immediate"}
                        ]
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]
                    )
                ]
            )
        ]
    )
)

# === 5. Display ===
st.plotly_chart(fig, use_container_width=True)

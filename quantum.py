mport streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import time

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Black Hole Anatomy — Quantum Singularity", layout="wide")
st.title("🪐 Black Hole Anatomy — Quantum Singularity Visualizer")

st.markdown("""
This visualization explores the **anatomy of a black hole** with a fractal quantum singularity core.  
You can observe the **Event Horizon**, **Photon Sphere**, **Accretion Disk**, and **Energy Flow Streams** that simulate
the dynamics of energy and data through the gravitational field.
""")

# -----------------------------
# Constants
# -----------------------------
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
Msun = 1.98847e30

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("⚙️ Controls")

mass = st.sidebar.slider("Mass (Solar Masses)", 1, 10000000, 4300000, step=100000)
r_q = st.sidebar.slider("Quantum Radius Scale (m)", 1e3, 1e10, 1e6, step=1e5, format="%.1e")
lambda_c = st.sidebar.slider("λ (Curvature Coupling)", 0.01, 10.0, 1.0)
live_mode = st.sidebar.checkbox("🔄 Enable Live Mode (Animated)", value=False)

show_disk = st.sidebar.checkbox("Show Accretion Disk", value=True)
show_core = st.sidebar.checkbox("Show Singularity Core", value=True)
show_sphere = st.sidebar.checkbox("Show Photon Sphere", value=True)
show_streams = st.sidebar.checkbox("Show Energy Streams", value=True)

# -----------------------------
# Derived physics
# -----------------------------
M = mass * Msun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s

def F_QG(r):
    return (G * M / r**2) * np.exp(-r / r_q)

def dM_dt(M):
    return - (hbar * c**2 / G) * (1 / M**2)

# -----------------------------
# Geometry
# -----------------------------
theta, phi = np.mgrid[0:np.pi:50j, 0:2*np.pi:50j]
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# -----------------------------
# Frame state
# -----------------------------
if "frame" not in st.session_state:
    st.session_state["frame"] = 0

num_frames = 1 if not live_mode else 60
placeholder = st.empty()

for frame in range(num_frames):
    t = st.session_state["frame"] / 15.0
    cam_angle = st.session_state["frame"] * 3

    fig = go.Figure()

    # --- Event Horizon ---
    fig.add_surface(
        x=r_s * x, y=r_s * y, z=r_s * z,
        colorscale="Viridis", showscale=False,
        opacity=0.3, name="Event Horizon"
    )

    # --- Photon Sphere ---
    if show_sphere:
        fig.add_surface(
            x=r_ph * x, y=r_ph * y, z=r_ph * z,
            colorscale="Plasma", showscale=False,
            opacity=0.2, name="Photon Sphere"
        )

    # --- Accretion Disk ---
    if show_disk:
        r_disk = np.linspace(1.5 * r_s, 4 * r_s, 200)
        phi_disk = np.linspace(0, 2 * np.pi, 200)
        R, P = np.meshgrid(r_disk, phi_disk)
        X = R * np.cos(P)
        Y = R * np.sin(P)
        Z = 0.02 * r_s * np.sin(P * 4 + t)

        fig.add_surface(
            x=X, y=Y, z=Z,
            surfacecolor=np.sin(P * 8 + t),
            colorscale="Inferno", opacity=0.7,
            showscale=False, name="Accretion Disk"
        )

    # --- Singularity Core ---
    if show_core:
        r_core = 0.5 * r_s * (1 + 0.1 * np.sin(10 * theta + t))
        Xc = r_core * x
        Yc = r_core * y
        Zc = r_core * z
        fig.add_surface(
            x=Xc, y=Yc, z=Zc,
            surfacecolor=np.cos(theta * 5 + t),
            colorscale="Purples",
            showscale=False,
            opacity=0.85,
            name="Fractal Singularity Core"
        )

    # --- Energy Flow Streams ---
    if show_streams:
        num_streams = 16
        phi_streams = np.linspace(0, 2 * np.pi, num_streams)
        for p in phi_streams:
            r_vals = np.linspace(4 * r_s, 0.7 * r_s, 100)
            x_stream = r_vals * np.cos(p + 0.5 * np.sin(t))
            y_stream = r_vals * np.sin(p + 0.5 * np.sin(t))
            z_stream = 0.3 * r_s * np.sin(4 * np.pi * r_vals / (4 * r_s) + t)

            # color gradient: red (inflow) → purple (core)
            color = np.linspace(0, 1, len(r_vals))
            fig.add_trace(go.Scatter3d(
                x=x_stream, y=y_stream, z=z_stream,
                mode="lines",
                line=dict(
                    width=3,
                    color=color,
                    colorscale="Magma"
                ),
                opacity=0.8,
                name="Energy Stream"
            ))

    # --- Camera orbit ---
    camera = dict(
        eye=dict(
            x=2.8 * math.cos(math.radians(cam_angle)),
            y=2.8 * math.sin(math.radians(cam_angle)),
            z=0.9
        )
    )

    # --- Layout ---
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            bgcolor="black"
        ),
        paper_bgcolor="black",
        margin=dict(l=0, r=0, t=0, b=0),
        scene_camera=camera
    )

    # Render
    placeholder.plotly_chart(fig, use_container_width=True)
    if not live_mode:
        break

    time.sleep(0.05)
    st.session_state["frame"] += 1

# -----------------------------
# Physics readout
# -----------------------------
st.subheader("🧮 Quantum–Relativistic Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Schwarzschild Radius (m)", f"{r_s:.3e}")
    st.metric("Photon Sphere (m)", f"{r_ph:.3e}")
with col2:
    st.metric("QGC Force @ 2rₛ (N)", f"{F_QG(2 * r_s):.3e}")
    st.metric("Mass-loss rate (kg/s)", f"{dM_dt(M):.3e}")
with col3:
    st.metric("Quantum Radius", f"{r_q:.3e}")
    st.metric("λ (Curvature coupling)", f"{lambda_c:.2f}")

st.markdown("""
---
**Interpretation:**  
Energy streams visualize plasma, spacetime curvature, and data flow pathways that could emerge
if the singularity’s core behaves as a fractal quantum lattice—channeling gravitational energy as structured flow rather than chaotic collapse.
""")

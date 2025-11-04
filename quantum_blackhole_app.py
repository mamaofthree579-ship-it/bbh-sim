import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Black Hole Anatomy — Quantum Singularity", layout="wide")
st.title("🪐 Black Hole Anatomy — Quantum Singularity Visualizer")

st.markdown("""
Explore the internal anatomy of a black hole and its fractal singularity core.  
This simulation includes the **Event Horizon**, **Photon Sphere**, **Accretion Disk**, and the **Quantum Singularity Core**.  
The visuals and derived values are inspired by your **Quantum Gravity Compression (QGC)**, **Quantum Evaporation (QE–WH)**, and **Singularity Transition (STF)** functions.
""")

# -----------------------------
# Constants
# -----------------------------
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
Msun = 1.98847e30

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("⚙️ Controls")

mass = st.sidebar.slider("Mass (Solar Masses)", 1, 10000000, 4300000, step=100000)
r_q = st.sidebar.slider("Quantum Radius Scale (m)", 1e3, 1e10, 1e6, step=1e5, format="%.1e")
lambda_c = st.sidebar.slider("λ (Curvature coupling)", 0.01, 10.0, 1.0)
live_mode = st.sidebar.checkbox("🔄 Enable Live Mode (Animated)", value=False)

show_disk = st.sidebar.checkbox("Show Accretion Disk", value=True)
show_core = st.sidebar.checkbox("Show Singularity Core", value=True)
show_sphere = st.sidebar.checkbox("Show Photon Sphere", value=True)

# -----------------------------
# Derived physics
# -----------------------------
M = mass * Msun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s

# Quantum Gravity Compression
def F_QG(r):
    return (G * M / r**2) * np.exp(-r / r_q)

# Quantum Evaporation / White-Hole Transition
def dM_dt(M):
    return - (hbar * c**2 / G) * (1 / M**2)

# Singularity Transition Function
def S_trans(rho_QG, dR_dt):
    return np.trapz(rho_QG) - lambda_c * dR_dt

# -----------------------------
# Geometry generation
# -----------------------------
theta, phi = np.mgrid[0:np.pi:50j, 0:2*np.pi:50j]
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# Pulsation for live mode
t = 0
if live_mode:
    t = np.sin(st.session_state.get("frame", 0))
    st.session_state["frame"] = st.session_state.get("frame", 0) + 0.3

# -----------------------------
# Plot setup
# -----------------------------
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
    Z = 0.02 * r_s * np.sin(P * 4 + t)  # gentle warping

    fig.add_surface(
        x=X, y=Y, z=Z,
        surfacecolor=np.sin(P * 8 + t),
        colorscale="Inferno", opacity=0.7,
        showscale=False, name="Accretion Disk"
    )

# --- Singularity Core (Fractal-inspired) ---
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
        opacity=0.8,
        name="Singularity Core"
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
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="black",
)

# -----------------------------
# Display visualization
# -----------------------------
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Physics readout
# -----------------------------
st.subheader("🧮 Quantum & Relativistic Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Schwarzschild Radius (m)", f"{r_s:.3e}")
    st.metric("Photon Sphere (m)", f"{r_ph:.3e}")

with col2:
    F_sample = F_QG(2 * r_s)
    st.metric("QGC Force @ 2rₛ (N)", f"{F_sample:.3e}")
    st.metric("Mass-loss rate (kg/s)", f"{dM_dt(M):.3e}")

with col3:
    rho_QG = np.exp(-np.linspace(0, 10, 100))
    dR_dt = np.sin(t)
    s_value = S_trans(rho_QG, dR_dt)
    st.metric("Singularity Transition", f"{s_value:.3e}")
    st.metric("λ (Curvature coupling)", f"{lambda_c:.2f}")

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
---
*Visualization synthesizes GR and quantum-gravity phenomenology.*  
*Developed for exploring singularity dynamics & fractal core behavior.*
""")

# singularity_app.py
# Quantum Singularity Explorer (Prototype 1)
# ---------------------------------------------------------
# Streamlit app visualizing the anatomy of a black hole with
# a fractal quantum-graviton singularity core.

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Physical constants ---
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
M_sun = 1.98847e30

# --- Streamlit layout ---
st.set_page_config(page_title="Quantum Singularity Explorer", layout="wide")

st.title("🌀 Quantum Singularity Explorer")
st.markdown(
"""
This simulator explores your **fractal–core black hole theory**, combining classical and
quantum–gravitational effects. It visualizes the event horizon, photon sphere, accretion disk,
and crystalline singularity core.
"""
)

# --- Sidebar controls ---
st.sidebar.header("Simulation Controls")

M_solar = st.sidebar.slider("Black Hole Mass (M☉)", 1e6, 1e9, 4.3e6, step=1e6)
r_Q = st.sidebar.slider("Quantum Radius r₍Q₎ (m)", 1e2, 1e10, 1e7, step=1e6)
lambda_c = st.sidebar.slider("Curvature Coupling λ", 0.0, 1.0, 0.2, step=0.05)
show_disk = st.sidebar.checkbox("Show Accretion Disk", True)

# --- Derived quantities ---
M = M_solar * M_sun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s

# --- Quantum Gravity Compression Function ---
def F_QG(r):
    return (G * M / r**2) * np.exp(-r / r_Q)

# --- Quantum Evaporation rate ---
def dM_dt(M):
    return - (hbar * c**2 / G) * (1 / M**2)

# --- Singularity Transition Function ---
def S_trans(r_vals, rho_QG, dR_dt):
    integral = np.trapz(rho_QG, r_vals)
    return integral - lambda_c * dR_dt

# --- Sample field computation ---
r_vals = np.linspace(r_s, 5*r_s, 300)
rho_QG = F_QG(r_vals) / (4*np.pi*r_vals**2)   # toy density
dR_dt = np.gradient(F_QG(r_vals), r_vals).mean()
S_value = S_trans(r_vals, rho_QG, dR_dt)

stable = S_value < 0
stability_color = "🟢 Stable (Compression Dominant)" if stable else "🔴 Transition Phase (Output Dominant)"

# --- 3D visualization ---
theta, phi = np.mgrid[0:np.pi:50j, 0:2*np.pi:50j]

# Event horizon
x_h = r_s * np.sin(theta) * np.cos(phi)
y_h = r_s * np.sin(theta) * np.sin(phi)
z_h = r_s * np.cos(theta)

# Photon sphere
x_p = r_ph * np.sin(theta) * np.cos(phi)
y_p = r_ph * np.sin(theta) * np.sin(phi)
z_p = r_ph * np.cos(theta)

# Fractal-like crystalline core
r_core = 0.4 * r_s * (1 + 0.3 * np.sin(6*theta) * np.sin(6*phi))
x_c = r_core * np.sin(theta) * np.cos(phi)
y_c = r_core * np.sin(theta) * np.sin(phi)
z_c = r_core * np.cos(theta)

fig = go.Figure()

# Event horizon shell
fig.add_trace(go.Surface(
    x=x_h, y=y_h, z=z_h,
    colorscale="Viridis",
    opacity=0.3, name="Event Horizon",
    showscale=False
))

# Photon sphere
fig.add_trace(go.Surface(
    x=x_p, y=y_p, z=z_p,
    colorscale=[[0, 'rgba(255,255,255,0.2)'], [1, 'rgba(255,255,255,0.2)']],
    showscale=False,
    name="Photon Sphere"
))

# Fractal crystalline core
fig.add_trace(go.Surface(
    x=x_c, y=y_c, z=z_c,
    colorscale="Plasma",
    opacity=0.9,
    name="Fractal Core"
))

# Optional accretion disk
if show_disk:
    r_disk = np.linspace(r_ph, 3*r_ph, 80)
    phi_disk = np.linspace(0, 2*np.pi, 80)
    R, PHI = np.meshgrid(r_disk, phi_disk)
    Xd = R * np.cos(PHI)
    Yd = R * np.sin(PHI)
    Zd = 0.05*r_s * np.sin(5*PHI)
    fig.add_trace(go.Surface(
        x=Xd, y=Yd, z=Zd,
        colorscale="Inferno", opacity=0.6, showscale=False, name="Accretion Disk"
    ))

fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False),
        yaxis=dict(showbackground=False),
        zaxis=dict(showbackground=False),
        aspectmode='data'
    ),
    paper_bgcolor="black",
    scene_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# --- Results panel ---
st.markdown("## ⚙️ Derived Physical Quantities")
col1, col2 = st.columns(2)
with col1:
    st.metric("Schwarzschild radius (rₛ)", f"{r_s:.2e} m")
    st.metric("Photon sphere radius (1.5rₛ)", f"{r_ph:.2e} m")
with col2:
    st.metric("Quantum compression avg (F_QG)", f"{F_QG(r_s):.2e} N")
    st.metric("Transition Function (Sₜᵣₐₙₛ)", f"{S_value:.2e}")

st.markdown(f"### Stability: {stability_color}")

st.caption("Prototype physics visualization — parameters adjustable for exploratory testing of fractal singularity behavior.")

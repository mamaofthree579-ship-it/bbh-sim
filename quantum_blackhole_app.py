import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="Black Hole Singularity Anatomy", layout="wide")
st.title("🌀 Black Hole Singularity Anatomy Explorer")

st.markdown("""
This visualization illustrates a **conceptual model** of a black hole’s internal structure.
It integrates both classical general relativity layers and speculative quantum-gravity features.
Use the checkboxes and sliders to reveal different layers of the singularity anatomy.
""")

# -----------------------------
# Controls
# -----------------------------
mass = st.slider("Black Hole Mass (Solar Masses)", 1e5, 1e8, 4.3e6, step=1e5, format="%.0f")
spin = st.slider("Spin Parameter (a*)", 0.0, 1.0, 0.6, step=0.05)
quantum_radius = st.slider("Quantum Compression Radius (relative scale)", 0.2, 1.5, 0.8, step=0.1)
show_horizon = st.checkbox("Show Event Horizon", True)
show_photon = st.checkbox("Show Photon Sphere", True)
show_disk = st.checkbox("Show Accretion Disk", True)
show_singularity = st.checkbox("Show Quantum Singularity Core", True)
show_quantum_field = st.checkbox("Show Quantum Boundary Glow", True)

# -----------------------------
# Physical radii
# -----------------------------
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30
M = mass * M_sun

r_s = 2 * G * M / (c**2)
r_p = 1.5 * r_s
r_q = r_s * quantum_radius

st.markdown(f"""
**Schwarzschild radius:** {r_s:.3e} m  
**Photon sphere radius:** {r_p:.3e} m  
**Quantum compression scale:** {r_q:.3e} m  
""")

# -----------------------------
# Generate 3D geometry
# -----------------------------
u = np.linspace(0, 2*np.pi, 80)
v = np.linspace(0, np.pi, 40)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones_like(u), np.cos(v))

fig = go.Figure()

# Event Horizon
if show_horizon:
    fig.add_surface(
        x=x, y=y, z=z,
        opacity=1.0,
        colorscale=[[0, "#0d0c1d"], [1, "#4b0082"]],
        showscale=False,
        name="Event Horizon"
    )

# Photon Sphere
if show_photon:
    fig.add_surface(
        x=1.3*x, y=1.3*y, z=1.3*z,
        opacity=0.3,
        colorscale=[[0, "#ffb703"], [1, "#fb8500"]],
        showscale=False,
        name="Photon Sphere"
    )

# Accretion Disk
if show_disk:
    theta = np.linspace(0, 2*np.pi, 120)
    r_disk = np.linspace(1.3, 3.5, 60)
    T, R = np.meshgrid(theta, r_disk)
    X = R * np.cos(T)
    Y = R * np.sin(T)
    Z = 0.2 * np.sin(4*T) * (1 / R)  # turbulence

    fig.add_surface(
        x=X, y=Y, z=Z,
        surfacecolor=R,
        colorscale=[[0, "#ff4500"], [1, "#ffff00"]],
        opacity=0.8,
        showscale=False,
        name="Accretion Disk"
    )

# Quantum Singularity Core
if show_singularity:
    try:
        with open("singularity.png", "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        surface_texture = f"data:image/png;base64,{image_b64}"
    except Exception:
        surface_texture = None

    fig.add_surface(
        x=0.6*x, y=0.6*y, z=0.6*z,
        opacity=1.0,
        colorscale=[[0, "#b5179e"], [1, "#f72585"]],
        surfacepattern="x",
        showscale=False,
        name="Singularity Core"
    )

# Quantum Boundary Glow (Field)
if show_quantum_field:
    fig.add_surface(
        x=quantum_radius * 1.8 * x,
        y=quantum_radius * 1.8 * y,
        z=quantum_radius * 1.8 * z,
        opacity=0.15,
        colorscale=[[0, "#7209b7"], [1, "#4361ee"]],
        showscale=False,
        name="Quantum Boundary"
    )

# -----------------------------
# Layout
# -----------------------------
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.0))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<hr><small>⚛️ Conceptual illustration blending classical GR and quantum-compression theory. "
    "Parameters control proportional scaling, not literal distance. Developed for exploratory visualization.</small>",
    unsafe_allow_html=True,
)

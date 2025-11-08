import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Anatomy — Quantum Accretion Disk", layout="wide")

st.title("🌀 Black Hole Anatomy — Quantum Accretion Disk Turbulence Model")

# --- Constants ---
G = 6.67430e-11
c = 3.0e8
M_sun = 1.989e30

# --- User controls ---
mass = st.slider("Black Hole Mass (solar masses)", 1e5, 1e9, 4.3e6, step=1e5, format="%.0f")
M = mass * M_sun
r_s = 2 * G * M / c**2  # Schwarzschild radius (m)

st.markdown(f"**Schwarzschild radius (rₛ):** {r_s/1000:.2e} km")

# Quantum gravity radius scale
r_Q = st.slider("Quantum Gravity Radius Scale (× rₛ)", 0.5, 5.0, 1.5)
r_Q *= r_s

# --- Core geometry (event horizon sphere) ---
theta = np.linspace(0, 2*np.pi, 100)
phi = np.linspace(0, np.pi, 100)
x = np.outer(np.cos(theta), np.sin(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.ones_like(theta), np.cos(phi))

# --- Figure setup ---
fig = go.Figure()

# Event horizon
fig.add_surface(
    x=r_s*x, y=r_s*y, z=r_s*z,
    colorscale=[[0, "black"], [1, "black"]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# Accretion disk geometry
r_disk_inner, r_disk_outer = 1.2*r_s, 2.5*r_s
disk_r = np.linspace(r_disk_inner, r_disk_outer, 60)
disk_t = np.linspace(0, 2*np.pi, 240)
R, T = np.meshgrid(disk_r, disk_t)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = 0.03 * np.sin(6*T) * r_s / 10

fig.add_surface(
    x=X, y=Y, z=Z,
    colorscale="inferno",
    opacity=0.6,
    showscale=False,
    name="Accretion Disk"
)

# --- Plasma micro-particles ---
N = 400
r_particles = np.random.uniform(r_disk_inner, r_disk_outer, N)
phi_particles = np.random.uniform(0, 2*np.pi, N)
z_particles = np.random.uniform(-0.015*r_s, 0.015*r_s, N)

# --- Quantum Gravity Compression Field ---
def F_QG(r, m=M, r_Q=r_Q):
    return (G*m / r**2) * np.exp(-r / r_Q)

# Normalize for brightness
F_vals = F_QG(r_particles)
F_norm = (F_vals - F_vals.min()) / (F_vals.max() - F_vals.min())

# --- UI Controls ---
col1, col2 = st.columns(2)
animate = col1.button("▶️ Animate Turbulence Disk")
reset = col2.button("⏹️ Reset View")

# --- Animation loop ---
if animate:
    # Continuous live animation
    placeholder = st.empty()
    t = 0
    while t < 10:
        phase = t
        # Simulate turbulence as brightness oscillation
        temp_turb = F_norm * (1 + 0.2 * np.sin(6*phase + r_particles/r_s))
        color_vals = np.clip(temp_turb, 0, 1)

        x_p = r_particles * np.cos(phi_particles + 0.5*phase)
        y_p = r_particles * np.sin(phi_particles + 0.5*phase)
        z_p = z_particles + 0.01*r_s*np.sin(5*phase + r_particles/r_s)

        fig2 = go.Figure(fig)
        fig2.add_trace(go.Scatter3d(
            x=x_p, y=y_p, z=z_p,
            mode="markers",
            marker=dict(
                size=3,
                color=color_vals,
                colorscale="YlOrRd",
                opacity=0.9
            ),
            name="Plasma Turbulence"
        ))
        fig2.update_layout(
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

        placeholder.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.1)
        t += 0.1
else:
    # Static frame
    fig.add_trace(go.Scatter3d(
        x=r_particles*np.cos(phi_particles),
        y=r_particles*np.sin(phi_particles),
        z=z_particles,
        mode="markers",
        marker=dict(size=3, color=F_norm, colorscale="YlOrRd", opacity=0.8),
        name="Quantum Plasma"
    ))
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

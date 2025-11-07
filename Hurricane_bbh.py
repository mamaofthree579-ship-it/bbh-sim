import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Black Hole Anatomy — Lensed View", layout="wide")

st.title("🌀 Black Hole Anatomy — Lensed Singularity Model")

st.markdown("""
This simulation shows a realistic **black hole anatomy** including event horizon, photon sphere,
and a visual approximation of **gravitational lensing** around the core.
""")

# --- Sidebar controls
st.sidebar.header("Simulation Controls")
mass = st.sidebar.slider("Mass (visual scale, M☉)", 1e3, 1e8, 4.3e6, step=1e3, format="%.0f")
spin = st.sidebar.slider("Spin parameter (a*)", 0.0, 0.99, 0.7, step=0.01)
disk_temp = st.sidebar.slider("Disk intensity", 0.1, 2.0, 1.0, step=0.1)
live_mode = st.sidebar.checkbox("Enable Rotation", value=True)
show_labels = st.sidebar.checkbox("Show Labels", value=True)

# --- Coordinate grid
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 100)
TH, PH = np.meshgrid(theta, phi)
x = np.sin(TH) * np.cos(PH)
y = np.sin(TH) * np.sin(PH)
z = np.cos(TH)

r_s = 1.0
r_inner = r_s * 0.98
r_outer = r_s * 3.0

# --- Event Horizon
horizon = go.Surface(
    x=r_inner*x, y=r_inner*y, z=r_inner*z,
    colorscale=[[0, "black"], [1, "rgb(80,0,100)"]],
    showscale=False, opacity=1, name="Event Horizon"
)

# --- Accretion Disk
r = np.linspace(r_outer, 10*r_outer, 200)
phi_disk = np.linspace(0, 2*np.pi, 200)
R, PHI = np.meshgrid(r, phi_disk)
X = R * np.cos(PHI)
Y = R * np.sin(PHI)
Z = 0.05 * np.sin(5*PHI)
color_intensity = np.clip(np.exp(-0.2*(R - r_outer)) * disk_temp, 0, 1)
disk = go.Surface(
    x=X, y=Y, z=Z, surfacecolor=color_intensity,
    colorscale="Inferno", showscale=False, opacity=0.9,
    name="Accretion Disk"
)

# --- Photon Sphere
r_photon = 1.5 * r_s
ring_phi = np.linspace(0, 2*np.pi, 200)
ring_x = r_photon * np.cos(ring_phi)
ring_y = r_photon * np.sin(ring_phi)
ring_z = np.zeros_like(ring_phi)
ring = go.Scatter3d(
    x=ring_x, y=ring_y, z=ring_z,
    mode="lines", line=dict(color="violet", width=6),
    name="Photon Sphere"
)

# --- Singularity Core (fractal-like crystalline)
r_core = 0.3 * r_s
core_x = r_core * np.sin(TH) * np.cos(PH)
core_y = r_core * np.sin(TH) * np.sin(PH)
core_z = r_core * np.cos(TH)
core = go.Surface(
    x=core_x, y=core_y, z=core_z,
    colorscale=[[0, "rgb(100,0,140)"], [1, "rgb(220,100,255)"]],
    showscale=False, opacity=0.85,
    name="Singularity Core"
)

# --- Gravitational Lensing Field (background stars)
Nstars = 500
np.random.seed(42)
star_x = np.random.uniform(-5*r_outer, 5*r_outer, Nstars)
star_y = np.random.uniform(-5*r_outer, 5*r_outer, Nstars)
star_z = np.random.uniform(-5*r_outer, 5*r_outer, Nstars)

# distance from origin
r_dist = np.sqrt(star_x**2 + star_y**2 + star_z**2)

# define region where light bends noticeably
mask = (r_dist > 1.2*r_s) & (r_dist < 1.8*r_s)
deflection_strength = 0.25 * np.exp(-((r_dist - 1.5*r_s)**2) / (0.05*r_s)**2)

# apply only within that mask
star_x_lensed = star_x.copy()
star_y_lensed = star_y.copy()
star_z_lensed = star_z.copy()

star_x_lensed[mask] += deflection_strength[mask] * (star_x[mask] / r_dist[mask])
star_y_lensed[mask] += deflection_strength[mask] * (star_y[mask] / r_dist[mask])
# small outward offset to create ring rather than collapse
star_x_lensed[mask] += 0.2 * (star_x[mask] / r_dist[mask])
star_y_lensed[mask] += 0.2 * (star_y[mask] / r_dist[mask])

stars = go.Scatter3d(
    x=star_x_lensed, y=star_y_lensed, z=star_z_lensed,
    mode="markers",
    marker=dict(size=2, color="white", opacity=0.6),
    name="Background Stars"
)

# --- Space Grid & Star Field ---
Nstars = 1000
np.random.seed(42)

# Push stars far out, forming a distant sky sphere
r_starfield = 50 * r_outer
theta = np.random.uniform(0, np.pi, Nstars)
phi = np.random.uniform(0, 2*np.pi, Nstars)

star_x = r_starfield * np.sin(theta) * np.cos(phi)
star_y = r_starfield * np.sin(theta) * np.sin(phi)
star_z = r_starfield * np.cos(theta)

stars = go.Scatter3d(
    x=star_x,
    y=star_y,
    z=star_z,
    mode="markers",
    marker=dict(size=2, color="white", opacity=0.7),
    name="Background Stars"
)

# --- Layout (expanded frame + realistic space background) ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-r_starfield, r_starfield]),
        yaxis=dict(visible=False, range=[-r_starfield, r_starfield]),
        zaxis=dict(visible=False, range=[-r_starfield, r_starfield]),
        aspectmode="data",
        bgcolor="black"
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Smooth camera animation
if live_mode:
    frames = []
    for angle in np.linspace(0, 360, 120):
        rad = np.radians(angle)
        cam = dict(eye=dict(x=2.2*np.cos(rad), y=2.2*np.sin(rad), z=0.8))
        frames.append(go.Frame(layout=dict(scene_camera=cam)))
    fig.frames = frames
    fig.update_layout(
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 60, "redraw": True},
                                 "fromcurrent": True, "mode": "immediate"}],
                 "label": "▶️ Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                 "label": "⏸ Pause", "method": "animate"}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 80},
            "showactive": True,
            "type": "buttons",
            "x": 0.3, "xanchor": "right",
            "y": 0, "yanchor": "top"
        }]
    )

st.plotly_chart(fig, use_container_width=True)

st.caption("Black hole rendering with lensing distortion — smooth rotation, full-frame visualization.")

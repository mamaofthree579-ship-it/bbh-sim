import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Black Hole Anatomy — Smooth Live Mode", layout="wide")

st.title("🌀 Black Hole Anatomy — Realistic Visualization (Smooth Mode)")

st.markdown("""
This version uses internal Plotly animation for seamless rotation.
""")

# --- Sidebar controls
st.sidebar.header("Simulation Controls")

mass = st.sidebar.slider("Mass (visual scale, M☉)", 1e3, 1e8, 4.3e6, step=1e3, format="%.0f")
spin = st.sidebar.slider("Spin parameter (a*)", 0.0, 0.99, 0.7, step=0.01)
disk_temp = st.sidebar.slider("Disk intensity (brightness)", 0.1, 2.0, 1.0, step=0.1)
live_mode = st.sidebar.checkbox("Enable Live Rotation", value=False)
show_labels = st.sidebar.checkbox("Show Labels", value=True)

# --- Base coordinate grid
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 100)
TH, PH = np.meshgrid(theta, phi)
x = np.sin(TH) * np.cos(PH)
y = np.sin(TH) * np.sin(PH)
z = np.cos(TH)

# --- Parameters
r_s = 1.0
r_inner = r_s * 0.98
r_outer = r_s * 3.0

# --- Event horizon
horizon = go.Surface(
    x=r_inner*x, y=r_inner*y, z=r_inner*z,
    colorscale=[[0, "black"], [1, "rgb(60,0,60)"]],
    showscale=False,
    opacity=1,
    name="Event Horizon"
)

# --- Accretion disk
r = np.linspace(r_outer, 10*r_outer, 200)
phi_disk = np.linspace(0, 2*np.pi, 200)
R, PHI = np.meshgrid(r, phi_disk)
X = R * np.cos(PHI)
Y = R * np.sin(PHI)
Z = 0.05 * np.sin(5*PHI)
color_intensity = np.clip(np.exp(-0.2 * (R - r_outer)) * disk_temp, 0, 1)
disk = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=color_intensity,
    colorscale="Inferno",
    showscale=False,
    opacity=0.9,
    name="Accretion Disk"
)

# --- Photon sphere
r_photon = 1.5 * r_s
ring_phi = np.linspace(0, 2*np.pi, 200)
ring_x = r_photon * np.cos(ring_phi)
ring_y = r_photon * np.sin(ring_phi)
ring_z = np.zeros_like(ring_phi)
ring = go.Scatter3d(
    x=ring_x, y=ring_y, z=ring_z,
    mode="lines",
    line=dict(color="violet", width=5),
    name="Photon Sphere"
)

# --- Core (Singularity)
r_core = 0.3 * r_s
core_x = r_core * np.sin(TH) * np.cos(PH)
core_y = r_core * np.sin(TH) * np.sin(PH)
core_z = r_core * np.cos(TH)
core = go.Surface(
    x=core_x, y=core_y, z=core_z,
    colorscale=[[0, "rgb(80,0,100)"], [1, "rgb(180,0,255)"]],
    showscale=False,
    opacity=0.8,
    name="Singularity Core"
)

# --- Optional lensing halo
r_lens = 2.5 * r_s
lens_x = r_lens * x
lens_y = r_lens * y
lens_z = r_lens * z
lens = go.Surface(
    x=lens_x, y=lens_y, z=lens_z,
    opacity=0.15,
    colorscale=[[0, "rgba(255,255,255,0.2)"], [1, "rgba(255,255,255,0.05)"]],
    showscale=False,
    name="Lensing Halo"
)

# --- Scene setup
scene = dict(
    xaxis=dict(showbackground=False, visible=False),
    yaxis=dict(showbackground=False, visible=False),
    zaxis=dict(showbackground=False, visible=False),
    aspectmode="cube"
)

# --- Build base figure
fig = go.Figure(data=[disk, horizon, ring, core, lens])
fig.update_layout(
    paper_bgcolor="black",
    scene=scene,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=show_labels
)

# --- Smooth internal animation (rotating camera)
if live_mode:
    frames = []
    for angle in np.linspace(0, 360, 90):
        rad = np.radians(angle)
        cam = dict(eye=dict(x=np.cos(rad)*1.6, y=np.sin(rad)*1.6, z=0.6))
        frames.append(go.Frame(layout=dict(scene_camera=cam)))
    fig.frames = frames
    fig.update_layout(
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 80, "redraw": True},
                                 "fromcurrent": True, "mode": "immediate"}],
                 "label": "▶️ Play",
                 "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                 "label": "⏸ Pause",
                 "method": "animate"}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 80},
            "showactive": True,
            "type": "buttons",
            "x": 0.3,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }]
    )

# --- Show
st.plotly_chart(fig, use_container_width=True)

st.caption("Internal Plotly animation ensures smooth rotation without flashing.")

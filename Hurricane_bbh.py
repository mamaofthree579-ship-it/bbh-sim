import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Anatomy Simulator", layout="wide")

st.title("🌀 Black Hole Anatomy Visualizer")
st.markdown("""
This simulation shows a stylized **black hole anatomy** based on your fractal singularity model:
- **Singularity Core:** crystalline-like quantum graviton condensate  
- **Accretion Nebula:** energetic plasma disk  
- **Starfield:** distant galactic background  

Use the controls to explore how the system behaves.
""")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Controls")

motion = st.sidebar.checkbox("Live Motion", value=False)
mass_scale = st.sidebar.slider("Singularity Scale", 0.5, 3.0, 1.0, 0.1)
nebula_density = st.sidebar.slider("Nebula Density", 500, 3000, 1000, 100)
star_density = st.sidebar.slider("Starfield Density", 1000, 5000, 2000, 200)
nebula_spread = st.sidebar.slider("Nebula Spread", 5.0, 20.0, 10.0, 0.5)

# --- Initialize Figure ---
fig = go.Figure()

# --- Starfield (Background Layer) ---
Nstars = star_density
phi = np.random.uniform(0, 2 * np.pi, Nstars)
costheta = np.random.uniform(-1, 1, Nstars)
u = np.random.uniform(0, 1, Nstars)

theta = np.arccos(costheta)
r = 150 * (u ** (1/3))

x_star = r * np.sin(theta) * np.cos(phi)
y_star = r * np.sin(theta) * np.sin(phi)
z_star = r * np.cos(theta)

fig.add_trace(go.Scatter3d(
    x=x_star, y=y_star, z=z_star,
    mode="markers",
    marker=dict(size=0.8, color="rgba(255,255,255,0.4)"),
    name="Starfield Background"
))

# --- Accretion Nebula (Mid Layer) ---
Nneb = nebula_density
theta = np.random.uniform(0, 2 * np.pi, Nneb)
r = nebula_spread * np.sqrt(np.random.rand(Nneb))
x_neb = r * np.cos(theta)
y_neb = r * np.sin(theta)
z_neb = np.random.normal(0, 0.4, Nneb)

fig.add_trace(go.Scatter3d(
    x=x_neb, y=y_neb, z=z_neb,
    mode="markers",
    marker=dict(size=2, color="rgba(255,165,0,0.25)"),
    name="Accretion Nebula"
))

# --- Singularity Core (Front Layer) ---
u = np.linspace(0, 2 * np.pi, 60)
v = np.linspace(0, np.pi, 60)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))

fig.add_surface(
    x=mass_scale*0.7*x, y=mass_scale*0.7*y, z=mass_scale*0.7*z,
    colorscale=[[0, "black"], [0.6, "purple"], [1, "violet"]],
    opacity=1.0,
    showscale=False,
    name="Singularity Core"
)

# --- Layout Settings ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        bgcolor="black"
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    showlegend=False
)

# --- Live Motion (Rotation Animation) ---
if motion:
    plot_area = st.empty()
    for frame in range(200):
        angle = frame * 0.02
        fig.update_layout(scene_camera=dict(
            eye=dict(x=2*np.cos(angle), y=2*np.sin(angle), z=0.5)
        ))
        plot_area.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.03)
else:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("""
*Visualization based on your crystalline singularity theory —
the fractal quantum-graviton core maintains structural integrity
through dynamic curvature flow and energy redistribution.*
""")

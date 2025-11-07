import numpy as np
import plotly.graph_objects as go
import streamlit as st
import time

st.set_page_config(page_title="Black Hole Anatomy — Singularity Study", layout="wide")

st.title("🌀 Black Hole Anatomy — Singularity Study")
st.markdown("""
Explore the anatomy of a black hole with a focus on the **fractal singularity core** concept.
Use *Live Motion* to animate the accretion disk and surrounding dynamics.
""")

# --- Controls ---
col1, col2 = st.columns(2)
with col1:
    live = st.toggle("Live Motion", value=False)
with col2:
    show_nebula = st.toggle("Show Cosmic Haze", value=True)

# --- Physical parameters ---
r_s = 1.0  # normalized Schwarzschild radius
r_disk_outer = 3.5 * r_s
r_disk_inner = 1.3 * r_s

# --- Coordinate grid ---
phi = np.linspace(0, 2*np.pi, 180)
theta = np.linspace(0, np.pi, 90)
phi_grid, theta_grid = np.meshgrid(phi, theta)

# --- Event horizon (black sphere) ---
x_bh = r_s * np.sin(theta_grid) * np.cos(phi_grid)
y_bh = r_s * np.sin(theta_grid) * np.sin(phi_grid)
z_bh = r_s * np.cos(theta_grid)

# --- Fractal Singularity Core (small purple sphere) ---
r_core = 0.5 * r_s
x_core = r_core * np.sin(theta_grid) * np.cos(phi_grid)
y_core = r_core * np.sin(theta_grid) * np.sin(phi_grid)
z_core = r_core * np.cos(theta_grid)

# --- Accretion Disk (flattened, rotating ring) ---
r_disk = np.linspace(r_disk_inner, r_disk_outer, 200)
phi_disk = np.linspace(0, 2*np.pi, 360)
r_d, phi_d = np.meshgrid(r_disk, phi_disk)
z_d = 0.05 * np.sin(10 * phi_d)  # small vertical ripple
x_disk = r_d * np.cos(phi_d)
y_disk = r_d * np.sin(phi_d)

# --- Initialize figure ---
fig = go.Figure()

# --- Distant star field (fixed skybox style) ---
Nstars = 1800
np.random.seed(42)
r_starfield = 100 * r_disk_outer
theta_s = np.random.uniform(0, np.pi, Nstars)
phi_s = np.random.uniform(0, 2*np.pi, Nstars)
mask = np.random.choice([True, False], Nstars, p=[0.7, 0.3])
r_starfield = np.where(mask, r_starfield * 1.2, r_starfield * 0.8)
star_x = r_starfield * np.sin(theta_s) * np.cos(phi_s)
star_y = r_starfield * np.sin(theta_s) * np.sin(phi_s)
star_z = r_starfield * np.cos(theta_s) - (0.5 * r_starfield)

fig.add_trace(go.Scatter3d(
    x=star_x, y=star_y, z=star_z,
    mode="markers",
    marker=dict(size=2, color="white", opacity=0.8),
    name="Stars"
))

# --- Optional cosmic haze / nebula ---
if show_nebula:
    Nneb = 400
    neb_radius = np.mean(r_starfield)  # use scalar average radius for nebula bounds
    neb_x = np.random.uniform(-neb_radius, neb_radius, Nneb)
    neb_y = np.random.uniform(-neb_radius, neb_radius, Nneb)
    neb_z = np.random.uniform(-neb_radius, -0.2 * neb_radius, Nneb)


# --- Event horizon ---
fig.add_surface(
    x=x_bh, y=y_bh, z=z_bh,
    colorscale=[[0, "black"], [1, "black"]],
    showscale=False, name="Event Horizon", opacity=1.0
)

# --- Singularity Core (fractal crystalline glow) ---
fig.add_surface(
    x=0.5*x_core, y=0.5*y_core, z=0.5*z_core,
    surfacecolor=np.sin(10*phi_grid)*np.cos(10*theta_grid),
    colorscale="Viridis",
    showscale=False,
    name="Singularity Core",
    opacity=0.8
)

# --- Accretion Disk (emissive plasma band) ---
fig.add_surface(
    x=x_disk, y=y_disk, z=z_d,
    surfacecolor=np.sin(2*phi_d),
    colorscale="Plasma",
    showscale=False,
    name="Accretion Disk",
    opacity=0.9
)

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.3, y=1.3, z=0.6))
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
)

# --- Live motion ---
plot_area = st.empty()
if live:
    for t in range(100):
        # animate rotation of the accretion disk
        angle = t * 0.06
        x_rot = x_disk * np.cos(angle) - y_disk * np.sin(angle)
        y_rot = x_disk * np.sin(angle) + y_disk * np.cos(angle)

        fig.data[-1].x = x_rot
        fig.data[-1].y = y_rot

        plot_area.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.08)
else:
    plot_area.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Footer ---
st.markdown("""
#### 🧠 Notes
- **Singularity Core:** Represents the hypothesized fractal crystalline structure of compressed quantum gravitons.  
- **Event Horizon:** Classical boundary; all light and matter beyond this radius are trapped.  
- **Accretion Disk:** Simulated luminous plasma ring; rotation speed visually scaled for clarity.  
- **Stars & Nebula:** Distant cosmic background for depth and realism.
""")

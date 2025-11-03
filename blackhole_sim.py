import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Constants ---
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

st.set_page_config(page_title="Black Hole Anatomy ", layout="wide")

st.title("🪐 Black Hole Anatomy — Mass Scaling, Lensing & Tilt")

st.markdown("""
Now the **mass slider** affects the apparent size of the event horizon and disk.  
We’ve also added a **gravitational lensing illusion** and a **tilt control** to view the black hole from any angle.
""")

# --- Mass & Controls ---
mass_solar = st.slider("Black Hole Mass (M☉)", 10, 10_000_000, 4_300_000, step=10_000)
mass = mass_solar * M_sun
r_s = 2 * G * mass / c**2

# Logarithmic visual normalization (so scale stays visible)
visual_scale = np.log10(mass_solar) / np.log10(10_000_000)
r_s_vis = 0.2 + 0.8 * visual_scale  # 0.2–1.0 range for display
r_disk_inner = 1.5 * r_s_vis
r_disk_outer = 6 * r_s_vis

# --- Sidebar controls ---
st.sidebar.header("🌠 Motion & View Controls")
speed_factor = st.sidebar.slider("Hotspot speed (fraction of c)", 0.01, 0.5, 0.1)
t = st.sidebar.slider("Orbital phase", 0.0, 1.0, 0.0, step=0.01)
tilt_angle = st.sidebar.slider("View tilt (degrees)", 0, 80, 25)

# --- Orbital math ---
theta = 2 * np.pi * t
x_hot = 1.2 * r_disk_inner * np.cos(theta)
y_hot = 1.2 * r_disk_inner * np.sin(theta)
z_hot = 0

# --- Disk Doppler shading ---
theta_disk = np.linspace(0, 2*np.pi, 300)
radii = np.linspace(r_disk_inner, r_disk_outer, 2)
R, T = np.meshgrid(radii, theta_disk)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = np.zeros_like(X)

v_over_c = speed_factor * np.cos(T - theta)
doppler_intensity = np.clip((1 + v_over_c) / (1 - v_over_c + 1e-6), 0.5, 2.0)

# --- Disk surface ---
disk = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=doppler_intensity,
    colorscale=[[0, "darkred"], [0.5, "orangered"], [1, "gold"]],
    cmin=0.5, cmax=2.0,
    showscale=False,
    opacity=0.9,
    name="Accretion Disk"
)

# --- Event horizon (purple sphere) ---
u = np.linspace(0, 2*np.pi, 60)
v = np.linspace(0, np.pi, 30)
xh = r_s_vis * np.outer(np.cos(u), np.sin(v))
yh = r_s_vis * np.outer(np.sin(u), np.sin(v))
zh = r_s_vis * np.outer(np.ones_like(u), np.cos(v))
horizon = go.Surface(
    x=xh, y=yh, z=zh,
    colorscale=[[0, "#b300ff"], [1, "#8e2de2"]],
    showscale=False,
    opacity=1.0,
    name="Event Horizon"
)

# --- Hotspot ---
hotspot = go.Scatter3d(
    x=[x_hot], y=[y_hot], z=[z_hot],
    mode="markers",
    marker=dict(size=8, color="yellow", opacity=0.95),
    name="Hotspot"
)

# --- Background lensing arcs ---
phi = np.linspace(0, 2*np.pi, 80)
r_arc = r_disk_outer * 3
arc_traces = []
for k in range(6):
    bend = 0.05 * np.sin(3 * phi + k)
    x_arc = r_arc * np.cos(phi)
    y_arc = r_arc * np.sin(phi)
    z_arc = bend
    color = f"rgba(255,255,255,{0.15 + 0.1*k})"
    arc_traces.append(
        go.Scatter3d(
            x=x_arc, y=y_arc, z=z_arc,
            mode="lines",
            line=dict(color=color, width=1.5),
            hoverinfo="skip",
            showlegend=False
        )
    )

# --- Assemble all traces ---
traces = [disk, horizon, hotspot] + arc_traces
fig = go.Figure(data=traces)

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.5*np.cos(np.radians(tilt_angle)),
                             y=1.5*np.sin(np.radians(tilt_angle)),
                             z=0.9))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# --- Info box ---
st.markdown(f"""
### ⚙️ Physical Parameters

**Mass:** {mass_solar:,.0f} M☉  
**Schwarzschild radius (rₛ):** {r_s:.3e} m  
**Visible radius scaling:** {r_s_vis:.2f} (normalized)  
**Hotspot velocity:** {speed_factor:.2f} c  
**Tilt angle:** {tilt_angle}°  

---

🟣 **Event Horizon** — visualized in purple for contrast  
🟠 **Accretion Disk** — Doppler brightened on approach  
✨ **Star Arcs** — background light bent by spacetime curvature  
🌌 **Hotspot Motion** — orbiting plasma feature
""")

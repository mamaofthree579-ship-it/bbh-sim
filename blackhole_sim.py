import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Constants ---
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30
AU = 1.496e11

st.set_page_config(page_title="Black Hole Anatomy — Step 2", layout="wide")

st.title("🌌 Black Hole Anatomy — Step 2: Accretion Disk & Hotspot")
st.markdown("""
In this step we add an **accretion disk** and an **orbiting plasma hotspot**.  
The black hole is shown with its **event horizon** (purple), **photon sphere** (gold),  
and a bright **inner disk** glowing from gravitational heating.
""")

# --- Mass selection ---
mass_solar = st.slider("Black-hole mass (solar masses)", 1, 10000000, 4300000, step=10000)
mass = mass_solar * M_sun

# --- Physical radii ---
r_s = 2 * G * mass / c**2
r_ph = 1.5 * r_s
r_isco = 3 * r_s   # inner stable circular orbit (for Schwarzschild)

# --- Normalized scale ---
scale = 1.0
r_s_vis = 1.0 * scale
r_ph_vis = (r_ph / r_s) * scale
r_disk_inner = (r_isco / r_s) * scale
r_disk_outer = 6 * scale

# --- 3D sphere builder ---
def make_sphere(radius, color, opacity, name):
    u = np.linspace(0, 2*np.pi, 80)
    v = np.linspace(0, np.pi, 40)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    return go.Surface(
        x=x, y=y, z=z,
        surfacecolor=np.ones_like(x),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=opacity,
        name=name,
        hoverinfo="skip"
    )

# --- Disk mesh ---
def make_disk(r_inner, r_outer, color, opacity, name):
    theta = np.linspace(0, 2*np.pi, 200)
    r = np.linspace(r_inner, r_outer, 2)
    R, T = np.meshgrid(r, theta)
    X = R * np.cos(T)
    Y = R * np.sin(T)
    Z = np.zeros_like(X)
    return go.Surface(
        x=X, y=Y, z=Z,
        surfacecolor=np.ones_like(X),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=opacity,
        name=name,
        hoverinfo="skip"
    )

# --- Build 3D components ---
horizon = make_sphere(r_s_vis, "#7d2ae8", 1.0, "Event Horizon")
photon = make_sphere(r_ph_vis, "gold", 0.25, "Photon Sphere")
disk = make_disk(r_disk_inner, r_disk_outer, "orangered", 0.3, "Accretion Disk")

# --- Hotspot (animated) ---
st.sidebar.header("🌀 Hotspot Controls")
speed_factor = st.sidebar.slider("Orbital speed (fraction of light speed)", 0.01, 0.5, 0.1)
t = st.slider("Time (orbital phase)", 0.0, 1.0, 0.0, step=0.01)
radius_hotspot = 1.2 * r_disk_inner
omega = speed_factor * c / radius_hotspot

x_hot = radius_hotspot * np.cos(2 * np.pi * t)
y_hot = radius_hotspot * np.sin(2 * np.pi * t)
z_hot = 0

hotspot = go.Scatter3d(
    x=[x_hot], y=[y_hot], z=[z_hot],
    mode="markers",
    marker=dict(size=6, color="yellow", opacity=0.9),
    name="Hotspot"
)

# --- Figure layout ---
fig = go.Figure(data=[disk, photon, horizon, hotspot])
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.6, y=1.6, z=0.9))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# --- Info summary ---
st.markdown(f"""
### ⚙️ Physical parameters

**Mass:** {mass_solar:,.0f} M☉  
**Schwarzschild radius (rₛ):** {r_s:.3e} m  
**Photon sphere (1.5 rₛ):** {r_ph:.3e} m  
**ISCO (3 rₛ):** {r_isco:.3e} m  

**Hotspot:** Orbit radius ≈ {radius_hotspot/r_s:.2f} rₛ, velocity ≈ {speed_factor:.2f} c  

---

🟣 **Event Horizon** — gravitational boundary of no return  
🟡 **Photon Sphere** — unstable light orbits  
🔴 **Accretion Disk** — ionized gas spiraling inward, emitting X-rays  
✨ **Hotspot** — simulated plasma knot orbiting near ISCO  
""")

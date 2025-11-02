import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ---- Streamlit Page Config ----
st.set_page_config(page_title="3D Black Hole Simulator", layout="wide")

st.title("🌌 3D Black Hole Simulator")
st.markdown("Explore the geometry and dynamics around a rotating black hole with adjustable parameters.")

# ---- Sidebar Controls ----
st.sidebar.header("Simulation Controls")

bh_mass = st.sidebar.slider("Black Hole Mass (solar masses)", 1e6, 1e10, 4.3e6, step=1e6, format="%.0e")
spin = st.sidebar.slider("Spin Parameter (a*)", 0.0, 0.99, 0.5, step=0.01)
disc_radius = st.sidebar.slider("Accretion Disc Radius (km)", 1000, 100000, 10000, step=1000)
orbital_speed = st.sidebar.slider("Hotspot Orbital Speed (fraction of c)", 0.01, 0.99, 0.3, step=0.01)
disc_inclination = st.sidebar.slider("Disc Inclination (degrees)", 0, 90, 45, step=1)

st.sidebar.markdown("---")
st.sidebar.write("Use the sliders to explore the black hole’s geometry and plasma motion.")

# ---- Physical Constants ----
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

# ---- Derived Parameters ----
M = bh_mass * M_sun
r_s = 2 * G * M / c**2  # Schwarzschild radius in meters
r_s_km = r_s / 1000

# ---- Create Disc Geometry ----
n = 200
theta = np.linspace(0, 2*np.pi, n)
r = np.linspace(r_s_km*1.5, disc_radius, n)
R, TH = np.meshgrid(r, theta)
X = R * np.cos(TH)
Y = R * np.sin(TH)
Z = 0.05 * np.sin(3 * TH) * (1 - np.exp(-R / (3 * r_s_km)))  # texture warp

# Incline the disc
incl = np.radians(disc_inclination)
Z_incl = Z * np.cos(incl) + Y * np.sin(incl)
Y_incl = Y * np.cos(incl)

# ---- Hotspot Orbit ----
phi = np.linspace(0, 2*np.pi, 100)
hotspot_r = r_s_km * 5
hx = hotspot_r * np.cos(phi)
hy = hotspot_r * np.sin(phi)
hz = 0.1 * np.sin(2 * phi)
hy_i = hy * np.cos(incl)
hz_i = hz * np.cos(incl) + hy * np.sin(incl)

# ---- Create Plotly Figure ----
fig = go.Figure()

# Black hole sphere
u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
x_bh = (r_s_km) * np.cos(u) * np.sin(v)
y_bh = (r_s_km) * np.sin(u) * np.sin(v)
z_bh = (r_s_km) * np.cos(v)
fig.add_trace(go.Surface(
    x=x_bh, y=y_bh, z=z_bh,
    colorscale=[[0, "#3a0066"], [1, "#000000"]],
    showscale=False, opacity=1.0,
    name="Black Hole"
))

# Accretion disc
fig.add_trace(go.Surface(
    x=X, y=Y_incl, z=Z_incl,
    surfacecolor=R,
    colorscale="Inferno",
    cmin=np.min(R), cmax=np.max(R),
    opacity=0.9, showscale=False
))

# Hotspot orbit
fig.add_trace(go.Scatter3d(
    x=hx, y=hy_i, z=hz_i,
    mode='lines',
    line=dict(color='violet', width=4),
    name="Hotspot Orbit"
))

# ---- Layout ----
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        bgcolor='black'
    ),
    paper_bgcolor='black',
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ---- Info Section ----
st.markdown(f"""
### ℹ️ Derived Parameters
- Schwarzschild Radius: **{r_s_km:,.0f} km**
- Spin Parameter (a*): **{spin:.2f}**
- Orbital Speed: **{orbital_speed:.2f} c**
- Disc Inclination: **{disc_inclination}°**
""")

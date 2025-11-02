import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Black Hole Simulator", layout="wide")

# --- Sidebar controls ---
st.sidebar.title("⚙️ Simulation Controls")
mass = st.sidebar.slider("Black Hole Mass (M☉)", 1e6, 1e9, 4.3e6, step=1e5, format="%.1e")
spin = st.sidebar.slider("Spin Parameter (a*)", 0.0, 0.99, 0.5)
speed = st.sidebar.slider("Hotspot Speed", 0.1, 5.0, 1.0)
trail = st.sidebar.checkbox("Show Trail", True)
inclination = st.sidebar.slider("View Inclination (°)", 0, 90, 45)
distance = st.sidebar.slider("Camera Distance", 3, 15, 7)

# --- Constants ---
G = 6.67430e-11
c = 3.0e8
M_sun = 1.989e30
M = mass * M_sun
r_s = 2 * G * M / c**2

# --- Geometry for disk ---
theta = np.linspace(0, 2*np.pi, 200)
r_disk = np.linspace(1.5*r_s, 6*r_s, 100)
R, T = np.meshgrid(r_disk, theta)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = 0.03 * np.sin(3*T)  # small warp

# --- Accretion disk color ---
colorscale = [[0, "rgba(80,0,100,0.1)"], [1, "rgba(180,0,255,0.6)"]]

# --- Hotspot orbit ---
t = np.linspace(0, 2*np.pi, 100)
x_hot = 3*r_s * np.cos(t)
y_hot = 3*r_s * np.sin(t)
z_hot = 0.1*r_s * np.sin(3*t)

# --- Trail (optional) ---
if trail:
    trail_trace = go.Scatter3d(
        x=x_hot, y=y_hot, z=z_hot,
        mode='lines',
        line=dict(color='violet', width=4),
        name="Trail"
    )
else:
    trail_trace = None

# --- Hotspot (glowing plasma blob) ---
hotspot = go.Scatter3d(
    x=[x_hot[-1]], y=[y_hot[-1]], z=[z_hot[-1]],
    mode='markers',
    marker=dict(size=8, color='magenta', opacity=0.9),
    name="Hotspot"
)

# --- Black hole sphere (photon ring effect) ---
phi, theta = np.mgrid[0:np.pi:50j, 0:2*np.pi:50j]
x_bh = r_s * np.sin(phi) * np.cos(theta)
y_bh = r_s * np.sin(phi) * np.sin(theta)
z_bh = r_s * np.cos(phi)
bh_surface = go.Surface(
    x=x_bh, y=y_bh, z=z_bh,
    colorscale=[[0, "rgb(40,0,60)"], [1, "rgb(120,0,180)"]],
    showscale=False,
    opacity=0.95
)

# --- Disk surface ---
disk_surface = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=R,
    colorscale=colorscale,
    opacity=0.9,
    showscale=False
)

# --- Layout and camera ---
camera = dict(
    eye=dict(x=np.sin(np.radians(inclination)) * distance,
             y=np.cos(np.radians(inclination)) * distance,
             z=distance / 2)
)
scene = dict(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    zaxis=dict(visible=False),
    aspectmode='data'
)

# --- Combine ---
data = [bh_surface, disk_surface, hotspot]
if trail_trace: data.append(trail_trace)

fig = go.Figure(data=data)
fig.update_layout(
    scene=camera | scene,
    paper_bgcolor='black',
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Display ---
st.markdown("## 🌌 3D Black Hole Simulator (Sagittarius A*)")
st.plotly_chart(fig, use_container_width=True)

# --- Physics info ---
gamma = np.sqrt(1 - (r_s / (6*r_s)))
st.markdown(f"""
**Black Hole Properties**

- Schwarzschild Radius: `{r_s:.2e} m`
- Time Dilation Factor (γ): `{gamma:.6f}`
- Mass: `{mass:.2e} M☉`
""")

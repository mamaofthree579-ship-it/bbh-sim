import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Black Hole Lensing (Fast Init)", layout="wide")

st.title("🌀 Black Hole Anatomy — Fast Visual Model")
st.markdown(
    "Instant render of the event horizon, accretion disk, and a visual gravitational-lensing warp. "
    "No loops during load; the lensing is applied analytically and rendered immediately."
)

# --- Controls ---
col1, col2 = st.columns(2)
with col1:
    mass = st.slider("Mass (visual scale, M☉)", 1e3, 1e8, 4.3e6, step=1_000, format="%d")
    lens_strength = st.slider("Lensing strength", 0.0, 3.0, 1.2, 0.05)
with col2:
    shimmer = st.slider("Warp shimmer amplitude", 0.0, 0.6, 0.05, 0.01)
    animate = st.button("Animate hotspot (safe loop)")

# --- Constants ---
G = 6.6743e-11
c = 2.9979e8
M_sun = 1.98847e30
def r_s(m): return 2*G*M_sun*m/c**2

r_s_val = r_s(mass)
st.markdown(f"**Schwarzschild radius:** {r_s_val/1000:,.2f} km")

# --- Geometry ---
def sphere(r, n=40):
    u = np.linspace(0, 2*np.pi, n)
    v = np.linspace(0, np.pi, n)
    x = r*np.outer(np.cos(u), np.sin(v))
    y = r*np.outer(np.sin(u), np.sin(v))
    z = r*np.outer(np.ones_like(u), np.cos(v))
    return x, y, z

def torus(R, r, nu=80, nv=30):
    u = np.linspace(0, 2*np.pi, nu)
    v = np.linspace(0, 2*np.pi, nv)
    x = (R + r*np.cos(v))*np.cos(u)
    y = (R + r*np.cos(v))*np.sin(u)
    z = r*np.sin(v)
    return x, y, z

def lens(x, y, z, r_s_visual, strength, shimmer_phase=0.0, shimmer_amp=0.0):
    r = np.sqrt(x**2 + y**2 + z**2) + 1e-9
    L = 1 + strength*np.exp(-r/(2.5*r_s_visual))
    if shimmer_amp > 0:
        L += shimmer_amp*0.2*np.sin(6*np.arctan2(y,x)+shimmer_phase)
    return x*L, y*L, z*L

r_s_visual = 0.03
sx, sy, sz = sphere(r_s_visual)
tx, ty, tz = torus(3*r_s_visual, 0.8*r_s_visual)
tx, ty, tz = lens(tx, ty, tz, r_s_visual, lens_strength, shimmer_phase=0.0, shimmer_amp=shimmer)

# --- Figure ---
fig = go.Figure()

# Accretion disk
fig.add_trace(go.Surface(
    x=tx, y=ty, z=tz,
    colorscale=[[0,'orange'],[1,'red']],
    opacity=0.85, showscale=False,
    lighting=dict(ambient=0.6, diffuse=0.6),
    hoverinfo='skip', name="Accretion Disk"
))

# Singularity
fig.add_trace(go.Surface(
    x=sx, y=sy, z=sz,
    colorscale=[[0,'purple'],[1,'violet']],
    opacity=1.0, showscale=False,
    hoverinfo='skip', name="Singularity Core"
))

# Hotspot
hotspot = go.Scatter3d(
    x=[tx[0,0]], y=[ty[0,0]], z=[tz[0,0]],
    mode='markers', marker=dict(size=5, color='yellow'),
    name="Hotspot"
)
fig.add_trace(hotspot)

# Layout
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data'
    ),
    paper_bgcolor='black', plot_bgcolor='black',
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Display ---
ph = st.empty()
ph.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- Animation ---
if animate:
    frames = 60
    R = 3*r_s_visual
    r = 0.8*r_s_visual
    for i in range(frames):
        a = 2*np.pi*i/frames
        hx = (R+r*np.cos(0))*np.cos(a)
        hy = (R+r*np.cos(0))*np.sin(a)
        hz = r*np.sin(a)
        hx, hy, hz = lens(np.array([hx]), np.array([hy]), np.array([hz]), r_s_visual, lens_strength)
        fig.data[-1].x = [hx[0]]
        fig.data[-1].y = [hy[0]]
        fig.data[-1].z = [hz[0]]
        ph.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(0.05)
    st.success("Animation complete.")

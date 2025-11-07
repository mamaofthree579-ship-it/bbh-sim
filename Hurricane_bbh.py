import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Gravitational Lensing — BBH Anatomy", layout="wide")

st.title("🔭 Black Hole Anatomy — Gravitational Lensing (Option A)")
st.markdown(
    "Interactive visualization: event horizon, accretion torus, and a physically-inspired lensing warp. "
    "This is a visualization — not a full GR ray tracer, but it uses a physically motivated warp function "
    "to produce realistic-looking lensing near the horizon."
)

#
# Controls
#
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    mass = st.slider("Mass (visual solar masses)", min_value=1e3, max_value=1e8, value=4_300_000, step=1_000, format="%d")
    # mass affects r_s scale (visual)
    show_grid = st.checkbox("Show coordinate grid", value=False)

with col2:
    lens_strength = st.slider("Lensing strength", min_value=0.0, max_value=4.0, value=1.0, step=0.05)
    shimmer = st.slider("Warp shimmer (amplitude)", min_value=0.0, max_value=0.6, value=0.08, step=0.01)

with col3:
    hotspot_speed = st.slider("Hotspot speed (visual)", min_value=0.0, max_value=2.0, value=0.6, step=0.05)
    animate = st.button("Animate hotspot (3 cycles)")

st.markdown("---")

#
# Constants & helper functions
#
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

# Compute Schwarzschild radius (meters)
def schwarzschild_radius(m_solar):
    M_kg = m_solar * M_sun
    return 2 * G * M_kg / (c ** 2)

# Lensing warp function: returns radial displacement factor (>=0)
# We use exp(-r / (scale * r_s)) so lensing strongest near horizon.
def lensing_factor(r, r_s, lens_strength):
    # r may be 0 at center; avoid division by zero
    epsilon = 1e-9
    # scale parameter sets how quickly warp decays (~ few r_s)
    scale = 2.8  # physically ~ photon-sphere ~1.5 r_s; use slightly larger for visual effect
    # base warp: exponential fall-off with radial distance
    base = np.exp(- (r + epsilon) / (scale * r_s + epsilon))
    # convert to displacement multiplier
    return 1.0 + lens_strength * base

# Relativistic color shift simulation: side-of-disk doping
def doppler_color_map(theta):
    # theta is azimuthal angle on disk; approaching side (cos theta > 0) -> blue shift
    # returns RGB tuple in 0..255
    v = 0.15  # fiducial orbital speed fraction of c for color effect (tunable)
    dop = (1 + v * np.cos(theta))  # simple proxy
    # map doppler to color: dop>1 -> slightly bluer, <1 -> redder
    # base disk color: warm amber
    r0, g0, b0 = 255, 180, 80
    # apply simple tint
    r = np.clip(r0 * (1.0 / dop), 0, 255)
    g = np.clip(g0 * (1.0 / np.sqrt(dop)), 0, 255)
    b = np.clip(b0 * dop * 1.1, 0, 255)
    return (r / 255.0, g / 255.0, b / 255.0)

#
# Geometry generation
#
# Sphere (singularity core / horizon visual)
def make_sphere(radius=1.0, u_res=40, v_res=40):
    u = np.linspace(0, 2 * np.pi, u_res)
    v = np.linspace(0, np.pi, v_res)
    uu, vv = np.meshgrid(u, v)
    x = radius * np.cos(uu) * np.sin(vv)
    y = radius * np.sin(uu) * np.sin(vv)
    z = radius * np.cos(vv)
    return x, y, z, uu, vv

# Torus-like accretion disk (simplified) — create thin torus / warped ring
def make_torus(R=2.4, r_minor=0.5, u_res=200, v_res=20):
    u = np.linspace(0, 2 * np.pi, u_res)
    v = np.linspace(0, 2 * np.pi, v_res)
    uu, vv = np.meshgrid(u, v)
    x = (R + r_minor * np.cos(vv)) * np.cos(uu)
    y = (R + r_minor * np.cos(vv)) * np.sin(uu)
    z = r_minor * np.sin(vv)
    return x, y, z, uu, vv

#
# Build the warped geometry and color arrays
#
# Visual scaling: choose a normalized r_s so big mass maps to reasonable visual scale
r_s_phys = schwarzschild_radius(mass)
# map physical r_s to visual radius units
visual_scale = np.cbrt(mass / 1e6)  # gentle scaling with mass for visibility
r_s_visual = 0.9 * visual_scale * 0.02  # tune constant so horizon visible

# core sphere
sphere_r = r_s_visual  # visual event horizon radius
sx, sy, sz, suu, svv = make_sphere(radius=sphere_r, u_res=56, v_res=28)

# torus disk
torus_R = sphere_r * 2.6
torus_minor = sphere_r * 0.85
tx, ty, tz, tuu, tvv = make_torus(R=torus_R, r_minor=torus_minor, u_res=420, v_res=28)

# Flatten arrays for Mesh/Surface
def flatten_grid(x):
    return x.flatten()

# Apply lensing warp to coordinates (visual mapping)
def apply_lensing(x, y, z, r_s_physical, lens_strength_param, shimmer_amp=0.0, time_phase=0.0):
    # r computed in visual coords (not physical) but we scale r_s to visual units using r_s_visual
    r = np.sqrt(x**2 + y**2 + z**2) + 1e-12
    # compute warp factor using physical r_s scaled to visual space
    # mapping: physical r_s -> r_s_visual; we pass r_s_physical only to compute ratio for clarity
    # use lensing_factor that expects r and r_s (visual)
    L = lensing_factor(r, r_s_visual, lens_strength_param)
    # shimmer adds a small sinusoidal perturbation with angular dependence
    if shimmer_amp > 1e-6:
        # angular coords
        theta = np.arctan2(y, x)
        phi = np.arctan2(z, np.sqrt(x**2 + y**2))
        shimmer = 1.0 + shimmer_amp * 0.2 * np.sin(6.0 * theta + 4.0 * phi + time_phase)
        L = L * shimmer
    xw = x * L
    yw = y * L
    zw = z * L
    return xw, yw, zw

#
# Prepare the initial warped disk & sphere
#
# Warp torus
txw, tyw, tzw = apply_lensing(tx, ty, tz, r_s_phys, lens_strength, shimmer, 0.0)
# Warp sphere slightly (we keep sphere mostly central; lensing doesn't move the horizon itself)
sxw, syw, szw = apply_lensing(sx, sy, sz, r_s_phys, 0.0, 0.0, 0.0)

#
# Color arrays for torus (use azimuthal doppler color)
#
u_angles = tuu.flatten()  # azimuth angles
colors = [doppler_color_map(theta) for theta in u_angles]
# colors as rgb strings
color_strings = [f"rgb({int(r*255)},{int(g*255)},{int(b*255)})" for r,g,b in colors]
# reshape for surface usage
color_grid = np.array(color_strings).reshape(tuw_shape:=txw.shape)

#
# Build Plotly figure
#
def make_figure(txw, tyw, tzw, tx, ty, tz, sxw, syw, szw, color_grid, show_grid=False):
    fig = go.Figure()

    # Torus surface (use surface to get smooth shading)
    # plot torus as Surface: requires 2D arrays x,y,z
    fig.add_trace(
        go.Surface(
            x=txw,
            y=tyw,
            z=tzw,
            surfacecolor=np.zeros_like(txw),
            colorscale=[[0, 'rgb(255,180,80)'], [1, 'rgb(255,100,20)']],
            cmin=0, cmax=1,
            showscale=False,
            opacity=0.87,
            hoverinfo='skip',
            lighting=dict(ambient=0.6, diffuse=0.6, specular=0.1, roughness=0.9),
            lightposition=dict(x=100, y=100, z=200),
            name="Accretion disk"
        )
    )

    # Add a tinted mesh overlay for azimuthal coloring (scatter surface approximation)
    # We'll plot thin ribbon lines colored by the doppler color for visual cue:
    U, V = tx.shape
    # Draw a limited set of ribbons to avoid too many traces
    ribbons = 40
    for i in np.linspace(0, U-1, ribbons, dtype=int):
        xi = txw[i, :]
        yi = tyw[i, :]
        zi = tzw[i, :]
        # Use the doppler colors mapped along each ribbon
        cols = [color_grid[i, j] for j in range(V)]
        fig.add_trace(
            go.Scatter3d(
                x=xi, y=yi, z=zi,
                mode='lines',
                line=dict(color='rgba(255,255,255,0.06)', width=2),
                showlegend=False,
                hoverinfo='skip'
            )
        )

    # Singularity core (semi-opaque purple sphere)
    fig.add_trace(
        go.Surface(
            x=sxw,
            y=syw,
            z=szw,
            surfacecolor=np.ones_like(sxw),
            colorscale=[[0, 'rgb(40,0,60)'], [1, 'rgb(140,80,255)']],
            showscale=False,
            opacity=1.0,
            hoverinfo='skip',
            lighting=dict(ambient=0.3, diffuse=0.7, specular=0.5),
            name="Singularity core"
        )
    )

    # hotspot marker (start position)
    hotspot_x = (txw[0, 0])
    hotspot_y = (tyw[0, 0])
    hotspot_z = (tzw[0, 0])
    fig.add_trace(
        go.Scatter3d(
            x=[hotspot_x],
            y=[hotspot_y],
            z=[hotspot_z],
            mode='markers',
            marker=dict(size=6, color='rgb(255,240,170)', symbol='circle'),
            name='Hotspot',
            hoverinfo='skip',
            showlegend=False
        )
    )

    # layout: camera, lighting, background
    camera = dict(
        eye=dict(x=1.6, y=1.2, z=0.9)
    )
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=show_grid, showgrid=show_grid, zeroline=False),
            yaxis=dict(visible=show_grid, showgrid=show_grid, zeroline=False),
            zaxis=dict(visible=False),
            aspectmode='auto',
        ),
        scene_camera=camera,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# initial figure
fig = make_figure(txw, tyw, tzw, tx, ty, tz, sxw, syw, szw, color_grid, show_grid)

plot = st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

#
# Animate hotspot briefly if button pressed: safe short loops
#
if animate:
    # create a small animation loop: 3 cycles, limited frames, update hotspot only
    cycles = 3
    frames = 80
    total_frames = cycles * frames
    t0 = time.time()
    for frame_idx in range(total_frames):
        phase = (frame_idx / frames) * 2 * np.pi
        # compute hotspot position around torus major circle
        # choose a ring radius close to torus_R
        ang = phase * hotspot_speed
        hx = (torus_R + 0.5 * torus_minor * np.cos(0.0)) * np.cos(ang)
        hy = (torus_R + 0.5 * torus_minor * np.cos(0.0)) * np.sin(ang)
        hz = 0.6 * torus_minor * np.sin(ang * 0.6)
        # apply lensing warp to hotspot
        hxw, hyw, hzw = apply_lensing(np.array([hx]), np.array([hy]), np.array([hz]), r_s_phys, lens_strength, shimmer, phase)
        # update the hotspot trace (it's the last trace)
        try:
            fig.data[-1].x = [float(hxw[0])]
            fig.data[-1].y = [float(hyw[0])]
            fig.data[-1].z = [float(hzw[0])]
            plot.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            # fallback: refresh full figure
            fig = make_figure(txw, tyw, tzw, tx, ty, tz, sxw, syw, szw, color_grid, show_grid)
            plot.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        # short sleep for responsive update
        time.sleep(0.04)
    t1 = time.time()
    st.write(f"Animation done — {(t1-t0):.2f}s")

#
# If user changes sliders, give updated static render and a short shimmer preview
#
if st.button("Update view (apply lens + shimmer preview)"):
    # recompute warped geometry using current controls and a small shimmer phase
    txw_new, tyw_new, tzw_new = apply_lensing(tx, ty, tz, r_s_phys, lens_strength, shimmer, time_phase=0.6)
    sxw_new, syw_new, szw_new = apply_lensing(sx, sy, sz, r_s_phys, 0.0, 0.0, 0.0)
    fig = make_figure(txw_new, tyw_new, tzw_new, tx, ty, tz, sxw_new, syw_new, szw_new, color_grid, show_grid)
    plot.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.success("View updated.")

st.markdown(
    """
    **Notes (physics vs visualization)**  
    - `lensing_strength` controls the visual warp amplitude (physically it models how strongly light paths deviate near r_s).  
    - `shimmer` adds a small time-dependent perturbation to simulate local curvature oscillations or passing gravitational modes.  
    - This app intentionally uses a lightweight warp model (exponential fall-off) so the visualization runs smoothly in the browser.
    """
)

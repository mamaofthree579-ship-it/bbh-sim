# streamlit_app.py
"""
Black-Hole Anatomy — Step 1 (Event horizon + Photon sphere)
Streamlit app using Plotly for a 3D interactive visualization.

Usage:
    pip install streamlit plotly numpy
    streamlit run streamlit_app.py
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Physical constants
G = 6.67430e-11         # m^3 kg^-1 s^-2
c = 2.99792458e8        # m / s
M_sun = 1.98847e30      # kg
METERS_PER_AU = 1.495978707e11
METERS_PER_KM = 1e3

st.set_page_config(page_title="Black Hole Anatomy — Step 1", layout="wide",
                   initial_sidebar_state="expanded")

st.title("🔭 Black Hole Anatomy — Step 1: Event Horizon & Photon Sphere")

st.markdown(
    """
    This interactive module renders the event horizon and the photon sphere for a
    Schwarzschild (non-rotating) black hole.  
    Use the **Mass** slider to change the black-hole mass (in solar masses) and watch
    the physical radii update. The 3D spheres themselves are shown at a normalized
    visual scale so they remain visible and comparable for all masses.
    """
)

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    mass = st.slider("Black hole mass (M☉)", min_value=3.0, max_value=1e8, value=4.3e6,
                     step=1.0, format="%.0f")
    show_stars = st.checkbox("Show starfield background", value=True)
    normalized_scale = st.checkbox("Normalized visualization scale (keeps spheres visible)", value=True)
    st.markdown("---")
    st.caption("Step 1: core geometry. Next steps will add accretion disk, jets, labels, and more.")

# Compute physical radii
M = mass * M_sun
r_s = 2 * G * M / c**2            # Schwarzschild radius (m)
r_photon = 1.5 * r_s              # Photon sphere approx location for Schwarzschild
# small safety: for very small r_s avoid underflow — but values are fine numerically.

# Display numbers in human-friendly units
def fmt_m(x):
    if x >= 1e12:
        return f"{x/1e12:.4g} ×10^12 m"
    if x >= 1e9:
        return f"{x/1e9:.4g} ×10^9 m"
    if x >= 1e6:
        return f"{x/1e6:.4g} ×10^6 m"
    return f"{x:.4g} m"

col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("Physical radii")
    st.write(f"**Mass:** {mass:,.0f} M☉")
    st.write("**Schwarzschild radius (rₛ):**")
    st.write(f"• {r_s:.6e} m  • {r_s/METERS_PER_KM:.6e} km  • {r_s/METERS_PER_AU:.6e} AU")
    st.write("**Photon sphere (≈ 1.5 rₛ):**")
    st.write(f"• {r_photon:.6e} m  • {r_photon/METERS_PER_KM:.6e} km  • {r_photon/METERS_PER_AU:.6e} AU")

    st.markdown("---")
    st.write("**Notes**")
    st.caption("The 3D spheres are shown at normalized visual scale by default to keep them visible at very different physical sizes.")

with col2:
    # Prepare Plotly figure
    # Create sphere mesh (unit sphere) -> scale later for visualization
    def sphere_mesh(radius=1.0, n_lat=60, n_lon=60):
        u = np.linspace(0, np.pi, n_lat)
        v = np.linspace(0, 2 * np.pi, n_lon)
        u, v = np.meshgrid(u, v)
        x = radius * np.sin(u) * np.cos(v)
        y = radius * np.sin(u) * np.sin(v)
        z = radius * np.cos(u)
        return x, y, z

    # Determine visualization radii
    if normalized_scale:
        vis_r_s = 1.0
        vis_r_ph = 1.5
    else:
        # Map physical r_s into visualization units by applying a log-scale normalization.
        # For stability and visibility we take log10(r_s) and map to a reasonable radius range.
        # This mode can make very large masses show larger spheres but still keep them visible.
        log_rs = np.log10(max(r_s, 1.0))
        # Map log_rs roughly into [0.2, 6.0]
        vis_r_s = np.interp(log_rs, [1, 20], [0.2, 6.0])
        vis_r_ph = vis_r_s * 1.5

    # sphere meshes
    x_e, y_e, z_e = sphere_mesh(vis_r_s, n_lat=80, n_lon=80)
    x_p, y_p, z_p = sphere_mesh(vis_r_ph, n_lat=80, n_lon=80)

    # Colors and opacities
    event_color = "rgba(120,30,160,1.0)"        # deep purple outline
    event_face = "rgba(80,20,120,1.0)"          # slightly different fill
    photon_color = "rgba(170,110,255,0.9)"
    photon_face = "rgba(170,110,255,0.25)"

    fig = go.Figure()

    # Photon sphere (semi-transparent)
    fig.add_trace(go.Surface(
        x=x_p, y=y_p, z=z_p,
        colorscale=[[0, 'rgba(170,110,255,0.28)'], [1, 'rgba(170,110,255,0.28)']],
        showscale=False,
        opacity=0.28,
        hoverinfo='skip',
        name='Photon sphere'
    ))

    # Event horizon (opaque-ish, but visually purple rather than pure black)
    fig.add_trace(go.Surface(
        x=x_e, y=y_e, z=z_e,
        colorscale=[[0, event_face], [1, event_face]],
        showscale=False,
        opacity=1.0,
        hoverinfo='skip',
        name='Event horizon'
    ))

    # Optional starfield
    if show_stars:
        # Generate a spherical shell of points outside the photon sphere
        rng = np.random.default_rng(seed=42)
        # points distributed in a sphere shell
        n_stars = 400
        r_min = vis_r_ph * 2.2
        r_max = vis_r_ph * 6.5
        phi = np.arccos(1 - 2 * rng.random(n_stars))
        theta = 2 * np.pi * rng.random(n_stars)
        r_stars = rng.random(n_stars) * (r_max - r_min) + r_min
        xs = r_stars * np.sin(phi) * np.cos(theta)
        ys = r_stars * np.sin(phi) * np.sin(theta)
        zs = r_stars * np.cos(phi)
        star_sizes = rng.random(n_stars) * 2 + 1
        star_brightness = rng.random(n_stars) * 0.8 + 0.2
        fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs,
                                   mode='markers',
                                   marker=dict(size=star_sizes, color='white',
                                               opacity=star_brightness),
                                   hoverinfo='skip',
                                   name='Stars'))

    # Add an annotation (text) in 3D using layout annotations projected
    phys_r_s_km = r_s / METERS_PER_KM
    phys_r_ph_km = r_photon / METERS_PER_KM
    phys_label = f"rₛ = {phys_r_s_km:.3e} km\nr_ph ≈ {phys_r_ph_km:.3e} km"

    # Camera defaults
    camera = dict(eye=dict(x=1.8, y=1.25, z=1.1))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='auto',
            camera=camera
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="black",
        plot_bgcolor="black",
        showlegend=False
    )

    # Add a 2D annotation overlay (on the figure) with the physical numbers
    fig.add_annotation(dict(
        showarrow=False,
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"<b>Mass</b>: {mass:,.0f} M☉<br><b>rₛ</b>: {r_s:.3e} m<br><b>r_ph</b>: {r_photon:.3e} m",
        font=dict(color="white", size=12),
        align="left",
        bgcolor="rgba(10,10,20,0.6)",
        bordercolor="rgba(120,90,200,0.6)",
        borderwidth=1,
        borderpad=6
    ))

    # Display the figure
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})

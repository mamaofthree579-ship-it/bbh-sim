import streamlit as st
import numpy as np
import measure from skimage 
import plotly.graph_objects as go
from math import sin, cos, pi

st.set_page_config(layout="wide", page_title="Singularity Anatomy — Step 1", initial_sidebar_state="expanded")

st.title("🔬 Singularity Anatomy — Fractal Core + Asymmetric Ripple (Step 1)")
st.markdown(
    "Interactive exploration of a fractal crystalline singularity core with a small asymmetric/time-dependent deformation."
)

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    mass = st.slider("Mass (M☉)", min_value=1e3, max_value=1e9, value=4.3e6, step=1e3, format="%.0f")
    deform_amp = st.slider("Deformation amplitude", 0.0, 0.6, 0.14, step=0.01)
    harmonic_k = st.slider("Harmonic frequency (k)", 1, 12, 6, step=1)
    ripple_mult = st.slider("Ripple strength", 0.0, 1.0, 0.28, step=0.02)
    r_Q = st.number_input("Quantum radius r_Q (m) (visual scale)", value=1e9, step=1e8, format="%.0e")
    visualize_scale = st.slider("Visual scale factor", 0.2, 3.0, 1.0, step=0.1)
    time_val = st.slider("Time (t) — step/animate", 0.0, 60.0, 0.0, step=0.5)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Step time +"):
            time_val = time_val + 0.5
    with col2:
        if st.button("Reset time"):
            time_val = 0.0

st.markdown("### Visual parameters (grid & resolution)")
res = st.selectbox("Grid resolution (tradeoff: speed vs detail)", options=[40, 56, 64, 80], index=2)
threshold = st.slider("Iso-surface threshold (0..1)", 0.05, 0.8, 0.5, step=0.01)

# Physics constants (used for illustrative diagnostics only)
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

# Diagnostics: compute some toy physics numbers to display
# QGC: F_QG(r) = G m / r^2 * exp(- r/r_Q)
# We'll evaluate it at a sample radius chosen relative to visual scale
sample_r = 1e10  # sample radius in meters (visual scale only)
m_kg = mass * M_sun
F_QG = (G * m_kg) / (sample_r ** 2) * np.exp(-sample_r / max(r_Q, 1.0))
# QE-WH toy: dM/dt = -hbar c^2 / G * 1/M^2  (we will normalize for display)
hbar = 1.054571817e-34
dMdt = - (hbar * c ** 2) / G * (1.0 / (m_kg ** 2))

# simple presentation (scaled)
st.sidebar.markdown("### Diagnostics (toy values)")
st.sidebar.write(f"Sample radius (visual): {sample_r:.3e} m")
st.sidebar.write(f"F_QG(r) (toy) = {F_QG:.3e} N (illustrative)")
st.sidebar.write(f"dM/dt (toy) = {dMdt:.3e} kg/s (illustrative)")

# Generate scalar field on a 3D grid, cache to speed UI
@st.cache_data(show_spinner=False)
def make_field(resolution, k, amp, ripple_s, t, scale):
    # grid in [-1,1]^3 scaled by 'scale'
    N = resolution
    lin = np.linspace(-1.0, 1.0, N)
    xg, yg, zg = np.meshgrid(lin, lin, lin, indexing='xy')
    # physical radial coordinate for shaping (normalized)
    r = np.sqrt(xg**2 + yg**2 + zg**2) + 1e-12

    # Fractal-ish base: product of sines to create crystalline pattern
    freq = float(k)
    base = np.abs(np.sin(freq * xg * pi) * np.sin(freq * yg * pi) * np.sin(freq * zg * pi))

    # Asymmetric, time-dependent ripple deformation (angular harmonics)
    # compute angles
    theta = np.arctan2(np.sqrt(xg**2 + yg**2), zg + 1e-12)  # polar-like
    phi = np.arctan2(yg, xg + 1e-12)
    # ripple term uses harmonics and time
    ripple = ripple_s * np.sin(3.0 * theta + 0.6 * t) * np.cos(2.0 * phi + 0.4 * t)

    # radial attenuation to keep surface near center visually
    radial_mask = np.exp(- (r / 0.9) ** 2)

    # combined scalar field
    field = base + amp * radial_mask * ripple

    # apply a soft Gaussian to favor inner structure vs outer noise
    field = field * np.exp(- (r / (0.95))**2 ) + 0.05 * base * (1 - np.exp(- (r / 0.6)**2))

    return field, xg * scale, yg * scale, zg * scale

# scale mapping from mass to visual core scale (arbitrary mapping for display)
visual_scale = visualize_scale * max(0.05, (mass / 1e6) ** (1.0 / 3.0))  # keep it reasonable

# build the field
with st.spinner("Generating 3D field (marching cubes)..."):
    field, X, Y, Z = make_field(res, harmonic_k, deform_amp, ripple_mult, time_val, visual_scale)

# marching cubes to extract isosurface
try:
    verts, faces, normals, values = measure.marching_cubes(field, level=threshold, spacing=(X[1,0,0]-X[0,0,0],
                                                                                             Y[0,1,0]-Y[0,0,0],
                                                                                             Z[0,0,1]-Z[0,0,0]))
except Exception as e:
    st.error("Error extracting surface (try lowering resolution or changing threshold).")
    st.write("Exception:", e)
    st.stop()

# Build Mesh3d with Plotly
xv, yv, zv = verts.T
ivi = faces  # triangular faces

# color mapping from values at vertices (interpolate)
# use the scalar field values at the vertex positions by indexing 'values' from marching result
vertex_color = values  # already returned as 'values' for vertices by marching_cubes

mesh = go.Mesh3d(
    x=xv, y=yv, z=zv,
    i=ivi[:, 0], j=ivi[:, 1], k=ivi[:, 2],
    intensity=vertex_color,
    colorscale='Plasma',
    intensitymode='vertex',
    showscale=False,
    opacity=0.95,
    flatshading=False,
    lighting=dict(ambient=0.6, diffuse=0.8, roughness=0.9, specular=0.5),
    name='Fractal core'
)

# Add a faint semi-transparent accretion ring (2D ring extruded slightly)
theta = np.linspace(0, 2 * np.pi, 160)
ring_r = 1.05 * visual_scale
ring_x = ring_r * np.cos(theta)
ring_y = ring_r * np.sin(theta)
ring_z = 0.06 * visual_scale * np.sin(6 * theta + 0.3 * time_val)
ring_line = go.Scatter3d(x=ring_x, y=ring_y, z=ring_z, mode='lines', line=dict(color='rgba(255,160,60,0.42)', width=4), name='Accretion ring')

# Combine into figure
fig = go.Figure(data=[mesh, ring_line])

# camera and layout tuned for dark background
cam = dict(eye=dict(x=1.6, y=1.6, z=1.2))
fig.update_layout(scene=dict(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    zaxis=dict(visible=False),
    aspectmode='data',
    camera=cam
), margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='black', plot_bgcolor='black')

# show the Plotly figure
st.plotly_chart(fig, use_container_width=True)

# Show numeric readouts below
st.markdown("### Diagnostics (illustrative)")
colA, colB, colC = st.columns(3)
with colA:
    st.metric("Mass (M☉)", f"{mass:,.0f}")
    Rs = 2 * G * m_kg / (c ** 2)
    st.caption("Schwarzschild radius (approx.)")
    st.write(f"{Rs:.3e} m")
with colB:
    st.metric("QG Compression F_QG (toy)", f"{F_QG:.3e} N")
    st.caption("Evaluated at sample radius (visual).")
with colC:
    st.metric("dM/dt (toy QE–WH)", f"{dMdt:.3e} kg/s")
    st.caption("Heuristic / illustrative only")

st.markdown("---")
st.markdown("**Notes:** This module is **visual & exploratory**. The scalar field and marching-cubes surface are procedural approximations chosen to illustrate a crystalline/fractal-looking core and an asymmetric, time-dependent ripple. When you want, I can:")
st.write("- connect `F_{QG}` and `S_{trans}` directly to surface color/opacity", "- add field-line tubes showing inflow", "- produce an exportable mesh (OBJ/STL) for external rendering / higher-quality visualization", "- add a stepping automatic animation loop (careful: Streamlit isn't ideal for continuous real-time animation).")

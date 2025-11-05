import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import time

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Black Hole Anatomy — Quantum Singularity", layout="wide")
st.title("🪐 Black Hole Anatomy — Quantum Singularity Visualizer")

st.markdown(
    "Visualize the event horizon, photon sphere, accretion disk and animated energy flow streams."
)

# -----------------------------
# Constants
# -----------------------------
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
Msun = 1.98847e30

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("⚙️ Controls")

mass = st.sidebar.slider("Mass (Solar Masses)", 1, 10_000_000, 4_300_000, step=100_000)
r_q = st.sidebar.number_input("Quantum Radius Scale (m)", value=1e6, format="%.1e")
lambda_c = st.sidebar.slider("λ (Curvature Coupling)", 0.01, 10.0, 1.0)
live_mode = st.sidebar.checkbox("🔄 Enable Live Mode (Animated)", value=False)

show_disk = st.sidebar.checkbox("Show Accretion Disk", value=True)
show_core = st.sidebar.checkbox("Show Singularity Core", value=True)
show_sphere = st.sidebar.checkbox("Show Photon Sphere", value=True)
show_streams = st.sidebar.checkbox("Show Energy Streams", value=True)

# -----------------------------
# Derived physics
# -----------------------------
M = mass * Msun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s

def F_QG(r):
    return (G * M / r**2) * np.exp(-r / r_q)

def dM_dt(Mval):
    return - (hbar * c**2 / G) * (1 / Mval**2)

# -----------------------------
# Precompute spherical mesh (used for surfaces once)
# -----------------------------
theta, phi = np.mgrid[0:np.pi:60j, 0:2*np.pi:60j]
xs = np.sin(theta) * np.cos(phi)
ys = np.sin(theta) * np.sin(phi)
zs = np.cos(theta)

# -----------------------------
# Create the base figure (built once) as a FigureWidget where possible
# -----------------------------
fig = go.FigureWidget(layout=dict(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        bgcolor="black"
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
))

# Event horizon (static surface)
if True:
    fig.add_surface(
        x=r_s * xs, y=r_s * ys, z=r_s * zs,
        colorscale="Purples", showscale=False, opacity=0.45,
        name="Event Horizon", hoverinfo="skip"
    )

# Photon sphere (optional, static)
if show_sphere:
    fig.add_surface(
        x=r_ph * xs, y=r_ph * ys, z=r_ph * zs,
        colorscale="Plasma", showscale=False, opacity=0.16,
        name="Photon Sphere", hoverinfo="skip"
    )

# Accretion disk (precompute mesh; we add as surface once)
if show_disk:
    r_disk = np.linspace(1.5 * r_s, 4 * r_s, 200)
    phi_disk = np.linspace(0, 2 * np.pi, 200)
    R, P = np.meshgrid(r_disk, phi_disk)
    X = R * np.cos(P)
    Y = R * np.sin(P)
    Z = 0.02 * r_s * np.sin(P * 4)  # static base shape
    fig.add_surface(
        x=X, y=Y, z=Z,
        surfacecolor=np.sin(P * 8),
        colorscale="Inferno", opacity=0.72, showscale=False,
        name="Accretion Disk", hoverinfo="skip"
    )

# Singularity core (static fractal-ish surface)
if show_core:
    r_core = 0.5 * r_s * (1 + 0.08 * np.sin(10 * theta))
    Xc = r_core * xs
    Yc = r_core * ys
    Zc = r_core * zs
    fig.add_surface(
        x=Xc, y=Yc, z=Zc,
        surfacecolor=np.cos(theta * 5),
        colorscale="Purples", opacity=0.88, showscale=False,
        name="Fractal Singularity Core", hoverinfo="skip"
    )

# Energy streams: add N empty line traces (we will update their data)
stream_traces_indices = []
num_streams = 16 if show_streams else 0
for i in range(num_streams):
    # placeholder empty traces
    tr = go.Scatter3d(x=[None], y=[None], z=[None],
                      mode="lines",
                      line=dict(width=3, color=i, colorscale="Magma"),
                      opacity=0.9,
                      hoverinfo="none",
                      showlegend=False,
                      name=f"Stream{i}")
    fig.add_trace(tr)
    stream_traces_indices.append(len(fig.data)-1)

# Initial camera
camera = dict(
    eye=dict(x=2.8, y=0.0, z=0.9)
)
fig.layout.scene.camera = camera

# Display the figure once
plot_placeholder = st.empty()
plot_placeholder.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Animation loop (in-place updates)
# -----------------------------
# Use session state so multiple runs persist
if "frame" not in st.session_state:
    st.session_state.frame = 0

def update_energy_streams(t, color_shift=0.0):
    # Generates stream coordinates (in normalized physical units around BH)
    # returns a list of (x,y,z) arrays, len = num_streams
    streams = []
    for j in range(num_streams):
        p = (2 * math.pi / num_streams) * j
        r_vals = np.linspace(4 * r_s, 0.75 * r_s, 160)
        # spiral inward with a little time-dependent twist
        x_stream = r_vals * np.cos(p + 0.5 * math.sin(t*0.6 + j*0.12))
        y_stream = r_vals * np.sin(p + 0.5 * math.sin(t*0.6 + j*0.12))
        z_stream = 0.25 * r_s * np.sin(2 * np.pi * (1 - r_vals / (4 * r_s)) * 3 + t*1.2 + j*0.2)
        streams.append((x_stream, y_stream, z_stream))
    return streams

# We attempt to update the FigureWidget in-place (no re-render)
if live_mode and num_streams > 0:
    # target framerate
    fps = 20
    delay = 1.0 / fps
    # Use a short streaming loop (Streamlit will keep server responsive)
    # Limit to a number of frames to avoid runaway server usage
    max_frames = 300  # you can increase if desired
    count = 0
    try:
        while True:
            t = st.session_state.frame * 0.032
            # update camera orbit (only camera object changed)
            cam_angle = (st.session_state.frame * 2.5) % 360
            fig.layout.scene.camera.eye = dict(
                x=2.8 * math.cos(math.radians(cam_angle)),
                y=2.8 * math.sin(math.radians(cam_angle)),
                z=0.9
            )
            # update just the stream traces in-place
            streams = update_energy_streams(t)
            for idx, stream_data in enumerate(streams):
                xi, yi, zi = stream_data
                # update trace arrays — this modifies the existing FigureWidget
                trace_index = stream_traces_indices[idx]
                try:
                    fig.data[trace_index].x = xi
                    fig.data[trace_index].y = yi
                    fig.data[trace_index].z = zi
                    # set a color array to create gradient if supported
                    fig.data[trace_index].line.color = np.linspace(0.0, 1.0, len(xi))
                except Exception:
                    # In some Streamlit/Plotly envs direct assignment may raise;
                    # fall back to replacing the whole trace data object.
                    fig.data[trace_index].update(x=xi, y=yi, z=zi,
                                                 line=dict(width=3, color=np.linspace(0,1,len(xi)), colorscale="Magma"))
            # increment frame
            st.session_state.frame += 1
            count += 1
            time.sleep(delay)
            # break condition to avoid indefinite loop for Streamlit Cloud
            if count >= max_frames:
                break
    except Exception:
        # fallback: if FigureWidget in-place updates are not available,
        # gracefully degrade by re-creating a lighter figure at lower frame rate
        st.warning("Realtime in-place updates unavailable in this environment — using a lower-framerate fallback.")
        for i in range(60):
            t = st.session_state.frame * 0.06
            cam_angle = (st.session_state.frame * 3) % 360
            # recalc streams
            streams = update_energy_streams(t)
            for idx, stream_data in enumerate(streams):
                xi, yi, zi = stream_data
                trace_index = stream_traces_indices[idx]
                fig.data[trace_index].update(x=xi, y=yi, z=zi)
            fig.layout.scene.camera.eye = dict(
                x=2.8 * math.cos(math.radians(cam_angle)),
                y=2.8 * math.sin(math.radians(cam_angle)),
                z=0.9
            )
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            st.session_state.frame += 1
            time.sleep(0.12)

# If not live mode, ensure we have an initial stream drawn
if not live_mode and show_streams and num_streams > 0:
    streams = update_energy_streams(0.0)
    for idx, (xi, yi, zi) in enumerate(streams):
        trace_index = stream_traces_indices[idx]
        fig.data[trace_index].update(x=xi, y=yi, z=zi)
    plot_placeholder.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Physics readout
# -----------------------------
st.subheader("🧮 Quantum–Relativistic Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Schwarzschild Radius (m)", f"{r_s:.3e}")
    st.metric("Photon Sphere (m)", f"{r_ph:.3e}")
with col2:
    st.metric("QGC Force @ 2rₛ (N)", f"{F_QG(2 * r_s):.3e}")
    st.metric("Mass-loss rate (kg/s)", f"{dM_dt(M):.3e}")
with col3:
    st.metric("Quantum Radius", f"{r_q:.3e}")
    st.metric("λ (Curvature coupling)", f"{lambda_c:.2f}")

st.markdown(
    "Energy streams visualize plasma/spacetime flow lines. Toggle live mode to animate camera & streams."
)

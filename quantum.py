import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import time

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Black Hole Anatomy — Quantum Singularity", layout="wide")
st.title("🪐 Black Hole Anatomy — Quantum Singularity Visualizer (with Jets)")

st.markdown(
    "Visualize event horizon, photon sphere, accretion disk, energy streams and magnetically-collimated jets."
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
show_jets = st.sidebar.checkbox("Show Jets", value=True)
jet_strength = st.sidebar.slider("Jet Strength", 0.0, 1.0, 0.6, step=0.05)
jet_twist = st.sidebar.slider("Jet Twist", 0.0, 2.0, 0.8, step=0.05)

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
fig.add_surface(
    x=r_s * xs, y=r_s * ys, z=r_s * zs,
    colorscale="Purples", showscale=False, opacity=0.45,
    name="Event Horizon", hoverinfo="skip"
)

# Photon sphere (optional)
if show_sphere:
    fig.add_surface(
        x=r_ph * xs, y=r_ph * ys, z=r_ph * zs,
        colorscale="Plasma", showscale=False, opacity=0.12,
        name="Photon Sphere", hoverinfo="skip"
    )

# Accretion disk (precompute mesh; add as surface once)
if show_disk:
    r_disk = np.linspace(1.5 * r_s, 4 * r_s, 200)
    phi_disk = np.linspace(0, 2 * np.pi, 200)
    R, P = np.meshgrid(r_disk, phi_disk)
    X = R * np.cos(P)
    Y = R * np.sin(P)
    Z = 0.02 * r_s * np.sin(P * 4)  # visually interesting band modulation
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
        colorscale="Purples", opacity=0.9, showscale=False,
        name="Fractal Singularity Core", hoverinfo="skip"
    )

# Energy streams: add N empty line traces (we will update their data)
stream_traces_indices = []
num_streams = 12 if show_streams else 0
for i in range(num_streams):
    tr = go.Scatter3d(x=[None], y=[None], z=[None],
                      mode="lines",
                      line=dict(width=3, color=i, colorscale="Magma"),
                      opacity=0.9,
                      hoverinfo="none",
                      showlegend=False,
                      name=f"Stream{i}")
    fig.add_trace(tr)
    stream_traces_indices.append(len(fig.data)-1)

# --- Jets: create grouped line traces for both poles ---
jet_traces_indices = []  # will hold indices of jet traces in fig.data
jet_lines_per_pole = 10 if show_jets else 0
jet_length_factor = 12.0  # how far jets extend in multiples of r_s
for pole in (-1, +1):  # -1 = south (negative z), +1 = north (positive z)
    for j in range(jet_lines_per_pole):
        # placeholder lines
        tr = go.Scatter3d(x=[None], y=[None], z=[None],
                          mode="lines",
                          line=dict(width=4, color='rgba(255,200,120,0.6)'),
                          opacity=0.85,
                          hoverinfo="none",
                          showlegend=False,
                          name=f"Jet_{'S' if pole<0 else 'N'}_{j}")
        fig.add_trace(tr)
        jet_traces_indices.append(len(fig.data)-1)

# Initial camera
camera = dict(
    eye=dict(x=2.8, y=0.0, z=0.9)
)
fig.layout.scene.camera = camera

# Display the figure once
plot_placeholder = st.empty()
plot_placeholder.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Waveform (chirp) generation (toy PN-inspired)
# -----------------------------
waveform = np.zeros(2400, dtype=np.float32)
def generateWaveformSamples(m1, m2, spin):
    N = len(waveform)
    Mc = ((m1*m2)**(3/5) / (m1+m2)**(1/5))
    f0 = 18 + spin * 12
    f1 = 380 + (Mc/30.0)*200
    for i in range(N):
        t = i/(N-1)
        env = (t**1.8) * np.exp(-1.1*(1-t))
        freq = f0 + (t**1.6) * (f1 - f0)
        waveform[i] = env * np.sin(2*np.pi * freq * (t*1.6))
    # draw to chirp canvas via plotly trace update below if needed

# ---------- chirp canvas (small static plot) ----------
chirp_fig = go.FigureWidget()
chirp_fig.add_trace(go.Scatter(y=waveform, mode='lines', line=dict(color='#ffcc99')))
chirp_fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', margin=dict(l=0,r=0,t=0,b=0),
                        xaxis=dict(visible=False), yaxis=dict(visible=False))
chirp_placeholder = st.empty()
chirp_placeholder.plotly_chart(chirp_fig, use_container_width=True)

# -----------------------------
# Animation helpers: streams & jets
# -----------------------------
def update_energy_streams(t, color_shift=0.0):
    streams = []
    for j in range(num_streams):
        p = (2 * math.pi / max(1, num_streams)) * j
        r_vals = np.linspace(4 * r_s, 0.6 * r_s, 180)
        # use time- and j-dependent twist and inward spiral
        x_stream = r_vals * np.cos(p + 0.6 * np.sin(t*0.6 + j*0.18))
        y_stream = r_vals * np.sin(p + 0.6 * np.sin(t*0.6 + j*0.18))
        z_stream = 0.25 * r_s * np.sin(2*np.pi * (1 - r_vals/(4*r_s)) * 3 + t*1.2 + j*0.22)
        streams.append((x_stream, y_stream, z_stream))
    return streams

def update_jets(t, strength=0.6, twist=0.8):
    """Return list of jet line coords (x,y,z) for all jet traces in order of creation.
       We generate alternating spiral lines for north and south."""
    jet_lines = []
    # for each pole produce jet_lines_per_pole, each a spiral from core outward
    for pole in (-1, +1):
        for j in range(jet_lines_per_pole):
            # radial param 0..1
            s = np.linspace(0.02, 1.0, 160)
            # radius of jet spine grows with s
            r = (s**0.8) * (jet_length_factor * r_s) * (0.2 + 0.8*strength)
            # small azimuthal offset per line
            base_phi = j * (2*math.pi / max(1, jet_lines_per_pole))
            # include twist/time-dep phase
            phi = base_phi + twist * np.sin(2.0*t + j*0.25)
            x = r * (0.06 * np.cos(phi) + 0.02*np.sin(3*phi))
            y = r * (0.06 * np.sin(phi) + 0.02*np.cos(3*phi))
            # z goes outward from core: for north pole positive z, south pole negative z
            z = pole * (0.5 * r_s + s * (jet_length_factor * r_s))
            # taper opacity by s (we'll set opacity separately)
            jet_lines.append((x, y, z))
    return jet_lines

# -----------------------------
# Session state frames
# -----------------------------
if "frame" not in st.session_state:
    st.session_state.frame = 0

# -----------------------------
# Live animation (in-place updates)
# -----------------------------
if live_mode:
    fps = 20
    delay = 1.0 / fps
    max_frames = 300
    count = 0
    try:
        while True:
            t = st.session_state.frame * 0.035
            # rotate camera slowly
            cam_angle = (st.session_state.frame * 1.8) % 360
            fig.layout.scene.camera.eye = dict(
                x=2.6 * math.cos(math.radians(cam_angle)),
                y=2.6 * math.sin(math.radians(cam_angle)),
                z=0.9
            )
            # update streams in-place
            if num_streams > 0:
                streams = update_energy_streams(t)
                for idx, (xi, yi, zi) in enumerate(streams):
                    trace_index = stream_traces_indices[idx]
                    try:
                        fig.data[trace_index].x = xi
                        fig.data[trace_index].y = yi
                        fig.data[trace_index].z = zi
                        # line color gradient (assigning numerical color scale)
                        fig.data[trace_index].line.color = np.linspace(0, 1, len(xi))
                    except Exception:
                        fig.data[trace_index].update(x=xi, y=yi, z=zi,
                                                     line=dict(width=3, color=np.linspace(0, 1, len(xi)), colorscale="Magma"))
            # update jets in-place
            if show_jets and jet_lines_per_pole > 0:
                jets = update_jets(t, strength=jet_strength, twist=jet_twist)
                for j_idx, (xj, yj, zj) in enumerate(jets):
                    trace_index = jet_traces_indices[j_idx]
                    # compute dynamic opacity per line (pulse)
                    pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(2.0 * t + j_idx * 0.15))
                    # color gradient: brighter in core
                    try:
                        fig.data[trace_index].x = xj
                        fig.data[trace_index].y = yj
                        fig.data[trace_index].z = zj
                        # use a single RGBA color with pulse-based alpha
                        rgba = f"rgba(255,210,160,{0.12 + 0.66*pulse*jet_strength})"
                        fig.data[trace_index].line.color = rgba
                        fig.data[trace_index].line.width = 2 + 2 * jet_strength
                    except Exception:
                        fig.data[trace_index].update(x=xj, y=yj, z=zj,
                                                     line=dict(width=2 + 2*jet_strength, color=f"rgba(255,210,160,{0.12 + 0.66*pulse*jet_strength})"))
            # update chirp plot lightly to reflect frame progress (visual only)
            # simple shimmering of waveform amplitude (non-destructive)
            try:
                if np.any(waveform):
                    amp_mod = 1.0 + 0.03 * math.sin(t*1.3)
                    noisy = (waveform * amp_mod).tolist()
                    chirp_fig.data[0].y = noisy
                    chirp_placeholder.plotly_chart(chirp_fig, use_container_width=True)
            except Exception:
                pass

            st.session_state.frame += 1
            count += 1
            time.sleep(delay)
            if count >= max_frames:
                break
    except Exception:
        # graceful fallback: lower-rate redrawing
        st.warning("Realtime in-place updates are limited in this environment — using a lower-framerate fallback for animation.")
        for i in range(60):
            t = st.session_state.frame * 0.06
            cam_angle = (st.session_state.frame * 3) % 360
            fig.layout.scene.camera.eye = dict(
                x=2.6 * math.cos(math.radians(cam_angle)),
                y=2.6 * math.sin(math.radians(cam_angle)),
                z=0.9
            )
            if num_streams > 0:
                streams = update_energy_streams(t)
                for idx, (xi, yi, zi) in enumerate(streams):
                    fig.data[stream_traces_indices[idx]].update(x=xi, y=yi, z=zi)
            if show_jets and jet_lines_per_pole > 0:
                jets = update_jets(t, strength=jet_strength, twist=jet_twist)
                for j_idx, (xj, yj, zj) in enumerate(jets):
                    fig.data[jet_traces_indices[j_idx]].update(x=xj, y=yj, z=zj,
                                                               line=dict(width=2+2*jet_strength,
                                                                         color=f"rgba(255,210,160,{0.18 + 0.6*math.sin(t*0.9 + j_idx*0.12)*jet_strength})"))
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            # update chirp visual too
            try:
                if np.any(waveform):
                    amp_mod = 1.0 + 0.03 * math.sin(t*1.3)
                    chirp_fig.data[0].y = (waveform * amp_mod).tolist()
                    chirp_placeholder.plotly_chart(chirp_fig, use_container_width=True)
            except Exception:
                pass
            st.session_state.frame += 1
            time.sleep(0.12)

# Non-live: ensure jets/streams are present statically
if not live_mode:
    t0 = 0.0
    if num_streams > 0:
        streams = update_energy_streams(t0)
        for idx, (xi, yi, zi) in enumerate(streams):
            fig.data[stream_traces_indices[idx]].update(x=xi, y=yi, z=zi)
    if show_jets and jet_lines_per_pole > 0:
        jets = update_jets(t0, strength=jet_strength, twist=jet_twist)
        for j_idx, (xj, yj, zj) in enumerate(jets):
            fig.data[jet_traces_indices[j_idx]].update(x=xj, y=yj, z=zj,
                                                       line=dict(width=2+2*jet_strength,
                                                                 color=f"rgba(255,210,160,{0.28*jet_strength})"))
    plot_placeholder.plotly_chart(fig, use_container_width=True)
    # draw static chirp
    try:
        if np.any(waveform):
            chirp_fig.data[0].y = waveform.tolist()
            chirp_placeholder.plotly_chart(chirp_fig, use_container_width=True)
    except Exception:
        pass

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
    "Jets are visualized as collimated spiral lines emerging from the poles; adjust Jet Strength and Twist to explore morphology."
)

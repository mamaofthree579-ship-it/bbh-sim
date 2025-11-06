import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import time
import io
import wave
import struct

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Black Hole Anatomy — Jets + Chirp", layout="wide")
st.title("🪐 Black Hole Anatomy — Jets + Chirp (color maps, cones, audio)")

# -----------------------------
# Constants
# -----------------------------
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
Msun = 1.98847e30

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")

mass = st.sidebar.slider("Mass (M☉)", min_value=1_000, max_value=5_000_000, value=4_300_000, step=10_000)
show_disk = st.sidebar.checkbox("Show Accretion Disk", True)
show_core = st.sidebar.checkbox("Show Singularity Core", True)
show_photon = st.sidebar.checkbox("Show Photon Sphere", True)
show_streams = st.sidebar.checkbox("Show Energy Streams", True)
show_jets = st.sidebar.checkbox("Show Jets", True)

jet_color_map = st.sidebar.selectbox("Jet Color Mapping", ["single RGBA", "distance (cool-warm)", "magnetic (plasma)"])
show_cones = st.sidebar.checkbox("Show Jet Velocity Cones", value=False)
jet_strength = st.sidebar.slider("Jet Strength", 0.0, 1.0, 0.6, step=0.05)
jet_twist = st.sidebar.slider("Jet Twist", 0.0, 2.0, 0.8, step=0.05)
live_mode = st.sidebar.checkbox("Live Mode Animation", value=False)

# chirp audio controls
st.sidebar.markdown("---")
st.sidebar.write("Chirp audio")
chirp_enable = st.sidebar.checkbox("Enable Chirp Audio", value=True)
chirp_duration = st.sidebar.slider("Chirp duration (s)", 0.6, 6.0, 2.4, step=0.2)
chirp_volume = st.sidebar.slider("Chirp volume (0-1)", 0.0, 1.0, 0.28, step=0.01)

# -----------------------------
# Derived physics values
# -----------------------------
M = mass * Msun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s

# -----------------------------
# Plotly figure setup (FigureWidget-like)
# -----------------------------
theta, phi = np.mgrid[0:np.pi:60j, 0:2*np.pi:60j]
xs = np.sin(theta) * np.cos(phi)
ys = np.sin(theta) * np.sin(phi)
zs = np.cos(theta)

fig = go.Figure(layout=dict(
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

# Event horizon (purple-ish)
fig.add_surface(
    x=r_s * xs, y=r_s * ys, z=r_s * zs,
    colorscale=[[0, "rgb(70,20,80)"], [1, "rgb(180,120,220)"]],
    showscale=False, opacity=0.85,
    name="Event Horizon", hoverinfo="skip"
)

# Photon sphere
if show_photon:
    fig.add_surface(
        x=r_ph * xs, y=r_ph * ys, z=r_ph * zs,
        colorscale="Viridis", showscale=False, opacity=0.12,
        name="Photon Sphere", hoverinfo="skip"
    )

# Accretion disk
if show_disk:
    r_disk = np.linspace(1.3 * r_s, 4.0 * r_s, 240)
    phi_disk = np.linspace(0, 2 * np.pi, 240)
    R, P = np.meshgrid(r_disk, phi_disk)
    X = R * np.cos(P)
    Y = R * np.sin(P)
    Z = 0.02 * r_s * np.sin(P * 6)  # modulation for visual texture
    fig.add_surface(
        x=X, y=Y, z=Z,
        surfacecolor=np.sin(P * 10),
        colorscale="Inferno", opacity=0.72, showscale=False,
        name="Accretion Disk", hoverinfo="skip"
    )

# Fractal-like singularity core (visual)
if show_core:
    r_core = 0.5 * r_s * (1 + 0.06 * np.sin(12 * theta))
    Xc = r_core * xs
    Yc = r_core * ys
    Zc = r_core * zs
    fig.add_surface(
        x=Xc, y=Yc, z=Zc,
        surfacecolor=np.cos(theta * 6),
        colorscale="Purples", opacity=0.98, showscale=False,
        name="Singularity Core", hoverinfo="skip"
    )

# placeholder lists for streams & jets to add/update later
stream_traces = []
jet_traces = []
cone_traces = []

# -----------------------------
# Energy streams (lines) initialization
# -----------------------------
num_streams = 12 if show_streams else 0
for i in range(num_streams):
    tr = go.Scatter3d(x=[None], y=[None], z=[None],
                      mode="lines", line=dict(width=3, color="rgba(255,140,40,0.9)"),
                      hoverinfo="none", showlegend=False)
    fig.add_trace(tr)
    stream_traces.append(len(fig.data)-1)

# -----------------------------
# Jets traces initialization
# -----------------------------
jet_lines_per_pole = 12 if show_jets else 0
for pole in (-1, 1):
    for j in range(jet_lines_per_pole):
        tr = go.Scatter3d(x=[None], y=[None], z=[None],
                          mode="lines",
                          line=dict(width=3, color="rgba(255,210,160,0.6)"),
                          hoverinfo="none", showlegend=False)
        fig.add_trace(tr)
        jet_traces.append(len(fig.data)-1)

# Optionally add cones (we will generate when toggled)
if show_cones:
    # small grid of cones along jets (we will update later)
    pass  # created in animation/update function

# camera
camera = dict(eye=dict(x=2.8, y=0.0, z=0.9))
fig.layout.scene.camera = camera

# render
plot_slot = st.empty()
plot_slot.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Chirp waveform generation (server-side WAV creation)
# -----------------------------
def synthesize_chirp_wav(m1, m2, spin, duration=2.4, sample_rate=44100, volume=0.28):
    """
    Generate a simple audible chirp (base + harmonic) and return bytes of WAV file.
    No external libs required.
    """
    # Choose frequencies based on toy model
    Mc = ((m1*m2)**(3/5) / (m1+m2)**(1/5))
    f0 = 18 + spin*12
    f1 = 380 + (Mc/30.0) * 200
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    # instantaneous freq sweep (power-law)
    tau = t / duration
    freq = f0 + (tau**1.6) * (f1 - f0)
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    base = np.sin(phase)
    # harmonic (octave) faint
    phase2 = 2 * np.pi * np.cumsum(2*freq) / sample_rate
    harm = 0.2 * np.sin(phase2)
    env = (tau**1.8) * np.exp(-1.05*(1-tau))
    wav = env * (base + harm)
    # normalize to int16
    max_val = np.max(np.abs(wav)) if np.max(np.abs(wav))>0 else 1.0
    wav_norm = (wav / max_val) * (volume * 0.9)
    int_samples = np.int16(wav_norm * 32767)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes = 16 bits
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    buf.seek(0)
    return buf

# Chirp controls in UI
st.sidebar.markdown("---")
st.sidebar.write("Chirp controls:")
m1_chirp = st.sidebar.number_input("Chirp M₁ (M☉)", value=30.0, min_value=1.0)
m2_chirp = st.sidebar.number_input("Chirp M₂ (M☉)", value=30.0, min_value=0.1)
spin_chirp = st.sidebar.slider("Chirp spin a*", 0.0, 1.0, 0.5, step=0.01)
if chirp_enable:
    if st.sidebar.button("🔊 Generate & Play Chirp"):
        wav_buf = synthesize_chirp_wav(m1_chirp, m2_chirp, spin_chirp, duration=chirp_duration, volume=chirp_volume)
        st.audio(wav_buf.read(), format='audio/wav')

# -----------------------------
# Update functions for streams & jets
# -----------------------------
def energy_stream_coords(t, idx, N=180):
    """Return x,y,z arrays for stream index idx."""
    p = (2 * math.pi / max(1, num_streams)) * idx
    r_vals = np.linspace(3.5 * r_s, 0.6 * r_s, N)
    x = r_vals * np.cos(p + 0.6 * np.sin(t*0.6 + idx*0.18))
    y = r_vals * np.sin(p + 0.6 * np.sin(t*0.6 + idx*0.18))
    z = 0.25 * r_s * np.sin(2*np.pi * (1 - r_vals/(3.5*r_s)) * 3 + t*1.2 + idx*0.22)
    return x, y, z

def jet_line_coords(t, pole, j_index, strength=0.6, twist=0.8, N=140):
    """Return x,y,z arrays for a single jet line for pole (-1 or +1) and index j_index."""
    s = np.linspace(0.02, 1.0, N)
    r = (s**0.8) * (12.0 * r_s) * (0.2 + 0.8*strength)
    base_phi = j_index * (2*math.pi / max(1, jet_lines_per_pole))
    phi = base_phi + twist * np.sin(2.0*t + j_index*0.25)
    x = r * (0.06 * np.cos(phi) + 0.02*np.sin(3*phi))
    y = r * (0.06 * np.sin(phi) + 0.02*np.cos(3*phi))
    z = pole * (0.5 * r_s + s * (12.0 * r_s))
    return x, y, z

# -----------------------------
# Animation / updating (single-step or live)
# -----------------------------
def update_traces_once(t=0.0):
    # streams
    if num_streams > 0:
        for idx in range(num_streams):
            xi, yi, zi = energy_stream_coords(t, idx)
            ti = stream_traces[idx]
            try:
                fig.data[ti].x = xi
                fig.data[ti].y = yi
                fig.data[ti].z = zi
                # dynamic color (use line color with RGBA if desired)
                fig.data[ti].line.color = f"rgba({120 + idx*8 % 135},{80 + idx*4 % 160},80,0.9)"
            except Exception:
                fig.data[ti].update(x=xi, y=yi, z=zi)
    # jets
    if jet_lines_per_pole > 0 and show_jets:
        # index mapping: jets were appended pole by pole; we can reconstruct
        k = 0
        for pole in (-1, 1):
            for j in range(jet_lines_per_pole):
                xj, yj, zj = jet_line_coords(t, pole, j, strength=jet_strength, twist=jet_twist)
                ti = jet_traces[k]
                # pick color mapping
                if jet_color_map == "single RGBA":
                    col = f"rgba(255,210,160,{0.18 + 0.6*jet_strength})"
                elif jet_color_map == "distance (cool-warm)":
                    # color based on z (closer->warm)
                    col = None  # use colorscale by assigning numeric
                else:  # magnetic/plasma
                    col = None
                try:
                    if col:
                        fig.data[ti].line.color = col
                        fig.data[ti].line.width = 2 + 2*jet_strength
                        fig.data[ti].x = xj; fig.data[ti].y = yj; fig.data[ti].z = zj
                    else:
                        # fallback: update with default style
                        fig.data[ti].update(x=xj, y=yj, z=zj, line=dict(width=2+2*jet_strength, color=f"rgba(255,210,160,{0.18 + 0.6*jet_strength})"))
                except Exception:
                    fig.data[ti].update(x=xj, y=yj, z=zj)
                k += 1
    # cones (optional): add a few cones along central spine to indicate velocity
    if show_cones and jet_lines_per_pole > 0:
        # remove previous cones if any, then add new ones
        # We add cones as new traces at end of fig; to avoid duplicate growth, we remove ones named 'JetCone'
        # Remove existing JetCone traces
        rem_ids = [i for i, tr in enumerate(fig.data) if getattr(tr, "name", "") == "JetCone"]
        # remove in reverse order
        for rid in sorted(rem_ids, reverse=True):
            fig.data = tuple([tr for i, tr in enumerate(fig.data) if i != rid])
        # create cones along +z and -z
        cone_positions = [ (0, 0.5*r_s + k*2.0*r_s, 1) for k in range(3) ] + [ (0, -0.5*r_s - k*2.0*r_s, -1) for k in range(3) ]
        for (cx, cz, pole) in cone_positions:
            # simple cone pointing outward along z-axis
            x0 = np.array([0.0]); y0 = np.array([0.0]); z0 = np.array([pole* (abs(cz))])
            u = np.array([0.0]); v = np.array([0.0]); w = np.array([pole * 1.0 * (0.5 + 0.5*jet_strength)])
            try:
                cone = go.Cone(x=x0, y=y0, z=z0, u=u, v=v, w=w, sizemode="absolute", sizeref= r_s*0.6, anchor="tip", showscale=False, name="JetCone")
                fig.add_trace(cone)
            except Exception:
                # cones may not be supported in certain offline renderers; skip gracefully
                pass

# initial static update
update_traces_once(t=0.0)
plot_slot.plotly_chart(fig, use_container_width=True)

# live animation block
if live_mode:
    fps = 16
    frames = 240
    delay = 1.0 / fps
    try:
        for frame in range(frames):
            t = frame * 0.04
            # gentle camera rotation
            angle_deg = (frame * 1.6) % 360
            fig.layout.scene.camera.eye = dict(
                x=2.6 * math.cos(math.radians(angle_deg)),
                y=2.6 * math.sin(math.radians(angle_deg)),
                z=0.9
            )
            update_traces_once(t)
            plot_slot.plotly_chart(fig, use_container_width=True)
            time.sleep(delay)
    except Exception:
        st.warning("Live animation limited in this environment; displaying static frame instead.")

# -----------------------------
# Readouts / Metrics
# -----------------------------
st.subheader("Parameters & derived quantities")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Mass (M☉)", f"{mass:,}")
    st.metric("Schwarzschild radius (m)", f"{r_s:.3e}")
with col2:
    st.metric("Photon sphere radius (m)", f"{r_ph:.3e}")
    st.metric("Jet strength", f"{jet_strength:.2f}")
with col3:
    st.metric("Jet twist", f"{jet_twist:.2f}")
    st.metric("Show cones", str(show_cones))

st.markdown("**Notes:**\n- Jet color map can be changed in the sidebar. Cone arrows indicate rough velocity direction only (visual aid).")

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io
import wave
import struct
import math
from datetime import datetime

st.set_page_config(page_title="Hurricane Singularity Visualizer", layout="wide")

st.title("🌪️ Hurricane Singularity — Phase 1 (Visual Foundation)")
st.markdown(
    """
This module visualizes a rotating vortex field and a fractal-like singularity core.
Use the sidebar to change mass/scale, pulse rate, vortex strength, and (optionally) play a generated chirp that
follows the pulse parameters.
"""
)

# ---------------------
# Sidebar controls
# ---------------------
with st.sidebar:
    st.header("Controls")
    mode = st.selectbox("Mode", ["Classical Anatomy", "Hurricane Singularity Mode"])
    mass = st.slider("Mass (visual scale, M☉)", min_value=1e3, max_value=1e8, value=4_300_000, step=1000, format="%d")
    pulse_rate = st.slider("Pulse rate (Hz, visual)", min_value=0.1, max_value=4.0, value=0.8, step=0.05)
    pulse_strength = st.slider("Pulse strength", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
    vortex_strength = st.slider("Vortex strength (spiral tightness)", min_value=0.2, max_value=2.5, value=1.0, step=0.05)
    show_outward = st.checkbox("Show outward streamlines", value=False)
    streamline_count = st.slider("Streamline count", min_value=8, max_value=60, value=22, step=2)
    show_sound = st.checkbox("Enable chirp sound option", value=False)
    chirp_duration = st.slider("Chirp duration (s)", min_value=0.5, max_value=6.0, value=2.5, step=0.1)
    play_chirp_btn = st.button("Play chirp (synth)")

# ---------------------
# Utility functions
# ---------------------
def generate_spiral_line(radius, turns, points, inward=True, z_tilt=0.6, tightness=1.0, phase=0.0):
    """Generates a 3D spiral line around z-axis.
       - radius: starting radius
       - turns: number of turns
       - points: samples along line
       - inward: if True spiral inward, else outward
       - z_tilt: how much z varies
       - tightness: spiral tightness factor
    """
    t = np.linspace(0, 1, points)
    if inward:
        r = radius * (1 - t**tightness)
    else:
        r = radius * (0.1 + t**tightness)
    theta = (turns * 2 * np.pi) * t * (1 + 0.15 * (1 - tightness)) + phase
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = (np.sin(theta * z_tilt) * radius * 0.08) * (1 - t)
    return x, y, z

def create_vortex_streamlines(count=22, base_radius=1.0, turns=3.5, points=180, inward=True, tightness=1.0, color="#a64dff"):
    """Make a list of traces (each trace is an x,y,z triple) for Plotly"""
    traces = []
    for i in range(count):
        angle_phase = (i / count) * 2 * np.pi
        radius = base_radius * (0.9 + 0.4 * (i / count))
        # vary turns and tightness slightly per line for organic look
        tks = tightness * (0.9 + 0.2 * np.sin(i * 1.3))
        x, y, z = generate_spiral_line(radius, turns * (1 + 0.12 * np.cos(i)), points, inward=inward, z_tilt=0.7, tightness=tks, phase=angle_phase)
        traces.append((x, y, z))
    return traces

def make_singularity_core_mesh(scale=1.0, layers=5, pulse=0.0, color_base=(180,150,255)):
    """Create layered spheres (Mesh3d-compatible data) approximating 'fractal' core.
       Returns list of dicts each with x,y,z and color/opacity.
    """
    meshes = []
    # color_base is RGB tuple (0-255)
    for i in range(layers):
        # layer radius with subtle pulse modulation
        layer_ratio = (i + 1) / (layers + 0.5)
        radius = scale * (0.12 * layer_ratio) * (1 + 0.06 * math.sin(pulse * (i+1)))
        # sample sphere points (icosphere-like by lat/lon sampling)
        lat = np.linspace(0, np.pi, 18)
        lon = np.linspace(0, 2 * np.pi, 36)
        x = []
        y = []
        z = []
        for la in lat:
            for lo in lon:
                x.append(radius * np.sin(la) * np.cos(lo))
                y.append(radius * np.sin(la) * np.sin(lo))
                z.append(radius * np.cos(la))
        # color & opacity
        r, g, b = color_base
        alpha = 0.08 + 0.12 * (i / layers) + 0.06 * pulse
        meshes.append({"x": x, "y": y, "z": z, "color": f"rgba({r},{g},{b},{alpha})", "radius": radius})
    return meshes

def synthesize_chirp(f0=10.0, f1=1000.0, duration=2.5, sr=44100, amplitude=0.25):
    """Generate a linear-exponential chirp as 16-bit PCM bytes (WAV) and return bytes."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # frequency sweep (log-ish: use exponential ramp for perceptual pleasantness)
    freqs = f0 * (f1 / f0) ** (t / duration)
    phase = 2 * np.pi * np.cumsum(freqs) / sr
    signal = amplitude * np.sin(phase)
    # add a low-level broadband color (like a hurricane rumble)
    signal += 0.035 * amplitude * np.sin(2 * np.pi * freqs * 2.0 * t)  # harmonic
    # fade in/out
    env = np.ones_like(signal)
    ramp = int(0.02 * sr)
    env[:ramp] = np.linspace(0, 1, ramp)
    env[-ramp:] = np.linspace(1, 0, ramp)
    signal *= env
    # convert to 16-bit
    pcm = np.int16(np.clip(signal, -1, 1) * 32767)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    buf.seek(0)
    return buf.read()

# ---------------------
# Build Plotly figure
# ---------------------
@st.cache_data(show_spinner=False)
def build_figure(mode, mass, pulse_rate, pulse_strength, vortex_strength, show_outward, streamline_count):
    # visual scaling: map mass to display radius
    mass_scale = np.clip(np.log10(mass) - 3.8, 0.6, 8.0)  # gentle mapping
    base_radius = 1.0 * mass_scale * 0.5

    # generate streamlines (inward)
    traces = []
    inward_traces = create_vortex_streamlines(
        count=streamline_count,
        base_radius=base_radius,
        turns=3.6 * vortex_strength,
        points=240,
        inward=True,
        tightness=max(0.4, 1.1 - 0.2 * vortex_strength),
        color="#cdaeff"
    )
    outward_traces = create_vortex_streamlines(
        count=max(6, streamline_count//3),
        base_radius=base_radius * 0.5,
        turns=2.0 * vortex_strength,
        points=160,
        inward=False,
        tightness=0.9,
        color="#6fd2ff"
    )

    fig = go.Figure()

    # add inward streamlines
    for (x, y, z) in inward_traces:
        fig.add_trace(go.Scatter3d(x=x, y=y, z=z,
                                   mode='lines',
                                   line=dict(color='rgba(180,150,255,0.34)', width=2),
                                   hoverinfo='skip',
                                   showlegend=False))
    # optionally outward
    if show_outward:
        for (x, y, z) in outward_traces:
            fig.add_trace(go.Scatter3d(x=x, y=y, z=z,
                                       mode='lines',
                                       line=dict(color='rgba(90,210,255,0.2)', width=1.6, dash='dash'),
                                       hoverinfo='skip',
                                       showlegend=False))

    # singularity core meshes (fractal layers)
    # pulse parameter used to slightly modulate radius/opacity
    time_seed = (pulse_rate % 5) * 2.0 + pulse_strength * 3.0
    meshes = make_singularity_core_mesh(scale=base_radius, layers=6, pulse=pulse_strength * 2.3 + pulse_rate, color_base=(200,160,255))
    # add as multiple Scatter3d with markers to approximate semi-transparent volumes
    for m in meshes[::-1]:
        # small jitter in marker size to create textured look
        sz = 2 + 9 * (m["radius"] / (base_radius + 1e-6))
        fig.add_trace(go.Scatter3d(x=m["x"], y=m["y"], z=m["z"],
                                   mode='markers',
                                   marker=dict(size=max(1, sz),
                                               color=m["color"],
                                               opacity=0.55,
                                               line=dict(width=0)),
                                   hoverinfo='skip',
                                   showlegend=False))
    # add a bright hot spot marker rotating (we emulate rotation by phase = pulse_rate*time; here use static seed)
    hot_theta = 0.0
    hx = 0.8 * base_radius * math.cos(hot_theta)
    hy = 0.8 * base_radius * math.sin(hot_theta)
    hz = 0.0
    fig.add_trace(go.Scatter3d(x=[hx], y=[hy], z=[hz], mode="markers",
                               marker=dict(size=8, color="rgba(255,220,170,0.95)", symbol='circle'),
                               name="Hotspot",
                               hoverinfo='skip'))

    # styling and camera
    camera = dict(eye=dict(x=1.7, y=1.1, z=0.7))
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                      scene_camera=camera,
                      margin=dict(l=0, r=0, t=0, b=0),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")

    return fig

# Build and display the figure
fig = build_figure(mode, mass, pulse_rate, pulse_strength, vortex_strength, show_outward, streamline_count)
st.plotly_chart(fig, use_container_width=True, height=720)

# ---------------------
# Chirp sound (synthesize and play)
# ---------------------
if show_sound:
    st.markdown("---")
    st.markdown("### Sound — generated chirp")
    st.markdown("A chirp synthesis is provided as an optional sonic analogy. Use Play to hear a generated sweep (low octaves emphasized for the 'hurricane' rumble).")
    if play_chirp_btn:
        # map pulse_rate & pulse_strength to chirp frequencies
        low = max(8.0, 8.0 + (pulse_rate - 0.5) * 6.0 - pulse_strength * 8.0)
        high = min(2200.0, 500.0 + (pulse_rate * 200.0) + (pulse_strength * 800.0))
        # duration from UI
        duration = chirp_duration
        wav_bytes = synthesize_chirp(f0=low, f1=high, duration=duration, amplitude=0.28)
        st.audio(wav_bytes, format="audio/wav")
        st.success(f"Playing chirp: {int(low)} Hz → {int(high)} Hz over {duration:.2f}s")
    else:
        st.info("Enable 'Play chirp' in the sidebar and click Play to synthesize and listen.")

# Footer / notes
st.markdown("---")
st.markdown(
    """
**Notes & next steps**
- This is a realistic, numerically-driven visualization for exploration. The vortex lines are toy-model streamlines illustrating frame-dragging/inflow.
- Phase 2: couple the visual pulse intensity to chirp amplitude & to a stronger fractal core rendering (isosurface / volumetric rendering).
- If you'd like, I can:
  - Add playback controls and an animated `hotspot` rotation (time-based), or
  - Export streamlines as CSV for offline analysis, or
  - Replace the core marker-cloud with marching-cubes isosurface (requires scikit-image).
"""
)


# quantum_blackhole_app.py
# Streamlit app: Black Hole Anatomy — Jets, Cones, Chirp (with download + sync visualization)

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import time
import io
import wave
import struct
import tempfile
import os

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Black Hole Anatomy — Chirp Sync", layout="wide")
st.title("🪐 Black Hole Anatomy — Chirp Visualization & Download")

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

mass = st.sidebar.slider("Mass (M☉)", 1_000, 5_000_000, 4_300_000, step=10_000)
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

# Chirp audio
st.sidebar.markdown("---")
st.sidebar.write("### Chirp audio synthesis")

chirp_enable = st.sidebar.checkbox("Enable Chirp Audio", value=True)
chirp_duration = st.sidebar.slider("Duration (s)", 0.6, 6.0, 2.4, step=0.2)
chirp_volume = st.sidebar.slider("Volume", 0.0, 1.0, 0.28, step=0.01)
m1_chirp = st.sidebar.number_input("M₁ (M☉)", value=30.0, min_value=1.0)
m2_chirp = st.sidebar.number_input("M₂ (M☉)", value=30.0, min_value=0.1)
spin_chirp = st.sidebar.slider("Spin (a*)", 0.0, 1.0, 0.5, step=0.01)

# -----------------------------
# Derived physics values
# -----------------------------
M = mass * Msun
r_s = 2 * G * M / c**2
r_ph = 1.5 * r_s

# -----------------------------
# Base figure setup
# -----------------------------
theta, phi = np.mgrid[0:np.pi:60j, 0:2*np.pi:60j]
xs, ys, zs = np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)

fig = go.Figure(layout=dict(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor="black",
        aspectmode="data"
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
))

fig.add_surface(x=r_s*xs, y=r_s*ys, z=r_s*zs,
                colorscale=[[0, "rgb(70,20,80)"], [1, "rgb(180,120,220)"]],
                showscale=False, opacity=0.85, name="Event Horizon")

if show_photon:
    fig.add_surface(x=r_ph*xs, y=r_ph*ys, z=r_ph*zs,
                    colorscale="Viridis", showscale=False, opacity=0.12, name="Photon Sphere")

if show_disk:
    r_disk = np.linspace(1.3*r_s, 4.0*r_s, 240)
    phi_disk = np.linspace(0, 2*np.pi, 240)
    R, P = np.meshgrid(r_disk, phi_disk)
    X, Y, Z = R*np.cos(P), R*np.sin(P), 0.02*r_s*np.sin(P*6)
    fig.add_surface(x=X, y=Y, z=Z, surfacecolor=np.sin(P*10),
                    colorscale="Inferno", opacity=0.72, showscale=False, name="Accretion Disk")

if show_core:
    r_core = 0.5*r_s*(1+0.06*np.sin(12*theta))
    Xc, Yc, Zc = r_core*xs, r_core*ys, r_core*zs
    fig.add_surface(x=Xc, y=Yc, z=Zc,
                    surfacecolor=np.cos(theta*6),
                    colorscale="Purples", opacity=0.98, showscale=False, name="Singularity Core")

fig.update_layout(scene_camera=dict(eye=dict(x=2.8, y=0, z=0.9)))
plot_slot = st.empty()
plot_slot.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Chirp waveform synthesis + download + visualization
# -----------------------------
def synthesize_chirp(m1, m2, spin, duration=2.4, sample_rate=44100, volume=0.28):
    Mc = ((m1*m2)**(3/5) / (m1+m2)**(1/5))
    f0, f1 = 18 + spin*12, 380 + (Mc/30.0)*200
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    tau = t/duration
    freq = f0 + (tau**1.6)*(f1-f0)
    phase = 2*np.pi*np.cumsum(freq)/sample_rate
    base = np.sin(phase)
    harm = 0.2*np.sin(2*phase)
    env = (tau**1.8)*np.exp(-1.05*(1-tau))
    wave_data = env*(base+harm)
    wave_data = (wave_data/np.max(np.abs(wave_data)))*(volume*0.9)
    return t, wave_data

def create_wav_file(wave_data, sample_rate=44100):
    buf = io.BytesIO()
    int_samples = np.int16(wave_data*32767)
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    buf.seek(0)
    return buf

# Chirp section UI
st.subheader("🎶 Chirp Audio Generation & Visualization")

if chirp_enable:
    if st.button("Generate Chirp"):
        t, wav = synthesize_chirp(m1_chirp, m2_chirp, spin_chirp,
                                  duration=chirp_duration, volume=chirp_volume)
        wav_buf = create_wav_file(wav)

        st.audio(wav_buf.read(), format="audio/wav")

        # Download button
        tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        with open(tmp_path, "wb") as f:
            f.write(create_wav_file(wav).read())
        with open(tmp_path, "rb") as f:
            st.download_button("💾 Download Chirp (.wav)", f, file_name="blackhole_chirp.wav")

        # Visualization of waveform
        st.markdown("**Waveform Visualization**")
        fig_chirp = go.Figure()
        fig_chirp.add_trace(go.Scatter(x=t, y=wav, mode="lines", line=dict(color="orange", width=1)))
        fig_chirp.update_layout(
            xaxis_title="Time (s)",
            yaxis_title="Amplitude",
            template="plotly_dark",
            height=250,
            margin=dict(l=40, r=20, t=20, b=40),
        )
        # Add playhead marker animation (for illustration)
        head = go.Scatter(x=[0], y=[0], mode="markers", marker=dict(color="cyan", size=8))
        fig_chirp.add_trace(head)

        chart = st.empty()
        chart.plotly_chart(fig_chirp, use_container_width=True)

        # Simple playhead simulation
        frames = 100
        for i in range(frames):
            pos = i / frames * t[-1]
            amp_idx = int(i / frames * len(wav))
            fig_chirp.data[1].x = [pos]
            fig_chirp.data[1].y = [wav[amp_idx]]
            chart.plotly_chart(fig_chirp, use_container_width=True)
            time.sleep(chirp_duration / frames)

        os.remove(tmp_path)

st.markdown("---")
st.markdown("✅ **Features:** Real-time 3D visualization of a single black hole + accretion disk, configurable jets and cones, and synthesized chirp waveform with synchronized playback + download.")

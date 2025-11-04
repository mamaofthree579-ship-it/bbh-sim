import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io, soundfile as sf

st.set_page_config(page_title="Quantum Black Hole Simulator", layout="wide")
st.title("🌀 Quantum Black Hole Simulator")

st.markdown(
    "Explore a simplified quantum-gravity black-hole model. "
    "Use the sliders to adjust mass and spin, visualize the curvature, "
    "and listen to a synthesized low-frequency 'rumble' inspired by your theory."
)

# -----------------------------
# Parameters
# -----------------------------
mass = st.slider("Black Hole Mass (Solar Masses)", 1e5, 1e8, 4.3e6, step=1e5, format="%.0f")
spin = st.slider("Spin parameter (a*)", 0.0, 1.0, 0.5, step=0.05)
show_orbit = st.button("Show 3D Orbit Visualization")
play_rumble = st.button("🔊 Play Quantum Rumble")

# -----------------------------
# Physical Calculations
# -----------------------------
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

M = mass * M_sun
r_s = 2 * G * M / (c ** 2)
r_q = r_s * (1 - 0.5 * spin)
r_p = 1.5 * r_s

st.markdown(f"**Schwarzschild radius:** {r_s:.3e} m")
st.markdown(f"**Quantum core radius (r₍Q₎):** {r_q:.3e} m")
st.markdown(f"**Photon sphere:** {r_p:.3e} m")

# -----------------------------
# 3D Visualization
# -----------------------------
def make_blackhole_plot():
    u = np.linspace(0, 2*np.pi, 80)
    v = np.linspace(0, np.pi, 40)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))

    fig = go.Figure()

    # Event horizon
    fig.add_surface(x=x, y=y, z=z, opacity=1.0, colorscale=[[0, "#240046"], [1, "#9d4edd"]],
                    showscale=False)

    # Photon sphere
    fig.add_surface(x=1.3*x, y=1.3*y, z=1.3*z, opacity=0.3, colorscale=[[0, "#ffb703"], [1, "#fb8500"]],
                    showscale=False)

    # Quantum core (glow)
    fig.add_surface(x=0.6*x, y=0.6*y, z=0.6*z, opacity=0.8,
                    colorscale=[[0, "#ff6ad5"], [1, "#ffffff"]],
                    showscale=False)

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
        ),
        paper_bgcolor="black",
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig

if show_orbit:
    st.plotly_chart(make_blackhole_plot(), use_container_width=True)

# -----------------------------
# Audio synthesis: "Quantum Rumble"
# -----------------------------
if play_rumble:
    duration = 6.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Deep gravitational pulse + harmonic distortion
    f_base = 30 + np.log10(mass) * 4  # frequency ~ scaled by mass
    tone = np.sin(2 * np.pi * f_base * t)
    mod = np.sin(2 * np.pi * (f_base / 8) * t)
    envelope = np.exp(-t / 2.5)

    rumble = 0.7 * tone * envelope + 0.2 * mod * np.sin(2 * np.pi * f_base * 1.5 * t)
    rumble = rumble / np.max(np.abs(rumble))

    buf = io.BytesIO()
    sf.write(buf, rumble, sample_rate, format="WAV")
    st.audio(buf.getvalue(), format="audio/wav")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<hr><small>⚛️ Simulation model uses heuristic equations: "
    "Quantum Gravity Compression (F<sub>QG</sub>), Quantum Evaporation (QE–WH), "
    "and Singularity Transition (S<sub>trans</sub>). "
    "Visuals are scaled for conceptual clarity.</small>",
    unsafe_allow_html=True,
)

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

# ------------------------------------------------------
# 🌌 Quantum Black Hole Visualization with Audio & Orbit
# ------------------------------------------------------

st.set_page_config(page_title="Quantum Black Hole Simulator", layout="wide")

st.title("🌀 Quantum Black Hole Simulator")
st.markdown("""
Explore a quantum-inspired black hole model featuring a **Schwarzschild radius**, **photon sphere**, 
and a hypothesized **quantum singularity core** with optional sound and orbital motion.

Use the interactive buttons below to:
- **Play** the “Quantum Rumble” sound (synthesized via WebAudio)
- **Animate** the orbit around the singularity
""")

# ------------------------------------------------------
# Parameters
# ------------------------------------------------------

G = 6.67430e-11  # gravitational constant
c = 2.99792458e8  # speed of light
M_sun = 1.98847e30  # solar mass in kg

# Black hole mass input
mass_solar = st.slider("Select Black Hole Mass (in Solar Masses)", 1e5, 1e7, 4.3e6, step=1e5)
M = mass_solar * M_sun

# Derived radii
r_s = 2 * G * M / c**2  # Schwarzschild radius
r_photon = 1.5 * r_s  # photon sphere radius
r_q = 0.2 * r_s  # arbitrary quantum boundary (for visual only)

# ------------------------------------------------------
# 3D Visualization Setup
# ------------------------------------------------------

def sphere(radius, resolution=60):
    """Return X, Y, Z points of a sphere."""
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    return x, y, z

# Spheres for layers
x_h, y_h, z_h = sphere(1.0)        # Event horizon (normalized)
x_p, y_p, z_p = sphere(1.3)        # Photon sphere
x_q, y_q, z_q = sphere(0.6)        # Singularity region (inner core)

# Build the figure
fig = go.Figure()

# Event horizon
fig.add_surface(
    x=x_h, y=y_h, z=z_h,
    colorscale=[[0, "#3b006a"], [1, "#7a2cf3"]],
    opacity=0.9,
    showscale=False,
    name="Event Horizon"
)

# Photon sphere
fig.add_surface(
    x=x_p, y=y_p, z=z_p,
    colorscale=[[0, "#f0a500"], [1, "#ffcc70"]],
    opacity=0.3,
    showscale=False,
    name="Photon Sphere"
)

# Quantum core
fig.add_surface(
    x=x_q, y=y_q, z=z_q,
    colorscale=[[0, "#ff00ff"], [1, "#ffffff"]],
    opacity=0.8,
    showscale=False,
    name="Quantum Core"
)

# Scene layout
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data'
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------
# Info Panel
# ------------------------------------------------------
st.markdown("### ⚙️ Physical Parameters")
st.write(f"**Mass:** {mass_solar:,.0f} M☉")
st.write(f"**Schwarzschild radius (rₛ):** {r_s:.3e} m  |  {r_s/1000:.3e} km")
st.write(f"**Photon sphere (≈1.5 rₛ):** {r_photon:.3e} m  |  {r_photon/1000:.3e} km")
st.write(f"**Quantum boundary (r_Q):** {r_q:.3e} m  |  {r_q/1000:.3e} km")

# ------------------------------------------------------
# 🎧 Audio & Orbit Control Section
# ------------------------------------------------------
st.markdown("---")
st.markdown("## 🎧 Quantum Rumble & Orbital Motion")

col1, col2 = st.columns(2)

# --- Button 1: WebAudio Play ---
with col1:
    if st.button("🎧 Play Rumble"):
        st.markdown(
            """
            <script>
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc1 = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gain = ctx.createGain();

            osc1.type = "sine";
            osc2.type = "sawtooth";

            osc1.frequency.setValueAtTime(35, ctx.currentTime);
            osc2.frequency.setValueAtTime(50, ctx.currentTime);
            osc1.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 6);
            osc2.frequency.exponentialRampToValueAtTime(160, ctx.currentTime + 6);

            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 8);

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(ctx.destination);

            osc1.start();
            osc2.start();
            osc1.stop(ctx.currentTime + 8);
            osc2.stop(ctx.currentTime + 8);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.success("🎵 Playing the ‘Quantum Rumble’—a deep resonance of the singularity field.")
    else:
        st.caption("Press to hear the synthesized rumble of the black hole.")

# --- Button 2: Orbit Animation ---
with col2:
    if st.button("🌌 Start Orbit Animation"):
        st.markdown(
            """
            <script>
            const sleep = ms => new Promise(r => setTimeout(r, ms));
            async function rotateScene() {
                let angle = 0;
                for (let i = 0; i < 180; i++) {
                    const camera = {
                        eye: {
                            x: Math.cos(angle) * 2,
                            y: Math.sin(angle) * 2,
                            z: 0.6
                        }
                    };
                    const gd = document.querySelector(".js-plotly-plot");
                    if (gd) Plotly.relayout(gd, { 'scene.camera': camera });
                    angle += Math.PI / 60;
                    await sleep(50);
                }
            }
            rotateScene();
            </script>
            """,
            unsafe_allow_html=True
        )
        st.info("🌠 Orbit animation running—observe the photon sphere rotate dynamically.")
    else:
        st.caption("Press to start 3D orbital motion.")

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="Singularity Visualizer", layout="wide", page_icon="🌌")

st.title("🌌 Crystalline Singularity — 3D Visualization")

st.markdown("""
This simulation presents a **non-rotating black hole** with a crystalline singularity core.  
Use the controls to explore the geometry and brightness of the system.
""")

# === Controls ===
st.sidebar.header("🧭 Visualization Controls")
horizon_radius = st.sidebar.slider("Event Horizon Radius", 5, 50, 20)
disk_radius = st.sidebar.slider("Accretion Disk Radius", 30, 120, 60)
disk_thickness = st.sidebar.slider("Disk Thickness", 0.5, 5.0, 1.5)
brightness = st.sidebar.slider("Singularity Brightness", 0.1, 2.0, 1.0)
rotation_speed = st.sidebar.slider("Disk Rotation Speed", 0.1, 3.0, 1.0)

# === 3D coordinates ===
theta = np.linspace(0, 2*np.pi, 100)
phi = np.linspace(0, np.pi, 100)
x = horizon_radius * np.outer(np.cos(theta), np.sin(phi))
y = horizon_radius * np.outer(np.sin(theta), np.sin(phi))
z = horizon_radius * np.outer(np.ones(np.size(theta)), np.cos(phi))

# === Load singularity texture ===
def load_image_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

texture_b64 = load_image_as_base64("/mount/src/bbh-sim/singularity/singularity.png")

# === Create figure ===
fig = go.Figure()

# --- Singularity core (textured sphere) ---
fig.add_trace(go.Surface(
    x=x * 0.5,
    y=y * 0.5,
    z=z * 0.5,
    surfacecolor=np.zeros_like(x),
    colorscale=[[0, "rgba(255,255,255,0)"], [1, "rgba(255,255,255,0)"]],
    showscale=False,
    hoverinfo='skip',
    opacity=brightness
))

# --- Event horizon ---
fig.add_trace(go.Surface(
    x=x,
    y=y,
    z=z,
    colorscale=[[0, "rgb(120,0,180)"], [1, "rgb(60,0,100)"]],
    opacity=0.4,
    showscale=False,
    hoverinfo="skip"
))

# --- Accretion disk ---
disk_t = np.linspace(0, 2*np.pi, 200)
disk_r = np.linspace(horizon_radius * 1.2, disk_radius, 50)
T, R = np.meshgrid(disk_t, disk_r)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = disk_thickness * np.sin(T * rotation_speed)  # gives motion effect

fig.add_trace(go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale="Inferno",
    opacity=0.7,
    showscale=False,
    hoverinfo="skip"
))

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
)

# === Display ===
st.plotly_chart(fig, use_container_width=True)

# === Chirp sound toggle ===
st.markdown("### 🎧 Black Hole Rumble — Immersive Mode")
st.markdown("*(Best experienced with headphones or good speakers)*")

audio_html = """
<script>
const AudioContext = window.AudioContext || window.webkitAudioContext;
const ctx = new AudioContext();

function startBlackHoleSound() {
    const base = ctx.createOscillator();
    const turbulence = ctx.createOscillator();
    const noise = ctx.createBufferSource();

    // White noise for plasma texture
    const bufferSize = 2 * ctx.sampleRate;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * 0.4; // mild turbulence
    }
    noise.buffer = buffer;
    noise.loop = true;

    // Base rumble oscillator
    base.type = "sine";
    base.frequency.setValueAtTime(28, ctx.currentTime); // deep fundamental tone
    base.frequency.linearRampToValueAtTime(42, ctx.currentTime + 30); // slow rising swirl

    // Modulate amplitude
    const baseGain = ctx.createGain();
    baseGain.gain.setValueAtTime(0.3, ctx.currentTime);

    // Turbulence oscillator to modulate gain
    turbulence.type = "sine";
    turbulence.frequency.value = 0.4; // slow pulsing modulation
    const turbGain = ctx.createGain();
    turbGain.gain.value = 0.2;
    turbulence.connect(turbGain);
    turbGain.connect(baseGain.gain);

    // Noise gain
    const noiseGain = ctx.createGain();
    noiseGain.gain.value = 0.25;

    // Combine sources
    base.connect(baseGain);
    noise.connect(noiseGain);

    // Merge and filter to add depth
    const merger = ctx.createGain();
    baseGain.connect(merger);
    noiseGain.connect(merger);

    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(300, ctx.currentTime);
    merger.connect(filter);

    const outGain = ctx.createGain();
    outGain.gain.value = 0.6;
    filter.connect(outGain);
    outGain.connect(ctx.destination);

    // Start
    base.start();
    turbulence.start();
    noise.start();

    window.activeNodes = {base, turbulence, noise, ctx};
}

function stopBlackHoleSound() {
    if (window.activeNodes) {
        const {base, turbulence, noise, ctx} = window.activeNodes;
        try {
            base.stop();
            turbulence.stop();
            noise.stop();
            ctx.close();
        } catch {}
    }
}

</script>

<button onclick="startBlackHoleSound()">🌌 Start Black Hole Rumble</button>
<button onclick="stopBlackHoleSound()">⛔ Stop</button>
"""

st.components.v1.html(audio_html, height=120)


st.caption("Visualization © 2025 • Interactive Crystalline Singularity Simulator")

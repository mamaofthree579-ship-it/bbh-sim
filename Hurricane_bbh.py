import streamlit as st
import numpy as np
import plotly.graph_objects as go
import soundfile as sf
import io
import base64
import time

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Black Hole Control Panel 🌌")

mass_scale = st.sidebar.slider(
    "Mass (visual scale, affects low-band)",
    min_value=1000,
    max_value=100_000_000,
    value=4_300_000,
    step=1000,
    format="%d"
)

rotation_speed = st.sidebar.slider(
    "Rotation Speed (a*)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.01
)

st.sidebar.markdown("---")
st.sidebar.subheader("Audio Controls")
sound_intensity = st.sidebar.slider("Sound Intensity", 0.1, 2.0, 1.0, step=0.1)
play_sound = st.sidebar.button("🔊 Play Black Hole Sound")

st.sidebar.markdown("---")
st.sidebar.subheader("Simulation")
animate = st.sidebar.button("▶️ Live Motion")

# --- 3D GEOMETRY FOR BLACK HOLE ---
theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 100)
r_event = 1.0
x = r_event * np.outer(np.cos(theta), np.sin(phi))
y = r_event * np.outer(np.sin(theta), np.sin(phi))
z = r_event * np.outer(np.ones(np.size(theta)), np.cos(phi))

# --- ACCRETION DISK ---
r_disk = np.linspace(1.2, 2.5, 80)
theta_disk = np.linspace(0, 2 * np.pi, 180)
rd, td = np.meshgrid(r_disk, theta_disk)
x_disk = rd * np.cos(td)
y_disk = rd * np.sin(td)
z_disk = 0.1 * np.sin(3 * td)

# --- FRACTAL CORE (SINGULARITY) ---
r_core = 0.3
theta_core = np.linspace(0, 2 * np.pi, 50)
phi_core = np.linspace(0, np.pi, 50)
xc = r_core * np.outer(np.cos(theta_core), np.sin(phi_core))
yc = r_core * np.outer(np.sin(theta_core), np.sin(phi_core))
zc = r_core * np.outer(np.ones(np.size(theta_core)), np.cos(phi_core))

# --- BUILD PLOTLY FIGURE ---
fig = go.Figure()

# Event horizon (black sphere)
fig.add_surface(
    x=x, y=y, z=z,
    colorscale=[[0, "black"], [1, "black"]],
    showscale=False,
    opacity=1.0
)

# Accretion disk
fig.add_surface(
    x=x_disk, y=y_disk, z=z_disk,
    surfacecolor=np.log(rd),
    colorscale="Inferno",
    showscale=False,
    opacity=0.95
)

# Fractal-like singularity core
fig.add_surface(
    x=xc, y=yc, z=zc,
    surfacecolor=np.abs(np.sin(xc * 10) * np.cos(yc * 10)),
    colorscale="Electric",
    showscale=False,
    opacity=0.85
)

fig.update_layout(
    title="Hurricane Black Hole Visualization",
    margin=dict(l=0, r=0, t=40, b=0),
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="cube",
        bgcolor="black"
    ),
    paper_bgcolor="black"
)

# --- ANIMATION (FRAME-ONLY REFRESH-FIXED) ---
plot_area = st.empty()
rotation = 0

if animate:
    for _ in range(150):
        rotation += rotation_speed * 3
        fig.update_layout(scene_camera=dict(
            eye=dict(x=2.5*np.cos(rotation/50), y=2.5*np.sin(rotation/50), z=0.8)
        ))
        plot_area.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)
else:
    plot_area.plotly_chart(fig, use_container_width=True)

# --- SOUND GENERATION ---
if play_sound:
    sample_rate = 44100
    duration = 6  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Whirling + hurricane sound layers
    base = np.sin(2 * np.pi * 30 * t) * np.exp(-0.0001 * t * mass_scale / 1e6)
    swirl = np.sin(2 * np.pi * (0.5 * np.sin(t * 0.2) + 1) * 100 * t)
    roar = np.random.normal(0, 0.2, len(t))
    sound = sound_intensity * (0.6 * base + 0.3 * swirl + 0.1 * roar)

    # Normalize sound
    sound = sound / np.max(np.abs(sound))

    buf = io.BytesIO()
    sf.write(buf, sound, sample_rate, format='WAV')
    buf.seek(0)
    audio_base64 = base64.b64encode(buf.read()).decode()

    st.markdown(
        f"""
        <audio controls autoplay>
        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True
    )

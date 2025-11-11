import streamlit as st
import numpy as np
import plotly.graph_objects as go
import soundfile as sf
import io, base64

st.set_page_config(page_title="Hurricane Black Hole", layout="wide")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Black Hole Control Panel 🌌")

mass_scale = st.sidebar.slider(
    "Mass (visual scale, affects low-band)",
    1000, 100_000_000, 4_300_000, step=1000, format="%d"
)
rotation_speed = st.sidebar.slider("Rotation Speed (a*)", 0.0, 1.0, 0.7, step=0.01)
sound_intensity = st.sidebar.slider("Sound Intensity", 0.1, 2.0, 1.0, step=0.1)
play_sound = st.sidebar.button("🔊 Play Black Hole Sound")

# --- BLACK HOLE GEOMETRY ---
theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 100)
r_event = 1.0
x = r_event * np.outer(np.cos(theta), np.sin(phi))
y = r_event * np.outer(np.sin(theta), np.sin(phi))
z = r_event * np.outer(np.ones(np.size(theta)), np.cos(phi))

# Accretion disk
r_disk = np.linspace(1.2, 2.5, 80)
theta_disk = np.linspace(0, 2 * np.pi, 180)
rd, td = np.meshgrid(r_disk, theta_disk)
x_disk = rd * np.cos(td)
y_disk = rd * np.sin(td)
z_disk = 0.1 * np.sin(3 * td)

# Core
r_core = 0.3
theta_core = np.linspace(0, 2 * np.pi, 50)
phi_core = np.linspace(0, np.pi, 50)
xc = r_core * np.outer(np.cos(theta_core), np.sin(phi_core))
yc = r_core * np.outer(np.sin(theta_core), np.sin(phi_core))
zc = r_core * np.outer(np.ones(np.size(theta_core)), np.cos(phi_core))

# --- BASE FIGURE ---
fig = go.Figure()

# Event horizon
fig.add_surface(x=x, y=y, z=z, colorscale=[[0, "black"], [1, "black"]],
                showscale=False, opacity=1.0)
# Disk
fig.add_surface(x=x_disk, y=y_disk, z=z_disk, surfacecolor=np.log(rd),
                colorscale="Inferno", showscale=False, opacity=0.95)
# Core
fig.add_surface(x=xc, y=yc, z=zc,
                surfacecolor=np.abs(np.sin(xc*10)*np.cos(yc*10)),
                colorscale="Electric", showscale=False, opacity=0.85)

# Camera frames for smooth built-in animation
frames = []
for i in range(60):
    angle = i * rotation_speed * 0.2
    frames.append(go.Frame(
        layout=dict(scene_camera=dict(
            eye=dict(x=2.5*np.cos(angle), y=2.5*np.sin(angle), z=0.8)
        ))
    ))

fig.frames = frames

fig.update_layout(
    updatemenus=[{
        "type": "buttons",
        "buttons": [{
            "label": "▶️ Live Motion",
            "method": "animate",
            "args": [None, {"frame": {"duration": 80, "redraw": True},
                            "fromcurrent": True,
                            "mode": "immediate"}]
        }]
    }],
    scene=dict(xaxis=dict(visible=False),
               yaxis=dict(visible=False),
               zaxis=dict(visible=False),
               aspectmode="cube",
               bgcolor="black"),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=40, b=0),
    title="Hurricane Black Hole Simulation"
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# --- SOUND GENERATION ---
if play_sound:
    sr = 44100
    t = np.linspace(0, 6, int(sr * 6), endpoint=False)
    base = np.sin(2 * np.pi * 30 * t) * np.exp(-0.0001 * t * mass_scale / 1e6)
    swirl = np.sin(2 * np.pi * (0.5 * np.sin(t * 0.2) + 1) * 100 * t)
    roar = np.random.normal(0, 0.2, len(t))
    sound = sound_intensity * (0.6 * base + 0.3 * swirl + 0.1 * roar)
    sound = sound / np.max(np.abs(sound))

    buf = io.BytesIO()
    sf.write(buf, sound, sr, format="WAV")
    buf.seek(0)
    audio_b64 = base64.b64encode(buf.read()).decode()

    st.markdown(
        f"""
        <audio controls autoplay>
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True,
    )

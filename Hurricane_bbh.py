import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io, base64, soundfile as sf

st.set_page_config(page_title="Black Hole — Vortex Simulation", layout="wide")
st.title("🌀 Quantum Black Hole — Accretion Vortex Sound & Animation")

# === Parameters ===
mass = st.slider("Black Hole Mass (M☉, visual scale)", 1e5, 1e9, 4.3e6, step=1e5, format="%.0f")
mass_label = f"{mass:,.0f} M☉"
r_Q_factor = st.slider("Quantum radius scale (× rₛ)", 0.5, 5.0, 1.5, step=0.1)

num_particles = 400
frames_count = 60
animation_seconds = 4.0

G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30
M = mass * M_sun
r_s = 2 * G * M / c**2
r_Q = r_Q_factor * r_s

# === Geometry ===
r_disk_inner = 1.2 * r_s
r_disk_outer = 2.5 * r_s

rng = np.random.default_rng(42)
r_particles = rng.uniform(r_disk_inner, r_disk_outer, size=num_particles)
phi_particles = rng.uniform(0, 2*np.pi, size=num_particles)
z_particles = rng.uniform(-0.015*r_s, 0.015*r_s, size=num_particles)

def F_QG_scalar(r, m=M, r_Q=r_Q):
    r_safe = np.maximum(r, 1e-12)
    return (G * m / (r_safe**2)) * np.exp(-r_safe / r_Q)

F_vals = F_QG_scalar(r_particles)
F_min, F_max = F_vals.min(), F_vals.max()
F_norm = (F_vals - F_min) / (F_max - F_min + 1e-12)

# === Plotly setup ===
theta = np.linspace(0, 2*np.pi, 80)
phi = np.linspace(0, np.pi, 40)
th_mesh, ph_mesh = np.meshgrid(theta, phi)
x_sphere = np.cos(th_mesh) * np.sin(ph_mesh)
y_sphere = np.sin(th_mesh) * np.sin(ph_mesh)
z_sphere = np.cos(ph_mesh)

fig = go.Figure()

# Event Horizon
fig.add_trace(go.Surface(
    x=r_s*x_sphere, y=r_s*y_sphere, z=r_s*z_sphere,
    colorscale=[[0, 'rgb(10,5,20)'], [1, 'rgb(90,20,120)']],
    showscale=False, opacity=0.95, name='Event Horizon'
))

# Accretion Disk
disk_r = np.linspace(r_disk_inner, r_disk_outer, 60)
disk_t = np.linspace(0, 2*np.pi, 240)
R, Tm = np.meshgrid(disk_r, disk_t)
X = R * np.cos(Tm)
Y = R * np.sin(Tm)
Z = 0.03 * np.sin(6 * Tm) * (r_s / 10)
fig.add_trace(go.Surface(
    x=X, y=Y, z=Z, colorscale='Inferno', showscale=False, opacity=0.62, name='Accretion Disk'
))

def scatter3d(xp, yp, zp, cvals):
    return go.Scatter3d(
        x=xp, y=yp, z=zp,
        mode='markers',
        marker=dict(size=3, color=cvals, colorscale='YlOrRd', opacity=0.9),
        hoverinfo='none', showlegend=False
    )

# Initial particle frame
x0 = r_particles * np.cos(phi_particles)
y0 = r_particles * np.sin(phi_particles)
z0 = z_particles
fig.add_trace(scatter3d(x0, y0, z0, F_norm))

# Animation frames
frames = []
for i in range(frames_count):
    t = (i / frames_count) * (2*np.pi)
    x_p = r_particles * np.cos(phi_particles + 0.6*t)
    y_p = r_particles * np.sin(phi_particles + 0.6*t)
    z_p = z_particles + 0.012 * r_s * np.sin(5*t + r_particles/r_s)
    color_mod = np.clip(F_norm * (1 + 0.22*np.sin(6*t + r_particles/r_s)), 0, 1)
    frames.append(go.Frame(data=[scatter3d(x_p, y_p, z_p, color_mod)], name=f"f{i}"))
fig.frames = frames

# Layout / Animation settings
frame_duration_ms = int(1000 * animation_seconds / frames_count)
fig.update_layout(
    import time

# Create a container to hold the animated plot
plot_container = st.empty()

if st.button("Play / Live Motion"):
    st.write("🌀 Simulating black hole rotation...")

    for frame in range(180):
        angle = frame * 2  # degrees per frame
        camera = dict(
            eye=dict(
                x=1.5 * np.sin(np.radians(angle)),
                y=1.5 * np.cos(np.radians(angle)),
                z=0.3
            )
        )
        fig.update_layout(scene_camera=camera)

        # Update the plot in-place
        plot_container.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)  # control rotation speed

else:
    plot_container.plotly_chart(fig, use_container_width=True)
                                        transition=dict(duration=0),
                                                                 fromcurrent=True, mode="immediate",
            dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False),
                                                                    transition=dict(duration=0),
                                                                    mode="immediate")])
)
    
    sliders=[dict(steps=[dict(method="animate", args=[[f.name],
                                                      dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                                           transition=dict(duration=0))],
                              label=str(k)) for k, f in enumerate(frames)], active=0)]
)

fig.update_layout(
    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
               aspectmode='data', bgcolor='black'),
    paper_bgcolor="black", margin=dict(l=0, r=0, t=30, b=0)
)

# === Display ===
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# === Soundscape synthesis ===
st.subheader("🎧 Black Hole Soundscape (Hurricane + Whirlpool)")

if st.button("Generate & Play Soundscape"):
    sr = 44100
    dur = 8.0
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)

    # Layer 1: low subsonic hurricane (AM modulated)
    base1 = np.sin(2*np.pi*30*t) * (0.6 + 0.4*np.sin(2*np.pi*0.5*t))

    # Layer 2: turbulent vortex mid (rough modulation)
    base2 = 0.5*np.sin(2*np.pi*(80 + 20*np.sin(2*np.pi*0.2*t))*t)

    # Layer 3: high flicker quantum plasma (noisy)
    noise = 0.2 * np.random.randn(len(t))
    flicker = np.sin(2*np.pi*800*t + 4*np.sin(2*np.pi*5*t)) * 0.2
    sound = base1 + base2 + flicker + noise

    sound /= np.max(np.abs(sound) + 1e-9)
    buf = io.BytesIO()
    sf.write(buf, sound, sr, format='wav')
    audio_bytes = buf.getvalue()

    st.audio(audio_bytes, format='audio/wav')

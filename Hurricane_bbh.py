import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Black Hole — Client-side Animation", layout="wide")

st.title("🌀 Black Hole — Accretion Plasma (Client-side Animation)")

# Physical / UI controls
mass = st.slider("Black Hole Mass (M☉, visual scale)", min_value=1e5, max_value=1e9, value=4.3e6, step=1e5, format="%.0f")
mass_label = f"{mass:,.0f} M☉"
st.markdown(f"**Mass:** {mass_label}")

r_Q_factor = st.slider("Quantum radius scale (× rₛ)", 0.5, 5.0, 1.5, step=0.1)

# Visual tuning
num_particles = int(st.slider("Number of plasma particles (for animation)", 100, 1200, 400, step=50))
frames_count  = int(st.slider("Animation frames (smoothness)", 20, 120, 60, step=4))
animation_seconds = float(st.slider("Animation duration (s)", 1.0, 10.0, 4.0, step=0.5))

# Constants (visual / toy)
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30
M = mass * M_sun
r_s = 2 * G * M / c**2  # Schwarzschild radius (meters)
r_Q = r_Q_factor * r_s

st.write(f"Schwarzschild radius (visual): {r_s:.3e} m (used as scale)")

# Geometry: normalized to r_s to keep numbers sane for plotting
r_disk_inner = 1.2 * r_s
r_disk_outer = 2.5 * r_s

# Precompute particle base values (in units of meters)
rng = np.random.default_rng(42)
r_particles = rng.uniform(r_disk_inner, r_disk_outer, size=num_particles)
phi_particles = rng.uniform(0, 2*np.pi, size=num_particles)
z_particles = rng.uniform(-0.015*r_s, 0.015*r_s, size=num_particles)

# Quantum Gravity Compression (toy) - used for color/brightness mapping
def F_QG_scalar(r, m=M, r_Q=r_Q):
    # avoid divide by zero
    r_safe = np.maximum(r, 1e-12)
    return (G * m / (r_safe**2)) * np.exp(-r_safe / r_Q)

F_vals = F_QG_scalar(r_particles)
# Normalize to [0,1] for color mapping (avoid degenerate)
F_min, F_max = F_vals.min(), F_vals.max()
if F_max > F_min:
    F_norm = (F_vals - F_min) / (F_max - F_min)
else:
    F_norm = np.zeros_like(F_vals)

# Build static figure: event horizon + accretion disk (one-time)
theta = np.linspace(0, 2*np.pi, 80)
phi = np.linspace(0, np.pi, 40)
th_mesh, ph_mesh = np.meshgrid(theta, phi)
x_sphere = np.cos(th_mesh) * np.sin(ph_mesh)
y_sphere = np.sin(th_mesh) * np.sin(ph_mesh)
z_sphere = np.cos(ph_mesh)

fig = go.Figure()

# Event horizon (draw as purple-ish sphere, slightly translucent to keep hotspot visible)
fig.add_trace(go.Surface(
    x=r_s * x_sphere,
    y=r_s * y_sphere,
    z=r_s * z_sphere,
    colorscale=[[0, 'rgb(25,8,40)'], [1, 'rgb(70,30,120)']],
    showscale=False,
    opacity=0.95,
    name='Event Horizon'
))

# Accretion disk surface (thin)
disk_r = np.linspace(r_disk_inner, r_disk_outer, 60)
disk_t = np.linspace(0, 2*np.pi, 240)
R, Tm = np.meshgrid(disk_r, disk_t)
X = R * np.cos(Tm)
Y = R * np.sin(Tm)
# slight vertical perturbation for visual texture (small amplitude)
Z = 0.03 * np.sin(6 * Tm) * (r_s / 10)
fig.add_trace(go.Surface(
    x=X, y=Y, z=Z,
    colorscale='Inferno',
    showscale=False,
    opacity=0.62,
    name='Accretion Disk'
))

# Helper to create a Scatter3d trace (particles)
def scatter3d_for_positions(xp, yp, zp, cvals, size=3):
    return go.Scatter3d(
        x=xp, y=yp, z=zp,
        mode='markers',
        marker=dict(size=size, color=cvals, colorscale='YlOrRd', cmin=0, cmax=1, opacity=0.9),
        hoverinfo='none',
        showlegend=False
    )

# Initial particle positions (first frame)
x0 = r_particles * np.cos(phi_particles)
y0 = r_particles * np.sin(phi_particles)
z0 = z_particles
fig.add_trace(scatter3d_for_positions(x0, y0, z0, F_norm, size=3))

# Build frames for client-side animation
frames = []
for frame_idx in range(frames_count):
    t = (frame_idx / frames_count) * (2 * np.pi)  # phase
    # particles orbit and wobble with phase; adjust amplitude so motion is visible but subtle
    x_p = r_particles * np.cos(phi_particles + 0.6 * t)
    y_p = r_particles * np.sin(phi_particles + 0.6 * t)
    z_p = z_particles + 0.012 * r_s * np.sin(5 * t + r_particles / r_s)
    # color modulation (turbulence)
    color_mod = np.clip(F_norm * (1 + 0.22 * np.sin(6 * t + r_particles / r_s)), 0, 1)
    # frame only needs the particle trace (index -1 in fig.data)
    frames.append(go.Frame(data=[scatter3d_for_positions(x_p, y_p, z_p, color_mod, size=3)], name=f"f{frame_idx}"))

fig.frames = frames

# Animation settings: duration per frame in ms
frame_duration_ms = max(10, int(1000 * animation_seconds / frames_count))

# Add play/pause button (Plotly built-in)
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            y=1.05,
            x=0.0,
            xanchor="left",
            yanchor="top",
            pad=dict(t=0, r=10),
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, dict(frame=dict(duration=frame_duration_ms, redraw=True),
                                      transition=dict(duration=0),
                                      fromcurrent=True,
                                      mode="immediate")]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        transition=dict(duration=0),
                                        mode="immediate",
                                        showlegend=False)])
            ]
        )
    ]
)

# Layout tweaks: hide axis lines, set black background
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        bgcolor='black'
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=30, b=0),
    title=f"Black Hole visual — Mass {mass_label} (animation client-side)"
)

# Add a slider for manual scrubbing
sliders = [dict(steps=[
    dict(method='animate', args=[[f.name], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
         label=str(i))
    for i, f in enumerate(frames)
], active=0, x=0.05, y=0, xanchor='left', yanchor='top')]
fig.update_layout(sliders=sliders)

# Render the figure once — animation runs entirely client-side in the browser
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

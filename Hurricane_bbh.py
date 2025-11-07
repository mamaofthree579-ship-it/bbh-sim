# quantum_field_sim.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Quantum Field Flow — BBH Singularity", layout="wide")
st.title("🌀 Quantum Field Flow Simulator — Collapse ↔ Emergence")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    mode = st.selectbox("Core Mode", ["Classical Anatomy", "Quantum Fractal Core"])
    field_direction = st.selectbox("Field Direction (default)", ["Collapse (Inward)", "Emergence (Outward)"])
    play = st.checkbox("Play time evolution", value=False)
    speed = st.slider("Time evolution speed", min_value=0.2, max_value=5.0, value=1.0, step=0.1)
    rotation_speed = st.slider("Rotation speed", min_value=0.0, max_value=2.0, value=0.3, step=0.05)
    field_strength = st.slider("Field intensity (affects color scale)", min_value=0.1, max_value=1.0, value=0.6, step=0.05)
    fractal_detail = st.slider("Fractal/Texture detail (visual)", 0, 4, 2, 1)
    show_energy = st.checkbox("Color by energy-density (on lines)", value=True)
    show_labels = st.checkbox("Show labels", value=True)
    hide_ui = st.checkbox("Hide sidebar controls (for screenshots)", value=False)

if hide_ui:
    st.markdown("<style>.sidebar .sidebar-content {display:none;}</style>", unsafe_allow_html=True)

# Session state for animation/time
if "time_phase" not in st.session_state:
    st.session_state.time_phase = 0.0  # 0..1 where 0=collapse,0.5=stasis,1=emergence
if "angle" not in st.session_state:
    st.session_state.angle = 0.0
if "playing" not in st.session_state:
    st.session_state.playing = False

# Map UI fields to simple booleans
outward_default = (field_direction == "Emergence (Outward)")

# Geometry params
def build_core_mesh(core_radius=0.25, detail=50, fractal_detail=2, core_mode="Classical Anatomy"):
    theta, phi = np.mgrid[0:np.pi:detail*1j, 0:2*np.pi:detail*1j]
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    # Simple fractal-like perturbation (visual only)
    if core_mode == "Quantum Fractal Core" and fractal_detail > 0:
        for k in range(fractal_detail):
            perturb = 0.02 * (0.9**k) * np.sin((k+2) * phi + 0.5 * k)
            x = (1 + perturb) * x
            y = (1 + perturb) * y
            z = (1 + perturb) * z
    return core_radius * x, core_radius * y, core_radius * z

# Field line generator (returns list of x,y,z arrays and energy scalars per point)
def generate_field_lines(n_lines=28, points_per_line=160, outward=False, time_phase=0.0, field_strength=0.6):
    """
    time_phase in [0,1]: controls collapse->stasis->emergence
      0.0 => strongly inward flow
      0.5 => slow/stationary
      1.0 => strongly outward flow
    outward param can set default orientation (if provided)
    """
    lines = []
    # directional factor from time phase: -1 inward, 0 stasis, +1 outward
    dir_factor = np.interp(time_phase, [0.0, 0.5, 1.0], [-1.0, 0.0, 1.0])
    for i in range(n_lines):
        base_angle = i * (2 * np.pi / n_lines) + 0.3 * np.sin(i)
        r = np.linspace(0.18, 1.6, points_per_line)
        # small spiral/warp depends on phase & field_strength
        spiral_amp = 0.25 * (0.3 + 0.7 * (field_strength))
        spiral = spiral_amp * np.sin(6 * np.pi * r + 2 * dir_factor + i * 0.2)
        x = r * np.cos(base_angle + spiral)
        y = r * np.sin(base_angle + spiral)
        z = 0.15 * np.sin(4 * np.pi * r + i * 0.2) * (0.6 + 0.4 * dir_factor)
        # orientation flip: collapse=inward (points move towards center), emergence=outward
        if dir_factor < 0:
            # collapse: start from outer region moving inward visually (we invert param for visuals)
            x = x[::-1]; y = y[::-1]; z = z[::-1]
        # energy-like scalar: stronger near core when collapsing, stronger outward when emerging
        # simple model: energy ~ field_strength * (1/(r+0.05)) * (1 + dir_factor*r)
        energy = field_strength * (1.0 / (r + 0.05)) * (1.0 + dir_factor * r * 0.4)
        lines.append({"x": x, "y": y, "z": z, "energy": energy})
    return lines

# Build initial grid
theta = np.linspace(0, np.pi, 50)
phi = np.linspace(0, 2*np.pi, 50)
x = np.outer(np.sin(theta), np.cos(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.cos(theta), np.ones_like(phi))

# Core frame 0
surface = go.Surface(x=x, y=y, z=z, colorscale="Inferno", showscale=False)

# Animation frames – rotate around z axis
frames = []
for angle in np.linspace(0, 2*np.pi, 40):
    rot_x = np.cos(angle)*x - np.sin(angle)*y
    rot_y = np.sin(angle)*x + np.cos(angle)*y
    frames.append(go.Frame(data=[go.Surface(x=rot_x, y=rot_y, z=z,
                                            colorscale="Inferno", showscale=False)]))

fig = go.Figure(
    data=[surface],
    frames=frames,
    layout=go.Layout(
        scene=dict(aspectmode="data"),
        updatemenus=[dict(type="buttons", showactive=False,
            buttons=[dict(label="Play", method="animate", args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]),
                     dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])])]
    )
)

# Optional labels
if show_labels:
        fig.add_trace(go.Scatter3d(
            x=[0.0, 0.0, 1.1],
            y=[0.0, 0.0, 0.0],
            z=[0.5, -0.5, 0.0],
            mode="text",
            text=["Singularity Core", "Event Horizon", "Accretion Disk"],
            textfont=dict(color="white", size=12),
            hoverinfo="skip",
            showlegend=False
        ))
    
# Camera / rotation
cam_radius = 2.4
cam = dict(eye=dict(x=cam_radius * np.cos(angle), y=cam_radius * np.sin(angle), z=0.9))
fig.update_layout(scene=dict(
    xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
        aspectmode="auto"
    ), scene_camera=cam,
        paper_bgcolor="black", plot_bgcolor="black",
        margin=dict(l=0, r=0, t=0,
b=0))
return fig

# UI presentation (main column)
col1, col2 = st.columns([2, 1])
with col1:
    plot_area = st.empty()
with col2:
    st.markdown("### Controls (quick)")
    st.write(f"Mode: **{mode}**")
    st.write(f"Field intent: **{field_direction}**")
    st.write(f"Fractal detail: **{fractal_detail}**")
    st.write(" ")
    st.markdown("Use **Play** (sidebar) to animate between collapse → emergence.")

# Animation loop / update
st.session_state.playing = bool(play)

loop_delay = max(0.04, 0.14 / float(speed))

if st.session_state.playing:
    t0 = time.perf_counter()
    run_chunk_seconds = 1.0
    # Use a local placeholder to refresh safely
    frame_placeholder = st.empty()

    while st.session_state.playing and (time.perf_counter() - t0) < run_chunk_seconds:
        st.session_state.time_phase = (st.session_state.time_phase + 0.012 * speed) % 1.0
        st.session_state.angle += rotation_speed * 0.02

        fig = build_figure(
            mode, fractal_detail, field_strength,
            outward_default, st.session_state.time_phase,
            st.session_state.angle, rotation_speed,
            show_energy, show_labels
        )

        # ✅ SAFE update using the same placeholder, avoiding duplicate element IDs
        frame_placeholder.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        time.sleep(loop_delay)
    # final render once per chunk
    frame_placeholder.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    fig = build_figure(
        mode, fractal_detail, field_strength, outward_default,
        st.session_state.time_phase, st.session_state.angle,
        rotation_speed, show_energy, show_labels
    )
    st.empty().plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

# Provide a small legend / controls footer
with st.expander("Legend & Notes", expanded=False):
    st.markdown("""
    - **Field lines** are colored by a simple energy-like scalar (brighter = stronger).  
    - **Time evolution** cycles: 0.0 (collapse) → 0.5 (stasis) → 1.0 (emergence).  
    - This is a phenomenological visualization — parameters are for exploration, not exact GR/quantum solutions.
    """)
    st.markdown("**Tip:** Toggle `Color by energy-density` to see constant-color flow instead.")

# Small buttons to step the phase manually (handy for testing)
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("Step →"):
        st.session_state.time_phase = min(1.0, st.session_state.time_phase + 0.05)
        st.experimental_rerun()
with col_b:
    if st.button("Step ←"):
        st.session_state.time_phase = max(0.0, st.session_state.time_phase - 0.05)
        st.experimental_rerun()
with col_c:
    if st.button("Reset Phase"):
        st.session_state.time_phase = 0.0
        st.experimental_rerun()

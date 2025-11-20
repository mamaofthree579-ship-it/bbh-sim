import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io, wave, struct, math, time

st.set_page_config(layout="wide", page_title="Black Hole Anatomy — Advanced", page_icon="🕳️")

st.title("🔭 Black Hole Anatomy — Advanced Visualizer (Version 3)")
st.markdown(
    "A 3D visual of a black hole (purple core), accretion disk rings, and a rotating hotspot. "
    "Use the controls to tune mass, spin, trail length, and animation speed. "
    "Play a hurricane+whirlpool-like audio texture synthesized on the fly."
)

# ---- Sidebar controls ----
with st.sidebar:
    st.header("Controls")
    mass = st.slider("Mass (M☉) — visual scale", min_value=1_000, max_value=1_000_000_00, value=4_300_000, step=1_000, format="%d")
    spin = st.slider("Spin a* (0 — 1)", 0.0, 1.0, 0.5, step=0.01)
    trail_len = st.slider("Hotspot trail length (points)", min_value=4, max_value=60, value=12, step=1)
    anim_speed = st.slider("Animation speed (affects frame duration)", 0.2, 3.0, 1.0, step=0.1)
    rings = st.slider("Accretion disk ring count (visual)", 6, 40, 18, step=1)
    hotspot_size = st.slider("Hotspot size (visual px)", 4, 24, 8, step=1)
    st.markdown("---")
    st.markdown("**Audio texture**")
    audio_dur = st.slider("Audio duration (s)", 1.0, 8.0, 3.0, step=0.5)
    audio_strength = st.slider("Audio intensity (0.0 quiet — 1.0 loud)", 0.0, 1.0, 0.6, step=0.05)

# ---- Derived visual params ----
# We keep the actual physical radii for info, but visualize at normalized scale so spheres remain visible.
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30
M_kg = mass * M_sun
r_s = 2 * G * M_kg / c**2  # physical Schwarzschild radius (m) -- for display only

# Visual radii (normalized for plotting)
horizon_r = 1.0            # normalized
photon_sphere_r = 1.5      # normalized multiplier
disk_inner = 1.15
disk_outer = 3.6

# Animation frame count (full rotation)
NFRAMES = 72

# Build accretion disk points (rings)
def make_disk_rings(cx=0, cy=0, cz=0, inner=disk_inner, outer=disk_outer, n_rings=18, pts_per_ring=120):
    rings_traces = []
    radii = np.linspace(inner, outer, n_rings)
    for r in radii:
        theta = np.linspace(0, 2*np.pi, pts_per_ring)
        x = cx + r * np.cos(theta)
        y = cy + r * np.sin(theta)
        # give a small vertical warp for visual interest
        z = cz + 0.03 * np.sin(4*theta) * (outer - r) / (outer - inner + 1e-6)
        rings_traces.append((x, y, z))
    return rings_traces

disk_rings = make_disk_rings(n_rings=rings, pts_per_ring=160)

# Create a smooth central "purple sphere" mesh (approx) using parametric param
def sphere_mesh(radius=0.98, u_res=30, v_res=30, color='#3b0066'):
    u = np.linspace(0, 2*np.pi, u_res)
    v = np.linspace(0, np.pi, v_res)
    uu, vv = np.meshgrid(u, v)
    x = radius * np.cos(uu) * np.sin(vv)
    y = radius * np.sin(uu) * np.sin(vv)
    z = radius * np.cos(vv)
    return x, y, z

sx, sy, sz = sphere_mesh(radius=horizon_r * 0.98, u_res=28, v_res=18)

# Hotspot path (circle with slight vertical wobble influenced by spin)
def hotspot_positions(nframes=NFRAMES, radius=2.2, wobble=0.12, spin_offset=0.0):
    angles = np.linspace(0, 2*np.pi, nframes, endpoint=False)
    xs = radius * np.cos(angles + spin_offset)
    ys = radius * np.sin(angles + spin_offset)
    zs = wobble * np.sin(angles * (1 + spin*2.0))
    return xs, ys, zs

xs_hot, ys_hot, zs_hot = hotspot_positions(NFRAMES, radius=(1.9 + 1.2*spin), wobble=0.18, spin_offset=0.0)

# Prepare frames for Plotly animation
frames = []
for fi in range(NFRAMES):
    # hotspot current position
    hx = xs_hot[fi]
    hy = ys_hot[fi]
    hz = zs_hot[fi]
    # trail: collect previous trail_len points (wrap-around)
    idxs = [(fi - k) % NFRAMES for k in range(trail_len)][::-1]  # oldest first
    trail_x = [xs_hot[i] for i in idxs]
    trail_y = [ys_hot[i] for i in idxs]
    trail_z = [zs_hot[i] for i in idxs]
    # make small trail marker sizes decreasing
    trail_sizes = [max(2, hotspot_size * (0.2 + 0.8*(i+1)/len(trail_x))) for i in range(len(trail_x))]

    frame_data = []
    # hotspot scatter (as single point) - trace index 1 in base figure will be replaced by frames
    frame_data.append(go.Scatter3d(x=[hx], y=[hy], z=[hz],
                                   mode='markers',
                                   marker=dict(size=hotspot_size, color='rgb(255,220,160)', opacity=0.95),
                                   name='Hotspot'))
    # trail scatter
    frame_data.append(go.Scatter3d(x=trail_x, y=trail_y, z=trail_z,
                                   mode='markers',
                                   marker=dict(size=trail_sizes, color='rgba(255,220,180,0.65)'),
                                   name='Trail'))
    # small dynamic ring ripple (weak)
    ripple_r = 1.0 + 0.9 * (fi / NFRAMES)
    theta = np.linspace(0, 2*np.pi, 80)
    rx = ripple_r * np.cos(theta)
    ry = ripple_r * np.sin(theta)
    rz = 0.02 * np.sin(8*theta + fi*0.12)
    frame_data.append(go.Scatter3d(x=rx, y=ry, z=rz, mode='lines',
                                   line=dict(color='rgba(255,200,160,0.06)', width=2), name='Ripple'))
    frames.append(go.Frame(data=frame_data, name=f'frame{fi}'))

# Build base (static) traces: central sphere (as surface), disk rings (lines)
fig = go.Figure()

# central purple sphere (use surface trace)
fig.add_trace(go.Surface(x=sx, y=sy, z=sz,
                         colorscale=[[0, 'rgb(44,0,70)'], [1, 'rgb(90,20,140)']],
                         showscale=False,
                         opacity=0.95,
                         lighting=dict(ambient=0.6, diffuse=0.6, specular=0.4, roughness=0.9),
                         name='Event Horizon (visual)'))

# accretion rings (lines)
for (rx, ry, rz) in disk_rings:
    fig.add_trace(go.Scatter3d(x=rx, y=ry, z=rz, mode='lines',
                               line=dict(color='rgba(255,180,80,0.12)', width=1),
                               hoverinfo='skip', showlegend=False))

# add a faint axis-free layout
fig.update_layout(scene=dict(
    xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
    aspectmode='auto',
    bgcolor='rgba(0,0,0,0)'
))

# Add placeholder traces for hotspot + trail + ripple which frames will replace (use initial frame 0)
initial_frame_data = frames[0].data
for d in initial_frame_data:
    # add each trace with same order so frames replace them in place
    fig.add_trace(d)

# Attach frames
fig.frames = frames

# Add Plotly animation buttons (Play/Pause) and configure frame duration from animation speed slider
frame_duration_ms = int(80 / anim_speed)  # mapping: larger speed -> shorter frame duration
play_button = dict(type="buttons",
                   showactive=False,
                   y=1,
                   x=0.1,
                   xanchor="right",
                   yanchor="top",
                   pad=dict(t=10, r=10),
                   buttons=[
                       dict(label="Play",
                            method="animate",
                            args=[None, dict(frame=dict(duration=frame_duration_ms, redraw=True),
                                             transition=dict(duration=0),
                                             fromcurrent=True,
                                             mode='immediate')]),
                       dict(label="Pause",
                            method="animate",
                            args=[[None], dict(frame=dict(duration=0, redraw=False),
                                               mode='immediate',
                                               transition=dict(duration=0))])
                   ])

fig.update_layout(updatemenus=[play_button],
                  margin=dict(l=0, r=0, t=40, b=0),
                  paper_bgcolor='rgba(0,0,0,0)',
                  title=f"Black Hole Visual — Mass: {mass:,} M☉ · spin a*={spin:.2f}",
                  showlegend=False)

# add a frame slider (Plotly's built in)
steps = []
for i in range(NFRAMES):
    step = dict(method="animate",
                args=[[f'frame{i}'], dict(frame=dict(duration=frame_duration_ms, redraw=True),
                                          mode='immediate')],
                label=str(i))
    steps.append(step)
sliders = [dict(active=0, pad={"t": 50}, steps=steps, currentvalue={"prefix":"Frame: "})]
fig.update_layout(sliders=sliders)

# render Plotly figure in Streamlit
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("3D Visual")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})
    st.caption("Use Play button (above) to animate. Speed slider changes frame timing when re-rendered.")

with col2:
    st.subheader("Model Info & Controls")
    st.write(f"**Mass (M☉):** {mass:,}")
    st.write(f"**Schwarzschild radius (physical):** {r_s:.3e} m")
    st.write(f"**Normalized visual horizon radius:** {horizon_r:.2f}")
    st.write(f"**Spin (a*):** {spin:.2f}")
    st.write(f"**Hotspot trail length:** {trail_len}")
    st.write(f"**Accretion rings (visual):** {rings}")
    st.write(f"**Animation speed:** {anim_speed:.2f} (higher = faster)")
    st.markdown("---")
    st.markdown("**Interactivity**")
    st.write("Change controls in the sidebar then click **Refresh Visual** to regenerate animation timing & assets.")

# A refresh button to re-generate figure with new frame_duration (Plotly uses frame duration baked into figure)
if st.button("Refresh Visual"):
    # Recompute frame duration and re-render (we simply rerun the app which regenerates fig above
    st.experimental_rerun()

# ------------------------------
# Audio synthesis: hurricane + whirlpool-like texture
# ------------------------------
def synth_hurricane_whirlpool(duration_s=3.0, sr=22050, intensity=0.6, mass_scale=1.0, spin_val=0.5):
    """
    Synthesize a layered texture:
    - low-frequency swirling base (sweep)
    - filtered noise for 'whirlpool'
    - amplitude modulation and slow tremor (hurricane-like)
    Returns bytes (WAV) and sample rate.
    """
    t = np.linspace(0, duration_s, int(sr*duration_s), endpoint=False)
    # base sweep: slow rising sine (like base rumble)
    f0 = 8.0 * (0.5 + 0.5*(spin_val))  # low base freq
    f1 = 220.0 * (0.6 + 0.8*(mass_scale/4_300_000))  # mass influences high end a little
    sweep = np.sin(2*np.pi*(f0*t + (f1-f0)/(2*duration_s) * t**2))  # quadratic chirp-like sweep

    # whirlpool: filtered noise shaped by 1/f envelope + bandpass-ish amplitude
    white = np.random.normal(0, 1.0, t.shape)
    # simple 1/f shaping by cumulative sum (integral) and highpass subtract
    pink = np.cumsum(white)
    pink = pink / (np.max(np.abs(pink)) + 1e-9)
    # bandpass component by modulating with low frequency sine
    whirl = pink * (0.3 + 0.7 * np.sin(2*np.pi*0.7*t + 1.2*spin_val))

    # hurricane turbulence: amplitude modulation
    trem = 0.6 + 0.4 * np.sin(2*np.pi*0.25*t + 0.6*spin_val)  # slow large-scale modulation

    # combine with weights
    audio = (0.7 * sweep + 0.9 * whirl * 0.6) * trem

    # gentle lowpass / taper (fade out)
    fade = np.ones_like(t)
    fade[int(0.85*len(t)):] = np.linspace(1.0, 0.0, len(t) - int(0.85*len(t)))
    audio = audio * fade

    # normalize and apply intensity
    audio = audio / (np.max(np.abs(audio)) + 1e-9)
    audio = audio * float(np.clip(intensity, 0.0, 1.0)) * 0.9

    # convert to 16-bit PCM
    pcm = np.int16(audio * 32767)
    # write WAV bytes with wave module
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    bio.seek(0)
    return bio, sr

# Play audio button
if st.button("Play Hurricane/Whirlpool Audio"):
    st.info("Generating audio... (synthesizing in memory)")
    bio, sr = synth_hurricane_whirlpool(duration_s=audio_dur, sr=22050, intensity=audio_strength, mass_scale=mass, spin_val=spin)
    st.audio(bio.read(), format="audio/wav", start_time=0)
    st.success("Playing (streaming via browser).")

st.markdown("---")
st.caption("Notes: This visualization is a pedagogical/visual model (toy physics). The audio is a synthesized texture inspired by hurricane/whirlpool dynamics — not a literal recording of spacetime.")

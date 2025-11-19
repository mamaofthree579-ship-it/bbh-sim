import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io, time, wave, struct
from PIL import Image
from matplotlib.colors import Normalize
from matplotlib import cm

st.set_page_config(page_title="BBH Anatomy — Full Upgrade", layout="wide")
st.title("🔭 Black Hole Anatomy — (Lensing, Jets, Multi-hotspots, Sound)")

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.header("Simulation Controls")

mass_scale = st.sidebar.slider("Mass scale (visual)", 1.0, 10.0, 4.3, 0.1)
spin = st.sidebar.slider("Spin (a*, 0..1)", 0.0, 0.99, 0.72, 0.01)
num_hotspots = st.sidebar.slider("Number of hotspots", 1, 6, 2, 1)
trail_len = st.sidebar.slider("Hotspot trail length", 3, 30, 12, 1)
disk_brightness = st.sidebar.slider("Disk brightness", 0.2, 3.0, 1.2, 0.05)
turbulence = st.sidebar.slider("Turbulence strength", 0.0, 0.6, 0.12, 0.01)
jet_strength = st.sidebar.slider("Jet strength", 0.0, 1.0, 0.45, 0.05)
lensing_strength = st.sidebar.slider("Lensing strength (visual)", 0.0, 1.0, 0.42, 0.02)
silhouette_softness = st.sidebar.slider("Silhouette softness", 0.0, 1.0, 0.24, 0.02)

st.sidebar.markdown("---")
st.sidebar.subheader("Audio / Playback")
enable_sound = st.sidebar.checkbox("Enable sound (synth rumble)", value=True)
sound_level = st.sidebar.slider("Sound level", 0.0, 1.0, 0.45, 0.05)
auto_play = st.sidebar.checkbox("Auto Play (loop)", value=False)

# Buttons
col1, col2, col3 = st.sidebar.columns([1,1,1])
if col1.button("Step ▶"):
    if "frame" not in st.session_state: st.session_state.frame = 0
    st.session_state.frame += 1
if col2.button("Reset ⟲"):
    st.session_state.frame = 0
if col3.button("Pause ⏸"):
    st.session_state.auto = False

# frame state
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "auto" not in st.session_state:
    st.session_state.auto = auto_play
else:
    st.session_state.auto = auto_play

# Canvas size
CANVAS_W = 720
CANVAS_H = 720

# ---------------------------
# Helper functions
# ---------------------------
def hex_to_rgba_tuple(hexcolor, alpha=1.0):
    hexcolor = hexcolor.lstrip('#')
    lv = len(hexcolor)
    return tuple(int(hexcolor[i:i+lv//3], 16)/255.0 for i in range(0, lv, lv//3)) + (alpha,)

def doppler_beam(vx):
    # approximate relativistic effect mapping velocity (-1..1) to intensity
    beta = np.clip(vx, -0.999, 0.999)
    g = 1.0 / np.sqrt(1 - beta**2)
    return (g * (1 + beta))**1.2

def hotspot_params(i, tframe):
    # provide radius, phase, omega for hotspot i
    base_r = 4.0 + 0.6 * spin + 0.3 * i
    phase = (tframe*0.02 + i * (2*np.pi/num_hotspots))
    omega = 0.6 + 0.04*i + 0.15*spin
    return base_r, phase, omega

def frame_drag_warp(x, y):
    # simple warp representing frame-dragging (Kerr-like)
    r = np.sqrt(x*x + y*y) + 1e-9
    twist = spin * 0.18 / (1 + 0.6*r*r)
    xp = x*np.cos(twist) - y*np.sin(twist)
    yp = x*np.sin(twist) + y*np.cos(twist)
    return xp, yp

def lens_warp(x, y):
    # pseudo-lensing: radial displacement inversely proportional to impact parameter
    r = np.sqrt(x*x + y*y) + 1e-6
    b = r
    # deflection angle ~ constant * 1/b scaled by lensing_strength
    k = 0.9 * lensing_strength * mass_scale
    alpha = k / (b + 0.1)
    # shift coordinates by rotating outward/inward by alpha
    xp = x + alpha * (x / r)
    yp = y + alpha * (y / r)
    return xp, yp

# ---------------------------
# Background / lensing image
# ---------------------------
def make_background_grid(size=CANVAS_W, stars=False):
    """Create a background grid that will be warped for lensing.
       Returns an RGB image (PIL)"""
    res = size
    bg = np.zeros((res, res, 3), dtype=np.float32)
    # polar grid lines to show bending
    xs = np.linspace(-10, 10, res)
    ys = np.linspace(-10, 10, res)
    X, Y = np.meshgrid(xs, ys)
    R = np.sqrt(X**2 + Y**2)
    # dark bluish background with faint grid
    bg[..., 0] = 0.02 + 0.02 * np.exp(-R*0.2)
    bg[..., 1] = 0.03 + 0.03 * np.exp(-R*0.12)
    bg[..., 2] = 0.06 + 0.06 * np.exp(-R*0.08)
    # add radial circular guide lines
    for rr in [3, 4.5, 7]:
        band = np.exp(-((R - rr)**2) / 0.02)
        bg[..., 0] += 0.02 * band
        bg[..., 1] += 0.01 * band
        bg[..., 2] += 0.00 * band
    # optional faint stars (sparse)
    if stars:
        rng = np.random.RandomState(1234)
        Nst = 180
        for _ in range(Nst):
            sx = rng.randint(0, res)
            sy = rng.randint(0, res)
            bg[max(0,sy-1):min(res,sy+2), max(0,sx-1):min(res,sx+2), :] += (0.5 + rng.rand()*0.5) * 0.65
    # clamp and convert
    bg = np.clip(bg, 0, 1.0)
    img = (bg * 255).astype(np.uint8)
    return Image.fromarray(img)

# cache the background for speed
if "bg_img" not in st.session_state:
    st.session_state.bg_img = make_background_grid(CANVAS_W, stars=True)

# ---------------------------
# Wave generator (audio) — creates a WAV bytes object
# ---------------------------
def synth_rumble(duration_s=3.0, sr=22050, mass_factor=1.0, spin_factor=0.5):
    """
    Create a synthetic 'whirlpool + hurricane' rumble:
    - low-frequency sweep + filtered noise + subtle harmonics
    Returns bytes (WAV) and sample rate.
    """
    t = np.linspace(0, duration_s, int(sr*duration_s), endpoint=False)
    # low base: 10..80 Hz sweep shaped by mass
    f0 = 8 + 10 * (1.0 / max(1.0, mass_factor/4.3))
    f1 = 40 + 80 * (spin_factor)
    base = np.sin(2*np.pi*(f0 + (f1-f0) * (t/duration_s)**1.8) * t)
    # swirling higher-frequency breath (hurricane-like)
    breath = 0.35 * np.sin(2*np.pi*(120 + 60*np.sin(2*np.pi*0.2*t)) * t)
    # filtered noise for turbulence
    rng = np.random.RandomState(42)
    noise = rng.normal(scale=0.6, size=t.shape)
    # simple band-limit by applying sin windowing in frequency domain (cheap)
    # combine with decaying envelope
    env = np.exp(-2.0 * (t/duration_s))
    sig = 0.9 * base + 0.25 * breath + 0.5 * 0.5 * noise
    sig *= env
    # normalize
    sig = sig / np.max(np.abs(sig) + 1e-9) * sound_level
    # convert to 16-bit PCM
    audio_bytes = io.BytesIO()
    with wave.open(audio_bytes, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for s in sig:
            s_int = int(np.clip(s, -1, 1) * 32767)
            wf.writeframes(struct.pack('<h', s_int))
    audio_bytes.seek(0)
    return audio_bytes

# ---------------------------
# Render function (main)
# ---------------------------
def render_scene(frame_index):
    # create background (warped)
    bg = np.array(st.session_state.bg_img).astype(np.float32) / 255.0
    res = bg.shape[0]
    # coordinate grid in "visual" units (-10..10)
    xs = np.linspace(-10, 10, res)
    ys = np.linspace(-10, 10, res)
    X, Y = np.meshgrid(xs, ys)
    # apply lensing warp (fast vectorized)
    Xw, Yw = lens_warp(X, Y)
    # sample BG by mapping coordinates to pixels (nearest)
    # map domain -10..10 to 0..res-1
    xi = np.clip(((Xw + 10) / 20.0 * (res - 1)).astype(int), 0, res-1)
    yi = np.clip(((Yw + 10) / 20.0 * (res - 1)).astype(int), 0, res-1)
    warped = bg[yi, xi, :].copy()

    # create matplotlib fig
    fig, ax = plt.subplots(figsize=(6,6), dpi=120)
    ax.imshow(warped, origin='lower', extent=[-10,10,-10,10])
    ax.set_xlim(-10,10); ax.set_ylim(-10,10); ax.set_xticks([]); ax.set_yticks([])
    ax.set_facecolor("black")

    # Ray-traced silhouette approx: draw a softened ellipse scaled by mass & soft parameter
    horizon_radius = 2.6 * (1.0 + 0.03*(mass_scale-4.3))
    soft = silhouette_softness * 1.6 + 0.02
    # create a radial alpha ring (soft edge)
    theta = np.linspace(0, 2*np.pi, 360)
    rx = horizon_radius * np.cos(theta)
    ry = horizon_radius * np.sin(theta)
    # soft shadow (several concentric rings)
    for k in range(10):
        alpha_k = 0.14 * np.exp(-k*0.6) * (1 + k*0.03) * (1.0 - silhouette_softness*0.6)
        ax.fill_between(rx*(1+0.01*k), ry*(1+0.01*k), color=(0.03, 0.00, 0.06, alpha_k), edgecolor=None)

    # hawking halo (soft bluish)
    halo_r = horizon_radius * 1.08
    ax.scatter(0,0, s=1600*halo_r, c=[(0.45,0.68,1.0,0.05)])

    # draw accretion disk (warped and with turbulence)
    # param grid for disk
    theta_d = np.linspace(0, 2*np.pi, 420)
    radii = np.linspace(horizon_radius + 0.4, 9.8, 240)
    TH, RR = np.meshgrid(theta_d, radii)
    # spiral inflow (simple)
    RR2 = RR - 0.02 * (frame_index % 360) / 60.0
    # convert to XY
    Xd = RR2 * np.cos(TH)
    Yd = RR2 * np.sin(TH)
    # apply frame-dragging warp
    Xd, Yd = frame_drag_warp(Xd, Yd)
    # sample a temperature map
    T = disk_brightness * ( (1.0 / np.maximum(RR2, 1.0))**0.75 ) * (1 + turbulence * (np.sin(TH*12 + frame_index*0.1)))
    # flatten and plot as scatter for speed & look
    ax.scatter(Xd.flatten(), Yd.flatten(), c=T.flatten(), cmap='inferno', s=0.45, alpha=0.78, linewidths=0)

    # Jets (axial beams)
    if jet_strength > 0.01:
        # draw cones up and down along y-axis
        for sign in [1, -1]:
            # flicker
            flick = 0.7 + 0.3*np.sin(frame_index*0.07 + sign*1.2)
            beam_alpha = 0.08 * jet_strength * flick
            beam_width = 0.22 + 0.08*jet_strength
            xsj = np.linspace(-0.6, 0.6, 10)
            ysj = sign * (np.linspace(horizon_radius*1.2, 10, 60))
            for idx in range(len(ysj)-1):
                xw = xsj * (1 + (idx/len(ysj))*4.5) * (1 + 0.2*np.sin(frame_index*0.12 + idx*0.06))
                yv = ysj[idx]
                ax.fill_between(xw, yv, yv+0.01, color=(0.6, 0.9, 1.0, beam_alpha*(1 - idx/len(ysj))))
    # Multi-hotspots
    for i in range(num_hotspots):
        r_i, phase_i, omega_i = hotspot_params(i, frame_index)
        # moving phase
        angle = phase_i + 0.9 * frame_index * 0.02 * (1 + 0.05*i)
        xh = r_i * np.cos(angle)
        yh = r_i * np.sin(angle)
        # small frame drag on hotspot
        xh, yh = frame_drag_warp(xh, yh)
        # doppler-ish brightening (based on tangential velocity projection toward viewer)
        vx = -r_i * omega_i * np.sin(angle)
        doping = doppler_beam(vx*0.01)  # scale down so effect is subtle
        # trail
        for k in range(trail_len):
            t = frame_index - k * (0.8 + 0.04*i)
            angle_t = phase_i + 0.9 * t * 0.02 * (1 + 0.04*i)
            tx = r_i * np.cos(angle_t)
            ty = r_i * np.sin(angle_t)
            tx, ty = frame_drag_warp(tx, ty)
            fade = max(0.05, (1.0 - k / trail_len))
            ax.scatter(tx, ty, color=(1.0, 0.78, 0.48, 0.38 * fade * (0.6 + 0.4*doping)), s=14 * (1.0 - 0.05*k))
        # hotspot core
        ax.scatter(xh, yh, color=(1, 0.92, 0.6, 0.92*doping), s=90 + 8*i, edgecolors='yellow', linewidths=0.6)

    # small annot
    ax.text(-9.2, 8.4, f"Mass scale: {mass_scale:.2f}  •  spin: {spin:.2f}  •  frame: {frame_index}", color="#d6c7ff", fontsize=9)

    # save figure to bytes image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf

# ---------------------------
# Main UI layout
# ---------------------------
col_visual, col_controls = st.columns([3,1])

with col_visual:
    placeholder = st.empty()
    # auto-play loop (careful: long loops on hosted platforms may block)
    if auto_play or st.session_state.auto:
        st.session_state.auto = True
        # run a modest number of frames in a loop to avoid infinite hogging
        for _ in range(12):  # step small chunk per run to keep UI responsive
            frame = st.session_state.frame
            img_buf = render_scene(frame)
            placeholder.image(Image.open(img_buf), use_column_width=True)
            # audio play triggered at first auto play iteration
            if enable_sound and frame % 40 == 0:
                audio_buf = synth_rumble(duration_s=3.0, mass_factor=mass_scale, spin_factor=spin)
                st.audio(audio_buf, format="audio/wav")
            st.session_state.frame += 1
            time.sleep(0.07)  # small pause for animation feel
        # cause Streamlit to rerun (so UI remains responsive)
        st.experimental_rerun()
    else:
        # single-frame render (on-demand)
        frame = st.session_state.frame
        img_buf = render_scene(frame)
        placeholder.image(Image.open(img_buf), use_column_width=True)
        # produce sound once per manual step if requested
        if enable_sound and st.button("Play Sound"):
            audio_buf = synth_rumble(duration_s=3.0, mass_factor=mass_scale, spin_factor=spin)
            st.audio(audio_buf, format="audio/wav")

with col_controls:
    st.markdown("### Controls & Diagnostics")
    st.write(f"Frame: {st.session_state.frame}")
    if st.button("Advance Frame ▶"):
        st.session_state.frame += 1
        st.experimental_rerun()
    st.markdown("---")
    if st.checkbox("Show lensing background (toggle)", value=True):
        st.image(st.session_state.bg_img, caption="Lensing background (base)", use_column_width=True)
    st.markdown("**Export:**")
    if st.button("Export current frame as PNG"):
        # re-render and provide as download
        imgbuf = render_scene(st.session_state.frame)
        st.download_button("Download PNG", data=imgbuf.getvalue(), file_name=f"bbh_frame_{st.session_state.frame}.png", mime="image/png")

st.sidebar.markdown("---")
st.sidebar.write("Tip: Toggle Auto Play for short looped previews. Use Step / Advance Frame to get single-step control.")

# ensure frame index increments if user pressed Step in sidebar (handled earlier)

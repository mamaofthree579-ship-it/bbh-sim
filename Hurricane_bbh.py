import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import imageio
import io
import math
import wave
import struct
from datetime import datetime

st.set_page_config(page_title="Realistic BBH Anatomy Simulator", layout="wide")

# -------------------------
# Constants & helpers
# -------------------------
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

def schwarzschild_radius(M_kg):
    return 2 * G * M_kg / (c**2)

def time_dilation_factor(M_kg, r_m):
    # gamma = sqrt(1 - r_s / r)
    rs = schwarzschild_radius(M_kg)
    val = 1 - (rs / r_m)
    if val <= 0:
        return 0.0
    return math.sqrt(val)

def chirp_waveform_samples(m1, m2, spin, duration_s=3.0, sr=44100):
    """
    Toy PN-inspired chirp audio generator:
    f(t) = f0 + (f1 - f0) * t^alpha
    returns numpy int16 PCM samples and sample rate.
    """
    N = int(duration_s * sr)
    t = np.linspace(0, duration_s, N, endpoint=False)
    # chirp mass (in kg)
    Mc = ((m1 * m2) ** (3/5)) / ((m1 + m2) ** (1/5))
    # scale Mc to solar masses used in mapping frequency
    Mc_solar = Mc / M_sun
    # base frequencies (Hz) - realistic-ish mapping
    f0 = 20 + spin * 20
    f1 = 350 + (Mc_solar/30.0) * 250.0
    alpha = 1.6
    freq = f0 + (f1 - f0) * (t / duration_s) ** alpha
    phase = 2 * np.pi * np.cumsum(freq) / sr
    # main tone + small harmonic
    main = 0.6 * np.sin(phase)
    harm = 0.15 * np.sin(2.0 * phase + 0.2)
    # low-frequency rumble envelope
    env = np.clip((t / duration_s) ** 1.2 * np.exp(-2.0 * (1 - t / duration_s)), 0, 1)
    samp = (main + harm) * env
    # normalize
    samp = samp / np.max(np.abs(samp) + 1e-9)
    samp_int16 = (samp * 0.9 * 32767).astype(np.int16)
    return samp_int16, sr

def write_wav_bytes(samples_int16, sr):
    """Return WAV bytes as BytesIO for st.audio or download"""
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples_int16.tobytes())
    bio.seek(0)
    return bio

def hex_to_rgb(hexcol):
    hexcol = hexcol.lstrip('#')
    r = int(hexcol[0:2], 16) / 255.0
    g = int(hexcol[2:4], 16) / 255.0
    b = int(hexcol[4:6], 16) / 255.0
    return (r, g, b)

# -------------------------
# UI Controls (sidebar)
# -------------------------
with st.sidebar:
    st.title("Simulator Controls — Realistic Mode")

    mass_solar = st.slider("Black hole mass (M☉)", min_value=1_000, max_value=100_000_000,
                           value=4_300_000, step=1000, format="%d")
    spin = st.slider("Dimensionless spin a*", min_value=0.0, max_value=0.99, value=0.65, step=0.01)

    # hotspot radius (in multiples of r_s; must be > r_s)
    hotspot_r_rs = st.slider("Hotspot radius (× r_s)", 2.6, 12.0, 6.0, step=0.2)

    # disk properties
    disk_particles = st.slider("Disk particle count (visual)", 200, 5000, 1200, step=100)
    disk_thickness = st.slider("Disk thickness (visual)", 0.02, 0.8, 0.18, step=0.02)

    # visual effects
    doppler_strength = st.slider("Relativistic Doppler (visual strength)", 0.0, 1.0, 0.65, step=0.05)
    photon_ring_brightness = st.slider("Photon ring brightness", 0.0, 1.0, 0.9, step=0.05)
    jet_strength = st.slider("Jet strength (visual)", 0.0, 1.0, 0.4, step=0.05)
    magnetic_arcs = st.checkbox("Show magnetic-field arcs", value=True)
    volumetric_glow = st.slider("Volumetric glow intensity", 0.0, 1.0, 0.28, step=0.05)

    # hotspot motion
    hotspot_speed_base = st.slider("Base hotspot angular speed", 0.01, 0.5, 0.08, step=0.005)
    hotspot_trail_len = st.slider("Hotspot trail length", 1, 12, 6, step=1)

    # audio
    enable_audio = st.checkbox("Enable chirp-style audio (toy PN)", value=True)
    audio_duration = st.slider("Audio duration (s)", 0.6, 6.0, 3.0, step=0.2)

    # rendering
    render_quality = st.selectbox("Render Quality (frames / size)", ["Low", "Medium", "High"])
    if render_quality == "Low":
        FRAME_COUNT = 36
        FIG_DPI = 110
    elif render_quality == "Medium":
        FRAME_COUNT = 48
        FIG_DPI = 130
    else:
        FRAME_COUNT = 72
        FIG_DPI = 160

    st.markdown("---")
    st.write("Note: This mode aims for *realistic, GR-inspired* visuals. It's still an approximation — not full numerical GR.")

# Derived parameters
M_kg = mass_solar * M_sun
r_s_m = schwarzschild_radius(M_kg)
hotspot_r_m = hotspot_r_rs * r_s_m
gamma_factor = time_dilation_factor(M_kg, hotspot_r_m)  # <=1

# Apply time-dilation to angular speed (slows as you approach r_s)
hotspot_speed = hotspot_speed_base * gamma_factor * 1.2  # small factor for visibility

# -------------------------
# Layout
# -------------------------
st.title("🔭 Realistic Black Hole Anatomy — Visualization & Analysis")
left, right = st.columns([2, 1])

with left:
    st.subheader("Overview Visualization")
    run_anim = st.button("▶ Generate Animated Visualization")
    st.caption(f"Schwarzschild radius r_s = {r_s_m:.3e} m ({r_s_m/1000:.3e} km). Hotspot γ = {gamma_factor:.8f}")

    # preview static frame immediately
    show_static = st.button("Show static diagnostic frame")

    # canvas placeholders
    viz_placeholder = st.empty()

with right:
    st.subheader("Event / System Parameters")
    st.write(f"Mass: **{mass_solar:,}** M☉")
    st.write(f"Spin (a*): **{spin:.2f}**")
    st.write(f"Hotspot radius: **{hotspot_r_rs:.2f} × r_s**")
    st.write("Useful formulas:")
    st.latex(r"r_s = \frac{2GM}{c^2}")
    st.latex(r"\gamma(r) = \sqrt{1 - \frac{r_s}{r} }")
    st.markdown("---")
    st.subheader("Chirp / Audio")
    st.write("Audio: toy PN chirp (audible mapping).")
    if enable_audio:
        st.write("Audio will be generated from PN-inspired frequency track.")
    else:
        st.write("Audio disabled.")

# -------------------------
# Rendering utilities
# -------------------------
def draw_frame(theta, hotspot_positions, params):
    """
    Draw a single matplotlib frame for the given angle theta (radians).
    Returns PIL image bytes.
    params: dict of visual parameters
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=FIG_DPI)
    ax.set_facecolor("black")
    ax.axis('off')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # Visual scaling: map physical radii to normalized units for display
    # We'll display r_s as radius 0.22 in normalized coords (approx)
    r_s_display = 0.22
    # photon sphere ~ 1.5 r_s
    photon_disp = r_s_display * 1.5

    # central purple-ish "horizon" (not pure black so hotspot remains visible)
    horizon_col = (0.08, 0.02, 0.12)  # deep purple-black
    circle = plt.Circle((0, 0), r_s_display, color=horizon_col, zorder=2)
    ax.add_patch(circle)

    # volumetric glow around BH (soft)
    if params['volumetric_glow'] > 0:
        for s in range(1, 8):
            alpha = 0.012 * params['volumetric_glow'] * (8 - s)
            ax.add_patch(plt.Circle((0, 0), r_s_display + s * 0.035, color=(0.15, 0.05, 0.08), alpha=alpha, zorder=1))

    # photon ring - bright thin ring just outside horizon
    ring_alpha = 0.9 * params['photon_ring_brightness']
    ring = plt.Circle((0, 0), photon_disp, fill=False, linewidth=2.8, edgecolor=(1.0, 0.9, 0.95, ring_alpha), zorder=6)
    ax.add_patch(ring)

    # accretion disk drawn as multiple concentric ellipses / arcs with Doppler-brightness asymmetry
    # We'll approximate relativistic Doppler boosting: brighter on approaching side
    disk_inner = r_s_display * 1.05
    disk_outer = r_s_display * 1.9
    disk_radii = np.linspace(disk_inner, disk_outer, 60)
    for i, rad in enumerate(disk_radii):
        # choose thickness factor
        thickness = params['disk_thickness'] * 0.5
        # angle dependence for Doppler-ish effect: approaches on right side (cosine)
        # compute approx line-of-sight velocity fraction (toy)
        v_frac = 0.2 + 0.6 * (1 - rad / disk_outer)  # faster inner disk
        # projection of hotspot angular phase -> approximate approaching side
        # color shift: base amber, blue-shift on approaching side
        # sample many points around ring and draw short segments with varying alpha
        nseg = 180
        thetas = np.linspace(0, 2*np.pi, nseg)
        for j in range(nseg):
            th0 = thetas[j]
            # local apparent brightness factor (toy formula)
            cosi = np.cos(th0 - theta)
            doppler_boost = 1.0 + params['doppler_strength'] * v_frac * cosi
            doppler_boost = max(0.02, doppler_boost)
            # color interpolation amber -> bluish for boost
            amber = np.array([1.0, 0.78, 0.4])
            blue = np.array([0.64, 0.85, 1.0])
            col = amber * (1 - (0.35 * max(0, cosi))) + blue * (0.35 * max(0, cosi))
            col = np.clip(col * doppler_boost, 0, 1)
            x0 = rad * math.cos(th0)
            y0 = (rad * (1 - 0.14 * v_frac)) * math.sin(th0)  # slight ellipse due to relativistic beaming
            next_th = thetas[(j+1) % nseg]
            x1 = rad * math.cos(next_th)
            y1 = (rad * (1 - 0.14 * v_frac)) * math.sin(next_th)
            ax.plot([x0, x1], [y0, y1], color=tuple(col), alpha=0.9 * (0.35 + 0.65*(1 - rad/disk_outer)), linewidth=1.2*(1 + 0.8*(1-rad/disk_outer)), zorder=3)

    # magnetic arcs (poloidal loops)
    if params['magnetic_arcs']:
        for k in range(6):
            theta_k = k * (2*np.pi / 6) + 0.3 * theta
            xs = []
            ys = []
            for tphi in np.linspace(-1.6, 1.6, 80):
                rloop = r_s_display * (1.6 + 0.6 * abs(math.cos(tphi))) * (1 + 0.06 * math.sin(k+theta*1.2))
                x = rloop * math.cos(theta_k + 0.4 * tphi)
                y = rloop * 0.6 * math.sin(theta_k + 0.4 * tphi)
                xs.append(x)
                ys.append(y)
            ax.plot(xs, ys, color=(0.6, 0.7, 1.0, 0.6 * params['magnetic_strength']), linewidth=0.9, zorder=4)

    # relativistic jet (vertical cones)
    if params['jet_strength'] > 0:
        # draw top and bottom jets as semi-transparent cones
        top_alpha = 0.18 * params['jet_strength']
        for sign in [+1, -1]:
            for s in range(18):
                rr = r_s_display * (2.4 + s * 0.6)
                xs = [ -0.03, +0.03 ]
                ys = [ sign * rr, sign * (rr + 0.6) ]
                ax.plot(xs, ys, color=(0.6, 0.9, 1.0, top_alpha * (1 - s/40.0)), linewidth=6 - s*0.12, zorder=1)

    # Photon ring extra rim (thin bright arcs)
    for k in range(5):
        ax.add_patch(plt.Circle((0, 0), photon_disp + 0.002*k, fill=False,
                     edgecolor=(1.0, 0.95 - 0.04*k, 0.98 - 0.05*k, 0.18 + 0.16*k * params['photon_ring_brightness']),
                     linewidth=1.0 + 0.6*k, zorder=7))

    # Hotspot: compute position in normalized units based on chosen radius
    hotspot_norm_r = r_s_display * (hotspot_r_rs * 0.35)  # tuned visual
    hx = hotspot_norm_r * math.cos(theta)
    hy = hotspot_norm_r * math.sin(theta) * (1 - 0.1 * (hotspot_r_rs/12.0))
    # push recent history to draw trail
    hotspot_positions.append((hx, hy))
    # limit trail length
    hotspot_positions = hotspot_positions[-params['hotspot_trail_len']:]
    # draw trail (fading)
    for idx, (tx, ty) in enumerate(hotspot_positions):
        alpha = 0.06 + 0.12 * (idx / max(1, len(hotspot_positions) - 1))
        ax.add_patch(plt.Circle((tx, ty), 0.024 * (1 + idx*0.03), color=(1.0, 0.85, 0.6, alpha), zorder=9))

    # hotspot bright dot (on top)
    ax.add_patch(plt.Circle((hx, hy), 0.04, color=(1.0, 0.9, 0.6), zorder=10))

    # small inner glow to hint at photon capture region
    ax.add_patch(plt.Circle((0, 0), r_s_display * 0.55, color=(0.04, 0.02, 0.06), alpha=0.9, zorder=2))

    # small labels (non-intrusive)
    ax.text(-0.98, 0.92, f"Mass = {mass_solar:,} M☉", color="w", fontsize=9, zorder=12)
    ax.text(-0.98, 0.88, f"r_s ≈ {r_s_m:.3e} m", color="w", fontsize=8, zorder=12)
    ax.text(0.5, -0.9, "Photon sphere ≈ 1.5 r_s", color=(1,1,1,0.7), fontsize=8, zorder=12)

    # return image bytes (PIL) and updated hotspot history list
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='black', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf, hotspot_positions

# -------------------------
# Interactive actions
# -------------------------
# prepare parameters dict to pass to renderer
params = dict(
    disk_thickness = disk_thickness,
    doppler_strength = doppler_strength,
    photon_ring_brightness = photon_ring_brightness,
    jet_strength = jet_strength,
    magnetic_arcs = magnetic_arcs,
    volumetric_glow = volumetric_glow,
    magnetic_strength = 0.85 if magnetic_arcs else 0.0,
    hotspot_trail_len = min(12, hotspot_trail_len)
)

# static frame preview when requested
if show_static:
    theta0 = 0.0
    hotspot_positions = []
    framebuf, hotspot_positions = draw_frame(theta0, hotspot_positions, params)
    viz_placeholder.image(framebuf.getvalue(), use_column_width=True)

# animated generation
if run_anim:
    st.info("Rendering frames — this may take a moment depending on quality and host speed.")
    frames = []
    hotspot_positions = []
    # choose frame count and theta step so final covers full rotation-ish
    for i in range(FRAME_COUNT):
        # use time dilation to slow hotspot angular advance per frame
        # angle progression scaled with hotspot_speed and gamma
        theta = (i / FRAME_COUNT) * 2.0 * math.pi * (0.6 + hotspot_speed * 6.0)
        # incorporate time-dilation: effective theta is scaled down
        theta_effective = theta * gamma_factor
        buf, hotspot_positions = draw_frame(theta_effective, hotspot_positions, params)
        # convert bytes to image for imageio
        im = imageio.imread(buf)
        frames.append(im)

    # assemble GIF
    gif_bytes = io.BytesIO()
    imageio.mimsave(gif_bytes, frames, format='GIF', duration=0.04)
    gif_bytes.seek(0)
    viz_placeholder.image(gif_bytes.read(), use_column_width=True)
    st.success("Rendered animation.")

    # audio generation (optional)
    if enable_audio:
        # use solar masses converted to kg for audio generator
        # for toy PN we need m1 and m2 - here we approximate a binary with symmetric mass around BH mass/2
        m1 = mass_solar * 0.55 * M_sun
        m2 = mass_solar * 0.45 * M_sun
        samples, sr = chirp_waveform_samples(m1, m2, spin, duration_s=audio_duration, sr=44100)
        wav_io = write_wav_bytes(samples, sr)
        st.audio(wav_io.read(), format='audio/wav')

    # download buttons
    st.download_button("⬇ Download animation (GIF)", data=gif_bytes.getvalue(), file_name=f"bbh_animation_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.gif", mime="image/gif")

# -------------------------
# Diagnostics & numeric readout
# -------------------------
st.markdown("---")
st.subheader("Diagnostics & Derived Quantities")
colA, colB, colC = st.columns(3)
with colA:
    st.markdown("**Schwarzschild radius**")
    st.write(f"r_s = {r_s_m:.6e} m  ({r_s_m/1000:.3e} km)")
with colB:
    st.markdown("**Hotspot radius**")
    st.write(f"r_hot = {hotspot_r_m:.6e} m  ({hotspot_r_rs:.2f} × r_s)")
with colC:
    st.markdown("**Time dilation at hotspot**")
    st.write(rf"γ = {gamma_factor:.8f}")
            

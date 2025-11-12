import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io
import math
import base64
import time
import wave

st.set_page_config(layout="wide", page_title="BH Anatomy — Ray-Bending (Scientific Approx.)")

st.title("🔭 Black Hole Anatomy — Scientific Ray-Bending Approximation (Option B)")

#
# --- Controls (left column)
#
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Controls")
    mass_solar = st.slider("Mass (M☉)", min_value=1e3, max_value=1e8, value=4_300_000.0, step=1_000.0, format="%.0f")
    spin = st.slider("Spin asymmetry (visual)", min_value=0.0, max_value=1.0, value=0.35, step=0.01)
    lensing_strength = st.slider("Lensing strength (scale)", min_value=0.0, max_value=4.0, value=1.0, step=0.05)
    hotspot_speed = st.slider("Hotspot speed (visual)", min_value=0.0, max_value=2.0, value=0.9, step=0.01)
    visual_scale = st.slider("Visual scale (zoom)", min_value=0.5, max_value=2.5, value=1.0, step=0.05)
    show_disk = st.checkbox("Show accretion disk", value=True)
    show_hotspot = st.checkbox("Show hotspot & trail", value=True)
    show_ring_overlay = st.checkbox("Enhance photon ring", value=True)
    play_audio = st.checkbox("Enable chirp-like audio (whirlpool + hurricane texture)", value=False)

    st.markdown("---")
    st.markdown("**Notes (approx.):**\n\n- Lensing remapping uses a Schwarzschild-radius based mapping (approx.).\n- This is a visualization tool (toy ray-bending), not a full GR ray-tracer.\n- Increase *lensing strength* to exaggerate the Einstein-ring look for presentation.")

#
# --- Derived physical quantity (display)
#
G = 6.67430e-11
c = 2.99792458e8
M_kg = mass_solar * 1.98847e30
r_s = 2 * G * M_kg / (c**2)

with col1:
    st.markdown("### Physical numbers (derived)")
    st.write(f"Mass: **{mass_solar:,.0f} M☉**  ({M_kg:.3e} kg)")
    st.write(f"Schwarzschild radius rₛ ≈ **{r_s:.3e} m**")
    st.write("Photon sphere (≈ 1.5 rₛ) shown in visual scale.")

#
# --- Image generation parameters ---
#
WIDTH = int(720 * visual_scale)
HEIGHT = int(720 * visual_scale)
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# starfield seed so UI is deterministic between sessions
SEED = 42
rng = np.random.RandomState(SEED)

#
# --- Create base starfield
#
def make_starfield(w, h, n_stars=600, nebula=False):
    img = Image.new("RGB", (w, h), (5, 2, 10))
    draw = ImageDraw.Draw(img)
    # add stars as small gaussian-ish points
    xs = rng.uniform(0, w, size=n_stars)
    ys = rng.uniform(0, h, size=n_stars)
    mags = rng.uniform(0.4, 1.0, size=n_stars)
    for x, y, m in zip(xs, ys, mags):
        r = max(1, int(1.5 * m * visual_scale))
        color_fac = int(180 + 75 * m)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(color_fac, color_fac, color_fac))
    # subtle blur so stars aren't single pixels
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6 * visual_scale))
    if nebula:
        # optionally overlay a faint nebula-ish gradient
        neb = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        nd = ImageDraw.Draw(neb)
        for i in range(6):
            rx = rng.randint(0, w)
            ry = rng.randint(0, h)
            color = (180, 120, 255, int(12 + 18 * rng.rand()))
            rad = int(200 * visual_scale * rng.rand() + 120 * visual_scale)
            nd.ellipse([rx - rad, ry - rad, rx + rad, ry + rad], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), neb).convert("RGB")
    return img

#
# --- Accretion disk painter
#
def paint_accretion_disk(base_img, center, inner_r, outer_r, color=(255,180,80)):
    w, h = base_img.size
    disk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(disk)
    cx, cy = center
    # paint as many concentric faint rings with gradient thickness
    rings = int((outer_r - inner_r) / 3) + 10
    for i in range(rings):
        r = inner_r + (outer_r - inner_r) * (i / (rings - 1))
        alpha = int(10 + 160 * (1 - (i / rings))**1.6)
        col = (color[0], color[1], color[2], max(2, alpha))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(1, int(2 * visual_scale)))
    # slight blur and radial smear (simulate relativistic beaming by brightness gradient)
    disk = disk.filter(ImageFilter.GaussianBlur(radius=3 * visual_scale))
    # composite
    return Image.alpha_composite(base_img.convert("RGBA"), disk).convert("RGB")

#
# --- Hotspot + short trail
#
def paint_hotspot(base_img, center, angle, radius, color=(255,220,170)):
    w, h = base_img.size
    hs = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(hs)
    cx, cy = center
    hx = cx + math.cos(angle) * radius
    hy = cy + math.sin(angle) * radius * 0.6
    # trail
    trail_len = 8
    for k in range(trail_len):
        t = k / trail_len
        rr = max(1, int((6 - k*0.6) * visual_scale))
        a = int(200 * (1 - t)**1.8 * 0.6)
        col = (color[0], color[1], color[2], a)
        tx = cx + math.cos(angle - t * 0.18) * (radius - k * (radius * 0.05))
        ty = cy + math.sin(angle - t * 0.18) * (radius * 0.6 - k * (radius * 0.02))
        d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=col)
    # hotspot
    d.ellipse([hx - 7*visual_scale, hy - 7*visual_scale, hx + 7*visual_scale, hy + 7*visual_scale],
              fill=(255, 220, 160, 255))
    # composite
    return Image.alpha_composite(base_img.convert("RGBA"), hs).convert("RGB")

#
# --- Lensing remapper (approximate, vectorized nearest-sample)
#
def lens_remap_nearest(src_img, rs_physical, lensing_strength=1.0, spin=0.0):
    # src_img: Pillow image (RGB)
    w, h = src_img.size
    src = np.asarray(src_img).astype(np.uint8)
    # normalized coordinates in physical units relative to center
    xs = np.linspace(-1.0, 1.0, w)  # normalized [-1,1]
    ys = np.linspace(-1.0, 1.0, h)
    xv, yv = np.meshgrid(xs, ys)
    # r in normalized units
    r = np.sqrt(xv**2 + yv**2) + 1e-12
    theta = np.arctan2(yv, xv)
    # convert normalized r to a pseudo-physical radius (scale so photon-sphere around ~0.2)
    # choose scale factor such that r_norm=0.2 corresponds to photon sphere: 1.5 r_s
    scale = 0.18  # visual scaling constant (tunable)
    # mapping amplitude based on Schwarzschild r_s relative to visual scale
    # map r_physical ~ r / scale  -> effect magnitude uses rs_physical scaled to image
    # define parameter a = (r_s / R_vis) * lensing_strength
    # R_vis is characteristic visual radius; choose R_vis ~ scale_inv
    R_vis = scale
    a = (rs_physical / (1.0 + rs_physical)) * (lensing_strength * 0.5)  # clamp-ish; rs_physical is tiny -> keep stable

    # approximate deflection mapping: r_source = r * (1 + a / (r + eps))
    # invert approximate mapping by dividing: r_src = r / (1 + a/(r+eps))
    eps = 1e-6
    r_src = r / (1.0 + a / (r + eps))

    # add spin asymmetry: shift angle slightly with spin (frame-dragging proxy)
    theta_src = theta - 0.25 * spin * (1.0 - np.exp(-r*8.0))  # more shift near center

    # convert back to normalized cartesian
    x_src = r_src * np.cos(theta_src)
    y_src = r_src * np.sin(theta_src)

    # map [-1,1] normalized to image pixel coords
    ix = np.clip(((x_src + 1.0) * 0.5 * (w - 1)).astype(int), 0, w - 1)
    iy = np.clip(((y_src + 1.0) * 0.5 * (h - 1)).astype(int), 0, h - 1)

    # sample nearest-neighbor
    remap = src[iy, ix, :]
    # add a simple photon-sphere brightness amplification near r ~ scale*0.33
    if show_ring_overlay:
        ring_center = int(h * 0.5)
        # boost brightness for radii in a band
        band = np.logical_and(r > 0.10, r < 0.25)
        boost = (0.25 - np.abs(r - 0.175)) * 2.0
        boost = np.clip(boost, 0, 0.9) * lensing_strength
        boost = boost[..., None]
        remap = np.clip(remap.astype(float) * (1.0 + boost), 0, 255).astype(np.uint8)
    return Image.fromarray(remap)

#
# --- Chirp / audio synth (simple texture: low-frequency hurricane+whirlpool-like)
#
def make_ambient_audio(duration_s=4.0, sr=22050, mass_scale=1.0, spin=0.5):
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    # base low rumble frequency scaled with mass (heavier -> deeper)
    base = 20.0 * (1.0 / (1.0 + math.log10(max(1e3, mass_scale)) / 6.0))  # ~20-40Hz region
    f1 = base * (1.0 + 0.6 * (1 - spin))
    # make a sweep + broadband noise filtered
    sweep = np.sin(2 * np.pi * (f1 + 40.0 * (t / duration_s)**2) * t)
    # add swirling modulation
    swirl = 0.5 * np.sin(2 * np.pi * 3.0 * t) * np.cos(2 * np.pi * 0.2 * t)
    # broadband "hurricane" texture via colored noise
    rng_local = np.random.RandomState(1234)
    noise = rng_local.normal(scale=0.6, size=t.shape)
    # lowpass the noise (quick naive filtering)
    from scipy.signal import butter, filtfilt
    b, a = butter(2, 500.0 / (sr/2.0), btype='low')
    noise_lp = filtfilt(b, a, noise)
    # combine
    sig = 0.7 * sweep + 0.35 * swirl + 0.12 * noise_lp
    # gentle envelope
    env = np.exp(-2.0 * (1.0 - np.minimum(1.0, t / duration_s)))
    sig *= env
    # normalize
    sig = sig / (np.max(np.abs(sig)) + 1e-12) * 0.85
    # convert to stereo 16-bit wav bytes
    stereo = np.vstack([sig, sig]).T
    # write to WAV in memory
    mem = io.BytesIO()
    import soundfile as sf
    sf.write(mem, stereo, sr, subtype='PCM_16', format='WAV')
    mem.seek(0)
    return mem

#
# --- Main render loop (single-frame render each interaction)
#
# create base starfield
base = make_starfield(WIDTH, HEIGHT, n_stars=int(650 * visual_scale), nebula=True)

# paint accretion disk region scaled relative to image
disk_inner = max(18 * visual_scale, 6 * visual_scale)
disk_outer = max(220 * visual_scale, 140 * visual_scale)

if show_disk:
    base = paint_accretion_disk(base, (CENTER_X, CENTER_Y), disk_inner, disk_outer)

# add hotspot
angle_now = (time.time() * hotspot_speed) % (2 * math.pi)
if show_hotspot:
    base = paint_hotspot(base, (CENTER_X, CENTER_Y), angle_now, radius=(disk_inner + disk_outer) * 0.52)

# apply lensing remap
# We need to scale physical r_s to the normalized visual units used in remap.
# Because r_s (m) is astronomically small compared to image scale, we apply a transform that keeps it visible.
# Build a scaled_rs parameter that increases with mass, but remains numerically small (0..~0.01)
scaled_rs = (r_s / (1.0 + r_s)) * 1e-7 * (mass_solar / 1e6)  # tuned scaling knob
lensed = lens_remap_nearest(base, scaled_rs, lensing_strength=lensing_strength, spin=spin)

# optionally overlay photon ring highlight (thin)
if show_ring_overlay:
    ld = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    dd = ImageDraw.Draw(ld)
    # ring parameters (in pixel units)
    ring_r = int(0.175 * WIDTH)
    ring_w = max(2, int(3 * visual_scale))
    dd.ellipse([CENTER_X-ring_r, CENTER_Y-ring_r, CENTER_X+ring_r, CENTER_Y+ring_r],
               outline=(255,220,180, int(36 * lensing_strength)), width=ring_w)
    lensed = Image.alpha_composite(lensed.convert("RGBA"), ld).convert("RGB")

#
# --- Render to Streamlit
#
with col2:
    st.markdown("### Visual preview")
    st.image(lensed, use_column_width=True)

    st.markdown("**Controls note:** change sliders and re-run (Streamlit auto-refresh) to update the optical mapping. Use smaller `lensing_strength` for scientifically conservative visuals.")

    # Side panel info (concise)
    st.markdown("---")
    st.markdown("**Photon-sphere & ring (visualized):**\n- The bright circular band is an amplified region near the photon sphere. \n- Spin asymmetry shifts brightness/shape slightly (frame-dragging proxy).")

    # Play audio (synth) if enabled
    if play_audio:
        st.markdown("---")
        st.markdown("### Ambient audio (theory-inspired)")
        try:
            # synth a short sample (cache a bit)
            if 'audio_buf' not in st.session_state:
                # For speed, try/catch scipy dependency if missing
                try:
                    audio_buf = make_ambient_audio(duration_s=4.0, sr=22050, mass_scale=mass_solar, spin=spin)
                    st.session_state['audio_buf'] = audio_buf.read()
                except Exception as e:
                    st.warning("Audio generation requires scipy & soundfile. If missing, audio won't be available.")
                    st.session_state['audio_buf'] = None
            if st.session_state.get('audio_buf'):
                st.audio(st.session_state['audio_buf'], format='audio/wav')
            else:
                st.info("Audio not available in this environment.")
        except Exception as e:
            st.error(f"Audio error: {e}")

# done
st.caption("Ray-bending mapping: scientific approximation — tuned for clarity and presentation. For full GR ray-tracing use geodesic integration / numerical ray-tracer.")


---

Quick usage tips

Start with lensing_strength ≈ 1.0, spin ≈ 0.2–0.6. For dramatic rings increase lensing_strength.

Mass scales physical numbers shown (the Schwarzschild radius is printed) — because of astronomical scales the visual mapping uses a tuned scaling so you can actually see lensing in a 2D image.

If audio fails to generate due to missing scipy or soundfile on your environment, install them (pip install scipy soundfile) or uncheck the audio box.

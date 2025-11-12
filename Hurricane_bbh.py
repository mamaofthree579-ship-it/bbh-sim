import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io, math, time, base64
import wave

st.set_page_config(layout="wide", page_title="BH Anatomy — Bilinear Ray-Bending (Option B)")

st.title("🔭 Black Hole Anatomy — Scientific Ray-Bending (Bilinear sampling)")

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
    visual_scale = st.slider("Visual scale (zoom)", min_value=0.6, max_value=2.2, value=1.0, step=0.05)
    show_disk = st.checkbox("Show accretion disk", value=True)
    show_hotspot = st.checkbox("Show hotspot & trail", value=True)
    show_ring_overlay = st.checkbox("Enhance photon ring", value=True)
    play_audio = st.checkbox("Enable ambient audio (whirlpool + hurricane)", value=False)

    st.markdown("---")
    st.markdown("**Notes:** This uses a Schwarzschild-based, approximate remap and **bilinear** sampling for smoother output. Not a full GR ray-tracer — it's a fast visual approximation.")

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

# deterministic randomness
SEED = 42
rng = np.random.RandomState(SEED)

#
# --- Starfield generator (kept but subdued) ---
#
def make_starfield(w, h, n_stars=600, nebula=False):
    img = Image.new("RGB", (w, h), (5, 2, 10))
    draw = ImageDraw.Draw(img)
    xs = rng.uniform(0, w, size=n_stars)
    ys = rng.uniform(0, h, size=n_stars)
    mags = rng.uniform(0.35, 1.0, size=n_stars)
    for x, y, m in zip(xs, ys, mags):
        r = max(1, int(1.2 * m * visual_scale))
        color_fac = int(200 * m)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(color_fac, color_fac, color_fac))
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6 * visual_scale))
    if nebula:
        neb = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        nd = ImageDraw.Draw(neb)
        for i in range(5):
            rx = rng.randint(0, w)
            ry = rng.randint(0, h)
            color = (150 + rng.randint(0,100), 90 + rng.randint(0,90), 220, int(10 + 20 * rng.rand()))
            rad = int(160 * visual_scale * rng.rand() + 90 * visual_scale)
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
    rings = int((outer_r - inner_r) / 3) + 10
    for i in range(rings):
        r = inner_r + (outer_r - inner_r) * (i / (rings - 1))
        alpha = int(8 + 150 * (1 - (i / rings))**1.6)
        col = (color[0], color[1], color[2], max(2, alpha))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(1, int(2 * visual_scale)))
    disk = disk.filter(ImageFilter.GaussianBlur(radius=2.6 * visual_scale))
    return Image.alpha_composite(base_img.convert("RGBA"), disk).convert("RGB")

#
# --- Hotspot + trail painter
#
def paint_hotspot(base_img, center, angle, radius, color=(255,220,170)):
    w, h = base_img.size
    hs = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(hs)
    cx, cy = center
    hx = cx + math.cos(angle) * radius
    hy = cy + math.sin(angle) * radius * 0.62
    trail_len = 8
    for k in range(trail_len):
        t = k / trail_len
        rr = max(1, int((5.6 - k*0.5) * visual_scale))
        a = int(200 * (1 - t)**1.9 * 0.7)
        col = (color[0], color[1], color[2], a)
        tx = cx + math.cos(angle - t * 0.18) * (radius - k * (radius * 0.05))
        ty = cy + math.sin(angle - t * 0.18) * (radius * 0.62 - k * (radius * 0.02))
        d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=col)
    d.ellipse([hx - 6*visual_scale, hy - 6*visual_scale, hx + 6*visual_scale, hy + 6*visual_scale],
              fill=(255, 220, 160, 255))
    return Image.alpha_composite(base_img.convert("RGBA"), hs).convert("RGB")

#
# --- Bilinear sampling remapper (vectorized)
#
def bilinear_remap(src_img, rs_physical, lensing_strength=1.0, spin=0.0):
    # src_img: Pillow RGB image
    w, h = src_img.size
    src = np.asarray(src_img).astype(np.float32)
    # normalized coordinates [-1,1]
    xs = np.linspace(-1.0, 1.0, w)
    ys = np.linspace(-1.0, 1.0, h)
    xv, yv = np.meshgrid(xs, ys)
    r = np.sqrt(xv**2 + yv**2) + 1e-12
    theta = np.arctan2(yv, xv)

    # visual scaling constants (tuned)
    scale = 0.18
    R_vis = scale
    a = (rs_physical / (1.0 + rs_physical)) * (lensing_strength * 0.5)

    eps = 1e-6
    r_src = r / (1.0 + a / (r + eps))
    theta_src = theta - 0.25 * spin * (1.0 - np.exp(-r*8.0))

    x_src = r_src * np.cos(theta_src)
    y_src = r_src * np.sin(theta_src)

    # map [-1,1] to pixel coords (float)
    fx = (x_src + 1.0) * 0.5 * (w - 1)
    fy = (y_src + 1.0) * 0.5 * (h - 1)

    # bilinear interpolation
    x0 = np.floor(fx).astype(np.int32)
    x1 = np.clip(x0 + 1, 0, w - 1)
    y0 = np.floor(fy).astype(np.int32)
    y1 = np.clip(y0 + 1, 0, h - 1)

    # weights
    wx = fx - x0
    wy = fy - y0

    # sample four corners
    Ia = src[y0, x0, :]
    Ib = src[y0, x1, :]
    Ic = src[y1, x0, :]
    Id = src[y1, x1, :]

    # interpolate along x, then y
    Iab = Ia * (1 - wx[..., None]) + Ib * (wx[..., None])
    Icd = Ic * (1 - wx[..., None]) + Id * (wx[..., None])
    I = Iab * (1 - wy[..., None]) + Icd * (wy[..., None])

    # photon-sphere boost band
    if show_ring_overlay:
        boost = np.zeros((h, w), dtype=np.float32)
        band = np.logical_and(r > 0.10, r < 0.25)
        boost_val = (0.25 - np.abs(r - 0.175)) * 2.0  # small positive
        boost_val = np.clip(boost_val, 0, 0.9) * lensing_strength
        boost = boost_val
        I = np.clip(I * (1.0 + boost[..., None]), 0, 255)

    I = I.astype(np.uint8)
    return Image.fromarray(I)

#
# --- Simple FFT lowpass for audio texture (avoid scipy dependency)
#
def lowpass_fft(sig, sr, cutoff=800.0):
    # naive FFT lowpass
    N = sig.shape[0]
    fft = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(N, 1/sr)
    mask = freqs <= cutoff
    fft[~mask] = 0
    out = np.fft.irfft(fft, n=N)
    return out

#
# --- Ambient audio generator (no scipy)
#
def make_ambient_audio(duration_s=4.0, sr=22050, mass_scale=1.0, spin=0.5):
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    base = 18.0 * (1.0 / (1.0 + math.log10(max(1e3, mass_scale)) / 6.0))
    f1 = base * (1.0 + 0.6 * (1 - spin))
    sweep = np.sin(2 * np.pi * (f1 + 40.0 * (t / duration_s)**2) * t)
    swirl = 0.5 * np.sin(2 * np.pi * 3.0 * t) * np.cos(2 * np.pi * 0.2 * t)
    rng_local = np.random.RandomState(12345)
    noise = rng_local.normal(scale=0.7, size=t.shape)
    noise_lp = lowpass_fft(noise, sr, cutoff=600.0)
    sig = 0.75 * sweep + 0.40 * swirl + 0.12 * noise_lp
    env = np.minimum(1.0, 1.0 - 0.6 * (t / duration_s))
    sig *= env
    sig = sig / (np.max(np.abs(sig)) + 1e-12) * 0.85
    stereo = np.vstack([sig, sig]).T
    mem = io.BytesIO()
    try:
        import soundfile as sf
        sf.write(mem, stereo, sr, subtype='PCM_16', format='WAV')
        mem.seek(0)
        return mem
    except Exception:
        # fallback: return None if soundfile isn't available
        return None

#
# --- Build scene & remap (single frame)
#
base = make_starfield(WIDTH, HEIGHT, n_stars=int(580 * visual_scale), nebula=True)

disk_inner = max(18 * visual_scale, 6 * visual_scale)
disk_outer = max(220 * visual_scale, 140 * visual_scale)

if show_disk:
    base = paint_accretion_disk(base, (CENTER_X, CENTER_Y), disk_inner, disk_outer)

angle_now = (time.time() * hotspot_speed) % (2 * math.pi)
if show_hotspot:
    base = paint_hotspot(base, (CENTER_X, CENTER_Y), angle_now, radius=(disk_inner + disk_outer) * 0.52)

# scale r_s into a small param for remap (tuned)
scaled_rs = (r_s / (1.0 + r_s)) * 1e-7 * (mass_solar / 1e6)

lensed = bilinear_remap(base, scaled_rs, lensing_strength=lensing_strength, spin=spin)

if show_ring_overlay:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    ring_r = int(0.175 * WIDTH)
    ring_w = max(1, int(3 * visual_scale))
    od.ellipse([CENTER_X-ring_r, CENTER_Y-ring_r, CENTER_X+ring_r, CENTER_Y+ring_r],
               outline=(255,220,180, int(38 * lensing_strength)), width=ring_w)
    lensed = Image.alpha_composite(lensed.convert("RGBA"), overlay).convert("RGB")

#
# --- Display
#
with col2:
    st.markdown("### Visual preview")
    st.image(lensed, use_column_width=True)
    st.markdown("---")
    st.markdown("**Photon sphere note:** The bright band is an amplified visual proxy for the photon-sphere; spin produces slight azimuthal brightness asymmetry.")

    if play_audio:
        st.markdown("---")
        st.markdown("### Ambient audio (theory-inspired)")
        audio_buf = make_ambient_audio(duration_s=4.0, sr=22050, mass_scale=mass_solar, spin=spin)
        if audio_buf:
            st.audio(audio_buf.read(), format='audio/wav')
        else:
            st.info("Audio unavailable: `soundfile` not installed in environment.")

st.caption("Bilinear remapping applied for smoother lens visuals. For higher-physical-fidelity ray tracing use geodesic integration / a GR raytracer.")

import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io, math, time, wave, struct, os

st.set_page_config(page_title="Black Hole Anatomy — Preview", layout="wide")

st.title("🔭 Black Hole Anatomy — Animated Preview + Ambient Sound")
st.markdown(
    "This preview generates a short animated GIF of a rotating hotspot + accretion disk "
    "and optionally synthesizes an ambient 'vortex+storm' audio to accompany the visual."
)

# ---- Controls ----
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Visual controls")
    canvas_w = st.slider("Canvas width (px)", 480, 1200, 920, step=64)
    canvas_h = int(canvas_w * 0.46)
    hotspot_speed = st.slider("Hotspot angular speed (visual)", 0.01, 0.16, 0.026, step=0.002)
    trail_strength = st.slider("Trail length (frames)", 0, 24, 8, step=1)
    disk_rings = st.slider("Accretion disk rings", 6, 60, 28, step=1)
    horizon_color = st.color_picker("Horizon color (visual)", "#2f0050")
    disk_accent = st.color_picker("Disk accent", "#ffb24a")
    frames = st.slider("GIF frames", 12, 64, 28, step=4)
    duration_s = st.slider("GIF length (seconds)", 1, 6, 2, step=1)

with col2:
    st.subheader("Audio")
    synth_audio = st.checkbox("Generate ambient audio (vortex + storm)", value=True)
    audio_duration = st.slider("Audio duration (s)", 1.0, 8.0, 3.0, step=0.5)
    audio_loudness = st.slider("Audio loudness (0.0 - 1.0)", 0.0, 1.0, 0.28, step=0.02)

st.markdown("---")

# ---- Helper: draw single frame ----
def draw_frame(w, h, angle, horizon_r=70, hotspot_phase=0.0,
               horizon_col="#2f0050", disk_accent="#ffb24a",
               rings=28, trail_positions=None):
    im = Image.new("RGBA", (w, h), (3, 2, 6, 255))
    draw = ImageDraw.Draw(im, "RGBA")

    cx, cy = w // 2, h // 2
    # background radial subtle
    bg = Image.new("RGBA", (w, h), (0,0,0,0))
    bg_draw = ImageDraw.Draw(bg)
    # soft vignette by drawing ellipses
    for i, alpha in enumerate([6, 8, 10, 12]):
        r = max(w, h) * (0.5 + i*0.04)
        bbox = [cx - r, cy - r, cx + r, cy + r]
        bg_draw.ellipse(bbox, fill=(5,3,10,alpha))
    im = Image.alpha_composite(im, bg)

    # accretion disk rings
    for i in range(rings):
        rr = horizon_r + 8 + i * ( (w*0.22) / max(1, rings) )
        alpha = 4 + i * 2
        color = tuple(int(disk_accent.lstrip("#")[j:j+2], 16) for j in (0,2,4))
        draw.ellipse((cx-rr, cy-rr, cx+rr, cy+rr),
                     outline=(color[0], color[1], color[2], min(160, alpha)),
                     width=1)

    # event horizon (filled with subtle purple instead of pure black)
    hc = tuple(int(horizon_col.lstrip("#")[j:j+2], 16) for j in (0,2,4))
    draw.ellipse((cx-horizon_r, cy-horizon_r, cx+horizon_r, cy+horizon_r),
                 fill=(hc[0], hc[1], hc[2], 255))

    # inner black core (slightly darker to allow hotspot glow to pass 'behind' visually)
    core_r = int(horizon_r * 0.84)
    draw.ellipse((cx-core_r, cy-core_r, cx+core_r, cy+core_r),
                 fill=(0,0,0,255))

    # hotspot (orbiting light blob) + trail
    orb_radius = int(horizon_r * 1.57)
    hx = cx + math.cos(angle + hotspot_phase) * orb_radius
    hy = cy + math.sin(angle + hotspot_phase) * (orb_radius * 0.32)
    # draw trail positions (faded)
    if isinstance(trail_positions, list):
        for idx, (tx, ty) in enumerate(trail_positions):
            alpha = int(10 + (idx / max(1, len(trail_positions)-1)) * 160)
            r = max(1, 6 - idx*0.5)
            draw.ellipse((tx-r, ty-r, tx+r, ty+r), fill=(255,200,150,alpha))
    # hotspot core
    draw.ellipse((hx-6, hy-6, hx+6, hy+6), fill=(255,220,153,255))

    # a subtle jet cone above
    draw.rectangle((cx-5, 0, cx+5, cy-120), fill=(120,200,255,20))

    # finally, slight gaussian blur for atmosphere, then sharpen
    im = im.filter(ImageFilter.GaussianBlur(radius=0.8))
    return im

# ---- Generate GIF helper ----
def make_gif_bytes(w, h, frames, duration_s, speed, trail_len,
                   horizon_col, disk_accent, rings):
    imgs = []
    trail_buffer = []
    for i in range(frames):
        t = i / frames
        angle = i * (2 * math.pi / frames) * (speed * 10.0)
        # maintain trail buffer of recent hotspot positions
        orb_radius = int(70 * (w / 920) * 1.57)
        cx, cy = w // 2, h // 2
        hx = cx + math.cos(angle) * orb_radius
        hy = cy + math.sin(angle) * (orb_radius * 0.32)
        trail_buffer.insert(0, (hx, hy))
        if len(trail_buffer) > trail_len:
            trail_buffer = trail_buffer[:trail_len]
        im = draw_frame(w, h, angle, horizon_r=int(70*(w/920)),
                        hotspot_phase=0, horizon_col=horizon_col,
                        disk_accent=disk_accent, rings=rings,
                        trail_positions=list(trail_buffer))
        imgs.append(im.convert("P", palette=Image.ADAPTIVE))
    # save GIF to bytes
    bio = io.BytesIO()
    imgs[0].save(bio, format="GIF", save_all=True, append_images=imgs[1:],
                 duration=max(20, int(duration_s*1000/len(imgs))), loop=0, optimize=True)
    bio.seek(0)
    return bio.getvalue()

# ---- Audio synthesis helper (vortex + filtered noise) ----
def synthesize_ambient_wav(duration=3.0, sr=44100, loudness=0.28, spin=0.5):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    # low vortex: slow sine + small FM (sweep)
    base_freq = 20 + spin*10  # low fundamental
    sweep = base_freq + (np.sin(t * 0.2) * (6 + 8*spin))
    vortex = 0.9 * np.sin(2*np.pi * (sweep * t + 0.2*np.sin(2*np.pi*0.5*t)))
    # filtered wind noise: generate white noise and single-pole lowpass filter
    noise = np.random.normal(0, 1.0, size=t.shape)
    # simple one-pole lowpass (rc-like)
    rc = 1.0 / (2 * math.pi * (40 + 120*spin))
    alpha = (1.0 / sr) / (rc + (1.0 / sr))
    filt = np.zeros_like(noise)
    for i in range(1, len(noise)):
        filt[i] = filt[i-1] + alpha * (noise[i] - filt[i-1])
    wind = filt * np.hanning(len(t)) * 0.8
    # gentle pulsing amplitude linked to hotspot (simulate passing hot region)
    pulse = 0.3 + 0.7 * (0.5*(1 + np.sin(2*np.pi*(0.6 + 0.4*spin) * t)))
    out = (0.6 * vortex + 0.9 * wind) * pulse
    # Normalize to 16-bit range
    out = out / (np.max(np.abs(out)) + 1e-9)
    out = out * (loudness * 0.9)
    # convert to 16-bit PCM
    pcm = np.int16(out * 32767)
    # write WAV to bytes
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    bio.seek(0)
    return bio.getvalue()

# ---- UI actions ----
col_vis, col_out = st.columns([1, 1])
with col_vis:
    if st.button("Generate Animated Preview (GIF)"):
        with st.spinner("Rendering GIF..."):
            gif_bytes = make_gif_bytes(canvas_w, canvas_h, frames, duration_s,
                                       hotspot_speed, trail_strength,
                                       horizon_color, disk_accent, disk_rings)
            st.session_state["last_gif"] = gif_bytes
            st.success("GIF rendered — preview below.")

    if "last_gif" in st.session_state:
        st.image(st.session_state["last_gif"], use_column_width=True)
    else:
        st.info("No preview yet — click **Generate Animated Preview (GIF)**")

with col_out:
    if synth_audio:
        if st.button("Synthesize Ambient Audio (WAV)"):
            with st.spinner("Generating audio..."):
                wav_bytes = synthesize_ambient_wav(duration=audio_duration,
                                                   loudness=audio_loudness,
                                                   spin=float(spin_input if (spin_input := st.session_state.get('spin_input')) else 0.5) )
                st.session_state["last_wav"] = wav_bytes
                st.success("Audio synthesized — play below.")
        if "last_wav" in st.session_state:
            st.audio(st.session_state["last_wav"], format="audio/wav")
        else:
            st.info("No audio yet — click **Synthesize Ambient Audio (WAV)**")
    else:
        st.info("Audio is disabled. Check the 'Generate ambient audio' checkbox to enable.")

st.markdown("---")
st.caption("Implementation note: this app produces a GIF preview (safe & stable in Streamlit) and an optional synthesized WAV. "
           "If you want true real-time interactive animation, we can next add a WebGL-based front end (Plotly/three.js) or an HTML canvas with live JS — but those require a different embedding approach in Streamlit.")

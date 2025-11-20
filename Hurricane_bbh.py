import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import io, json, wave, struct, base64, math
from datetime import datetime

st.set_page_config(page_title="Black Hole Simulator", layout="wide")

# --- UI: Left controls / Right preview ---
st.title("🌌 Black Hole Anatomy & Sound Studio")

left, right = st.columns([1, 2])

with left:
    st.header("Controls")

    # Physical / visual mapping (for display only)
    mass = st.slider("Mass (visual scale, M☉)", min_value=1e3, max_value=1e8, value=4_300_000.0, step=1000.0, format="%d")
    # Note: mass here is purely visual scaling; we keep it float for safety
    hotspot_speed = st.slider("Hotspot speed (motion)", 0.0, 2.0, 0.26, step=0.01)
    trail_length = st.slider("Hotspot trail length", 1, 13, 6, step=1)
    disk_color = st.color_picker("Accretion disk accent color", "#ffb452")
    show_stars = st.checkbox("Show starfield (off recommended)", value=False)
    disk_thickness = st.slider("Disk thickness (visual)", 1, 60, 24, step=1)

    st.markdown("---")
    st.subheader("Audio / Sound")
    audio_choice = st.selectbox("Sound to generate", ["None", "Chirp (merger-like)", "Whirlpool+Hurricane (ambient)"])
    audio_duration = st.slider("Audio duration (s)", 0.8, 8.0, 3.0, step=0.1)
    audio_gain = st.slider("Audio gain (0.0 - 1.0)", 0.0, 1.0, 0.28, step=0.01)

    st.markdown("---")
    st.subheader("Actions")
    render_btn = st.button("Render Animation")
    gen_audio_btn = st.button("Generate Audio")
    export_btn = st.button("Export params+waveform")

    st.markdown("---")
    st.caption("Tip: press Render Animation, then Generate Audio (if desired). Audio will appear as a playable WAV player below.")

with right:
    st.header("Preview")
    preview_area = st.empty()
    audio_area = st.empty()
    info_area = st.empty()

# --- Helpers: wave generation (write PCM16 WAV to bytes) ---
def float_to_pcm16_bytes(samples: np.ndarray, gain=0.3, samplerate=44100):
    """
    Convert float32 samples (-1..1) to PCM16 bytes in-memory.
    """
    # clip and scale
    samples = np.asarray(samples, dtype=np.float32)
    samples = samples * float(gain)
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767.0).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes(int_samples.tobytes())
    buf.seek(0)
    return buf.read()

# --- Chirp generator (exponential sweep) ---
def generate_chirp_audio(duration=3.0, f_start=20.0, f_end=2000.0, samplerate=44100, gain=0.28):
    N = int(duration * samplerate)
    t = np.linspace(0, duration, N, endpoint=False)
    # exponential sweep formula
    if f_start <= 0: f_start = 0.1
    K = duration / np.log(f_end / f_start)
    instantaneous_phase = 2 * np.pi * K * (f_start * (np.exp(t / K) - 1.0))
    sig = np.sin(instantaneous_phase)
    # envelope
    env = np.sin(np.pi * t / duration) ** 0.9
    samples = sig * env
    return float_to_pcm16_bytes(samples, gain=gain, samplerate=samplerate)

# --- Whirlpool + Hurricane ambient generator (synth + colored noise) ---
def generate_whirlpool_hurricane(duration=3.0, samplerate=44100, gain=0.28):
    N = int(duration * samplerate)
    t = np.linspace(0, duration, N, endpoint=False)

    # Low-frequency rotating core (like a whirlpool)
    core_freq = 4.0  # low hum
    core = 0.5 * np.sin(2 * np.pi * core_freq * t)

    # Sweeping turbulent component (a slow frequency sweep)
    sweep = np.sin(2 * np.pi * (20.0 + 80.0 * (t / duration)) * t * 0.5)

    # Colored noise: pink-ish via filtering white noise in frequency domain
    wn = np.random.normal(0, 1, N)
    # simple 1/f filter by dividing FFT bins by sqrt(freq)
    fft = np.fft.rfft(wn)
    freqs = np.fft.rfftfreq(N, 1.0/samplerate)
    # avoid divide by zero
    freqs[0] = freqs[1] if len(freqs) > 1 else 1.0
    fft_filtered = fft / np.sqrt(freqs)
    pink = np.fft.irfft(fft_filtered, n=N)
    pink = pink / (np.max(np.abs(pink)) + 1e-9)

    # amplitude envelope: strong at middle, taper at edges
    env = (np.sin(np.pi * t / duration)) ** 1.2
    samples = 0.6 * core + 0.35 * sweep + 0.8 * 0.8 * pink
    samples *= env
    # mild distortion & normalization
    samples = samples / (np.max(np.abs(samples)) + 1e-9)
    return float_to_pcm16_bytes(samples, gain=gain, samplerate=samplerate)

# --- Animation renderer (non-blocking) ---
def render_bh_animation(frames=120, hotspot_speed=0.26, trail_len=6, disk_color="#ffb452",
                        show_stars=False, disk_thickness=24, mass_visual=4_300_000.0, fps=30):
    """
    Create an in-memory GIF showing:
    - accretion rings
    - rotating hotspot with trail
    - optional subtle starfield in background (off by default)
    Returns: GIF bytes
    """
    # visual scale param mapping (purely aesthetic)
    scale = np.clip(np.log10(max(mass_visual, 1000.0)) - 2.0, 0.6, 6.0)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(-2 * scale, 2 * scale)
    ax.set_ylim(-2 * scale, 2 * scale)
    ax.set_aspect('equal')
    ax.axis('off')

    # precompute ring radii
    horizon_R = 0.6 * scale
    ring_radii = [horizon_R + 0.2 + (i * (disk_thickness / 60.0)) for i in range(20)]

    # objects to draw
    rings_lines = [ax.plot([], [], lw=1, solid_capstyle='round', color=disk_color, alpha=0.12)[0] for _ in ring_radii]
    hotspot_point, = ax.plot([], [], 'o', color='#ffd9b3', markersize=8)
    trail_line, = ax.plot([], [], '-', color='#ffd9b3', alpha=0.6, lw=2)
    star_pts = None
    if show_stars:
        # place faint points around edges — not inside horizon (simple radial mask)
        Nstars = 120
        angles = np.random.rand(Nstars) * 2 * np.pi
        rs = np.random.uniform(horizon_R + 0.6*scale, 1.9*scale, Nstars)
        xs = rs * np.cos(angles)
        ys = rs * np.sin(angles)
        star_pts = ax.scatter(xs, ys, s=np.random.uniform(3, 8, Nstars), c='white', alpha=0.6)

    trail_xs, trail_ys = [], []

    def init():
        for ln in rings_lines:
            ln.set_data([], [])
        hotspot_point.set_data([], [])
        trail_line.set_data([], [])
        return rings_lines + [hotspot_point, trail_line] + ([star_pts] if star_pts is not None else [])

    def update(i):
        # time angle (controls hotspot)
        angle = i * (hotspot_speed * 0.12 + 0.02)
        # hotspot orbit radius (visual)
        hx = (horizon_R + 0.9 * scale) * math.cos(angle)
        hy = (horizon_R + 0.9 * scale) * math.sin(angle * 0.86)  # elliptical wobble

        # rings
        for idx, r in enumerate(ring_radii):
            theta = np.linspace(0, 2 * np.pi, 180)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            # slight brightness modulation to give motion impression
            alpha = 0.006 + (idx / len(ring_radii)) * 0.012 + 0.02 * math.sin(i * 0.08 + idx)
            rings_lines[idx].set_data(x, y)
            rings_lines[idx].set_alpha(alpha)

        # hotspot trail
        trail_xs.insert(0, hx)
        trail_ys.insert(0, hy)
        if len(trail_xs) > trail_len:
            trail_xs.pop()
            trail_ys.pop()
        hotspot_point.set_data(hx, hy)
        trail_line.set_data(trail_xs, trail_ys)
        # trail fade handled by alpha; matplotlib can't do per-point alpha easily without LineCollection; keep simple

        return rings_lines + [hotspot_point, trail_line]

    # create animation and save to GIF into buffer
    ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=1000/fps, repeat=False)
    buf = io.BytesIO()
    try:
        ani.save(buf, writer='pillow', fps=fps)
    except Exception as e:
        # fallback: render frames manually and save (less efficient)
        frames_list = []
        for idx in range(frames):
            update(idx)
            buf_frame = io.BytesIO()
            fig.canvas.draw()
            img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            w, h = fig.canvas.get_width_height()
            img = img.reshape((h, w, 3))
            import PIL.Image as Image
            pil = Image.fromarray(img)
            frames_list.append(pil.convert("P"))
        if frames_list:
            frames_list[0].save(buf, format="GIF", save_all=True, append_images=frames_list[1:], loop=0, duration=int(1000/fps))
    buf.seek(0)
    plt.close(fig)
    return buf.read()

# --- Main actions: render GIF & audio generation ---
gif_bytes = None
if render_btn:
    with st.spinner("Rendering animation — this returns quickly, please wait..."):
        gif_bytes = render_bh_animation(frames=140, hotspot_speed=hotspot_speed, trail_len=trail_length,
                                       disk_color=disk_color, show_stars=show_stars, disk_thickness=disk_thickness,
                                       mass_visual=mass, fps=30)
        preview_area.image(gif_bytes, use_column_width=True)
        info_area.markdown(f"**Rendered:** {datetime.utcnow().isoformat()} UTC  \nMass (visual) = {int(mass):,} M☉ — hotspot speed {hotspot_speed:.2f} — trail {trail_length}")
else:
    preview_area.info("Click **Render Animation** to produce the visualization GIF.")

# audio generation
if gen_audio_btn:
    if audio_choice == "None":
        audio_area.info("No audio selected.")
    else:
        with st.spinner("Generating audio..."):
            if audio_choice == "Chirp (merger-like)":
                # generate chirp params loosely tied to mass and visual spin
                f0 = 20 + (hotspot_speed * 8.0)
                f1 = 400 + (np.clip(np.log10(mass + 1.0), 3.0, 8.0) - 3.0) * 200.0
                wav_bytes = generate_chirp_audio(duration=audio_duration, f_start=f0, f_end=f1, gain=audio_gain)
                audio_area.audio(wav_bytes, format="audio/wav")
                audio_area.markdown(f"Chirp generated: {f0:.1f} Hz → {f1:.1f} Hz, {audio_duration:.2f}s")
            else:
                wav_bytes = generate_whirlpool_hurricane(duration=audio_duration, gain=audio_gain)
                audio_area.audio(wav_bytes, format="audio/wav")
                audio_area.markdown(f"Whirlpool+Hurricane ambient, {audio_duration:.2f}s")

# export params + waveform (if generated)
if export_btn:
    # build payload: params + (if audio recently generated) sample snippet (we can't always attach huge arrays)
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "params": {
            "mass_visual": mass,
            "hotspot_speed": hotspot_speed,
            "trail_length": trail_length,
            "disk_color": disk_color,
            "show_stars": show_stars,
            "disk_thickness": disk_thickness,
            "audio_choice": audio_choice,
            "audio_duration_s": audio_duration,
            "audio_gain": audio_gain
        }
    }
    # if audio was generated in this session as wav_bytes, include base64 snippet
    # (Note: for simplicity we attach only last generated audio in memory if present)
    try:
        if 'wav_bytes' in locals() and wav_bytes:
            payload['audio_base64'] = base64.b64encode(wav_bytes[:20000]).decode('ascii')  # partial preview
    except Exception:
        pass

    blob = json.dumps(payload, indent=2)
    bbuf = io.BytesIO(blob.encode('utf-8'))
    st.download_button("Download JSON", data=bbuf, file_name="bbh_sim_params.json", mime="application/json")
    st.success("Export prepared.")

# display short help and diagnostics
with st.expander("About / Notes (click)"):
    st.markdown("""
    - **Visual scaling**: mass slider here controls an aesthetic visual scale; it does not run GR field equations.
    - **Audio**: the chirp is a pedagogical exponential sweep inspired by PN scaling; the ambient sound is a mix of low-frequency hum + colored noise.
    - **No infinite loops**: the renderer uses FuncAnimation with a finite number of frames; Streamlit will not hang.
    - **Tuning**: increase trail length for longer trails, or hotspot speed to make the hotspot orbit faster.
    - **Stars**: turned off by default to avoid occlusion; enable only for context.
    """)

st.caption("Built for iterative exploration — tell me which physics you want wired to visuals next (time dilation, decay overlays, or event merger binding).")

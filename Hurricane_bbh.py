import streamlit as st
import numpy as np
import io
import time
import matplotlib.pyplot as plt

# Prefer soundfile if available for WAV writing; otherwise fallback to scipy
try:
    import soundfile as sf
    HAS_SF = True
except Exception:
    from scipy.io import wavfile
    HAS_SF = False

st.set_page_config(page_title="BBH Audio Synth", layout="wide")

st.title("Black-Hole Multi-band Audio Synth — Pure Synthesis (Option 1)")

with st.sidebar:
    st.header("Synthesis Controls")
    # Visual-style controls which influence audio parameters:
    mass_scale = st.slider("Mass (visual scale, affects low-band)", min_value=1e3, max_value=1e8, value=4_300_000, step=1000, format="%d")
    spin = st.slider("Spin (a*, affects modulation)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    duration = st.slider("Duration (s)", min_value=0.8, max_value=8.0, value=3.0, step=0.2)
    gain_db = st.slider("Master gain (dB)", min_value=-24, max_value=6, value=-6, step=1)
    seed = st.number_input("Random seed (for turbulence)", value=12345, step=1)

st.markdown(
    """
**Concept:** we synthesize three bands and mix them:

- **Low (20–80 Hz)** — deep rolling rumble. Frequency & amplitude scale with `mass_scale`.
- **Mid (200–800 Hz)** — turbulent plasma band: filtered noise modulated by slow LFO (spin).
- **High (1–4 kHz)** — pulsed/tonal "crystal resonance" band: short pulses + FM influenced by spin.

Use **Play** to generate and listen, and watch the waveform playhead move while audio is playing.
"""
)

# Helpers
def db_to_gain(db):
    return 10.0 ** (db / 20.0)

def normalize(buf):
    peak = np.max(np.abs(buf)) if buf.size else 1.0
    if peak < 1e-9:
        return buf
    return buf / peak

def make_low_band(t, mass_scale, spin, sr):
    """
    Low band: sine-ish rumble with slow frequency modulation.
    mass_scale affects base frequency (larger = lower fundamental).
    """
    # map mass_scale (1e3..1e8) to freq range 20..80: heavier -> lower
    mnorm = (np.log10(mass_scale) - 3) / (8 - 3)  # roughly 0..1
    base = 80 - 60 * mnorm  # 20..80
    # slow FM by spin and a low-frequency noise component
    lfo = 0.5 * np.sin(2 * np.pi * (0.1 + 0.2*spin) * t)  # slow LFO
    # small random micro-mod
    micro = 0.4 * np.sin(2 * np.pi * (0.4 + 0.6*spin) * t * (1 + 0.1*np.sin(2*np.pi*0.07*t)))
    freq = base * (1 + 0.08 * lfo + 0.02 * micro)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    sig = 0.8 * np.sin(phase)
    # apply gentle exponential amplitude envelope (fade-in/out)
    env = np.minimum(1.0, (t / 0.15)) * np.minimum(1.0, ((duration - t) / 0.15))
    return sig * env

def make_mid_band(t, spin, sr):
    """
    Mid band: turbulent plasma — band-limited noise with amplitude modulation.
    We'll generate noise and bandpass by simple FFT filtering (cheap).
    """
    # create pink-leaning noise by summing a few random low-rate sinusoids + white noise
    rng = np.random.RandomState(int(seed))
    # base white noise
    white = rng.normal(size=t.shape)
    # add slow sinusoids to create swirling turbulence
    swirl = 0.6 * np.sin(2*np.pi*(0.8 + 1.2*spin) * t) + 0.4 * np.sin(2*np.pi*(1.6 + 2.4*spin) * t*0.5)
    raw = white * 0.7 + swirl * 0.6
    # simple bandpass via FFT: keep 180..900 Hz
    N = len(raw)
    spec = np.fft.rfft(raw)
    freqs = np.fft.rfftfreq(N, 1/sr)
    band = (freqs > 180) & (freqs < 900)
    # apply soft rolloffs
    window = np.zeros_like(spec, dtype=float)
    window[band] = 1.0
    # soft edges
    low_edge = (freqs > 150) & (freqs <= 180)
    high_edge = (freqs >= 900) & (freqs < 980)
    window[low_edge] = (freqs[low_edge] - 150) / (180 - 150)
    window[high_edge] = (980 - freqs[high_edge]) / (980 - 900)
    spec = spec * window
    mid = np.fft.irfft(spec, n=N)
    # amplitude modulation by spin-driven LFO (faster for higher spin)
    am = 0.5 + 0.5 * np.sin(2*np.pi*(0.6 + 2.0*spin) * t)
    return mid * am * 0.8

def make_high_band(t, spin, sr):
    """
    High band: pulsed shimmering band — short FM pulses that simulate 'crystal resonances'.
    We'll build a pulse train whose pulse rate & FM depend on spin.
    """
    rng = np.random.RandomState(int(seed)+7)
    base_freq = 1200 + 2000 * spin  # 1200..3200 Hz
    pulse_rate = 6 + 12*spin        # pulses per second
    N = len(t)
    sig = np.zeros_like(t)
    # create pulses at regular intervals but jittered slightly
    intervals = np.arange(0, duration, 1.0/pulse_rate)
    for idx, start in enumerate(intervals):
        # pulse envelope (short)
        start_i = int(start * sr)
        pulse_len = int(0.06 * sr)  # ~60 ms
        if start_i >= N: break
        end_i = min(N, start_i + pulse_len)
        tt = np.arange(end_i - start_i) / sr
        # FM inside pulse
        fm = base_freq * (1 + 0.05 * np.sin(2*np.pi*(2.0 + 4.0*spin) * tt + rng.uniform(-1,1)))
        phase = 2*np.pi * np.cumsum(fm) / sr
        envelope = np.exp(-12 * tt) * (np.sin(np.pi * (tt / (pulse_len/sr))))
        sig[start_i:end_i] += envelope * 1.0 * np.sin(phase)
    # add faint noise shimmer
    sig += 0.12 * rng.normal(size=N) * np.exp(-6*(t/duration))
    return sig * 0.9

# Main synth & play routine
def synth_and_package(mass_scale, spin, duration, sr=44100, gain_db=-6):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    low = make_low_band(t, mass_scale, spin, sr)
    mid = make_mid_band(t, spin, sr)
    high = make_high_band(t, spin, sr)
    mix = normalize(0.8*low + 0.7*mid + 0.9*high)
    # apply master gain
    mix *= db_to_gain(gain_db)
    # convert to 32-bit float PCM for smooth playback
    audio = mix.astype(np.float32)
    # package into BytesIO as WAV
    bio = io.BytesIO()
    if HAS_SF:
        sf.write(bio, audio, sr, format='WAV', subtype='FLOAT')
    else:
        # scipy wants int16; scale and write
        wav = np.int16(np.clip(audio, -1, 1) * 32767)
        wavfile.write(bio, sr, wav)
    bio.seek(0)
    return bio, audio, sr

# UI controls: generate & play
col1, col2 = st.columns([1,2])
with col1:
    if st.button("Generate & Prepare Audio"):
        # generate and store in session_state
        bio, audio_arr, sr = synth_and_package(mass_scale, spin, duration, sr=44100, gain_db=gain_db)
        st.session_state['audio_bytes'] = bio.getvalue()
        st.session_state['audio_array'] = audio_arr
        st.session_state['audio_sr'] = sr
        st.success("Audio generated and ready. Press Play to listen.")
    play = st.button("Play")
    stop = st.button("Stop")

with col2:
    st.empty()  # placeholder for layout balance

# Show generated waveform preview (static)
if 'audio_array' in st.session_state:
    audio_array = st.session_state['audio_array']
    sr = st.session_state['audio_sr']
    fig_wav, ax = plt.subplots(figsize=(9,2))
    # downsample for display if too long
    N = len(audio_array)
    display_samples = 4000
    if N > display_samples:
        step = N // display_samples
        display = audio_array[::step]
        xs = np.linspace(0, duration, len(display))
        ax.plot(xs, display, linewidth=0.6)
    else:
        xs = np.linspace(0, duration, N)
        ax.plot(xs, audio_array, linewidth=0.6)
    ax.set_xlim(0, duration)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Amplitude")
    ax.set_title("Generated waveform (preview)")
    plt.tight_layout()
    st.pyplot(fig_wav)
else:
    st.info("Click **Generate & Prepare Audio** to create the synthesized audio (then press Play).")

# Playback & playhead animation
play_placeholder = st.empty()
progress_placeholder = st.empty()
playhead_canvas = st.empty()

def run_playback():
    # get audio bytes and array
    audio_bytes = st.session_state.get('audio_bytes', None)
    audio_array = st.session_state.get('audio_array', None)
    sr = st.session_state.get('audio_sr', 44100)
    if audio_bytes is None or audio_array is None:
        st.warning("No audio generated yet. Click Generate first.")
        return

    # render audio player
    play_placeholder.audio(audio_bytes, format='audio/wav')

    # animate playhead on waveform while audio plays
    total_ms = int(duration * 1000)
    start_time = time.time()
    last_idx = -1

    # We'll update roughly 20 times per second
    update_interval = 0.05
    while True:
        elapsed = time.time() - start_time
        if elapsed * 1000 >= total_ms:
            # final update & break
            prog = 1.0
        else:
            prog = elapsed / duration

        # draw a small waveform with playhead
        fig, ax = plt.subplots(figsize=(9,2))
        N = len(audio_array)
        # sample for display
        display_samples = 3000
        if N > display_samples:
            step = N // display_samples
            display = audio_array[::step]
            xs = np.linspace(0, duration, len(display))
            ax.plot(xs, display, linewidth=0.6, color="#a64dff")
        else:
            xs = np.linspace(0, duration, N)
            ax.plot(xs, audio_array, linewidth=0.6, color="#a64dff")

        # playhead line
        px = prog * duration
        ax.axvline(px, color='red', linewidth=1.2, alpha=0.9)
        ax.set_xlim(0, duration); ax.set_ylim(-1.05, 1.05)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"Playback — {px:.2f}s / {duration:.2f}s")
        plt.tight_layout()
        playhead_canvas.pyplot(fig)
        plt.close(fig)

        if prog >= 1.0:
            break
        # allow user to stop by clicking Stop button
        if stop:
            break
        time.sleep(update_interval)

# Button actions
# We need to ensure click on Play triggers generation if not present
if play:
    if 'audio_bytes' not in st.session_state:
        bio, audio_arr, sr = synth_and_package(mass_scale, spin, duration, sr=44100, gain_db=gain_db)
        st.session_state['audio_bytes'] = bio.getvalue()
        st.session_state['audio_array'] = audio_arr
        st.session_state['audio_sr'] = sr
    # run playback loop (this will block until audio length; it's fine for small durations)
    run_playback()

if stop:
    # Clear audio player and playhead (soft stop)
    play_placeholder.empty()
    playhead_canvas.empty()
    progress_placeholder.empty()
    st.experimental_rerun()

# Small export option
st.markdown("---")
if 'audio_bytes' in st.session_state:
    st.download_button("Download WAV", data=st.session_state['audio_bytes'], file_name="bbh_synthesis.wav", mime="audio/wav")
    st.caption("WAV exported from mathematical synthesis (float32).")

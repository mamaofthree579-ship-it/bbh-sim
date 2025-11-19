import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import io
import soundfile as sf

st.set_page_config(page_title="Quantum Black Hole", layout="wide")

# ---------------------------------------------
# Sidebar Controls
# ---------------------------------------------
with st.sidebar:
    st.header("Simulation Controls")

    mass = st.slider(
        "Mass (M☉, visual scale)",
        min_value=1000,                 # int
        max_value=100_000_000,          # int
        value=4_300_000,                # int
        step=1000,                      # int
        format="%d"
    )

    spin = st.slider("Spin (a*)", 0.0, 0.99, 0.5, step=0.01)
    hotspot_speed = st.slider("Hotspot Angular Speed", 0.01, 0.2, 0.026, step=0.002)

    hotspot_trail = st.slider("Hotspot Trail Length (frames)", 2, 12, 6, step=1)

    disk_thickness = st.slider("Accretion Disk Thickness", 0.02, 0.5, 0.12, step=0.01)
    lensing_strength = st.slider("Gravitational Lensing Strength", 0.0, 1.0, 0.22, step=0.02)

    jet_activity = st.slider("Jet Particle Rate", 0, 200, 40, step=5)

    audio_enabled = st.checkbox("Enable Hurricane/Whirlpool Audio", value=True)

    quality = st.selectbox(
        "Render Quality",
        ["Balanced", "High", "Low"],
        index=0
    )


# ---------------------------------------------
# Helper: Generate the rotational frame
# ---------------------------------------------
def render_blackhole_frame(theta, hotspot_history):
    """Render a single black hole frame."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_facecolor("black")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")

    # Event horizon radius (scaled)
    r_h = 0.18 + 0.08 * spin

    # Draw event horizon
    circle = plt.Circle((0, 0), r_h, color="black", zorder=5)
    ax.add_patch(circle)

    # Accretion disk
    N = 2000 if quality == "High" else 900 if quality == "Balanced" else 400
    phi = np.random.uniform(0, 2 * np.pi, N)
    r = np.random.uniform(r_h * 1.1, 1.0, N)

    x = r * np.cos(phi)
    y = r * np.sin(phi)

    # Lensing distortion
    lens = 1 + lensing_strength * r**(-2)
    x *= lens
    y *= lens

    # Disk brightness
    colors = np.clip(1 - r, 0, 1)

    ax.scatter(x, y, c=plt.cm.inferno(colors), s=2, alpha=0.85, zorder=1)

    # Hotspot motion
    hx = 0.55 * np.cos(theta)
    hy = 0.25 * np.sin(theta) * (1 + disk_thickness)

    hotspot_history.append((hx, hy))
    if len(hotspot_history) > hotspot_trail:
        hotspot_history.pop(0)

    # Plot hotspot trail
    for i, (tx, ty) in enumerate(hotspot_history):
        alpha = (i + 1) / len(hotspot_history)
        ax.scatter(tx, ty, color=(1, 0.8, 0.4, alpha), s=30)

    # Plot hotspot
    ax.scatter(hx, hy, color="white", s=60, zorder=10)

    # Return image
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor="black")
    plt.close(fig)
    buf.seek(0)
    return buf


# ---------------------------------------------
# Generate Audio (Whirlpool + Hurricane)
# ---------------------------------------------
def generate_audio(duration=3.0, samplerate=48000):
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)

    # Deep black hole rumble
    base = 0.4 * np.sin(2 * np.pi * 22 * t)

    # Hurricane/whirlpool broadband noise
    noise = np.random.normal(0, 0.25, len(t))
    whirling = np.sin(2 * np.pi * 2.5 * t) * noise

    # Spin-modulation
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t)

    audio = (base + whirling * mod).astype(np.float32)
    return audio, samplerate


# ---------------------------------------------
# Main UI — Animation System
# ---------------------------------------------
st.title("🌀 Quantum Hurricane Black Hole Simulator v2.0")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Visualization")

    play_button = st.button("▶ Play Rotation")

    hotspot_history = []

    if play_button:
        # Basic animation loop
        frames = []
        for i in range(90):  # ~3 seconds at 30 FPS
            theta = i * hotspot_speed * 0.8
            frame = render_blackhole_frame(theta, hotspot_history)
            frames.append(frame)

        # Display as GIF
        import imageio
        gif_bytes = io.BytesIO()
        imageio.mimsave(
            gif_bytes,
            [imageio.imread(f) for f in frames],
            format="GIF",
            duration=0.04
        )
        gif_bytes.seek(0)

        st.image(gif_bytes.read(), caption="Black Hole Rotation")

    else:
        # Show static frame
        frame = render_blackhole_frame(0, hotspot_history)
        st.image(frame, caption="Black Hole (Static View)")


with col2:
    st.subheader("Audio Output")

    if audio_enabled:
        audio, rate = generate_audio()
        st.audio(audio, sample_rate=rate)
    else:
        st.info("Audio disabled.")


st.markdown("---")
st.markdown("Made with ❤️ — Real-time astrophysical visualization engine")

    // jet-disk interaction flash: if particle near disk inner radius and alpha high => small flash
    const d2 = Math.hypot(p.x - cx, p.y - cy);
    if(d2 < disk.rInner*1.2 && alpha > 0.65 && Math.random() < 0.02){{
      // small radial flash
      ctx.beginPath();
      ctx.arc(cx,cy, 22 + Math.random()*30, 0, Math.PI*2);
      ctx.fillStyle = `rgba(255,220,160,${0.06 + Math.random()*0.08})`; ctx.fill();
    
/* ---------- Summary graphs (small, lightweight) ---------- */
function drawSummaryMini(progress=0){{
  // subtle pulse ring showing inspiral progress
  const r = Math.max(40, 1 + schwarzschildRadius(mass)/1e8);
  ctx.beginPath();
  ctx.arc(cx,cy, r + 220*progress, 0, Math.PI*2);
  ctx.strokeStyle = 'rgba(120,200,255,' + (0.03 + 0.06*progress) + ')';
  ctx.lineWidth = 1 + 3*progress;
  ctx.stroke();

/* ---------- Main loop ---------- */
let raf = null;
function step(){{
  const now = performance.now();
  let dt = Math.min(40, now - lastTime); // ms
  lastTime = now;
  if(paused) raf = :requestAnimationFrame(step); return,

  // motion blur: fade previous frame with globalAlpha
  ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = 'rgba(3,0,6,0.22)'; // higher alpha leaves longer trail
  ctx.fillRect(0,0,W,H);
  ctx.globalCompositeOperation = 'lighter';

  drawBackground();
  drawPhotonRing();
  drawDisk();
  drawEventHorizon();

  // draw hotspots & trails
  drawHotspots(dt);

  // jets
  drawJet(dt);

  // slight Einstein ring overlay
  if(lensingStrength > 0.01) drawPhotonRing();

  // small summary
  const prog = Math.min(1, Math.max(0.001, (playhead % playDurMs) / playDurMs || 0));
  drawSummaryMini(prog);

  // audio: animate panner and whirl frequency by hotspot mean angular rate
  if(audioEnabled && audioCtx){{
    // compute average hotspot angular position to create stereo pan
    let sumCos = 0;
    for(const h of hotspots) sumCos += Math.cos(h.theta);
    const avg = sumCos / hotspots.length || 0;
    const pan = Math.max(-0.9, Math.min(0.9, avg));
    if(panner) panner.pan.linearRampToValueAtTime(pan, audioCtx.currentTime + 0.05);
    if(whirlNode) {{
      // mod frequency with spin and mass (lower mass -> higher frequency)
      const baseFreq = 20 + spin*40 + (4.3e6 / Math.max(1e4, mass)) * 0.02;
      whirlNode.frequency.linearRampToValueAtTime(baseFreq, audioCtx.currentTime + 0.05);

  // remove any hotspots that plunged inside horizon
  hotspots = hotspots.filter(h=> h.r > Math.max(10, 0.8 * (schwarzschildRadius(mass)/1e8)) );

  // occasionally spawn new hotspot at outer disk
  if(Math.random() < 0.01 * motionScale) {{
    const newr = disk.rOuter * (0.88 + Math.random()*0.12);
    hotspots.push(new Hotspot(newr, Math.random()*Math.PI*2, 0.8 + Math.random()*0.6));
    // keep hotspot count reasonable
    if(hotspots.length > 8) hotspots.shift();
  raf = requestAnimationFrame(step),
/* Start animation */
lastTime = performance.now();
let playDurMs = 4200;
let playStart = performance.now();
let playheadMs = 0;
if(audioEnabled) initAudio();
step();

/* Expose some runtime tuning (for dev) */
window.__QBH = {{
  hotspots, disk, jetParticles, cfg, redraw: ()=> ;drawBackground(); drawDisk(); drawEventHorizon(); drawHotspots(16),
/* --- utility: replace tokens inserted by python --- */
function replaceJSONTokens() /* placeholder if needed */

</script>
</body>
</html>

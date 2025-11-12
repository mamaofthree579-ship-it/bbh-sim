import streamlit as st
import numpy as np
import base64
import json
import wave
from io import BytesIO
import math
from typing import Tuple

st.set_page_config(page_title="BBH Simulator — Overview + Events + Calculators", layout="wide")

# --------------------
# Helper: synthesize chirp (wav bytes) + waveform array for canvas
# --------------------
def synthesize_chirp_wav(m1: float, m2: float, spin: float, duration: float = 3.0, sr: int = 44100) -> Tuple[bytes, np.ndarray, int]:
    """
    Create a toy chirp waveform (PN-inspired) and return:
      - wav bytes (16-bit PCM)
      - normalized float waveform array (for drawing waveform in canvas)
      - sample rate
    """
    N = int(duration * sr)
    t = np.linspace(0, duration, N, endpoint=False)
    # chirp mass (toy)
    Mc = ((m1 * m2) ** (3/5.0)) / ((m1 + m2) ** (1/5.0))
    f0 = 20.0 + spin * 15.0
    f1 = 400.0 + (Mc / 30.0) * 200.0
    # rising frequency law
    freq = f0 + (t / duration) ** 1.6 * (f1 - f0)
    env = (t / duration) ** 1.6
    env *= np.exp(-3.0 * (1 - t / duration))
    signal = env * np.sin(2 * np.pi * freq * t)
    # slight harmonic
    signal += 0.08 * env * np.sin(2 * np.pi * 2.0 * freq * t)
    maxval = np.max(np.abs(signal)) if np.max(np.abs(signal)) > 0 else 1.0
    signal_norm = signal / maxval * 0.95
    pcm = np.int16(signal_norm * 32767)

    bio = BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    wav_bytes = bio.getvalue()

    canvas_len = 1600
    idx = np.round(np.linspace(0, N - 1, canvas_len)).astype(int)
    canvas_waveform = signal_norm[idx].astype(float)

    return wav_bytes, canvas_waveform, sr

# --------------------
# Layout: tabs
# --------------------
tabs = st.tabs(["Overview", "Events", "Calculators"])
overview_tab, events_tab, calc_tab = tabs

# --------------------
# Overview tab: visual + WebAudio synth (client-side)
# --------------------
with overview_tab:
    st.markdown("## 🌌 Overview — Black Hole Anatomy (live audio + visual)")
    col_left, col_right = st.columns([3,1])
    with col_left:
        st.markdown("Adjust speed, trail length, hotspot radius, and color. Press **Play Audio** to hear the live synth driven by the visual energy readout.")
        speed = st.slider("Hotspot speed", min_value=0.0, max_value=1.2, value=0.26, step=0.01)
        trail_len = st.slider("Trail length (points)", min_value=3, max_value=30, value=8, step=1)
        hotspot_radius = st.slider("Hotspot orbit radius (visual)", min_value=50, max_value=180, value=110, step=2)
        bh_color = st.color_picker("Accretion accent color (purple → amber)", "#A64DFF")
        # pack config
        config = {
            "speed": float(speed),
            "trail_len": int(trail_len),
            "hotspot_radius": int(hotspot_radius),
            "accent": bh_color
        }

        # Client HTML: canvas visual + WebAudio synth (Play/Stop)
        html = f"""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8" />
          <style>
            body{{margin:0;background:transparent;color:#eae6ff;font-family:Inter,Arial,Helvetica,sans-serif}}
            #wrap{{display:flex;flex-direction:column;align-items:center;padding:10px}}
            canvas{{border-radius:8px;box-shadow:0 8px 20px rgba(0,0,0,0.6);background: radial-gradient(circle at center,#14001a 0%, #05000a 100%);}}
            .legend{{margin-top:8px;display:flex;align-items:center;gap:8px}}
            .colorbar{{width:18px;height:180px;border-radius:6px;background:linear-gradient(to top, rgba(255,180,80,0.95), rgba(140,80,255,0.95));box-shadow:inset 0 0 8px rgba(0,0,0,0.4)}}
            .controls{{margin-top:10px;display:flex;gap:8px;align-items:center}}
            .btn{{padding:6px 10px;border-radius:6px;border:none;background:#7a3bff;color:white;cursor:pointer}}
            .readout{{margin-top:10px;font-weight:700;color:#ffd;}}
            .muted{{color:#cfc3ff;font-weight:400;font-size:0.95rem}}
          </style>
        </head>
        <body>
         <div id="wrap">
          <canvas id="bh" width="880" height="420"></canvas>
          <div class="legend" aria-hidden="true">
            <div class="colorbar" title="Energy"></div>
            <div style="text-align:left">
              <div style="font-weight:700;color:#e6d8ff">Energy scale</div>
              <div class="muted">low ↔ high</div>
            </div>
          </div>

          <div class="controls">
            <button id="playBtn" class="btn">▶ Play Audio</button>
            <button id="stopBtn" class="btn" style="background:#444">⏸ Stop</button>
            <div style="margin-left:12px;color:#ffd" id="audioState">Audio: stopped</div>
          </div>

          <div id="numeric" class="readout">Energy (local intensity): <span id="energyVal">0.000</span></div>
         </div>

         <script>
           const cfg = {json.dumps(config)};
           const canvas = document.getElementById('bh');
           const ctx = canvas.getContext('2d');
           const W = canvas.width, H = canvas.height;
           const cx = W/2, cy = H/2;
           const horizonR = 70;
           let angle = 0;
           const trail = [];

           // --- WebAudio synth setup (client-side) ---
           let audioCtx = null;
           let masterGain = null;
           let oscLow = null;    // base low rumble
           let oscHarm = null;   // harmonic tone
           let noiseNode = null; // brown-ish noise via ScriptProcessor (fallback)
           let noiseGain = null;
           let lpFilter = null;
           let running = false;

           function createSynth(){
             audioCtx = new (window.AudioContext || window.webkitAudioContext)();
             masterGain = audioCtx.createGain(); masterGain.gain.value = 0.0;
             masterGain.connect(audioCtx.destination);

             // low oscillator
             oscLow = audioCtx.createOscillator(); oscLow.type = 'sine';
             const lowGain = audioCtx.createGain(); lowGain.gain.value = 0.0;
             oscLow.connect(lowGain); lowGain.connect(masterGain);

             // harmonic
             oscHarm = audioCtx.createOscillator(); oscHarm.type = 'sine';
             const harmGain = audioCtx.createGain(); harmGain.gain.value = 0.0;
             oscHarm.connect(harmGain); harmGain.connect(masterGain);

             // brown noise generator
             const bufferSize = 4096;
             const noiseProc = audioCtx.createScriptProcessor(bufferSize, 1, 1);
             let lastOut = 0.0;
             noiseProc.onaudioprocess = function(e){
               const out = e.outputBuffer.getChannelData(0);
               for(let i=0;i<bufferSize;i++){
                 const white = Math.random() * 2 - 1;
                 lastOut = (lastOut + 0.02 * white) / 1.02;
                 out[i] = lastOut * 3.5; // brown-ish
               }
             };
             noiseNode = noiseProc;
             noiseGain = audioCtx.createGain(); noiseGain.gain.value = 0.0;
             noiseNode.connect(noiseGain); noiseGain.connect(masterGain);

             // lowpass filter to shape noise timbre
             lpFilter = audioCtx.createBiquadFilter(); lpFilter.type = 'lowpass'; lpFilter.frequency.value = 400;
             // route master -> filter -> destination for a separate path (optional)
             // but for simplicity, filter inserted on noise path already connecting to masterGain

             // connect oscillators
             oscLow.start();
             oscHarm.start();
           }

           function startAudio(){
             if(!audioCtx) createSynth();
             // resume context if suspended
             if(audioCtx.state === 'suspended') audioCtx.resume();
             running = true;
             document.getElementById('audioState').textContent = 'Audio: playing';
           }

           function stopAudio(){
             running = false;
             // ramp gain down gently
             if(masterGain){
               masterGain.gain.cancelScheduledValues(audioCtx.currentTime);
               masterGain.gain.linearRampToValueAtTime(0.0, audioCtx.currentTime + 0.08);
             }
             document.getElementById('audioState').textContent = 'Audio: stopped';
           }

           document.getElementById('playBtn').addEventListener('click', ()=>{
             startAudio();
           });
           document.getElementById('stopBtn').addEventListener('click', ()=>{
             stopAudio();
           });

           // mapping: energy -> synth params
           function applyEnergyToSynth(energy){
             if(!audioCtx || !running) return;
             // energy in [0,1]
             const e = Math.max(0, Math.min(1, energy));
             // drive master gain (soft)
             masterGain.gain.cancelScheduledValues(audioCtx.currentTime);
             masterGain.gain.linearRampToValueAtTime(0.02 + 0.45 * e, audioCtx.currentTime + 0.04);

             // low oscillator frequency (rumble) map 20-120 Hz
             if(oscLow) {
               const lowFreq = 20 + 100 * Math.pow(e, 0.6);
               oscLow.frequency.exponentialRampToValueAtTime(lowFreq, audioCtx.currentTime + 0.02);
             }
             // harmonic frequency (for texture) map to 1.5x-3.5x low
             if(oscHarm && oscLow) {
               const harmFreq = (20 + 100 * Math.pow(e, 0.6)) * (1.8 + 1.7 * e);
               oscHarm.frequency.exponentialRampToValueAtTime(harmFreq, audioCtx.currentTime + 0.02);
             }
             // noise gain (hurricane texture)
             if(noiseGain){
               const ng = 0.002 + 0.08 * (e ** 1.4);
               noiseGain.gain.cancelScheduledValues(audioCtx.currentTime);
               noiseGain.gain.linearRampToValueAtTime(ng, audioCtx.currentTime + 0.02);
             }
             // filter cutoff to brighten with energy
             if(lpFilter){
               const cutoff = 200 + 3000 * (e ** 1.8);
               lpFilter.frequency.exponentialRampToValueAtTime(cutoff, audioCtx.currentTime + 0.03);
               // route noise through filter when present
               try {
                 // connect noiseNode -> noiseGain -> lpFilter -> masterGain
                 noiseGain.disconnect();
                 noiseGain.connect(lpFilter);
                 lpFilter.connect(masterGain);
               } catch(err){
                 // ignore if already connected
               }
             }
           }

           // --- Canvas visual + energy calculation ---
           function draw(){
             ctx.clearRect(0,0,W,H);

             // background radial
             const g = ctx.createRadialGradient(cx,cy,10,cx,cy,420);
             g.addColorStop(0,'#070012'); g.addColorStop(1,'#010006');
             ctx.fillStyle = g; ctx.fillRect(0,0,W,H);

             // accretion rings
             for(let i=0;i<36;i++){
               ctx.beginPath();
               ctx.arc(cx,cy,horizonR+6 + i*3,0,Math.PI*2);
               ctx.strokeStyle = `rgba(255,180,80,${0.003 + i*0.0006})`;
               ctx.lineWidth = 1;
               ctx.stroke();
             }

             // horizon outline and slightly purple fill
             ctx.beginPath(); ctx.arc(cx,cy,horizonR,0,Math.PI*2);
             ctx.strokeStyle = 'rgba(140,80,255,0.35)'; ctx.lineWidth=2; ctx.stroke();
             ctx.beginPath(); ctx.arc(cx,cy,horizonR-1,0,Math.PI*2); ctx.fillStyle='rgba(16,6,22,0.98)'; ctx.fill();

             // hotspot + trail
             const orbitR = cfg.hotspot_radius;
             const hx = cx + Math.cos(angle) * orbitR;
             const hy = cy + Math.sin(angle) * orbitR * 0.32;
             trail.push({x:hx,y:hy});
             while(trail.length > cfg.trail_len) trail.shift();

             for(let k=0;k<trail.length;k++){
               const p = trail[k]; const a = (k+1)/trail.length;
               ctx.beginPath();
               ctx.arc(p.x,p.y, Math.max(1.8, 4 - (trail.length - k)*0.4), 0, Math.PI*2);
               ctx.fillStyle = `rgba(255,220,180,${0.12 * a})`; ctx.fill();
             }
             ctx.beginPath(); ctx.arc(hx,hy,6,0,Math.PI*2); ctx.fillStyle='#ffcc99'; ctx.fill();

             // jet hint
             ctx.fillStyle='rgba(120,200,255,0.06)'; ctx.fillRect(cx-6, 0, 12, cy-120);

             // compute energy scalar
             const energy = Math.max(0, 0.20 + 0.80 * Math.abs(Math.sin(angle*1.4)) * ( (orbitR - 50)/160 ));
             document.getElementById('energyVal').textContent = energy.toFixed(3);

             // apply to synth (if running)
             try { applyEnergyToSynth(energy); } catch(e){ /* ignore in no-audio state */ }

             angle += cfg.speed;
             requestAnimationFrame(draw);
           }
           draw();

         </script>
        </body>
        </html>
        """

        st.components.v1.html(html, height=720, scrolling=False)

    with col_right:
        st.markdown("### Controls quick summary")
        st.markdown(f"- Accent color: **{bh_color}**")
        st.markdown("- Play audio inside the visual panel (Play/Stop).")
        st.markdown("- Energy readout shown below visual (live).")
        st.markdown("")

# --------------------
# Events tab (chirp generation + orbit canvas)
# --------------------
with events_tab:
    st.markdown("## 💫 Events — chirp waveform & orbit demo")
    ev_col1, ev_col2 = st.columns([2,1])

    with ev_col1:
        # Event selector & params
        event_options = {
            "GW150914": {"m1":36, "m2":29, "spin":0.30},
            "GW170104": {"m1":31, "m2":19, "spin":0.45},
            "GW190521": {"m1":85, "m2":66, "spin":0.70},
            "GW190814": {"m1":23, "m2":2.6, "spin":0.05},
            "Custom": {}
        }
        choice = st.selectbox("Select event", list(event_options.keys()), index=0)
        if choice != "Custom":
            params = event_options[choice]
            m1 = st.number_input("M₁ (M☉)", value=params["m1"], step=0.1)
            m2 = st.number_input("M₂ (M☉)", value=params["m2"], step=0.1)
            spin = st.slider("Spin a*", min_value=0.0, max_value=1.0, value=float(params["spin"]), step=0.01)
        else:
            m1 = st.number_input("M₁ (M☉)", value=30.0, step=0.1)
            m2 = st.number_input("M₂ (M☉)", value=30.0, step=0.1)
            spin = st.slider("Spin a*", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

        run_sim = st.button("Generate waveform & prepare chirp")

        color = "#a64dff"
        orbit_html = f"""
        <canvas id="orbit" width="880" height="320" style="border-radius:8px;background:radial-gradient(circle at center,#120014,#010006);display:block;margin:10px auto"></canvas>
        <script>
          const canvas = document.getElementById('orbit'), ctx = canvas.getContext('2d');
          const cx = canvas.width/2, cy = canvas.height/2;
          let angle = 0;
          const rA = 80, rB = 160;
          const cA = "{color}", cB = "#33ccff";
          function draw(){
            ctx.clearRect(0,0,canvas.width,canvas.height);
            // subtle background circles
            for(let i=0;i<4;i++){
              ctx.beginPath(); ctx.arc(cx,cy,80+i*40,0,Math.PI*2);
              ctx.strokeStyle = 'rgba(160,0,255,0.03)'; ctx.stroke();
            }
            const xA = cx + Math.cos(angle)*rA, yA = cy + Math.sin(angle)*rA;
            const xB = cx - Math.cos(angle)*rB, yB = cy - Math.sin(angle)*rB;
            ctx.beginPath(); ctx.arc(xA,yA,12,0,Math.PI*2); ctx.fillStyle = cA; ctx.fill();
            ctx.beginPath(); ctx.arc(xB,yB,16,0,Math.PI*2); ctx.fillStyle = cB; ctx.fill();
            angle += 0.02 + ({spin}*0.01);
            requestAnimationFrame(draw);
          }
          draw();
        </script>
        """
        st.components.v1.html(orbit_html, height=360, scrolling=False)

    with ev_col2:
        st.markdown("**Event info**")
        chirp_mass = ((m1 * m2) ** (3/5.0)) / ((m1 + m2) ** (1/5.0))
        st.write(f"Chirp mass ℳ ≈ **{chirp_mass:.2f} M☉**")
        st.write("Frequency range (approx): **20–400 Hz**")
        est_h = 4e-21 * (chirp_mass / 30.0) ** (5/3.0)
        st.write(f"Estimated strain (order): **{est_h:.2e}**")
        st.write(f"Spin a*: **{spin:.2f}**")
        st.write("")

    st.markdown("---")
    chirp_col1, chirp_col2 = st.columns([3,1])
    with chirp_col1:
        waveform_placeholder = st.empty()
        if run_sim:
            wav_bytes, canvas_waveform, sr = synthesize_chirp_wav(m1, m2, spin, duration=3.0, sr=44100)
            wf_json = json.dumps([float(x) for x in canvas_waveform.tolist()])
            html_chirp = f"""
            <canvas id="chirp" width="880" height="180" style="display:block;margin:6px auto;border-radius:8px;background:linear-gradient(#09000a,#040006)"></canvas>
            <script>
              const data = {wf_json};
              const canvas = document.getElementById('chirp'), ctx = canvas.getContext('2d');
              const W = canvas.width, H = canvas.height;
              function draw(idx=-1){
                ctx.clearRect(0,0,W,H);
                ctx.beginPath();
                for(let i=0;i<data.length;i++){
                  const x = i/data.length * W;
                  const y = H/2 - data[i]* (H/2) * 0.9;
                  if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
                }
                ctx.strokeStyle = "{color}"; ctx.lineWidth=2; ctx.stroke();
                if(idx>=0){
                  const px = idx/data.length * W;
                  ctx.beginPath(); ctx.moveTo(px,0); ctx.lineTo(px,H); ctx.strokeStyle='rgba(255,80,80,0.9)'; ctx.lineWidth=1.4; ctx.stroke();
                }
              }
              draw(-1);
              window.drawChirp = draw;
            </script>
            """
            waveform_placeholder.components.html(html_chirp, height=200, scrolling=False)
            st.audio(wav_bytes, format='audio/wav')
        else:
            waveform_placeholder.info("Click 'Generate waveform & prepare chirp' to create waveform & playable audio.")

    with chirp_col2:
        if run_sim:
            samples = canvas_waveform.tolist()
            payload = {"params": {"m1": m1, "m2": m2, "spin": spin}, "samples": samples, "sample_rate": 44100}
            json_bytes = json.dumps(payload, indent=2).encode("utf-8")
            st.download_button("Export waveform JSON", json_bytes, file_name=f"{choice}_waveform.json", mime="application/json")
        else:
            st.write("Export available after generation.")

# --------------------
# Calculators tab
# --------------------
with calc_tab:
    st.markdown("## 🧮 Calculators — Time dilation & DM effects")
    st.markdown("Compute the time-dilation factor near Sagittarius A* and a toy DM-modified decay rate.")
    colA, colB = st.columns([1,2])
    with colA:
        r = st.number_input("Radius r (m)", value=7.8e17, format="%.6e")
        rho_dm = st.number_input("Dark matter density ρ_DM (kg/m³)", value=1e-21, format="%.6e")
        run_calc = st.button("Run calculator")
    with colB:
        out = st.empty()
        if run_calc:
            G = 6.67430e-11
            msun = 1.98847e30
            M_sgr = 4.3e6 * msun
            c = 299792458.0
            rs = 2 * G * M_sgr / (c ** 2)
            val = 1.0 - (G * M_sgr) / (r * c * c)
            gamma = math.sqrt(max(0.0, val))
            alpha = 1e21
            Gamma_dark = 1.0 * (1.0 + alpha * rho_dm)
            out.markdown(f"- Schwarzschild radius rₛ ≈ **{rs:.3e} m**  \n- Time dilation factor γ(r) ≈ **{gamma:.9f}**  \n- Toy DM-modified rate Γ_dark ≈ **{Gamma_dark:.3e}**")
        else:
            out.info("Enter radius and DM density then click Run calculator.")

# Footer
st.markdown("---")
st.markdown("**Notes:** the Overview audio is synthesized client-side (WebAudio). The Events chirp is synthesized server-side and offered as a WAV. Models are pedagogical (toy PN-like templates).")

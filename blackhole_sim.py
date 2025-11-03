<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>BBH Simulator — Overview (Crystalline Singularity)</title>
<style>
  :root{
    --bg:#05000a; --panel:#120018; --accent:#8a33ff; --muted:#33003d; --text:#eae6ff;
    --soft:#2b0037;
  }
  body{margin:0;font-family:Inter,Arial,Helvetica,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;}
  .tabs{display:flex;background:var(--panel);border-bottom:2px solid rgba(120,70,200,0.12)}
  .tabButton{flex:1;padding:12px;cursor:pointer;border:0;background:transparent;color:var(--text);font-weight:700}
  .tabButton.active{background:var(--accent);color:#fff}
  .container{padding:18px;max-width:1180px;margin:0 auto;}
  h2{margin:6px 0 10px;color:var(--text)}
  .panel{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:12px;border-radius:10px;border:1px solid rgba(120,70,200,0.06)}
  .controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:10px}
  label{font-size:0.9rem;color:#dcd6ff}
  input[type=range]{width:160px}
  button{background:var(--accent);border:0;padding:8px 12px;border-radius:6px;color:white;cursor:pointer}
  button.secondary{background:#444}
  #overviewArea{position:relative;height:520px;margin-top:12px;border-radius:10px;overflow:hidden;background:radial-gradient(ellipse at center,#070012 0%, #020004 70%)}
  canvas#bgCanvas{position:absolute;inset:0;width:100%;height:100%;display:block}
  /* place the crystal image centered */
  .crystalWrap{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none;mix-blend-mode:screen;display:flex;align-items:center;justify-content:center}
  img#crystalImg{max-width:62%; max-height:72%; display:block; filter: drop-shadow(0 12px 30px rgba(120,80,255,0.25)); transform-origin:center center;}
  /* glow layers */
  .glowLayer{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none;mix-blend-mode:screen}
  .glow{width:520px;height:520px;border-radius:50%;background:radial-gradient(circle at center, rgba(180,120,255,0.18), rgba(120,60,220,0.06) 40%, rgba(0,0,0,0) 60%);filter:blur(30px);opacity:0.7}
  .beam{position:absolute;left:50%;top:50%;transform:translate(-50%,-30%);width:260px;height:360px;background:linear-gradient(180deg, rgba(120,200,255,0.06), rgba(255,220,180,0.02));filter:blur(18px);opacity:0.6;border-radius:10px}
  /* annotations */
  .annotations{position:absolute;right:18px;top:18px;background:rgba(10,0,20,0.6);padding:8px;border-radius:8px;border:1px solid rgba(120,70,200,0.06);width:260px;color:#dcd6ff}
  .annotations h4{margin:0 0 6px 0;color:#ffd; font-size:1rem}
  .annotations ul{margin:0;padding-left:18px;font-size:0.95rem}
  .uploadRow{display:flex;gap:8px;align-items:center;margin-left:auto}
  .smallMuted{font-size:0.85rem;color:#cfc3ff}
  .legend{display:flex;gap:10px;margin-top:10px;align-items:center}
  .swatch{width:14px;height:10px;border-radius:3px;display:inline-block}
  footer{padding:10px;color:#bfb2ff;text-align:center;font-size:0.85rem}
</style>
</head>
<body>
  <div class="tabs" style="max-width:1180px;margin:0 auto;">
    <button class="tabButton active" data-tab="overviewTab">Overview</button>
    <button class="tabButton" data-tab="eventsTab">Events</button>
    <button class="tabButton" data-tab="calculatorsTab">Calculators</button>
  </div>

  <div class="container">
    <div id="overviewTab" class="tabContent" style="display:block">
      <h2>🔷 Crystalline Singularity — Overview</h2>
      <div class="panel">
        <p class="smallMuted">Interactive visual of your crystalline singularity anchored in the black hole. Playback and controls below modulate the plasma hum, crystal breathing and glow.</p>

        <div class="controls">
          <label>Spin speed</label>
          <input id="spinSlider" type="range" min="0" max="2.0" step="0.01" value="0.55">
          <label>Output / Pulse</label>
          <input id="outputSlider" type="range" min="0" max="2.0" step="0.01" value="0.9">
          <label>Visual size</label>
          <input id="sizeSlider" type="range" min="0.5" max="1.4" step="0.01" value="1.0">
          <div class="uploadRow" style="margin-left:auto">
            <input id="fileUpload" type="file" accept="image/*" />
            <button id="resetCrystal" class="secondary">Reset</button>
          </div>
        </div>

        <div id="overviewArea" aria-hidden="false">
          <canvas id="bgCanvas" width="1180" height="520"></canvas>

          <!-- glow and beam layers -->
          <div class="glowLayer" style="width:100%;height:100%;pointer-events:none">
            <div id="bigGlow" class="glow"></div>
            <div id="beam" class="beam" style="opacity:0.25"></div>
          </div>

          <!-- crystal image centered -->
          <div class="crystalWrap">
            <img id="crystalImg" src="" alt="crystal singularity" />
          </div>

          <!-- annotations panel -->
          <div class="annotations">
            <h4>Annotations</h4>
            <ul id="annoList">
              <li><strong>Crystalline singularity</strong> — conjectured photonic structure at the core.</li>
              <li><strong>Quantum plasma conduit</strong> — energy exchange / white-hole interface.</li>
              <li><strong>Accretion ring</strong> — heated material; shows gravitational lensing.</li>
            </ul>
            <div style="margin-top:8px">
              <label><input id="toggleAnnotations" type="checkbox" checked /> Show annotations</label>
            </div>
            <div class="legend" style="margin-top:8px">
              <span class="swatch" style="background:#8a33ff"></span><small class="smallMuted">Core</small>
              <span class="swatch" style="background:#ffd166"></span><small class="smallMuted">Accretion</small>
            </div>
          </div>
        </div>

        <div class="controls" style="margin-top:12px">
          <button id="playBtn">▶ Play Hum</button>
          <button id="pauseBtn" class="secondary">⏸ Pause</button>
          <button id="flashBtn" class="secondary">⚡ Flash (Live)</button>
          <label style="margin-left:12px">Mode</label>
          <select id="modeSelect">
            <option value="breath">Breathing</option>
            <option value="chime">Chime (tone-like)</option>
            <option value="silent">Silent</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Minimal placeholders for other tabs so page doesn't break -->
    <div id="eventsTab" class="tabContent" style="display:none">
      <h2>Events (kept minimal for now)</h2>
      <div class="panel">
        <p class="smallMuted">Events tab remains as in your project. I left this minimal to avoid overwriting your event code. Paste your events tab HTML/JS back here if you want me to re-integrate fully.</p>
      </div>
    </div>

    <div id="calculatorsTab" class="tabContent" style="display:none">
      <h2>Calculators</h2>
      <div class="panel">
        <p class="smallMuted">Calculators tab reserved; Sgr A* calculator can be moved here on request.</p>
      </div>
    </div>

  </div>

  <footer>Tip: upload your crystalline image or click Reset to use the placeholder. Use Play to allow audio-based modulation.</footer>

<script>
/* --------------------------
   Overview: visual + audio binding
   -------------------------- */
const bgCanvas = document.getElementById('bgCanvas');
const bgCtx = bgCanvas.getContext('2d');
const crystalImg = document.getElementById('crystalImg');
const bigGlow = document.getElementById('bigGlow');
const beam = document.getElementById('beam');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');
const flashBtn = document.getElementById('flashBtn');
const modeSelect = document.getElementById('modeSelect');

const spinSlider = document.getElementById('spinSlider');
const outputSlider = document.getElementById('outputSlider');
const sizeSlider = document.getElementById('sizeSlider');
const fileUpload = document.getElementById('fileUpload');
const resetCrystal = document.getElementById('resetCrystal');
const toggleAnnotations = document.getElementById('toggleAnnotations');

let width = bgCanvas.width, height = bgCanvas.height;
let coreAngle = 0;
let animHandle = null;
let liveFlash = false;

// placeholder crystal image URL — replace if you have one,
// or use the upload control below.
const PLACEHOLDER_URL = 'data:image/svg+xml;utf8,\
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800">\
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#2e0066"/><stop offset="1" stop-color="#ffcc99"/></linearGradient></defs>\
<rect width="100%" height="100%" fill="none"/>\
<g transform="translate(400,400)">\
<g fill="none" stroke="rgba(255,220,200,0.12)" stroke-width="4">\
<circle r="220" />\
<circle r="170" />\
</g>\
<text x="0" y="0" font-size="36" text-anchor="middle" fill="#cfc3ff" font-family="sans-serif">CRYSTAL</text>\
</g></svg>';

crystalImg.src = PLACEHOLDER_URL;

// upload handler
fileUpload.addEventListener('change', (e)=>{
  const f = e.target.files && e.target.files[0];
  if(!f) return;
  const url = URL.createObjectURL(f);
  crystalImg.src = url;
});

// reset to placeholder
resetCrystal.addEventListener('click', ()=>{
  crystalImg.src = PLACEHOLDER_URL;
  fileUpload.value = '';
});

/* annotations toggle */
toggleAnnotations.addEventListener('change', ()=>{
  document.querySelector('.annotations').style.display = toggleAnnotations.checked ? 'block' : 'none';
});

/* draw background (accretion rings + subtle lensing) */
function drawBackground(tick){
  bgCtx.clearRect(0,0,width,height);
  // radial vignette
  const g = bgCtx.createRadialGradient(width/2, height/2, 40, width/2, height/2, Math.max(width,height));
  g.addColorStop(0,'rgba(10,0,20,0.8)');
  g.addColorStop(1,'rgba(0,0,0,1)');
  bgCtx.fillStyle = g;
  bgCtx.fillRect(0,0,width,height);

  // dynamic thin accretion rings (animated)
  const cx = width/2, cy = height/2;
  for(let i=0;i<26;i++){
    const rr = 80 + i*8 + Math.sin(tick*0.0006 + i*0.4)*3;
    bgCtx.beginPath();
    bgCtx.arc(cx, cy, rr, 0, Math.PI*2);
    const alpha = 0.006 + 0.0009*i;
    bgCtx.strokeStyle = `rgba(255,160,60,${alpha})`;
    bgCtx.lineWidth = 1;
    bgCtx.stroke();
  }

  // lensing distortion hint: draw a faint ring warp
  const warp = 0.6 + 0.4*Math.sin(tick*0.0012);
  bgCtx.beginPath();
  bgCtx.arc(cx, cy, 52 + 6*warp, 0, Math.PI*2);
  bgCtx.strokeStyle = `rgba(140,80,255,0.08)`;
  bgCtx.lineWidth = 2;
  bgCtx.stroke();
}

/* animate crystal & glow according to controls and audio/amplitude */
let audioAnalyser = null;
let currentAmplitude = 0.0; // 0..1

function animate(now){
  drawBackground(now || performance.now());
  // spin and breathing
  const spin = parseFloat(spinSlider.value);
  const output = parseFloat(outputSlider.value);
  const size = parseFloat(sizeSlider.value);
  coreAngle += 0.016 * spin;
  // crystal transform: rotate + scale + breathing from amplitude
  const breath = 1 + 0.08 * Math.sin(coreAngle*1.6) + 0.25 * (currentAmplitude * output);
  crystalImg.style.transform = `translate(-50%,-50%) rotate(${coreAngle}rad) scale(${size * breath})`;
  // glow intensity
  const glowScale = 0.8 + 0.8 * (currentAmplitude * output) + 0.08*Math.sin(coreAngle*0.8);
  bigGlow.style.transform = `translate(-50%,-50%) scale(${1.0 * glowScale})`;
  bigGlow.style.opacity = Math.min(1, 0.24 + 0.6 * (currentAmplitude * output));
  beam.style.opacity = Math.min(0.8, 0.25 + 0.25*(currentAmplitude*output));
  // flash live
  if(liveFlash){
    // quick bright pulses controlled by amplitude
    const flashAlpha = Math.min(0.5, 0.16 + 0.6*Math.abs(Math.sin(now*0.02*spin)));
    bgCtx.fillStyle = `rgba(255,240,220,${flashAlpha*(currentAmplitude*output)})`;
    bgCtx.fillRect(0,0,width,height);
  }
  animHandle = requestAnimationFrame(animate);
}
animHandle = requestAnimationFrame(animate);

/* --------------------------
   Audio generation & analysis
   -------------------------- */
let audioCtx = null, oscMain = null, oscHarm = null, gainMain = null, gainHarm = null;
let analyser = null, dataArray = null, meterRAF = null;

function startAudio(){
  if(audioCtx && audioCtx.state !== 'closed') return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  const bufferLength = analyser.fftSize;
  dataArray = new Uint8Array(bufferLength);

  // main oscillator (sine sweep or steady depending on mode)
  oscMain = audioCtx.createOscillator();
  gainMain = audioCtx.createGain();
  oscMain.type = 'sine';
  oscMain.connect(gainMain); gainMain.connect(analyser); analyser.connect(audioCtx.destination);

  // harmonic for color
  oscHarm = audioCtx.createOscillator();
  gainHarm = audioCtx.createGain();
  oscHarm.type = 'sine';
  oscHarm.connect(gainHarm); gainHarm.connect(analyser);

  // set initial values; will be updated on play call
  gainMain.gain.value = 0.0;
  gainHarm.gain.value = 0.0;
  oscMain.start();
  oscHarm.start();
  // meter update
  meterLoop();
}

function stopAudio(){
  if(!audioCtx) return;
  try{ oscMain.stop(); oscHarm.stop(); }catch(e){}
  try{ oscMain.disconnect(); oscHarm.disconnect(); gainMain.disconnect(); gainHarm.disconnect(); analyser.disconnect(); }catch(e){}
  audioCtx.close().catch(()=>{});
  audioCtx = null; oscMain = null; oscHarm = null; gainMain = null; gainHarm = null; analyser = null;
  currentAmplitude = 0;
  if(meterRAF) cancelAnimationFrame(meterRAF);
  meterRAF = null;
}

function setAudioParams(mode){
  if(!audioCtx) startAudio();
  const now = audioCtx.currentTime;
  const spin = parseFloat(spinSlider.value);
  const output = parseFloat(outputSlider.value);
  let baseFreq = 30 + spin * 20; // base low frequency
  if(mode === 'chime') baseFreq *= 2.0;
  const maxFreq = 600 + output * 200;
  // frequency sweep around base for a more organic hum
  oscMain.frequency.cancelScheduledValues(now);
  oscMain.frequency.setValueAtTime(baseFreq, now);
  oscMain.frequency.exponentialRampToValueAtTime(Math.max(baseFreq*2, maxFreq), now + 1.8);

  oscHarm.frequency.cancelScheduledValues(now);
  oscHarm.frequency.setValueAtTime(baseFreq*2.0, now);
  oscHarm.frequency.exponentialRampToValueAtTime(Math.max(baseFreq*3, maxFreq*1.8), now + 1.8);

  // gain envelopes
  gainMain.gain.cancelScheduledValues(now);
  gainMain.gain.setValueAtTime(0.0001, now);
  gainMain.gain.linearRampToValueAtTime(0.24 * Math.min(1.0, output * 0.9), now + 0.05);
  gainMain.gain.exponentialRampToValueAtTime(0.0001, now + 2.5);

  gainHarm.gain.cancelScheduledValues(now);
  gainHarm.gain.setValueAtTime(0.0001, now);
  gainHarm.gain.linearRampToValueAtTime(0.06 * Math.min(1.0, output * 0.9), now + 0.05);
  gainHarm.gain.exponentialRampToValueAtTime(0.0001, now + 2.5);
}

/* meter loop: get amplitude from analyser */
function meterLoop(){
  if(!analyser || !dataArray) return;
  analyser.getByteTimeDomainData(dataArray);
  // compute RMS-like amplitude
  let sum = 0;
  for(let i=0;i<dataArray.length;i++){
    const v = (dataArray[i] - 128)/128;
    sum += v*v;
  }
  const rms = Math.sqrt(sum / dataArray.length);
  currentAmplitude = Math.min(1, rms * 3.2); // scale
  meterRAF = requestAnimationFrame(meterLoop);
}

/* UI actions */
playBtn.addEventListener('click', async ()=>{
  if(!audioCtx) startAudio();
  if(audioCtx.state === 'suspended') await audioCtx.resume().catch(()=>{});
  // create local envelope for continuous hum rather than one-shot
  setAudioParams(modeSelect.value);
  // keep oscillator running; to allow sustained hum, set steady gains (not scheduled decay)
  const now = audioCtx.currentTime;
  gainMain.gain.cancelScheduledValues(now);
  gainMain.gain.setValueAtTime(0.0001, now);
  gainMain.gain.linearRampToValueAtTime(0.24 * Math.min(1.0, parseFloat(outputSlider.value) * 0.9), now + 0.05);
  gainHarm.gain.cancelScheduledValues(now);
  gainHarm.gain.setValueAtTime(0.0001, now);
  gainHarm.gain.linearRampToValueAtTime(0.06 * Math.min(1.0, parseFloat(outputSlider.value) * 0.9), now + 0.05);
});

pauseBtn.addEventListener('click', ()=>{
  // ramp down gain quickly
  if(!audioCtx || !gainMain) return;
  const now = audioCtx.currentTime;
  gainMain.gain.cancelScheduledValues(now);
  gainHarm.gain.cancelScheduledValues(now);
  gainMain.gain.exponentialRampToValueAtTime(0.0001, now + 0.08);
  gainHarm.gain.exponentialRampToValueAtTime(0.0001, now + 0.08);
  // We keep oscillators alive (restarting costs). To fully stop:
  // stopAudio();
});

flashBtn.addEventListener('click', ()=>{
  liveFlash = !liveFlash;
  flashBtn.textContent = liveFlash ? '⚡ Live: ON' : '⚡ Flash (Live)';
});

modeSelect.addEventListener('change', ()=>{
  if(audioCtx) setAudioParams(modeSelect.value);
});

spinSlider.addEventListener('input', ()=>{
  if(audioCtx) setAudioParams(modeSelect.value);
});
outputSlider.addEventListener('input', ()=>{
  if(audioCtx) setAudioParams(modeSelect.value);
});
sizeSlider.addEventListener('input', ()=> {
  // immediate visual change handled in animate()
});

/* stop audio when page is hidden/unloaded to be tidy */
window.addEventListener('beforeunload', ()=> stopAudio());
document.addEventListener('visibilitychange', ()=> { if(document.hidden) { /* optionally pause */ } });

/* make canvas responsive to window resizing */
function resizeCanvas(){
  const rect = document.getElementById('overviewArea').getBoundingClientRect();
  width = Math.max(640, Math.floor(rect.width));
  height = Math.max(360, Math.floor(rect.height));
  bgCanvas.width = width; bgCanvas.height = height;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

</script>
</body>
</html>

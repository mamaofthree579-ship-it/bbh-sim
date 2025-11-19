import streamlit as st
import json
from textwrap import dedent
st.set_page_config(page_title="Quantum Black Hole — Anatomy Simulator", layout="wide")

st.title("🪐 Quantum Black Hole — Anatomy Simulator (Interactive)")

# Sidebar controls (these also seed the embedded canvas simulation)
with st.sidebar:
    st.header("Simulation controls")
    mass = st.slider("Mass (M☉, visual scale)", min_value=1e3, max_value=1e8, value=4_300_000, step=1000, format="%d")
    spin = st.slider("Spin (a*)", 0.0, 0.99, 0.5, step=0.01)
    hotspot_speed = st.slider("Hotspot angular speed", 0.01, 0.2, 0.026, step=0.002)
    hotspot_trail = st.slider("Hotspot trail length", 2, 12, 6, step=1)
    disk_thickness = st.slider("Disk thickness (H/R)", 0.02, 0.5, 0.12, step=0.01)
    lensing_strength = st.slider("Lensing / Einstein ring strength", 0.0, 1.0, 0.22, step=0.02)
    jet_activity = st.slider("Jet particle rate", 0, 200, 40, step=5)
    audio_on = st.checkbox("Enable immersive sound (stereo)", value=True)
    quality = st.selectbox("Render quality (performance)", ["Balanced", "High (more particles)", "Low (faster)"], index=0)
    # package settings
    settings = dict(
        mass=float(mass),
        spin=float(spin),
        hotspot_speed=float(hotspot_speed),
        hotspot_trail=int(hotspot_trail),
        disk_thickness=float(disk_thickness),
        lensing_strength=float(lensing_strength),
        jet_activity=int(jet_activity),
        audio_on=bool(audio_on),
        quality=str(quality),
    )

# Provide quick description
st.markdown(
    """
    **Notes**
    - Use the sidebar to tune mass, spin, hotspot behavior, disk thickness, jet activity and audio.
    - The simulation is rendered on an HTML5 `<canvas>` (inside this Streamlit app). Audio runs in your browser (if enabled).
    - For best results, use a modern browser (Chrome, Edge, Firefox).
    """
)

# Pack settings into JSON for JS
settings_json = json.dumps(settings)

# The HTML / JS simulator (embedded). It's self-contained: canvas + controls + WebAudio + animation loop.
html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
  :root{{ --bg: #05000a; --panel:#0f0210; --accent:#a66dff; --muted:#3a003f; --text:#e8ddff; }}
  body{{ margin:0; background:var(--bg); color:var(--text); font-family:Inter,Arial,Helvetica,sans-serif; }}
  #container{{ display:flex; gap:16px; padding:14px; align-items:flex-start; }}
  #left{{ flex:1; min-width:720px; max-width:1200px; }}
  #right{{ width:320px; }}
  canvas{{ width:100%; height:640px; border-radius:10px; background: radial-gradient(circle at 50% 45%, #0a0012 0%, #030006 60%); display:block; box-shadow: 0 8px 32px rgba(0,0,0,0.7); }}
  .panel{{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.03); color:var(--text); margin-bottom:12px; }}
  .row{ display:flex; align-items:center; gap:8px; margin-top:8px; }
  label{ font-size:0.95rem; color:#e3d7ff; }
  button{ padding:8px 12px; border-radius:8px; border:0; background:var(--accent); color:#090009; font-weight:700; cursor:pointer; }
  .small{ font-size:0.9rem; color:#cfc2ff; }
  .muted{ font-size:0.85rem; color:#b9aef8; }
  #legend{ display:flex; gap:8px; margin-top:8px; flex-wrap:wrap; }
  .sw{ display:flex; align-items:center; gap:6px; padding:6px 10px; border-radius:8px; border:1px solid rgba(255,255,255,0.02); background:rgba(255,255,255,0.01); }
</style>
</head>
<body>
<div id="container">
  <div id="left">
    <div class="panel">
      <canvas id="bhCanvas" width="1200" height="640"></canvas>
    </div>
    <div class="panel" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div class="small">Simulation controls (in-canvas quick knobs)</div>
        <div class="row" style="margin-top:8px;">
          <label class="muted">Motion speed</label>
          <input id="speedRange" type="range" min="0.2" max="2.0" step="0.02" value="1.0" style="width:220px;">
          <label id="speedVal" class="muted">1.00×</label>
        </div>
      </div>
      <div style="text-align:right;">
        <button id="toggleAudio">{'Audio: ON' if settings_json and settings['audio_on'] else 'Audio: OFF'}</button>
        <button id="pauseBtn" style="margin-left:8px;">Pause</button>
      </div>
    </div>
  </div>

  <div id="right">
    <div class="panel">
      <div class="small">Current parameters</div>
      <pre id="params" style="font-size:0.95rem; margin-top:8px;">Loading...</pre>
      <div id="legend" style="margin-top:8px;">
        <div class="sw"><div style="width:18px;height:12px;background:rgba(150,90,255,0.35);border-radius:3px;"></div><div class="muted">Event horizon</div></div>
        <div class="sw"><div style="width:18px;height:12px;background:rgba(255,180,80,0.18);border-radius:3px;"></div><div class="muted">Accretion disk</div></div>
        <div class="sw"><div style="width:18px;height:12px;background:rgba(120,200,255,0.18);border-radius:3px;"></div><div class="muted">Jet</div></div>
      </div>
    </div>

    <div class="panel">
      <div class="small">Quick tips</div>
      <ul class="muted">
        <li>Toggle audio to hear layered turbulence with Doppler panning.</li>
        <li>Use the sidebar for precise tuning (mass, spin, jet rate, etc.).</li>
        <li>Set quality to Low on slow machines.</li>
      </ul>
    </div>
  </div>
</div>

<script>
/* ---------- Settings ---------- */
const seedSettings = {json_settings};
let cfg = Object.assign({{
  canvasWidth:1200, canvasHeight:640
}}, seedSettings);

const qs = cfg.quality || "Balanced";
if(qs === "Low") {{
  cfg.diskSamples = 160;
  cfg.jetMax = Math.min(cfg.jet_activity, 60);
}} else if(qs === "High (more particles)") {{
  cfg.diskSamples = 640;
  cfg.jetMax = Math.min(cfg.jet_activity, 350);
}} else {{
  cfg.diskSamples = 320;
  cfg.jetMax = Math.min(cfg.jet_activity, 140);
}}

/* ---------- Canvas setup ---------- */
const canvas = document.getElementById('bhCanvas');
const ctx = canvas.getContext('2d', {{ alpha: false }});
canvas.width = cfg.canvasWidth;
canvas.height = cfg.canvasHeight;

const W = canvas.width, H = canvas.height;
const cx = W/2, cy = H/2;

/* ---------- Visual parameters ---------- */
let mass = cfg.mass;         // M_sun visual scale
let spin = cfg.spin;
let hotspotSpeed = cfg.hotspot_speed;
let hotspotTrail = cfg.hotspot_trail;
let diskThickness = cfg.disk_thickness;
let lensingStrength = cfg.lensing_strength;
let jetActivity = cfg.jet_activity;
let audioEnabled = cfg.audio_on;

/* Motion control */
const speedRange = document.getElementById('speedRange');
const speedVal = document.getElementById('speedVal');
speedRange.addEventListener('input', ()=> {{
  motionScale = parseFloat(speedRange.value);
  speedVal.textContent = motionScale.toFixed(2) + "×";
}});

document.getElementById('toggleAudio').addEventListener('click', ()=> {{
  audioEnabled = !audioEnabled;
  document.getElementById('toggleAudio').textContent = audioEnabled ? 'Audio: ON' : 'Audio: OFF';
  if(audioEnabled) initAudio(); else stopAllAudio();
}});

const pauseBtn = document.getElementById('pauseBtn');
let paused = false;
pauseBtn.addEventListener('click', ()=> {{ paused = !paused; pauseBtn.textContent = paused ? 'Resume' : 'Pause'; }});

/* reflect sidebar params in info block */
function updateParamsPanel() {{
  const p = {{
    mass: mass,
    spin: spin,
    hotspotSpeed: hotspotSpeed,
    hotspotTrail: hotspotTrail,
    diskThickness: diskThickness,
    lensingStrength: lensingStrength,
    jetActivity: jetActivity,
    quality: cfg.quality
  }};
  document.getElementById('params').textContent = JSON.stringify(p, null, 2);
}}
updateParamsPanel();

/* ---------- Physics helpers ---------- */
const G = 6.67430e-11;
const c = 2.99792458e8;
const M_sun = 1.98847e30;

/* Schwarzschild radius in meters (for display only) */
function schwarzschildRadius(Msol) {{
  const M = Msol * M_sun;
  return 2*G*M/(c*c);
}}

/* Relativistic Doppler factor (approx, special-relativistic) */
function dopplerFactor(beta, cosTheta) {{
  // beta = v/c, cosTheta = cos(angle to observer)
  return Math.sqrt((1 - beta)/(1 + beta)) ** -1 * (1.0); // simplified mapping; use approximate
}}

/* Color helper: map temperature-like to RGB (cool->hot) */
function tempToRGBA(t, alpha=1.0) {{
  // t in [0,1] (0 cold redder? we'll go blue->amber mapping)
  const r = Math.min(255, Math.floor(180 + 75 * t));
  const g = Math.min(255, Math.floor(120 + 100 * t));
  const b = Math.min(255, Math.floor(200 - 160 * t));
  return `rgba(${r},${g},${b},${alpha})`;
}}

/* ---------- Procedural disk: sample ring radii + local intensity ---------- */
function sampleDiskPoints(n) {{
  const pts = [];
  const rInner = Math.max(40, 8 + Math.log10(mass+1)*6);  // visually scaled inner radius
  const rOuter = Math.min(Math.max(rInner*3.5, 220), W*0.42);
  for(let i=0;i<n;i++){{
    // radial distribution biased toward inner radii
    const u = Math.random();
    const r = rInner + (rOuter - rInner) * Math.pow(u, 0.6);
    const theta = Math.random() * Math.PI * 2;
    // z height from torus H/R param -> gaussian vertical displacement
    const H_over_R = diskThickness;
    const z = (Math.random()*2 - 1) * H_over_R * r * (0.6 + 0.4*Math.random());
    pts.push({{ r, theta, z }});
  }}
  return {{ pts, rInner, rOuter }};
}

/* ---------- Hotspots ---------- */
class Hotspot {{
  constructor(r, theta, colorScale=1.0){{
    this.r = r;
    this.theta = theta;
    this.colorScale = colorScale;
    this.brightness = 1.0;
    this.age = 0;
  }}
  step(dt){{
    // angular motion plus spiral inward
    this.theta += hotspotSpeed * 0.8 * dt * motionScale;
    // small inward drift
    this.r *= 1.0 - 0.0007*dt*motionScale;  // slow drift
    this.age += dt;
    // cooling baseline
    this.brightness = Math.max(0.12, 1.0 - 0.12*this.age);
  }}
}}

/* ---------- Jet particles ---------- */
class JetParticle {{
  constructor(x,y,z,vx,vy,vz,color,life){{
    this.x=x;this.y=y;this.z=z;this.vx=vx;this.vy=vy;this.vz=vz;this.color=color;this.life=life;this.age=0;
  }}
  step(dt){{
    this.x += this.vx*dt*motionScale;
    this.y += this.vy*dt*motionScale;
    this.z += this.vz*dt*motionScale;
    this.age += dt;
    return this.age < this.life;
  }}
}}

/* ---------- Simulation state ---------- */
let motionScale = 1.0;
let lastTime = performance.now();
let hotspots = [];
let disk = sampleDiskPoints(cfg.diskSamples);
let jetParticles = [];
let playhead = 0;

/* initial hotspots */
for(let i=0;i<3;i++){{
  const r0 = disk.rInner + (disk.rOuter-disk.rInner)* (0.12 + i*0.12);
  hotspots.push(new Hotspot(r0, Math.random()*Math.PI*2));
}}

/* audio: layered wind + whirlpool texture synthesized in stereo */
let audioCtx = null, masterGain=null, cloudNode=null, whirlNode=null, panner=null, harmonicGain=null;
async function initAudio(){{
  if(!audioEnabled) return;
  if(!audioCtx) {{
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = audioCtx.createGain(); masterGain.gain.value = 0.28; masterGain.connect(audioCtx.destination);

    // cloud noise (hurricane-like)
    const bufferSize = 2*audioCtx.sampleRate;
    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    for(let i=0;i<bufferSize;i++) data[i] = (Math.random()*2-1)*0.25;
    cloudNode = audioCtx.createBufferSource(); cloudNode.buffer = noiseBuffer; cloudNode.loop = true;
    const cloudGain = audioCtx.createGain(); cloudGain.gain.value = 0.12;
    cloudNode.connect(cloudGain); cloudGain.connect(masterGain);

    // whirlpool layer: filtered oscillator with slow pitch modulation
    const osc = audioCtx.createOscillator(); osc.type = 'sine';
    const oscGain = audioCtx.createGain(); oscGain.gain.value = 0.05;
    const lpf = audioCtx.createBiquadFilter(); lpf.type='lowpass'; lpf.frequency.value = 300;
    osc.connect(oscGain); oscGain.connect(lpf); lpf.connect(masterGain);
    osc.start();

    // stereo panner for Doppler-like effect
    panner = audioCtx.createStereoPanner();
    // connect parts through panner so the whole mix can pan
    const merger = audioCtx.createGain(); merger.gain.value = 1.0;
    // rewire: cloudGain->merger->panner->masterGain
    cloudGain.disconnect(); cloudGain.connect(merger);
    oscGain.disconnect(); oscGain.connect(merger);
    merger.connect(panner); panner.connect(masterGain);

    cloudNode.start();

    // store nodes
    whirlNode = osc;
    harmonicGain = oscGain;
  }}
}}

function stopAllAudio(){{
  try{{ if(audioCtx) audioCtx.close(); }}catch(e){console.log(e);}
  audioCtx = null; masterGain=null; cloudNode=null; whirlNode=null; panner=null; harmonicGain=null;
}}

/* ---------- Drawing helpers ---------- */
function drawBackground(){{
  // subtle radial vignette / gradient
  const g = ctx.createRadialGradient(cx, cy*0.9, 10, cx, cy, Math.max(W,H));
  g.addColorStop(0, '#06000b');
  g.addColorStop(0.35, '#060010');
  g.addColorStop(1, '#020003');
  ctx.fillStyle = g; ctx.fillRect(0,0,W,H);
}}

function drawPhotonRing(){{
  const r = Math.max(48, 1.5 * (schwarzschildRadius(mass)/1e8)); // visual approx
  ctx.beginPath();
  ctx.arc(cx,cy, r * (1.0 + lensingStrength*0.3), 0, Math.PI*2);
  ctx.strokeStyle = `rgba(200,170,255,${0.08 + 0.08*lensingStrength})`;
  ctx.lineWidth = 2 + 6*lensingStrength;
  ctx.stroke();
}}

function drawEventHorizon(){{
  const r = Math.max(36, 1 * (schwarzschildRadius(mass)/1e8));
  ctx.beginPath();
  ctx.arc(cx,cy,r,0,Math.PI*2);
  // make it slightly purple instead of pure black
  ctx.fillStyle = '#080006';
  ctx.fill();
  // faint glow
  ctx.beginPath();
  ctx.arc(cx,cy,r+6,0,Math.PI*2); ctx.strokeStyle = 'rgba(150,90,255,0.12)'; ctx.lineWidth=2; ctx.stroke();
}}

function drawDisk(){{
  // procedural radial shading with vertical thickness & soft self-shadowing approximation
  const { pts, rInner, rOuter } = disk;
  // draw rings back-to-front: outer to inner to approximate occlusion
  const steps = 140;
  for(let i=steps;i>=0;i--){{
    const t = i/steps;
    const r = rInner + (rOuter - rInner)*t;
    // radial color and shadow factor (inner brighter)
    const shade = 0.12 + 0.88*(1 - Math.pow(t, 0.9));
    // tilt the disk slightly for pseudo-3D (viewing angle)
    // approximate self-shadow: when inner is bright it can shadow outer by spin factor
    const shadow = Math.max(0, Math.sin(spin * 3.0) * 0.08 * (1-t));
    const a = Math.max(0.03, 0.28*shade - shadow);
    // ring path
    ctx.beginPath();
    ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.strokeStyle = `rgba(255,180,80,${a})`;
    ctx.lineWidth = Math.max(1, Math.min(6, 6*(1 - t)* (1 + 0.4*diskThickness)));
    ctx.stroke();
  }}
  // small turbulence overlay: thin wispy curves (low cost)
  for(let k=0;k<6;k++){{
    ctx.beginPath(); const base = rInner + Math.random()*(rOuter-rInner);
    for(let a=0;a<360;a+=6){{
      const rad = base + Math.sin((a + k*23)*0.07 + performance.now()*0.0004*(1+k))*6;
      const x = cx + Math.cos(a*Math.PI/180) * rad;
      const y = cy + Math.sin(a*Math.PI/180) * rad * 0.95;
      if(a===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }}
    ctx.strokeStyle = 'rgba(255,200,150,0.012)'; ctx.lineWidth=1; ctx.stroke();
  }}
}}

function drawHotspots(dt){{
  for(let i=0;i<hotspots.length;i++){{
    const hs = hotspots[i];
    hs.step(dt);
    // map polar (r,theta,z=0) to screen
    const rx = cx + Math.cos(hs.theta) * hs.r;
    const ry = cy + Math.sin(hs.theta) * hs.r * 0.92; // slight flatten
    // doppler-ish brightness: approximate with angular velocity component
    const approachFactor = (Math.cos(hs.theta) * hotspotSpeed * spin) * 0.5 + 0.5;
    const dop = 0.7 + 0.6*approachFactor;
    const color = tempToRGBA( Math.min(1, hs.colorScale * dop) , Math.min(1, 0.42*hs.brightness) );
    // motion blur via drawing faded circles along small recent trail
    const trailLen = Math.max(2, Math.min(14, hotspotTrail));
    for(let t=0;t<trailLen;t++){{
      const tt = t / trailLen;
      const thetaT = hs.theta - tt * 0.08 * hotspotSpeed * 6;
      const rT = hs.r + tt * 6;
      const x = cx + Math.cos(thetaT) * rT;
      const y = cy + Math.sin(thetaT) * rT * 0.92;
      ctx.beginPath();
      const rad = Math.max(1.0, 6*(1-tt)*hs.brightness);
      ctx.arc(x,y,rad,0,Math.PI*2);
      ctx.fillStyle = tempToRGBA( Math.min(1, hs.colorScale * dop) , 0.10 * (1-tt) * hs.brightness );
      ctx.fill();
    }}
    // main core
    ctx.beginPath();
    ctx.arc(rx,ry, Math.max(3, 6*hs.brightness), 0, Math.PI*2);
    ctx.fillStyle = color; ctx.fill();

    // flare on pericenter (if r small)
    const flare = Math.max(0, 1.0 - (hs.r / (disk.rInner + 40)));
    if(flare > 0.35){
      ctx.beginPath();
      ctx.arc(rx,ry, 18*flare, 0, Math.PI*2);
      ctx.fillStyle = `rgba(255,230,200,${0.08*flare})`; ctx.fill();
      // brief brightening affects disk local brightness (we simulate by drawing small highlight)
      ctx.beginPath();
      ctx.arc(cx + Math.cos(hs.theta)* (hs.r*0.95), cy + Math.sin(hs.theta)*(hs.r*0.92), 28*flare, 0, Math.PI*2);
      ctx.strokeStyle = `rgba(255,200,160,${0.03*flare})`; ctx.lineWidth=2*flare; ctx.stroke();
    }}

  }}
}

/* ---------- Jet plume ---------- */
function emitJet(){{
  // occasionally emit a particle from near center up along +/- y axis
  if(jetParticles.length > cfg.jetMax) return;
  const side = Math.random() > 0.5 ? 1 : -1;
  const speed = 0.12 + Math.random()*0.24 + 0.02 * spin;
  const vx = (Math.random()-0.5)*0.6;
  const vy = - (0.5 + 0.2*Math.random()) * speed * side;
  const vz = (Math.random()-0.5)*0.6;
  const x = cx + (Math.random()-0.5)*6;
  const y = cy + (Math.random()-0.5)*6;
  const z = 0;
  const color = `rgba(160,220,255,${0.6 + Math.random()*0.4})`;
  const life = 1200 + Math.random()*1800;
  jetParticles.push(new JetParticle(x,y,z,vx,vy,vz,color,life));
}}

function drawJet(dt){{
  // spawn according to jetActivity scaled by motionScale
  const spawnProb = Math.min(1, (jetActivity / 40) * 0.04 * (motionScale));
  if(Math.random() < spawnProb) emitJet();
  // advance & draw particles
  for(let i=jetParticles.length-1;i>=0;i--){{
    const p = jetParticles[i];
    const alive = p.step(dt);
    // project z as small vertical offset
    ctx.beginPath();
    const alpha = Math.max(0, 1 - p.age / p.life);
    ctx.fillStyle = p.color.replace(/[^,]+\\)$/,' ' + alpha + ')');
    ctx.fillRect(p.x - 2, p.y - (p.age*0.02), 4, 6);
    if(!alive) jetParticles.splice(i,1);
    // jet-disk interaction flash: if particle near disk inner radius and alpha high => small flash
    const d2 = Math.hypot(p.x - cx, p.y - cy);
    if(d2 < disk.rInner*1.2 && alpha > 0.65 && Math.random() < 0.02){{
      // small radial flash
      ctx.beginPath();
      ctx.arc(cx,cy, 22 + Math.random()*30, 0, Math.PI*2);
      ctx.fillStyle = `rgba(255,220,160,${0.06 + Math.random()*0.08})`; ctx.fill();
    }}
  }}
}

/* ---------- Summary graphs (small, lightweight) ---------- */
function drawSummaryMini(progress=0){{
  // subtle pulse ring showing inspiral progress
  const r = Math.max(40, 1 + schwarzschildRadius(mass)/1e8);
  ctx.beginPath();
  ctx.arc(cx,cy, r + 220*progress, 0, Math.PI*2);
  ctx.strokeStyle = 'rgba(120,200,255,' + (0.03 + 0.06*progress) + ')';
  ctx.lineWidth = 1 + 3*progress;
  ctx.stroke();
}}

/* ---------- Main loop ---------- */
let raf = null;
function step(){{
  const now = performance.now();
  let dt = Math.min(40, now - lastTime); // ms
  lastTime = now;
  if(paused) {{ raf = requestAnimationFrame(step); return; }}

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
    }}
  }}

  // remove any hotspots that plunged inside horizon
  hotspots = hotspots.filter(h=> h.r > Math.max(10, 0.8 * (schwarzschildRadius(mass)/1e8)) );

  // occasionally spawn new hotspot at outer disk
  if(Math.random() < 0.01 * motionScale) {{
    const newr = disk.rOuter * (0.88 + Math.random()*0.12);
    hotspots.push(new Hotspot(newr, Math.random()*Math.PI*2, 0.8 + Math.random()*0.6));
    // keep hotspot count reasonable
    if(hotspots.length > 8) hotspots.shift();
  }}

  raf = requestAnimationFrame(step);
}}

/* Start animation */
lastTime = performance.now();
let playDurMs = 4200;
let playStart = performance.now();
let playheadMs = 0;
if(audioEnabled) initAudio();
step();

/* Expose some runtime tuning (for dev) */
window.__QBH = {{
  hotspots, disk, jetParticles, cfg, redraw: ()=>{{ drawBackground(); drawDisk(); drawEventHorizon(); drawHotspots(16); }}
}};

/* --- utility: replace tokens inserted by python --- */
function replaceJSONTokens(){{ /* placeholder if needed */ }}

</script>
</body>
</html>
""".replace("{json_settings}", settings_json)

# Render the HTML component. Give it a large height so canvas is not clipped.
st.components.v1.html(html, height=820, scrolling=True)

# Footer / README link
st.markdown(
    """
    **Next steps**
    - If you'd like, I will: (A) add a compact event-chirp generator linked to the Events tab, (B) wire the time-dilation calculators into per-hotspot cooling, or (C) export frames as PNG sequence for high-quality renders.
    - Tell me which and I'll update the app.
    """
)

## Start: Crystalline singularity widget (paste into your Overview tab panel) -->
<div id="crystalWidget" style="max-width:920px;margin:12px auto;padding:12px;background:rgba(10,0,20,0.6);border-radius:10px;border:1px solid rgba(120,60,160,0.15);">
  <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
    <div style="flex:1;min-width:320px">
      <canvas id="crystalCanvas" width="640" height="360" style="width:100%;height:auto;border-radius:8px;background:radial-gradient(circle at 40% 30%, #130018 0%, #040006 60%);display:block"></canvas>
      <div style="margin-top:8px;display:flex;gap:8px;align-items:center;">
        <input id="crystalFile" type="file" accept="image/*">
        <button id="startSoundBtn" class="btn" style="padding:6px 10px">Start Sound</button>
        <button id="stopSoundBtn" class="btn secondary" style="padding:6px 10px">Stop Sound</button>
      </div>
    </div>

    <div style="width:320px">
      <div style="margin-bottom:8px"><strong>Crystalline Singularity Controls</strong></div>

      <label class="smallMuted">Spin</label>
      <input id="spinSlider" type="range" min="0" max="2.0" step="0.01" value="0.5" style="width:100%"><div id="spinVal" class="muted" style="text-align:right">0.50</div>

      <label class="smallMuted">Output Strength</label>
      <input id="outputSlider" type="range" min="0" max="1" step="0.01" value="0.12" style="width:100%"><div id="outVal" class="muted" style="text-align:right">0.12</div>

      <label class="smallMuted">Plasma Hum</label>
      <input id="humSlider" type="range" min="0" max="1" step="0.01" value="0.25" style="width:100%"><div id="humVal" class="muted" style="text-align:right">0.25</div>

      <div style="margin-top:10px;color:#dcdaf8;font-size:0.9rem">
        <strong>Legend</strong>
        <ul style="margin:6px 0 0 16px;padding:0;color:#d6ccff;font-size:0.9rem">
          <li>Core image: crystalline singularity (upload)</li>
          <li>Glow: near-horizon plasma / energy</li>
          <li>Beam: white-hole output when <em>Output Strength</em> &gt; 0</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  const canvas = document.getElementById('crystalCanvas');
  const ctx = canvas.getContext('2d', { alpha: true });
  let W = canvas.width, H = canvas.height;
  let coreImg = null;
  let t0 = performance.now();
  let spin = Number(document.getElementById('spinSlider').value);
  let outputStrength = Number(document.getElementById('outputSlider').value);
  let hum = Number(document.getElementById('humSlider').value);
  const spinVal = document.getElementById('spinVal');
  const outVal = document.getElementById('outVal');
  const humVal = document.getElementById('humVal');

  // audio
  let audioCtx = null, baseOsc=null, harmOsc=null, baseGain=null, harmGain=null;
  let isPlaying = false;

  // responsive canvas (keeps internal resolution stable)
  function resize() {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    W = Math.floor(rect.width * ratio);
    H = Math.floor(rect.height * ratio);
    canvas.width = W; canvas.height = H;
  }
  window.addEventListener('resize', resize);
  resize();

  // load uploaded image
  document.getElementById('crystalFile').addEventListener('change', function(ev){
    const f = ev.target.files && ev.target.files[0];
    if(!f) return;
    const url = URL.createObjectURL(f);
    const img = new Image();
    img.onload = ()=> { coreImg = img; URL.revokeObjectURL(url); };
    img.src = url;
  });

  // sliders
  document.getElementById('spinSlider').addEventListener('input', (e)=>{
    spin = Number(e.target.value); spinVal.textContent = spin.toFixed(2);
  });
  document.getElementById('outputSlider').addEventListener('input', (e)=>{
    outputStrength = Number(e.target.value); outVal.textContent = outputStrength.toFixed(2);
  });
  document.getElementById('humSlider').addEventListener('input', (e)=>{
    hum = Number(e.target.value); humVal.textContent = hum.toFixed(2);
    updateAudioParams();
  });

  // audio controls
  document.getElementById('startSoundBtn').addEventListener('click', async ()=>{
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') await audioCtx.resume().catch(()=>{});
    if(!isPlaying) startAudio(); // create and start
  });
  document.getElementById('stopSoundBtn').addEventListener('click', ()=> stopAudio());

  function startAudio(){
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    // base deep hum (low freq)
    baseOsc = audioCtx.createOscillator(); baseGain = audioCtx.createGain();
    baseOsc.type = 'sine'; baseOsc.frequency.value = 16 + hum*30; # 16–46 Hz
    baseGain.gain.value = 0.12 * (0.5 + hum*0.8); // amplitude controlled by hum
    baseOsc.connect(baseGain); baseGain.connect(audioCtx.destination);

    // harmonic to make it audible
    harmOsc = audioCtx.createOscillator(); harmGain = audioCtx.createGain();
    harmOsc.type = 'sine'; harmOsc.frequency.value = (16 + hum*30) * 3.6; // harmonic
    harmGain.gain.value = 0.02 + outputStrength*0.08;
    harmOsc.connect(harmGain); harmGain.connect(audioCtx.destination);

    // subtle LFO to modulate amplitude (simulate plasma breathing)
    const lfo = audioCtx.createOscillator(); const lfoGain = audioCtx.createGain();
    lfo.type = 'sine'; lfo.frequency.value = 0.12 + spin*0.4; // slow modulation depending on spin
    lfoGain.gain.value = 0.05 * (0.6 + hum);
    lfo.connect(lfoGain);
    lfoGain.connect(baseGain.gain);
    lfoGain.connect(harmGain.gain);
    lfo.start();

    baseOsc.start(); harmOsc.start();
    isPlaying = true;
    updateAudioParams();
  }

  function updateAudioParams(){
    if(!audioCtx || !isPlaying) return;
    try{
      baseOsc.frequency.setTargetAtTime(16 + hum*30, audioCtx.currentTime, 0.05);
      baseGain.gain.setTargetAtTime(0.12 * (0.5 + hum*0.8), audioCtx.currentTime, 0.05);
      harmOsc.frequency.setTargetAtTime((16 + hum*30) * (2.2 + outputStrength*1.8), audioCtx.currentTime, 0.05);
      harmGain.gain.setTargetAtTime(0.02 + outputStrength*0.1 + hum*0.02, audioCtx.currentTime, 0.05);
    }catch(e){
      // nodes may be stopped
    }
  }

  function stopAudio(){
    if(!isPlaying) return;
    try{ baseOsc.stop(); harmOsc.stop(); }catch(e){}
    try{ baseOsc.disconnect(); harmOsc.disconnect(); baseGain.disconnect(); harmGain.disconnect(); }catch(e){}
    baseOsc = harmOsc = baseGain = harmGain = null;
    isPlaying = false;
  }

  // draw loop
  function draw(now){
    const dt = (now - t0)/1000;
    t0 = now;
    // clear
    ctx.clearRect(0,0,W,H);

    // center coordinates
    const cx = W/2, cy = H/2;

    // background subtle radial (simulating warped space)
    const rg = ctx.createRadialGradient(cx, cy, 10, cx, cy, Math.max(W,H)/1.2);
    rg.addColorStop(0, 'rgba(30,8,30,1)');
    rg.addColorStop(1, 'rgba(2,0,6,1)');
    ctx.fillStyle = rg; ctx.fillRect(0,0,W,H);

    // a faint horizon ring (deep purple gradient) slightly responsive to spin
    const horizonR = Math.min(W,H) * 0.095 * (1 + 0.03*spin);
    ctx.beginPath();
    ctx.arc(cx, cy, horizonR, 0, Math.PI*2);
    ctx.lineWidth = Math.max(2, 2 + spin*1.5);
    ctx.strokeStyle = `rgba(140,80,255,${0.35 + 0.1*Math.sin(now*0.002)})`;
    ctx.stroke();

    // draw accretion disk as gradient rings (animated)
    const diskBands = 26;
    for(let i=0;i<diskBands;i++){
      const rr = horizonR + 8 + i * (horizonR*0.06);
      ctx.beginPath();
      ctx.arc(cx, cy, rr, 0, Math.PI*2);
      const alpha = 0.003 + 0.009 * Math.exp(-i/8) * (0.8 + 0.4*Math.sin(now*0.001 + i*0.12));
      ctx.strokeStyle = `rgba(${240 - i*4}, ${160 - i*3}, ${40 + i}, ${alpha})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // core: if user image loaded, draw it as textured crystal with rotation; otherwise draw polygonal crystalline shape
    ctx.save();
    ctx.translate(cx, cy);
    const rot = now*0.0008 * (1 + spin*1.6); // rotation speed scaled by spin
    ctx.rotate(rot);

    // draw glow behind core
    const glowR = horizonR * (0.9 + 0.6 * (0.5 + outputStrength));
    const glow = ctx.createRadialGradient(0,0,0,0,0,glowR);
    glow.addColorStop(0, `rgba(${200 + 55*outputStrength}, ${120 + 80*spin}, ${255 - 40*spin}, ${0.22 + 0.35*outputStrength})`);
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(0,0,glowR,0,Math.PI*2); ctx.fill();

    if(coreImg){
      // draw image centered, clipped to circle
      const imgSize = horizonR * 1.6;
      ctx.beginPath(); ctx.arc(0,0,imgSize*0.62,0,Math.PI*2); ctx.closePath(); ctx.clip();
      // slight scale-pulse based on hum
      const scalePulse = 1 + 0.03*Math.sin(now*0.002 * (1 + spin));
      ctx.drawImage(coreImg, -imgSize/2*scalePulse, -imgSize/2*scalePulse, imgSize*scalePulse, imgSize*scalePulse);
      ctx.restore();
    } else {
      // polygonal crystalline core fallback
      const petals = 12;
      const coreR = horizonR * 0.55;
      ctx.beginPath();
      for(let k=0;k<petals;k++){
        const a = (k / petals) * Math.PI*2;
        const rLocal = coreR * (0.7 + 0.35*Math.sin(a*3 + now*0.001 + spin));
        const x = Math.cos(a) * rLocal, y = Math.sin(a) * rLocal * (0.76 + 0.1*Math.cos(now*0.001 + a*2));
        if(k===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
      }
      ctx.closePath();
      ctx.fillStyle = `rgba(200,170,255,${0.95 - 0.35*outputStrength})`;
      ctx.fill();
      ctx.restore();
    }

    // white-hole beam: a cone/beam that pulses when Output > 0
    if(outputStrength > 0.01){
      ctx.save();
      ctx.translate(cx, cy - horizonR*0.2);
      // beam angle & length
      const beamLen = H*0.6 * (0.4 + outputStrength*1.6);
      const beamWidth = Math.max(6, 40 * (0.1 + outputStrength));
      // pulse
      const pulse = 0.5 + 0.5*Math.sin(now*0.01* (1 + spin));
      const g = ctx.createLinearGradient(0, -20, 0, -beamLen);
      g.addColorStop(0, `rgba(255, 240, 200, ${0.06 + 0.42*outputStrength*pulse})`);
      g.addColorStop(1, 'rgba(255,200,150,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.moveTo(-beamWidth, -20);
      ctx.lineTo(-beamWidth*0.3, -beamLen);
      ctx.lineTo(beamWidth*0.3, -beamLen);
      ctx.lineTo(beamWidth, -20);
      ctx.closePath();
      ctx.fill();
      // a bright central jet line
      ctx.beginPath();
      ctx.moveTo(0, -20);
      ctx.lineTo(0, -beamLen);
      ctx.strokeStyle = `rgba(255, 220, 180, ${0.25 + 0.7*outputStrength})`;
      ctx.lineWidth = Math.max(1, 3 + 12*outputStrength);
      ctx.stroke();
      ctx.restore();
    }

    // small annotation text (light)
    ctx.fillStyle = 'rgba(220,210,255,0.7)';
    ctx.font = `${Math.max(12, Math.round(W*0.015))}px sans-serif`;
    ctx.fillText('Crystalline Singularity (visual)', 16, H - 28);
    ctx.fillStyle = 'rgba(180,170,255,0.45)';
    ctx.fillText(`spin: ${spin.toFixed(2)}   output: ${outputStrength.toFixed(2)}   hum: ${hum.toFixed(2)}`, 16, H - 10);

    requestAnimationFrame(draw);
  }

  requestAnimationFrame(draw);

  // expose a small API for external wiring if you want
  window.crystalWidget = {
    setSpin: v => { spin = v; document.getElementById('spinSlider').value = v; spinVal.textContent = v.toFixed(2); },
    setOutput: v => { outputStrength = v; document.getElementById('outputSlider').value = v; outVal.textContent = v.toFixed(2); },
    setHum: v => { hum = v; document.getElementById('humSlider').value = v; humVal.textContent = v.toFixed(2); updateAudioParams(); }
  };
})();
</script>
<!-- End: Crystalline singularity widget -->

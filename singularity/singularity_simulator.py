import streamlit as st
import base64

st.set_page_config(page_title="Crystalline Singularity Simulator", layout="wide")

st.title("🔷 Crystalline Singularity — Black Hole Core Visualizer")
st.caption("An interactive visualization exploring the crystalline singularity concept and plasma dynamics within a black hole environment.")

# Sidebar controls
st.sidebar.header("Control Panel")
spin_speed = st.sidebar.slider("Spin speed", 0.0, 2.0, 0.55, 0.01)
output_strength = st.sidebar.slider("Output / Pulse strength", 0.0, 2.0, 0.9, 0.01)
visual_size = st.sidebar.slider("Visual size", 0.5, 1.4, 1.0, 0.01)
live_flash = st.sidebar.checkbox("Enable live flash effect", value=False)
mode = st.sidebar.selectbox("Audio mode", ["breathing", "chime", "silent"])
play_audio = st.sidebar.button("▶ Play Hum")
pause_audio = st.sidebar.button("⏸ Pause Audio")

import os
import base64

# Determine the absolute path of singularity.png
root_dir = os.path.dirname(os.path.abspath(__file__))
local_image_path = os.path.join(root_dir, "singularity.png")

uploaded_file:
    data = uploaded_file.read()
    encoded = base64.b64encode(data).decode()
    crystal_src = f"data:image/png;base64,{encoded}"

elif os.path.exists(local_image_path):
    with open(local_image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    crystal_src = f"data:image/png;base64,{encoded}"

else:
    # Fallback placeholder
    crystal_src = "https://placehold.co/600x600/1b0033/FFFFFF?text=Singularity"


# Use a regular triple-quoted string (not f-string) and insert Python vars via .format()
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    background: radial-gradient(ellipse at center,#070012 0%, #020004 70%);
    overflow: hidden;
    color: white;
    font-family: Arial, sans-serif;
  }}
  canvas {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }}
  .crystal {{
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%,-50%) scale({visual_size});
    width: 60%;
    mix-blend-mode: screen;
    filter: drop-shadow(0 0 30px rgba(150,100,255,0.4));
    animation: spin {spin_time}s linear infinite;
  }}
  @keyframes spin {{
    from {{ transform: translate(-50%,-50%) rotate(0deg) scale({visual_size}); }}
    to {{ transform: translate(-50%,-50%) rotate(360deg) scale({visual_size}); }}
  }}
  .glow {{
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%,-50%);
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle at center, rgba(150,80,255,0.3), rgba(0,0,0,0));
    filter: blur(60px);
    animation: pulse {pulse_time}s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%,100% {{ opacity: 0.6; transform: translate(-50%,-50%) scale(1.0); }}
    50% {{ opacity: 1; transform: translate(-50%,-50%) scale(1.2); }}
  }}
</style>
</head>
<body>
  <canvas id="bgCanvas"></canvas>
  <div class="glow"></div>
  <img src="{crystal_src}" class="crystal" alt="Crystalline Singularity">
  <script>
    const canvas = document.getElementById('bgCanvas');
    const ctx = canvas.getContext('2d');
    let w, h;
    function resize() {{
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }}
    window.addEventListener('resize', resize);
    resize();

    function drawRings(t) {{
      ctx.clearRect(0, 0, w, h);
      const cx = w / 2, cy = h / 2;
      for (let i = 0; i < 26; i++) {{
        const r = 80 + i * 8 + Math.sin(t * 0.002 + i) * 2;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255,160,60,${{0.004 + 0.001 * i}})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }}
      requestAnimationFrame(drawRings);
    }}
    requestAnimationFrame(drawRings);

    // WebAudio hum simulation
    let audioCtx, osc1, gain1;
    function startAudio() {{
      if ({play_audio}) {{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        osc1 = audioCtx.createOscillator();
        gain1 = audioCtx.createGain();
        osc1.type = 'sine';
        osc1.frequency.value = 40 + {spin_speed} * 40;
        gain1.gain.value = 0.25 * {output_strength};
        osc1.connect(gain1).connect(audioCtx.destination);
        osc1.start();
      }}
    }}
    function stopAudio() {{
      if ({pause_audio}) {{
        try {{ osc1.stop(); audioCtx.close(); }} catch(e) {{}}
      }}
    }}
    startAudio();
    stopAudio();
  </script>
</body>
</html>
""".format(
    visual_size=visual_size,
    spin_time=5 / max(spin_speed, 0.01),
    pulse_time=3 / (output_strength + 0.2),
    crystal_src=crystal_src,
    play_audio=str(play_audio).lower(),
    pause_audio=str(pause_audio).lower(),
    spin_speed=spin_speed,
    output_strength=output_strength
)

# Render to Streamlit
st.components.v1.html(html_code, height=700, scrolling=False)

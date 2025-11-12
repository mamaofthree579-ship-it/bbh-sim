import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math, time, io, wave

st.set_page_config(page_title="🌀 Quantum Black Hole Simulator", layout="wide")

st.title("🌀 Quantum Black Hole — Real-Time Singularity Simulation")

st.markdown(
"""
### Description
This live visualization simulates a **quantum-fractal singularity** with an orbiting hotspot
and dynamic accretion disk.  
It represents the flow of gravity and energy near the event horizon — showing your theory’s
concept of a crystalline, quantum-graviton core.
"""
)

# --- Controls
st.sidebar.header("Simulation Controls")
speed = st.sidebar.slider("Rotation Speed", 0.02, 0.25, 0.08)
rings = st.sidebar.slider("Accretion Disk Rings", 6, 50, 24)
trail = st.sidebar.slider("Hotspot Trail Length", 2, 10, 5)
blur = st.sidebar.slider("Visual Blur", 0.0, 2.0, 0.6)
size = st.sidebar.slider("Canvas Size (px)", 400, 1000, 700, step=50)
show_sound = st.sidebar.checkbox("Enable Ambient Sound")

run_sim = st.button("▶ Start Live Simulation")

# --- Core rendering
def draw_frame(angle, trail_points):
    w, h = size, size
    cx, cy = w//2, h//2
    horizon_r = int(size*0.08)
    disk_r = int(size*0.45)
    img = Image.new("RGBA", (w, h), (0,0,0,255))
    d = ImageDraw.Draw(img, "RGBA")

    # soft purple plasma glow
    for i in range(6):
        alpha = max(0, 100 - i*12)
        d.ellipse(
            (cx-disk_r*(1+i/12), cy-disk_r*(1+i/12), cx+disk_r*(1+i/12), cy+disk_r*(1+i/12)),
            outline=(90, 0, 160, alpha)
        )

    # accretion disk rings
    for i in range(rings):
        r = horizon_r + i*((disk_r - horizon_r)/rings)
        alpha = int(70 + 150*(1 - i/rings))
        color = (255, 160 + i%40, 60, alpha)
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=color)

    # event horizon (black-purple)
    d.ellipse(
        (cx-horizon_r, cy-horizon_r, cx+horizon_r, cy+horizon_r),
        fill=(30, 0, 40, 255)
    )

    # hotspot + trail
    orbit_r = horizon_r * 2.8
    hx = cx + math.cos(angle)*orbit_r
    hy = cy + math.sin(angle)*orbit_r*0.4
    trail_points.insert(0, (hx, hy))
    while len(trail_points) > trail:
        trail_points.pop()

    for i, (tx, ty) in enumerate(trail_points):
        fade = (1 - i/trail)
        a = int(200 * fade)
        r = 6 * fade + 1
        d.ellipse((tx-r, ty-r, tx+r, ty+r), fill=(255, 180, 80, a))

    return img.filter(ImageFilter.GaussianBlur(blur))

# --- Sound synthesis (optional)
def synth_audio(duration=3.0, sr=44100):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    base = 25 + 10*np.sin(2*np.pi*0.1*t)
    vortex = np.sin(2*np.pi*base*t)
    noise = np.random.normal(0, 0.4, len(t))
    out = 0.6*vortex + 0.8*np.convolve(noise, [0.1,0.2,0.3,0.2,0.1], "same")
    out /= np.max(np.abs(out))
    pcm = np.int16(out * 32767)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    bio.seek(0)
    return bio

# --- Display and run
if run_sim:
    st.write("Running real-time simulation... Stop it anytime by reloading.")
    frame_spot = st.empty()
    trail_points = []
    start = time.time()

    if show_sound:
        st.audio(synth_audio(), format="audio/wav")

    # Real-time loop
    while True:
        angle = (time.time() - start) * speed * 20
        img = draw_frame(angle, trail_points)
        frame_spot.image(img, use_column_width=True)
        time.sleep(0.05)
else:
    st.info("Adjust settings and press **▶ Start Live Simulation** to begin.")

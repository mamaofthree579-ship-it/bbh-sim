import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io, math, wave

st.set_page_config(page_title="Black Hole Animation", layout="wide")

st.title("🌀 Black Hole Animated Preview")

# --- Controls
frames = st.slider("Frames", 12, 60, 30)
duration_s = st.slider("Animation Duration (s)", 1, 6, 2)
speed = st.slider("Rotation Speed", 0.05, 0.3, 0.1)
rings = st.slider("Accretion Disk Rings", 6, 50, 24)
trail = st.slider("Hotspot Trail Length", 0, 20, 6)
size = st.slider("Canvas Size (px)", 400, 1000, 700, step=50)

# --- Draw frame
def draw_frame(angle, trail_points):
    w, h = size, size
    cx, cy = w//2, h//2
    horizon_r = int(size*0.08)
    disk_r = int(size*0.45)
    img = Image.new("RGBA", (w, h), (0,0,0,255))
    d = ImageDraw.Draw(img, "RGBA")

    # subtle background glow
    for i in range(8):
        alpha = max(0, 100 - i*12)
        d.ellipse((cx-disk_r*(1+i/10), cy-disk_r*(1+i/10),
                   cx+disk_r*(1+i/10), cy+disk_r*(1+i/10)),
                  outline=(40,0,80,alpha))

    # accretion disk rings
    for i in range(rings):
        r = horizon_r + i*((disk_r - horizon_r)/rings)
        alpha = int(40 + 160*(1 - i/rings))
        color = (255, 160 + i%40, 40, alpha)
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=color)

    # event horizon
    d.ellipse((cx-horizon_r, cy-horizon_r, cx+horizon_r, cy+horizon_r),
              fill=(10,0,30,255))

    # hotspot + trail
    orbit_r = horizon_r*2.5
    hx = cx + math.cos(angle)*orbit_r
    hy = cy + math.sin(angle)*orbit_r*0.4
    trail_points.insert(0,(hx,hy))
    if len(trail_points)>trail:
        trail_points.pop()
    for i,(tx,ty) in enumerate(trail_points):
        a = 255 - int((i/trail)*230)
        r = 6 - i*0.5
        d.ellipse((tx-r,ty-r,tx+r,ty+r), fill=(255,200,100,a))

    img = img.filter(ImageFilter.GaussianBlur(0.8))
    return img

# --- Make GIF
def make_gif():
    frames_list=[]
    trail_points=[]
    for i in range(frames):
        ang = i*2*math.pi/frames*speed*10
        img = draw_frame(ang, trail_points)
        frames_list.append(img.convert("P",palette=Image.ADAPTIVE))
    bio=io.BytesIO()
    frames_list[0].save(bio, format="GIF", save_all=True,
                        append_images=frames_list[1:],
                        duration=int(duration_s*1000/frames),
                        loop=0)
    bio.seek(0)
    return bio

if st.button("🎞 Generate GIF"):
    gif_bytes=make_gif()
    st.image(gif_bytes, caption="Rotating Hotspot", use_column_width=True)
else:
    st.info("Adjust parameters and click **Generate GIF** to preview motion.")

# --- Optional sound (simple vortex + storm)
def synth_audio(duration=3.0, sr=44100):
    t=np.linspace(0,duration,int(sr*duration),endpoint=False)
    base=20+10*np.sin(2*np.pi*0.1*t)
    vortex=np.sin(2*np.pi*base*t)
    noise=np.random.normal(0,0.3,len(t))
    out=0.6*vortex+0.8*np.convolve(noise,[0.1,0.2,0.3,0.2,0.1],"same")
    out/=np.max(np.abs(out))
    pcm=np.int16(out*32767)
    bio=io.BytesIO()
    with wave.open(bio,"wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    bio.seek(0)
    return bio

if st.button("🎧 Generate Ambient Audio"):
    st.audio(synth_audio(), format="audio/wav")

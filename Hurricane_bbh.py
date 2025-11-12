import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math, time, io, wave, random

st.set_page_config(page_title="🔬 Quantum Black Hole — Flux + Heatmap", layout="wide")
st.title("🔬 Quantum Black Hole — Flux Map & Energy Heatmap")

st.markdown("""
**New:** energy-density heatmap overlay (toggleable).  
This overlay colors the region around the horizon by a phenomenological energy density that depends on radius and local flux curvature.
""")

# Sidebar controls
st.sidebar.header("Simulation Controls")
speed = st.sidebar.slider("Rotation Speed", 0.01, 0.35, 0.09)
rings = st.sidebar.slider("Accretion Disk Rings", 6, 60, 26)
trail_len = st.sidebar.slider("Hotspot Trail Length", 2, 12, 6)
blur = st.sidebar.slider("Visual Blur", 0.0, 2.0, 0.7)
canvas_size = st.sidebar.slider("Canvas Size (px)", 400, 1200, 760, step=20)
crystal_detail = st.sidebar.slider("Crystal Complexity", 4, 26, 12)
flux_lines = st.sidebar.slider("Flux Line Density", 8, 80, 30)
flux_strength = st.sidebar.slider("Flux Flow Strength", 0.4, 3.2, 1.25)
show_sound = st.sidebar.checkbox("Enable Ambient Sound", value=False)
show_heatmap = st.sidebar.checkbox("Show Energy Heatmap", value=True)
heatmap_intensity = st.sidebar.slider("Heatmap Intensity", 0.1, 6.0, 1.6)
heatmap_falloff = st.sidebar.slider("Heatmap Falloff (steepness)", 0.2, 4.0, 1.0)

run_sim = st.button("▶ Start Live Simulation")

# -------------------------
# Utilities & Generators
# -------------------------
def hex_color_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def synth_audio(duration=4.0, sr=44100):
    # simple "whirlpool + hurricane" texture
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    base = 18 + 8 * np.sin(2*np.pi*0.08*t)           # low swirling core
    vortex = np.sin(2*np.pi*(base) * t)              # sweep
    breath = 0.3 * np.sin(2*np.pi*0.5 * t)           # wind-like
    noise = np.random.normal(0, 0.35, len(t))
    out = 0.55 * vortex + 0.9 * np.convolve(noise, [0.05,0.2,0.4,0.2,0.05], "same") + breath
    if np.max(np.abs(out)) > 0:
        out = out / np.max(np.abs(out))
    pcm = np.int16(out * 32767)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    bio.seek(0)
    return bio

def generate_crystal_pattern(size, detail, angle):
    w = h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = w//2, h//2
    for i in range(detail):
        r = int((i/detail) * (size * 0.06))
        spokes = int(6 + i*2)
        for j in range(spokes):
            theta = 2*math.pi*j/spokes + angle/6
            x = cx + math.cos(theta) * r
            y = cy + math.sin(theta) * r
            alpha = int(90 + 130*(i/detail))
            col = (90 + i*8, 40 + i*3, 180 + i*2, alpha)
            d.ellipse((x-2,y-2,x+2,y+2), fill=col)
    return img.filter(ImageFilter.GaussianBlur(0.6))

def generate_flux_overlay(size, n_lines, strength, angle, colorize=True):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = size//2, size//2
    for _ in range(n_lines):
        theta0 = random.uniform(0, 2*math.pi)
        r0 = random.uniform(size*0.15, size*0.45)
        pts = []
        for i in range(36):
            t = theta0 + i*0.18 + angle/8
            r = r0 * (1 - i/36)
            x = cx + r * math.cos(t*strength)
            y = cy + r * math.sin(t*strength*0.8)
            pts.append((x,y))
        # color varies with theta0 for richness
        base_r = int(120 + 80 * math.sin(theta0*2.3))
        base_g = int(90 + 70 * math.cos(theta0*1.9))
        col = (base_r, base_g, 255, 72) if colorize else (255,255,255,72)
        d.line(pts, fill=col, width=1)
    return img.filter(ImageFilter.GaussianBlur(0.6))

def compute_energy_field(size, intensity=1.0, falloff=1.0):
    """Phenomenological energy density field: stronger near the horizon and along curvature."""
    cx, cy = size//2, size//2
    xv = np.linspace(-1,1,size)
    yv = np.linspace(-1,1,size)
    X, Y = np.meshgrid(xv, yv)
    R = np.sqrt(X**2 + (Y*0.8)**2)  # elliptical scaling
    # base profile: power-law + exponential
    field = (1.0 / (R + 0.02)**(1.5*falloff)) * np.exp(-R*3.5*falloff)
    # add azimuthal modulation (simulate flux bending)
    theta = np.arctan2(Y, X)
    spiral = 0.3 * np.sin(6*theta + 2.6*R*5)
    field = (field + spiral) * intensity
    # normalize 0..1
    field -= field.min()
    if field.max() > 0:
        field = field / field.max()
    return field

def heatmap_to_image(field, cmap="plasma", alpha=0.6):
    # simple colormap: plasma-like custom
    import colorsys
    size = field.shape[0]
    img = Image.new("RGBA", (size,size), (0,0,0,0))
    pix = img.load()
    for i in range(size):
        for j in range(size):
            v = float(field[j,i])
            # map 0..1 to hue 0.7 (purple) -> 0.0 (yellow)
            h = 0.7 - 0.7*v
            r,g,b = [int(255*c) for c in colorsys.hsv_to_rgb(h, 0.9, 0.95*v + 0.05)]
            a = int(255 * (alpha * v))
            pix[i,j] = (r,g,b,a)
    return img.filter(ImageFilter.GaussianBlur(2.0))

# -------------------------
# Frame drawing
# -------------------------
def draw_frame(size, angle, trail_points, params):
    # params: rings, horizon fraction, flux overlay, heatmap image or None, etc.
    w = h = size
    cx, cy = w//2, h//2
    horizon_r = int(size * 0.08)
    disk_r = int(size * 0.45)

    img = Image.new("RGBA", (w,h), (6,6,10,255))
    d = ImageDraw.Draw(img, "RGBA")

    # soft vignette/background rings
    for i in range(5):
        rr = disk_r * (1 + i*0.04)
        alpha = int(18 - i*2)
        if alpha > 0:
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), outline=(40,6,70,alpha))

    # accretion disk rings
    for i in range(rings):
        r = horizon_r + i * ((disk_r - horizon_r) / max(1, rings))
        alpha = int(30 + 160 * (1 - i / max(1, rings)))
        color = (255, 150 + (i%80), 70, alpha)
        d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=color)

    # paste crystal core
    crystal = generate_crystal_pattern(size, crystal_detail, angle)
    img.paste(crystal, (0,0), crystal)

    # flux lines on top of core
    flux = generate_flux_overlay(size, flux_lines, flux_strength, angle, colorize=True)
    img.paste(flux, (0,0), flux)

    # optional heatmap overlay
    if show_heatmap:
        field = compute_energy_field(size, intensity=heatmap_intensity, falloff=heatmap_falloff)
        heat_img = heatmap_to_image(field, alpha=0.9)
        img.paste(heat_img, (0,0), heat_img)

    # horizon (dark translucent)
    d.ellipse((cx-horizon_r, cy-horizon_r, cx+horizon_r, cy+horizon_r), fill=(20,8,40,200))

    # hotspot + trail
    orbit_r = horizon_r * 2.8
    hx = cx + math.cos(angle) * orbit_r
    hy = cy + math.sin(angle) * orbit_r * 0.44
    trail_points.insert(0, (hx, hy))
    while len(trail_points) > trail_len:
        trail_points.pop()
    for idx, (tx,ty) in enumerate(trail_points):
        fade = 1 - idx / max(1, trail_len)
        a = int(220 * fade)
        r = 5 * (0.6 + fade)
        d.ellipse((tx-r, ty-r, tx+r, ty+r), fill=(255,220,170,a))

    # subtle outer glow
    glow = Image.new("RGBA", (w,h), (0,0,0,0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse((cx- (horizon_r*3), cy-(horizon_r*3), cx+(horizon_r*3), cy+(horizon_r*3)), outline=(170,80,255,18), width=6)
    img = Image.alpha_composite(img, glow)

    # final blur for visual coherence
    return img.filter(ImageFilter.GaussianBlur(blur))

# -------------------------
# Run / Display loop
# -------------------------
if run_sim:
    st.info("Running simulation — press browser stop/refresh to halt.")
    frame_area = st.empty()
    trail_points = []
    start = time.time()

    if show_sound:
        # one-shot audio playback (not looped)
        st.audio(synth_audio(), format="audio/wav")

    # precompute energy field once (used only if user changes heatmap params; acceptable)
    last_params_hash = None

    try:
        while True:
            angle = (time.time() - start) * speed * 18.0
            img = draw_frame(canvas_size, angle, trail_points, params=None)
            frame_area.image(img, use_column_width=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
else:
    st.info("Adjust controls on the left and press ▶ **Start Live Simulation** to run.")

st.markdown("""
**Notes**
- Heatmap is phenomenological: it blends a radius-dependent profile with azimuthal modulation to emulate curvature-driven energy flow.
- Toggle the heatmap off if you prefer just flux lines + crystal core.
""")

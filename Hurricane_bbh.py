import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image

st.set_page_config(page_title="Black Hole Hurricane Simulator", layout="wide")

# ----------------------------------------
# SIDEBAR CONTROLS
# ----------------------------------------
st.sidebar.title("Black Hole Controls")

mass = st.sidebar.slider("Mass scale", 1.0, 10.0, 4.0, 0.1)
spin = st.sidebar.slider("Spin (a*)", 0.0, 0.99, 0.7, 0.01)
trail_len = st.sidebar.slider("Hotspot Trail Length", 3, 50, 25)
brightness = st.sidebar.slider("Disk Brightness", 0.2, 3.0, 1.4, 0.1)
turbulence_strength = st.sidebar.slider("Disk Turbulence Strength", 0.0, 0.5, 0.12)
frames = st.sidebar.slider("Animation Frames", 50, 500, 150)

if "frame" not in st.session_state:
    st.session_state.frame = 0

run = st.sidebar.button("► Play Animation")
reset = st.sidebar.button("⟲ Reset")

if reset:
    st.session_state.frame = 0


# ----------------------------------------
# PHYSICS FUNCTIONS
# ----------------------------------------

def accretion_temperature(r):
    """Thin-disk temperature profile (relativistic falloff)."""
    return brightness * (r**(-0.75)) * np.exp(-r / (8 + 4 * spin))


def hotspot_position(t, radius):
    """Hotspot orbital motion."""
    omega = np.sqrt(1 / (radius**3 + 0.2 * mass))
    x = radius * np.cos(omega * t)
    y = radius * np.sin(omega * t)
    return x, y, omega


def doppler_factor(vx):
    """Relativistic Doppler beaming based on x-velocity."""
    beta = vx
    gamma = 1 / np.sqrt(1 - beta**2 + 1e-9)
    return gamma * (1 + beta)


def frame_dragging(x, y):
    """Simple Kerr frame dragging twist."""
    r = np.sqrt(x**2 + y**2)
    twist = spin * 0.15 / (1 + r**2)
    xp = x * np.cos(twist) - y * np.sin(twist)
    yp = x * np.sin(twist) + y * np.cos(twist)
    return xp, yp


def turbulent_wobble():
    """Disk turbulence noise field."""
    return 1 + turbulence_strength * (np.random.rand() - 0.5)


def spiral_inflow(r, theta):
    """Inward spiral motion of disk matter."""
    r2 = r - 0.005 * (r - 2.8)  # slow inward drift
    theta2 = theta + 0.04 / r   # slight azimuth shift
    return r2, theta2


# ----------------------------------------
# RENDER FRAME
# ----------------------------------------
def render_frame(frame_index):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor("black")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_xticks([])
    ax.set_yticks([])

    # ---------- Black hole shadow ----------
    ax.add_artist(plt.Circle((0, 0), 2.6, color="black"))

    # ---------- Hawking glow ----------
    glow_r = np.linspace(2.6, 3.8, 200)
    glow_theta = np.linspace(0, 2*np.pi, 200)
    GR, GTH = np.meshgrid(glow_r, glow_theta)
    gx = GR * np.cos(GTH)
    gy = GR * np.sin(GTH)
    hawk_intensity = np.exp(-(GR - 2.6) * 1.8)
    ax.scatter(gx, gy, color=(0.52, 0.7, 1, 0.22), s=hawk_intensity * 2)

    # ---------- Accretion disk ----------
    r = np.linspace(2.8, 10, 450)
    theta = np.linspace(0, 2*np.pi, 450)
    R, TH = np.meshgrid(r, theta)

    # Spiral inflow
    R2, TH2 = spiral_inflow(R, TH)

    disk_x = R2 * np.cos(TH2)
    disk_y = R2 * np.sin(TH2)

    # Frame dragging warp
    disk_x, disk_y = frame_dragging(disk_x, disk_y)

    temp = accretion_temperature(R2) * turbulent_wobble()
    ax.scatter(disk_x, disk_y, c=temp, cmap="inferno", s=0.35, alpha=0.6)

    # ---------- Hotspot ----------
    hotspot_r = 4.1 + 0.3 * spin
    hot_x, hot_y, omega = hotspot_position(frame_index, hotspot_r)

    # Doppler effect based on x-velocity derivative
    vx = -hotspot_r * omega * np.sin(omega * frame_index)
    dop = doppler_factor(vx) ** 1.5

    # ---------- Hotspot trail ----------
    for k in range(trail_len):
        t = frame_index - k * 0.8
        tx, ty, om = hotspot_position(t, hotspot_r)
        fade = max(0, 1 - k / trail_len)
        ax.scatter(tx, ty, color=(1, 0.7, 0.4, 0.7 * fade), s=20)

    # ---------- Hotspot core ----------
    ax.scatter(hot_x, hot_y,
               color=(1, 1, 1, min(1, 0.4 * dop)),
               edgecolor="yellow",
               s=80)

    # ---------- Save to buffer ----------
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)


# ----------------------------------------
# MAIN RENDER
# ----------------------------------------
placeholder = st.empty()

if run:
    st.session_state.frame = (st.session_state.frame + 1) % frames

image = render_frame(st.session_state.frame)
placeholder.image(image, use_column_width=True)
        

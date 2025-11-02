import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Constants ---
G = 6.67430e-11          # gravitational constant (m^3 kg^-1 s^-2)
c = 2.99792458e8         # speed of light (m/s)
M_sun = 1.98847e30       # solar mass (kg)
AU = 1.496e11            # astronomical unit (m)

st.set_page_config(page_title="Black Hole Anatomy — Step 1", layout="wide")

st.title("🌀 Black Hole Anatomy — Step 1: Event Horizon & Photon Sphere")
st.markdown("""
This module displays the **event horizon** and **photon sphere** of a Schwarzschild (non-rotating) black hole.  
Use the slider to change the black-hole mass and observe how the physical radii scale.  
The visual scale is normalized for consistent appearance.
""")

# --- Mass selection ---
mass_solar = st.slider("Black-hole mass (solar masses)", 1, 10000000, 4300000, step=10000)
mass = mass_solar * M_sun

# --- Physical calculations ---
r_s = 2 * G * mass / c**2           # Schwarzschild radius
r_ph = 1.5 * r_s                    # photon sphere radius

# Normalized visual radii
scale = 1.0
r_s_vis = 1.0 * scale
r_ph_vis = (r_ph / r_s) * scale

# --- 3D sphere mesh function ---
def make_sphere(radius, color, opacity, name):
    u = np.linspace(0, 2*np.pi, 80)
    v = np.linspace(0, np.pi, 40)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    return go.Surface(
        x=x, y=y, z=z,
        surfacecolor=np.ones_like(x),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=opacity,
        name=name,
        hoverinfo="skip"
    )

# --- Create surfaces ---
horizon = make_sphere(r_s_vis, "#7d2ae8", 1.0, "Event Horizon")  # rich purple
photon = make_sphere(r_ph_vis, "gold", 0.25, "Photon Sphere")

# --- Build figure ---
fig = go.Figure(data=[photon, horizon])
fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False, visible=False),
        yaxis=dict(showbackground=False, showticklabels=False, visible=False),
        zaxis=dict(showbackground=False, showticklabels=False, visible=False),
        aspectmode="data",
        camera=dict(eye=dict(x=1.6, y=1.6, z=0.8))
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0),
)

# --- Display plot ---
st.plotly_chart(fig, use_container_width=True)

# --- Text summary ---
st.markdown(f"""
### 📏 Physical Radii

**Mass:** {mass_solar:,.0f} M☉  
**Schwarzschild radius (rₛ):**  
• {r_s:.6e} m  
• {r_s/1000:.6e} km  
• {r_s/AU:.6e} AU  

**Photon sphere (≈ 1.5 rₛ):**  
• {r_ph:.6e} m  
• {r_ph/1000:.6e} km  
• {r_ph/AU:.6e} AU  

---

**Notes:**  
- The purple surface marks the **event horizon**.  
- The translucent golden shell marks the **photon sphere** where light can orbit.  
- Visual size is normalized so both remain visible across different masses.
""")

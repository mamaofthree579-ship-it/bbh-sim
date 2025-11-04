# graviton_singularity_app.py
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time as tm

st.set_page_config(page_title="Graviton Well–Singularity Simulator", layout="wide")

# ─────────────────────────────────────────────────────────────
# 1. Constants
# ─────────────────────────────────────────────────────────────
G  = 6.67430e-11
c  = 3.0e8
ħ  = 1.0545718e-34
π  = np.pi

# ─────────────────────────────────────────────────────────────
# 2. UI controls
# ─────────────────────────────────────────────────────────────
st.title("🌀 Graviton Input/Output Well Simulation")
st.write("Visualize transitions between compressive (black-hole) and expansive (white-hole) phases.")

col1, col2 = st.columns(2)
with col1:
    # log-scale sliders so you can explore wide numeric ranges
    M0_exp = st.slider("log₁₀(Initial Mass [kg])", 2.0, 10.0, 5.0, 0.1)
    rQ_exp = st.slider("log₁₀(Quantum Radius [m])", -40.0, -20.0, -35.0, 0.5)
    M0 = 10 ** M0_exp
    r_Q = 10 ** rQ_exp

    λ = st.slider("Singularity Coupling Constant λ", 0.001, 2.0, 0.1, 0.001)
    N_r = st.slider("Spatial Resolution (steps)", 200, 1500, 500, 50)

with col2:
    Δt = float(st.text_input("Time Step (s)", "1e-3"))
    T_max = float(st.text_input("Total Simulation Time (s)", "10.0"))
    show_3D = st.checkbox("Show 3-D Graviton-Well Surface", True)
    show_anim = st.checkbox("Show Quantum-Tunnelling Animation", True)

# ─────────────────────────────────────────────────────────────
# 3. Helper equations
# ─────────────────────────────────────────────────────────────
def F_QG(r, m, r_Q): return (G * m / r**2) * np.exp(-r / r_Q)
def dM_dt(M):        return - (ħ * c**2 / G) * (1 / M**2)
def S_trans(rho_QG, R_curv, λ):
    integral_rho = np.trapz(rho_QG)
    dR_dt = np.gradient(R_curv).mean()
    return integral_rho - λ * dR_dt

# ─────────────────────────────────────────────────────────────
# 4. Initialize arrays
# ─────────────────────────────────────────────────────────────
r_min, r_max = 1e-6, 1.0
r = np.linspace(r_min, r_max, N_r)
rho_QG = (M0 / r_max**3) * np.exp(-r / r_Q)
R_curv = (2 * G * M0) / (r**3 * c**2)

M = M0
time_points, S_values, M_values = [], [], []

# ─────────────────────────────────────────────────────────────
# 5. Simulation loop
# ─────────────────────────────────────────────────────────────
time = 0
while time < T_max and M > 0:
    F = F_QG(r, M, r_Q)
    rho_QG += (F / c**2) * Δt
    M += dM_dt(M) * Δt
    R_curv = (2 * G * M) / (r**3 * c**2)
    S = S_trans(rho_QG, R_curv, λ)

    time_points.append(time)
    S_values.append(S)
    M_values.append(M)

    if S < 0:
        st.warning(f"Transition triggered at t = {time:.3f}s → Output-well phase")
        break
    time += Δt

# ─────────────────────────────────────────────────────────────
# 6. 2-D Plots
# ─────────────────────────────────────────────────────────────
fig1, ax1 = plt.subplots()
ax1.plot(time_points, S_values)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Singularity Transition S(t)")
ax1.set_title("Transition Function Evolution")

fig2, ax2 = plt.subplots()
ax2.plot(r, rho_QG)
ax2.set_xlabel("Radius (m)")
ax2.set_ylabel("Quantum Density ρ_QG")
ax2.set_title("Final Density Distribution")

fig3, ax3 = plt.subplots()
ax3.plot(time_points, M_values)
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("Mass (kg)")
ax3.set_title("Mass Evolution")

st.pyplot(fig1)
st.pyplot(fig2)
st.pyplot(fig3)

# ─────────────────────────────────────────────────────────────
# 7. Optional 3-D potential surface
# ─────────────────────────────────────────────────────────────
if show_3D:
    R, θ = np.meshgrid(np.linspace(0, 1, 100), np.linspace(0, 2*π, 200))
    Z = -np.exp(-R / r_Q) * (M / M0)  # simple potential depth
    X, Y = R*np.cos(θ), R*np.sin(θ)
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_title("Graviton-Well Surface")
    st.pyplot(fig)

# ─────────────────────────────────────────────────────────────
# 8. Improved tunnelling animation (smooth + dual wells)
# ─────────────────────────────────────────────────────────────
if show_anim:
    st.subheader("Quantum-Tunnelling Pulse Across Dual Wells")

    # Create placeholder for animation
    anim_placeholder = st.empty()

    # Define x-space and potential
    x = np.linspace(-2, 2, 600)
    potential = -np.exp(-np.abs(x + 0.8) / 0.3) - np.exp(-np.abs(x - 0.8) / 0.3)
    # central singularity line (x=0)
    singularity_x = 0

    # Create initial figure
    fig_anim, ax_anim = plt.subplots(figsize=(6, 3))
    ax_anim.set_xlim(-2, 2)
    ax_anim.set_ylim(-1.5, 0.2)
    line_pot, = ax_anim.plot(x, potential, 'k-', lw=1)
    ax_anim.axvline(singularity_x, color='red', linestyle='--', lw=1, label="Singularity")
    pulse, = ax_anim.plot([], [], 'ro', markersize=8)
    ax_anim.legend(loc='upper right')
    ax_anim.set_xlabel("Position (arbitrary units)")
    ax_anim.set_ylabel("Potential / Energy")
    ax_anim.set_title("Quantum Tunnelling Through Connected Wells")

    # Animate the pulse
    for frame in range(100):
        x_pulse = -1.6 + 0.032 * frame
        y_pulse = -np.exp(-abs(x_pulse + 0.8) / 0.3) - np.exp(-abs(x_pulse - 0.8) / 0.3)
        pulse.set_data([x_pulse], [y_pulse])

        # Clear and re-draw each frame in same placeholder
        anim_placeholder.pyplot(fig_anim)
        tm.sleep(0.04)

        # Once the pulse has crossed to the right side and S < 0 → transition complete
        if S < 0 and x_pulse > 0.8:
            break

    st.success("Pulse successfully traversed from input to output well (singularity transition).")

# ─────────────────────────────────────────────────────────────
# 8b. Optional 3-D dual-well visualization (interactive view)
# ─────────────────────────────────────────────────────────────
show_3D_dual = st.checkbox("Show 3-D Dual-Well Structure", False)

if show_3D_dual:
    st.subheader("3D Dual Graviton Wells – Singularity Bridge")

    from mpl_toolkits.mplot3d import Axes3D  # ensure available
    fig3d = plt.figure(figsize=(8, 6))
    ax3d = fig3d.add_subplot(111, projection="3d")

    # Coordinates for two funnel-shaped wells connected at the center
    r = np.linspace(0.1, 1.0, 100)
    theta = np.linspace(0, 2 * np.pi, 200)
    R, Θ = np.meshgrid(r, theta)

    # Define two potential wells offset along z-axis (input/output)
    z_input = -np.exp(-R) - 1.0
    z_output = np.exp(-R) + 1.0  # mirrored
    X = R * np.cos(Θ)
    Y = R * np.sin(Θ)

    # Plot both wells
    ax3d.plot_surface(X, Y, z_input, alpha=0.8, linewidth=0, antialiased=False, cmap='viridis')
    ax3d.plot_surface(X, Y, z_output, alpha=0.8, linewidth=0, antialiased=False, cmap='plasma')

    # Singularity bridge (center tube)
    z_bridge = np.linspace(-0.2, 0.2, 30)
    θ_bridge = np.linspace(0, 2 * np.pi, 40)
    Θb, Zb = np.meshgrid(θ_bridge, z_bridge)
    Rb = np.full_like(Θb, 0.1)
    Xb = Rb * np.cos(Θb)
    Yb = Rb * np.sin(Θb)
    ax3d.plot_surface(Xb, Yb, Zb, color="red", alpha=0.6)

    # Styling
    ax3d.set_title("3D Representation of Input/Output Wells Connected by Singularity")
    ax3d.set_xlabel("X-axis (spatial)")
    ax3d.set_ylabel("Y-axis (spatial)")
    ax3d.set_zlabel("Energy potential")
    ax3d.view_init(elev=25, azim=45)

    st.pyplot(fig3d)

    st.markdown("""
    **Interpretation**  
    - Left funnel → *graviton input well* (black-hole analogue).  
    - Right funnel → *graviton output well* (white-hole analogue).  
    - Red tube → *singularity bridge*, allowing bidirectional energy–information tunneling.
    """)

# ─────────────────────────────────────────────────────────────
# 8c. 3D animation of quantum pulse through the singularity bridge
# ─────────────────────────────────────────────────────────────
animate_3D_pulse = st.checkbox("Animate 3D Quantum Pulse Through Bridge", False)

if animate_3D_pulse:
    st.subheader("3D Animation: Quantum Pulse Traversing the Singularity Bridge")

    anim_placeholder_3D = st.empty()
    frames = 80

    # Set up coordinate grids (same as before)
    r = np.linspace(0.1, 1.0, 100)
    theta = np.linspace(0, 2 * np.pi, 200)
    R, Θ = np.meshgrid(r, theta)

    # Define wells and bridge
    z_input = -np.exp(-R) - 1.0
    z_output = np.exp(-R) + 1.0
    X = R * np.cos(Θ)
    Y = R * np.sin(Θ)

    z_bridge = np.linspace(-0.2, 0.2, 30)
    θ_bridge = np.linspace(0, 2 * np.pi, 40)
    Θb, Zb = np.meshgrid(θ_bridge, z_bridge)
    Rb = np.full_like(Θb, 0.1)
    Xb = Rb * np.cos(Θb)
    Yb = Rb * np.sin(Θb)

    # Animate frame by frame
    for i in range(frames):
        fig3d = plt.figure(figsize=(8, 6))
        ax3d = fig3d.add_subplot(111, projection="3d")

        # Plot wells and bridge
        ax3d.plot_surface(X, Y, z_input, alpha=0.7, linewidth=0, cmap="viridis")
        ax3d.plot_surface(X, Y, z_output, alpha=0.7, linewidth=0, cmap="plasma")
        ax3d.plot_surface(Xb, Yb, Zb, color="red", alpha=0.5)

        # Pulse motion (through bridge)
        t = i / frames
        z_pulse = -1.0 + 2.0 * t  # moves from bottom to top
        x_pulse, y_pulse = 0.0, 0.0  # centered at singularity axis

        ax3d.scatter(x_pulse, y_pulse, z_pulse, color="cyan", s=60, label="Quantum Pulse")

        ax3d.set_title(f"Quantum Pulse Traversing Singularity (Frame {i+1}/{frames})")
        ax3d.set_xlabel("X-axis")
        ax3d.set_ylabel("Y-axis")
        ax3d.set_zlabel("Energy Potential")
        ax3d.set_xlim(-1, 1)
        ax3d.set_ylim(-1, 1)
        ax3d.set_zlim(-1.5, 1.5)
        ax3d.view_init(elev=25, azim=45)
        ax3d.legend(loc="upper right")

        anim_placeholder_3D.pyplot(fig3d)
        tm.sleep(0.05)

    st.success("Quantum pulse successfully traversed from input well through the singularity to the output well.")

# ─────────────────────────────────────────────────────────────
# 9. Summary
# ─────────────────────────────────────────────────────────────
st.subheader("Simulation Summary")
st.write(f"**Initial Mass:** {M0:.3e} kg")
st.write(f"**Final Mass:** {M:.3e} kg")
st.write(f"**Final Singularity State S:** {S:.3e}")
st.write("**Interpretation:**")
if S > 0:
    st.info("System remains in compressive (input-well) phase.")
else:
    st.success("System reached expansion (output-well / white-hole) phase.")

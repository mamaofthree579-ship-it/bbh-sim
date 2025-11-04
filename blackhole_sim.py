import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# --------------------------------------
# 1. Constants
# --------------------------------------
G = 6.67430e-11     # gravitational constant
c = 3.0e8            # speed of light
ħ = 1.0545718e-34    # reduced Planck constant
π = np.pi

# --------------------------------------
# 2. Streamlit UI
# --------------------------------------
st.title("🌀 Graviton Well–Singularity Dynamics Simulator")
st.write("Explore transitions between gravitational input (black hole) and output (white hole) wells.")

# Simulation controls
M0 = st.sidebar.number_input("Initial Mass (kg)", 1e3, 1e8, 1e5, format="%.2e")
r_Q = st.sidebar.number_input("Quantum Radius (m)", 1e-40, 1e-20, 1e-35, format="%.2e")
λ = st.sidebar.slider("Singularity Coupling Constant (λ)", 0.01, 2.0, 0.1, 0.01)
Δt = st.sidebar.number_input("Time Step (s)", 1e-5, 1.0, 1e-3, format="%.1e")
T_max = st.sidebar.number_input("Total Simulation Time (s)", 1.0, 1000.0, 10.0)
N_r = st.sidebar.slider("Spatial Resolution (steps)", 100, 2000, 500)

# --------------------------------------
# 3. Helper functions
# --------------------------------------
def F_QG(r, m, r_Q):
    return (G * m / r**2) * np.exp(-r / r_Q)

def dM_dt(M):
    return - (ħ * c**2 / G) * (1 / M**2)

def S_trans(rho_QG, R_curv, λ):
    integral_rho = np.trapz(rho_QG)
    dR_dt = np.gradient(R_curv).mean()
    return integral_rho - λ * dR_dt

# --------------------------------------
# 4. Initialize arrays
# --------------------------------------
r_min, r_max = 1e-6, 1.0
r = np.linspace(r_min, r_max, N_r)
rho_QG = (M0 / r_max**3) * np.exp(-r / r_Q)
R_curv = (2 * G * M0) / (r**3 * c**2)

M = M0
time_points = []
S_values = []
M_values = []

# --------------------------------------
# 5. Simulation loop
# --------------------------------------
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
        st.warning(f"Transition triggered at t = {time:.3f}s → Output Well Phase")
        break

    time += Δt

# --------------------------------------
# 6. Visualization
# --------------------------------------
fig1, ax1 = plt.subplots()
ax1.plot(time_points, S_values)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Singularity Transition Function S(t)")
ax1.set_title("Evolution of Singularity Transition State")

fig2, ax2 = plt.subplots()
ax2.plot(r, rho_QG)
ax2.set_xlabel("Radius (m)")
ax2.set_ylabel("Quantum Gravity Density ρ_QG")
ax2.set_title("Final Density Distribution")

fig3, ax3 = plt.subplots()
ax3.plot(time_points, M_values)
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("Mass (kg)")
ax3.set_title("Mass Evolution (Quantum Evaporation)")

st.pyplot(fig1)
st.pyplot(fig2)
st.pyplot(fig3)

# --------------------------------------
# 7. Results Summary
# --------------------------------------
st.subheader("Simulation Summary")
st.write(f"**Initial Mass:** {M0:.3e} kg")
st.write(f"**Final Mass:** {M:.3e} kg")
st.write(f"**Final Singularity State (S):** {S:.3e}")
st.write("**Interpretation:**")
if S > 0:
    st.info("System remains in compressive phase (Graviton Input Well).")
else:
    st.success("System transitioned to expansion phase (Graviton Output Well / White Hole).")

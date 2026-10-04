import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import pandas as pd
import io

# ---------------------------------------------------------
# Streamlit Page & Theme Configurations
# ---------------------------------------------------------
st.set_page_config(page_title="Information-Geometric Mechanics WebApp 2.0", layout="wide")
st.title("🌌 Information-Geometric Mechanics Framework Sandbox (v2.0)")
st.markdown("""
This advanced workspace implements the full, interlocking multi-sector mathematical formulations of 
**Information-Geometric Mechanics (IGM)**. 
Use the tabs and sliders below to interact with the 4D space-division matrices, black hole horizon math, 
and subatomic spin state modulators.
""")

# ---------------------------------------------------------
# Sidebar Panel Controls
# ---------------------------------------------------------
st.sidebar.header("🛠️ Universal Framework Configuration")
sector = st.sidebar.selectbox("Select Target Framework Sector:", 
                              ["1. Galactic Disk & SPH Grid Solver", 
                               "2. Strong-Field Horizon Transformations", 
                               "3. Quantum Phase-Crystallization", 
                               "4. Global Consciousness Network Data Ingestion"])

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Fundamental Invariant Coefficients")
I_0 = st.sidebar.slider("Information Profile Scale Factor (I_0)", 0.1, 5.0, 1.0, 0.1)
kappa = st.sidebar.slider("Geometric Elasticity Constant (kappa)", 0.1, 2.0, 0.5, 0.1)
eta = st.sidebar.slider("Stress Tensor Deficit Coupling (eta)", 0.1, 2.0, 1.0, 0.1)

# Physics Core Constant Registry
G = 4.300e-6                      # kpc (km/s)^2 M_sun^-1
M_bar_core = 5.0e10               # Standard spiral core baryonic mass scale (M_sun)
hbar = 1.0545718e-34              # Reduced Planck constant (J*s)

# ---------------------------------------------------------
# Sector 1: Galactic Disk & SPH Grid Solver
# ---------------------------------------------------------
if sector == "1. Galactic Disk & SPH Grid Solver":
    st.header("🛸 4D Space-Within-Space Galactic Solver")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("LaTeX Field Formulations")
        st.latex(r"\nabla_\mu V^\mu = \sigma I(r)")
        st.latex(r"I(r) = I_0 r^{-n} \implies V_r \propto r^{1-n} \quad [n=1 \rightarrow V_r = \text{const.}]")
        st.latex(r"\chi(r) = \frac{1}{V_{4D}}\sum A_i\phi_i \propto \frac{r^3}{r^4} \propto r^{-m} \quad [m=1]")
        st.latex(r"\text{Scale Lock: } 2n + m = 2(1) + 1 = 3")
        
        st.markdown("---")
        r_max = st.slider("Max Galactic Horizon Boundary (kpc)", 10.0, 100.0, 50.0, 5.0)
        N_points = 500
        
    with col2:
        r = np.linspace(0.1, r_max, N_points)
        I_r = I_0 / r
        chi_r = (4.0 * I_0) / (3.0 * r)
        alpha_r = np.abs(-eta * kappa * chi_r) * 40.0
        
        a_bar = (G * M_bar_core) / (r**2)
        a_anomalous = alpha_r * r
        a_total = a_bar + a_anomalous
        
        v_baryonic = np.sqrt(r * a_bar)
        v_total = np.sqrt(r * a_total)
        
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
        ax[0].plot(r, v_baryonic, 'r--', label='Newtonian Pure Baryonic (Decay)')
        ax[0].plot(r, v_total, 'b-', label='Unified IGM 4D Model (Flat Plateau)')
        ax[0].set_title('Asymptotically Flat Rotation Curve')
        ax[0].set_xlabel('Galactic Radius r (kpc)')
        ax[0].set_ylabel('Circular Velocity v (km/s)')
        ax[0].grid(True, ls=":")
        ax[0].legend()
        
        ax[1].loglog(r, I_r, 'g-', label='Information Density I(r) [n=1]')
        ax[1].loglog(r, chi_r, 'm-.', label='Compression Density $\chi$(r) [m=1]')
        ax[1].set_title('Log-Log Constraint Code Validation')
        ax[1].set_xlabel('Log Radius')
        ax[1].set_ylabel('Log Scalar Magnitude')
        ax[1].grid(True, which="both", ls=":")
        ax[1].legend()
        
        st.pyplot(fig)
        
        # CSV Export Generator Engine
        df = pd.DataFrame({"Radius_kpc": r, "V_Newtonian_kms": v_baryonic, "V_IGM_kms": v_total, "Compression_Density": chi_r})
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Download Galactic Rotation Data Run (CSV)", data=csv_buffer.getvalue(), file_name="igm_galactic_run.csv", mime="text/csv")

# ---------------------------------------------------------
# Sector 2: Strong-Field Horizon Transformations
# ---------------------------------------------------------
elif sector == "2. Strong-Field Horizon Transformations":
    st.header("🕳️ Schwarzschild Metric Strong-Field Boundary Conditions")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Horizon Scaling Equations")
        st.latex(r"ds^2 = -\left(1-\frac{r_s}{r}\right)c^2dt^2 + \left(1-\frac{r_s}{r}\right)^{-1}dr^2 + r^2d\Omega^2")
        st.latex(r"\chi_{\rm relativistic}(r) = \frac{\chi_0}{r}\left(1-\frac{r_s}{r}\right)^{-1} = \frac{\chi_0}{r - r_s}")
        st.latex(r"\lim_{r \to r_s} \chi(r) = \infty \quad [\text{Total Phase-Crystallization Threshold}]")
        
        st.markdown("---")
        r_s = st.slider("Schwarzschild Radius Boundary r_s (kpc-scaled value)", 1.0, 5.0, 2.0, 0.5)
        
    with col2:
        r_horizon = np.linspace(r_s + 0.1, r_s + 20.0, 1000)
        chi_rel = (4.0 * I_0) / (3.0 * (r_horizon - r_s))
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(r_horizon, chi_rel, 'k-', linewidth=2, label=r'$\chi_{\rm relativistic}(r)$')
        ax.axvline(x=r_s, color='r', linestyle='--', label='Event Horizon Boundary ($r_s$)')
        ax.set_title("Geometric Compression Singularity Divergence")
        ax.set_xlabel("Radial Distance r")
        ax.set_ylabel("Compression Density Scalar")
        ax.set_ylim(0, np.max(chi_rel)*0.1)
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# Sector 3: Quantum Phase-Crystallization
# ---------------------------------------------------------
elif sector == "3. Quantum Phase-Crystallization":
    st.header("⚛️ Subatomic Spin State Phase Precession")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Pauli-Schrödinger Modified Hamiltonian")
        st.latex(r"H_{\rm total} = \frac{e}{2m_e}(\vec{\sigma}\cdot\vec{B}) + \xi_0(\mathcal{C}_{\mu\nu}\sigma^\mu \otimes \hat{k}^\nu)")
        st.latex(r"\Delta \theta_{\rm spin} = \frac{2 \xi_0}{\hbar} \int_0^{\tau_0} \mathcal{A}_M(t) \cdot [ \partial_x \theta_M(t) \omega(t) ] \, dt")
        
        st.markdown("---")
        xi_0 = st.slider("Psycho-Physical Spin Scaling Scalar (xi_0 * 10^-34)", 0.1, 10.0, 2.5, 0.5) * 1e-34
        chopper_f = st.slider("Attentional Chopper Resonant Frequency (Hz)", 0.05, 1.0, 0.1, 0.05)
        
    with col2:
        t = np.linspace(0, 20, 1000)
        intent_wave = np.sin(2.0 * np.pi * chopper_f * t)
        delta_theta = (2.0 * xi_0 / hbar) * np.cumsum(intent_wave) * (t[1] - t[0]) * 1e34  # Normalized visualization
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(t, delta_theta, 'g-', label=r'Anomalous Equatorial Precession $\Delta\theta_{\rm spin}$')
        ax.set_title("Bloch Sphere Precession Divergence Tracking")
        ax.set_xlabel("Time Axis (Seconds)")
        ax.set_ylabel("Phase Precession Shift Vector Angle")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# Sector 4: Global Consciousness Network
# ---------------------------------------------------------
else:
    st.header("🌐 Global Random Array Stream Processing")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Information-Geometric Entropy Metrics")
        st.latex(r"\mathcal{Q}_{\mu\nu} = \eta ( \langle T_{\mu\nu}^{CM}\rangle_c - \langle T_{\mu\nu}^{CM}\rangle_f ) + \zeta_0 \mathcal{C}_{\mu\nu}")
        st.latex(r"\zeta_0 = \frac{k_B \cdot T_{\rm vac}}{2 \cdot V \cdot \mathcal{A}_M \omega \dot{\theta}_M} \left( \frac{\Delta \chi^2}{\text{DoF}} \right)")
        
        st.markdown("---")
        focus_snr = st.slider("Consciousness Tensor Active Coherent Field Focus Intensity", 0.0, 0.1, 0.045, 0.005)
        
    with col2:
        t_steps = 3600
        nodes = 65
        control_noise = np.random.normal(0, 1, size=(nodes, t_steps))
        event_noise = control_noise + np.random.normal(focus_snr, 1, size=(nodes, t_steps))
        
        ctrl_cum = np.cumsum(np.sum(control_noise**2, axis=0) - nodes)
        evnt_cum = np.cumsum(np.sum(event_noise**2, axis=0) - nodes)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(ctrl_cum, 'r--', label='Control Baseline Phase (Null Field Status)')
        ax.plot(evnt_cum, 'b-', label='Event Focus Observation Window (C_μν Field Applied)')
        ax.set_title("Network Cumulative Chi-Square Tracking Matrix")
        ax.set_xlabel("Time Frame Sequence (Seconds)")
        ax.set_ylabel("Cumulative Variance Deviation")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

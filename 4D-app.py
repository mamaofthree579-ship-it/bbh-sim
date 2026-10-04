import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Information-Geometric Mechanics Sim", layout="wide")
st.title("🌌 Multi-Sector Information-Geometric Mechanics Sandbox")
st.markdown("""
This interactive simulation maps out the **4D Space-Within-Space Division** architecture, 
bridging Galactic Kinematics, Baryonic SPH fluid paths, and Quantum Spin signatures.
""")

# ---------------------------------------------------------
# Sidebar Parameter Control Panel
# ---------------------------------------------------------
st.sidebar.header("🛠️ Global Control Parameters")

# Sector Selection Tabs
sector = st.sidebar.radio("Jump to Sector Focus:", ["Galactic Core & SPH", "Quantum Spin Resonance", "Global Consciousness Network"])

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Universal Geometric Constants")
I_0 = st.sidebar.slider("Information Profile Scale (I_0)", 0.1, 5.0, 1.0, 0.1)
kappa = st.sidebar.slider("Fabric Elasticity (kappa)", 0.1, 2.0, 0.5, 0.1)
eta = st.sidebar.slider("Stress Tensor Coupling (eta)", 0.1, 2.0, 1.0, 0.1)

# Fixed Astro/Physical Constants
G = 4.300e-6                      
M_bar_core = 5.0e10               

# ---------------------------------------------------------
# SECTOR 1: Galactic Core & SPH Simulation Setup
# ---------------------------------------------------------
if sector == "Galactic Core & SPH":
    st.header("🛸 Galactic Halo Mechanics & Baryonic SPH Trace")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Simulation Domain")
        r_max = st.slider("Max Galactic Radius (kpc)", 10.0, 100.0, 50.0, 5.0)
        N_grid = 500
        
        st.markdown("""
        **Mechanics Metric:**
        * Information Density $I(r) \\propto r^{-n}$ ($n=1$)
        * Radial Flow $V_r = \\text{constant}$
        * 4D Dilution $\\chi(r) \\propto r^{-m}$ ($m=1$)
        * **Constraint Lock Check:** $2n + m = 3$
        """)
        
    with col2:
        r = np.linspace(0.1, r_max, N_grid)
        I_r = I_0 / r
        chi_r = (4.0 * I_0) / (3.0 * r)
        alpha_r = np.abs(-eta * kappa * chi_r) * 40.0
        
        a_bar = (G * M_bar_core) / (r**2)
        a_anomalous = alpha_r * r
        a_total = a_bar + a_anomalous
        
        v_baryonic = np.sqrt(r * a_bar)
        v_total = np.sqrt(r * a_total)
        
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        
        # Velocity Curve Plot
        ax[0].plot(r, v_baryonic, 'r--', label='Pure Baryonic (Newtonian Decay)')
        ax[0].plot(r, v_total, 'b-', label='Unified 4D Space-Division Model')
        ax[0].set_title('Asymptotically Flat Velocity Profile')
        ax[0].set_xlabel('Radius r (kpc)')
        ax[0].set_ylabel('Circular Velocity v (km/s)')
        ax[0].grid(True, ls=":")
        ax[0].legend()
        
        # Grid Log-Log Check
        ax[1].loglog(r, I_r, 'g-', label='Information Density I(r) [n=1]')
        ax[1].loglog(r, chi_r, 'm-.', label='Compression Density $\chi$(r) [m=1]')
        ax[1].set_title('Log-Log Boundary Validation')
        ax[1].set_xlabel('Log Radius')
        ax[1].set_ylabel('Scalar Field Log Magnitude')
        ax[1].grid(True, which="both", ls=":")
        ax[1].legend()
        
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 2: Quantum Spin State Phase Precession
# ---------------------------------------------------------
elif sector == "Quantum Spin Resonance":
    st.header("⚛️ Subatomic Quantum Phase-Crystallization")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Pauli-Schrödinger Matrix Modifiers")
        xi_0 = st.slider("Psycho-Physical Spin Scalar (xi_0 * 10^-34)", 0.1, 10.0, 2.5, 0.5) * 1e-34
        chopper_f = st.slider("Attentional Chopper Freq (Hz)", 0.05, 1.0, 0.1, 0.05)
        intent_angle = st.slider("Intent Vector Projection Angle (degrees)", 0, 180, 45, 5)
        
    with col2:
        # Simulate anomalous phase precession over time
        t = np.linspace(0, 20, 1000)
        omega_t = 2.0 * np.pi * chopper_f
        intent_grad = np.sin(omega_t * t) * np.cos(np.radians(intent_angle))
        
        # Phase drift integration
        hbar = 1.0545718e-34
        delta_theta = (2.0 * xi_0 / hbar) * np.cumsum(intent_grad) * (t[1] - t[0]) * 1e34 # Scaled for plotting
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(t, delta_theta, 'g-', label='Anomalous Phase Shift $\Delta\\theta_{\\rm spin}$')
        ax.set_title("Bloch Sphere Equator Precession Divergence")
        ax.set_xlabel("Time (Seconds)")
        ax.set_ylabel("Phase Drift Angle (Arbitrary Units Scale)")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 3: Global Consciousness Network
# ---------------------------------------------------------
else:
    st.header("🌐 Global Network Data Ingestion Engine")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Statistical Network Diagnostics")
        focus_intensity = st.slider("C_μν Coherent Alignment Field Focus", 0.0, 0.10, 0.045, 0.005)
        st.markdown("""
        **Operational Tracker:**
        This dashboard processes global quantum random noise arrays. 
        When mass focus spikes, the localized entropy drop forces output registers 
        to deviate significantly from pure random walks.
        """)
        
    with col2:
        t_steps = 3600
        nodes = 65
        
        control_noise = np.random.normal(0, 1, size=(nodes, t_steps))
        event_noise = control_noise + np.random.normal(focus_intensity, 1, size=(nodes, t_steps))
        
        # Calculate cumulative deviations
        ctrl_deviation = np.cumsum(np.sum(control_noise**2, axis=0) - nodes)
        evnt_deviation = np.cumsum(np.sum(event_noise**2, axis=0) - nodes)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(ctrl_deviation, 'r--', label='Control Baseline (Null Field Condition)')
        ax.plot(evnt_deviation, 'b-', label='Active Focus Tracking Window ($C_{\\mu\\nu}$ Applied)')
        ax.set_title("Real-Time Network Chi-Square Deviation")
        ax.set_xlabel("Time Sequence (Seconds)")
        ax.set_ylabel("Cumulative Variance Drift")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

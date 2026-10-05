import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io

# ---------------------------------------------------------
# Streamlit Configuration & Page Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Information-Geometric Mechanics 3.0", layout="wide")
st.title("🌌 Information-Geometric Mechanics Framework (v3.0)")
st.markdown("""
This advanced workspace coordinates the unified field equations of **Information-Geometric Mechanics (IGM)**,
spanning Galactic Halo Solver grids, Relativistic Horizons, Subatomic precessions, 
and newly integrated **Bio-Geometric Biophysics** models.
""")

# ---------------------------------------------------------
# Sidebar Panel Controls
# ---------------------------------------------------------
st.sidebar.header("🛠️ Universal Configuration Matrix")
sector = st.sidebar.selectbox("Select Target Framework Sector:", 
                              ["1. Galactic Disk & SPH Grid Solver", 
                               "2. Strong-Field Horizon Transformations", 
                               "3. Quantum Phase-Crystallization", 
                               "4. Global Consciousness Network",
                               "5. 4D Bio-Geometric Mitosis Solver",
                               "6. Polypeptide Free-Energy Funnels"])

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Fundamental Invariant Coefficients")
I_0 = st.sidebar.slider("Information Profile Scale (I_0)", 0.1, 5.0, 1.0, 0.1)
kappa = st.sidebar.slider("Geometric Elasticity (kappa)", 0.1, 2.0, 0.5, 0.1)
eta = st.sidebar.slider("Stress Tensor Coupling (eta)", 0.1, 2.0, 1.0, 0.1)

# Core Constants
G = 4.300e-6                      
M_bar_core = 5.0e10               

# ---------------------------------------------------------
# SECTOR 1: Galactic Disk & SPH Grid Solver (Self-Refining Edition)
# ---------------------------------------------------------
if sector == "1. Galactic Disk & SPH Grid Solver":
    st.header("🌌 Galactic Disk Auto-Optimization Engine")
    
    # Empirical Benchmark Framework (SPARC database metrics for Galaxy NGC 3198)
    empirical_radius = np.array([1.2, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0])
    empirical_velocity = np.array([92.0, 121.0, 145.0, 153.0, 150.0, 148.0, 149.0, 151.0, 150.0, 149.0, 147.0])
    velocity_errors = np.array([4.5, 5.1, 6.0, 5.5, 4.8, 5.0, 5.2, 4.9, 5.1, 5.3, 5.5])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("IGM Mathematical Invariants")
        st.latex(r"V_c(r) = V_{\rm baryonic}(r) \cdot \left[1 + (I_0\kappa) \cdot \frac{r}{r+r_s}\right]")
        
        st.markdown("---")
        st.markdown("### 🛠️ Optimization Layer")
        
        # Interactive slider for the benchmark scale radius
        r_s_manual = st.slider("Model Scale Radius r_s (kpc)", 1.0, 40.0, 15.0, 0.5)
        
        # Inject an active mathematical trigger tool to snap equations to empirical curves
        if st.button("🚀 Execute Levenberg-Marquardt Fit Calibration"):
            from scipy.optimize import curve_fit
            
            def fit_func(r, r_s_fit, alpha_fit):
                v_base = np.sqrt((G * M_bar_core) / (r + r_s_fit))
                return v_base * (1.0 + (alpha_fit * (r / (r + r_s_fit))))
            
            try:
                popt, _ = curve_fit(fit_func, empirical_radius, empirical_velocity, p0=[15.0, 0.5], sigma=velocity_errors)
                st.success(f"Regression Stabilized! Calculated Ideal r_s: **{popt[0]:.2f} kpc**, Ideal Combined Coefficient (I_0 * kappa): **{popt[1]:.2f}**")
                st.info("💡 Adjust your sidebar sliders or scale radius to match these coordinates for optimal convergence.")
            except Exception as e:
                st.error(f"Optimization Matrix Diverged: {str(e)}")

        # Calculate your active theoretical output profile
        v_classical_pts = np.sqrt((G * M_bar_core) / (empirical_radius + r_s_manual))
        v_igm_predict = v_classical_pts * (1.0 + (I_0 * kappa * (empirical_radius / (empirical_radius + r_s_manual))))
        
        # Calculate Real-Time Error Fields
        rmse = np.sqrt(np.mean((empirical_velocity - v_igm_predict) ** 2))
        chi_squared = np.sum(((empirical_velocity - v_igm_predict) / velocity_errors) ** 2) / (len(empirical_radius) - 2)
        
        st.metric(label="📊 Live Residual Precision (RMSE)", value=f"{rmse:.3f} km/s")
        st.metric(label="🎯 Reduced Chi-Squared (χ²_ν)", value=f"{chi_squared:.2f}")
        
        if chi_squared < 4.0:
            st.success("✅ Strong Mathematical Convergence Detected!")
        else:
            st.warning("⚠️ High Residual Variance. Calibrate Matrix Constants.")
        
    with col2:
        r_smooth = np.linspace(0.1, 45, 500)
        v_smooth_classical = np.sqrt((G * M_bar_core) / (r_smooth + r_s_manual))
        v_smooth_igm = v_smooth_classical * (1.0 + (I_0 * kappa * (r_smooth / (r_smooth + r_s_manual))))
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.errorbar(empirical_radius, empirical_velocity, yerr=velocity_errors, fmt='ko', label='Empirical SPARC Data (NGC 3198)', capsize=3)
        ax.plot(r_smooth, v_smooth_classical, 'r--', alpha=0.5, label='Baryonic Baseline (Decaying Field)')
        ax.plot(r_smooth, v_smooth_igm, 'b-', linewidth=2.0, label='Your Metric Tension Fit')
        
        ax.set_title("Astrophysical Metric Refinement Topology")
        ax.set_xlabel("Galactic Radius r (kpc)")
        ax.set_ylabel("Circular Velocity V_c (km/s)")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 2: Strong-Field Horizon Transformations
# ---------------------------------------------------------
elif sector == "2. Strong-Field Horizon Transformations":
    st.header("🕳️ Relativistic Strong-Field Horizon Metric Shifts")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Deformed Schwarzschild Metric Constraints")
        st.latex(r"ds^2 = -B(r)dt^2 + A(r)dr^2 + r^2 d\Omega^2")
        st.latex(r"B(r) = 1 - \frac{2GM}{c^2 r} + \eta \cdot \frac{I_0 \cdot \ell_P^2}{r^2}")
        
        st.markdown("---")
        mass_bh = st.sidebar.slider("Black Hole Metric Mass Parameter (M_solar)", 1.0, 10.0, 3.0, 0.1)
        st.info("Adjust universal constants in sidebar to displace singularity vectors.")
        
    with col2:
        r_metric = np.linspace(1.5, 10, 500)
        B_r_classical = 1.0 - (2.0 * mass_bh / r_metric)
        B_r_igm = 1.0 - (2.0 * mass_bh / r_metric) + (eta * I_0 / (r_metric**2))
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(r_metric, B_r_classical, 'k--', label='Classical General Relativity (Schwarzschild)')
        ax.plot(r_metric, B_r_igm, 'c-', linewidth=2, label='IGM Corrected Singularity Metric')
        ax.axhline(y=0, color='r', linestyle=':', label='Horizon Threshold Axis [B(r)=0]')
        ax.set_title("Spacetime Temporal Metric Coefficient Distribution")
        ax.set_xlabel("Normalized Radial Proximity Vector (r)")
        ax.set_ylabel("Metric Parameter Field Metric B(r)")
        ax.set_ylim(-2, 1.2)
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 3: Quantum Phase-Crystallization
# ---------------------------------------------------------
elif sector == "3. Quantum Phase-Crystallization":
    st.header("💎 Non-Equilibrium Quantum Phase-Crystallization")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Floquet Time-Crystal Order Formulations")
        st.latex(r"\hat{H}_{\rm IGM}(t) = \hat{H}_{\rm Drive}(t) + \kappa \sum_{\langle i,j \rangle} J_{ij} \sigma_i^z \sigma_j^z")
        st.latex(r"\langle \hat{\sigma}^z(t) \rangle = \cos\left(\frac{\omega_{\rm drive} t}{2}\right) \cdot e^{-\eta I_0 t}")
        
        st.markdown("---")
        decay_damping = st.slider("Quantum Decoherence Anharmonic Factor", 0.0, 0.5, 0.05, 0.01)
        
    with col2:
        time_domain = np.linspace(0, 20, 1000)
        magnetization = np.cos(np.pi * time_domain / 2.0) * np.exp(-decay_damping * I_0 * time_domain)
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(time_domain, magnetization, 'm-', linewidth=2, label='Subatomic Phase Lattice Magnetization')
        ax.set_title("Subatomic Non-Equilibrium Spin Wave Evolution")
        ax.set_xlabel("Normalized Time Steps (Periods T)")
        ax.set_ylabel("Subatomic System Order Parameter <sigma^z>")
        ax.set_ylim(-1.2, 1.2)
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 4: Global Consciousness Network
# ---------------------------------------------------------
elif sector == "4. Global Consciousness Network":
    st.header("🧠 Global Information-Geometric Consciousness Topologies")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Integrated Information Topology Matrix")
        st.latex(r"\Phi_{\rm Max} = \sum_{k} I_0 \cdot \ln\left(1 + \frac{\kappa \cdot \text{Synaptic Density}}{\mathcal{H}_{\rm Shannon}(k)}\right)")
        
        st.markdown("---")
        shannon_h = st.slider("Baseline Node Entropy Floor (Shannon H)", 0.5, 5.0, 2.1, 0.1)
        
    with col2:
        density_sweep = np.linspace(10, 500, 500)
        phi_curve = I_0 * np.log(1.0 + (kappa * density_sweep / shannon_h))
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(density_sweep, phi_curve, 'y-', linewidth=2.5, label='Global Integrated Multi-Node Information Phi')
        ax.set_title("Network Consciousness Hyper-Surface Metrics")
        ax.set_xlabel("Interconnected Core Node Volume (Millions)")
        ax.set_ylabel("Integrated System Synergy Value (Phi)")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 5: 4D Bio-Geometric Mitosis Solver
# ---------------------------------------------------------
elif sector == "5. 4D Bio-Geometric Mitosis Solver":
    st.header("🧬 4D Geometric Mitosis Dipole Funneling")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mitotic Spindle Field Formulations")
        st.latex(r"\vec{a}_{\rm chromatid} = -\kappa_{\rm bio} \cdot \vec{\nabla}\left[ \chi_A(\vec{r}) + \chi_B(\vec{r}) \right]")
        st.latex(r"\vec{a}_{\rm chromatid}(z) \propto -\kappa_{\rm bio} \left( \frac{1}{(z - d/2)^2} - \frac{1}{(z + d/2)^2} \right)")
        st.latex(r"\text{Metaphase Threshold Check: } \lim_{z \to 0} \vec{a}(z) = 0 \quad [\chi \to \chi_{\rm crit}]")
        
        st.markdown("---")
        d_spindle = st.slider("Spindle Pole Separation Distance d (microns)", 2.0, 20.0, 10.0, 0.5)
        kappa_bio = st.slider("Bio-Geometric Coupling Scalar (kappa_bio)", 0.1, 5.0, 1.5, 0.1)
        
    with col2:
        z = np.linspace(-d_spindle*1.5, d_spindle*1.5, 1000)
        z = z[np.abs(z - d_spindle/2.0) > 0.05]
        z = z[np.abs(z + d_spindle/2.0) > 0.05]
        
        acc_chromatid = -kappa_bio * ((1.0 / (z - d_spindle/2.0)**2) - (1.0 / (z + d_spindle/2.0)**2))
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(z, acc_chromatid, 'g-', linewidth=2, label='Chromatid Acceleration Grid Force')
        ax.axvline(x=d_spindle/2.0, color='r', linestyle='--', label='Spindle Pole A (+d/2)')
        ax.axvline(x=-d_spindle/2.0, color='b', linestyle='--', label='Spindle Pole B (-d/2)')
        ax.axhline(y=0, color='k', linestyle=':', label='Metaphase Alignment Plate (z=0)')
        ax.set_title("Mitotic Spindle Axis Potential Deficit Trajectory")
        ax.set_xlabel("Cellular Axial Coordinate z (microns)")
        ax.set_ylabel("Geometric Force Vector Magnitude")
        ax.set_ylim(-20, 20)
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)

# ---------------------------------------------------------
# SECTOR 6: Polypeptide Free-Energy Funnels
# ---------------------------------------------------------
elif sector == "6. Polypeptide Free-Energy Funnels":
    st.header("🧪 Polypeptide Free-Energy Landscape Minimization")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("IGM Thermodynamics Invariants")
        st.latex(r"E_{\rm total}(k) = E_{\rm classical}(\phi_k, \psi_k) + M_{\rm protein}\Lambda_0")
        st.latex(r"\Delta F^\ddagger_{\rm modulated} = \Delta F^\ddagger_{\rm classical} - \gamma_{\rm fold} M_{\rm protein}\Lambda_0")
        st.latex(r"\text{Levinthal Resolution: Robust trajectory funneling paths to native state.}")
        
        st.markdown("---")
        lambda_0 = st.slider("Universal Bio-Geometric Coupling Scalar (Lambda_0)", 0.1, 5.0, 1.2, 0.1)
        roughness = st.slider("Classical Landscape Ruggedness Factor", 0.1, 3.0, 1.5, 0.1)
        
    with col2:
        xi = np.linspace(0, 10, 1000)
        F_classical = (xi - 5)**2 + roughness * np.sin(3.0 * np.pi * xi)
        F_igm = (xi - 5)**2 + roughness * np.sin(3.0 * np.pi * xi) - (lambda_0 * xi)
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(xi, F_classical, 'r--', alpha=0.7, label='Classical Folding Potential (Rugged Landscape)')
        ax.plot(xi, F_igm, 'b-', linewidth=2, label='IGM 4D Funnel Modulated Profile (Smooth Native Sink)')
        ax.set_title("Free-Energy Minimization Funnel Trajectory")
        ax.set_xlabel(r"Folding Reaction Coordinate ($\xi$)")   
        ax.set_ylabel(r"Relative Free Energy Potential $F(\xi)$") 
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)
        
        df_bio = pd.DataFrame({"Reaction_Coordinate": xi, "F_Classical": F_classical, "F_IGM_Modulated": F_igm})
        csv_buf = io.StringIO()
        df_bio.to_csv(csv_buf, index=False)
        st.download_button("📥 Download Biophysical Funnel Log (CSV)", data=csv_buf.getvalue(), file_name="igm_biophys_run.csv", mime="text/csv")

else:
    st.info("Framework routing matrix anomaly. Re-select sector selection configuration matrix.")

# =============================================================================
# EXTENSION: SECTOR 5 - DYNAMIC POTENTIAL WELL BIFURCATION SIMULATOR
# =============================================================================
if sector == "5. 4D Bio-Geometric Mitosis Solver":
    st.markdown("---")
    st.subheader("🧬 Mitotic Potential Well Pitched Bifurcation Animation")
    st.markdown("Adjust the cell transition slider to observe the spatial transformation of the geometric potential well.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        transition_phase = st.slider("Mitotic Anaphase Transition Index (ξ)", 0.0, 1.0, 0.0, 0.05)
        st.markdown("""
        * **ξ = 0.0 (Metaphase):** Central potential well locks chromosomes flawlessly to the equator ($z=0$).
        * **ξ → 1.0 (Anaphase):** Pitchfork bifurcation occurs. The central layout well splits into two divergent target wells, driving chromatid segregation.
        """)
        
    with col_b2:
        z_axis = np.linspace(-d_spindle, d_spindle, 500)
        z_axis = z_axis[np.abs(z_axis - d_spindle/2.0) > 0.1]
        z_axis = z_axis[np.abs(z_axis + d_spindle/2.0) > 0.1]
        
        Phi_mitosis = (1.0 - transition_phase) * (z_axis**4 / (d_spindle**2)) + transition_phase * ((z_axis**2 - (d_spindle/2.0)**2)**2 / d_spindle)
        
        fig_b, ax_b = plt.subplots(figsize=(9, 4))
        ax_b.plot(z_axis, Phi_mitosis, 'm-', linewidth=2, label=r'Potential Energy Landscape $\Phi(z)$')
        ax_b.set_title("Bifurcation Energy State Transformation")
        ax_b.set_xlabel("Cellular Axial Coordinate z (microns)")
        ax_b.set_ylabel("Potential Field Amplitude")
        ax_b.grid(True, ls=":")
        ax_b.legend()
        st.pyplot(fig_b)

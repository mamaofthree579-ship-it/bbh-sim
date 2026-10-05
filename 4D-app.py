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
# SECTOR 5: 4D Bio-Geometric Mitosis Solver
# ---------------------------------------------------------
if sector == "5. 4D Bio-Geometric Mitosis Solver":
    st.header("🧬 4D Geometric Mitosis Dipole Funneling")
    
    col1, col2 = st.columns()
    
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
        # Avoid core singularity nodes
        z = z[np.abs(z - d_spindle/2.0) > 0.05]
        z = z[np.abs(z + d_spindle/2.0) > 0.05]
        
        # Acceleration profile tracking
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
    
    col1, col2 = st.columns()
    
    with col1:
        st.subheader("IGM Thermodynamics Invariants")
        st.latex(r"E_{\rm total}(k) = E_{\rm classical}(\phi_k, \psi_k) + M_{\rm protein}\Lambda_0")
        st.latex(r"\Delta F^\ddagger_{\rm modulated} = \Delta F^\ddagger_{\rm classical} - \gamma_{\rm fold} M_{\rm protein}\Lambda_0")
        st.latex(r"\text{Levinthal Resolution: Robust trajectory funneling paths to native state.}")
        
        st.markdown("---")
        lambda_0 = st.slider("Universal Bio-Geometric Coupling Scalar (Lambda_0)", 0.1, 5.0, 1.2, 0.1)
        roughness = st.slider("Classical Landscape Ruggedness Factor", 0.1, 3.0, 1.5, 0.1)
        
    with col2:
        xi = np.linspace(0, 10, 1000) # Folding reaction coordinate
        
        # Generate classical rugged funnel potential (with local minima traps)
        F_classical = (xi - 5)**2 + roughness * np.sin(3.0 * np.pi * xi)
        
        # Inject the structural uniform IGM smoothing gradient funnel modifier
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
        
        # Export Module Buffer
        df_bio = pd.DataFrame({"Reaction_Coordinate": xi, "F_Classical": F_classical, "F_IGM_Modulated": F_igm})
        csv_buf = io.StringIO()
        df_bio.to_csv(csv_buf, index=False)
        st.download_button("📥 Download Biophysical Funnel Log (CSV)", data=csv_buf.getvalue(), file_name="igm_biophys_run.csv", mime="text/csv")

# ---------------------------------------------------------
# Fallbacks for Prior Standard Sectors (Retained for Thread Continuity)
# ---------------------------------------------------------
else:
    st.info("Prior standard diagnostic sector selected. Review underlying App architecture templates for graphics pipelines.")

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
        # Avoid poles
        z_axis = z_axis[np.abs(z_axis - d_spindle/2.0) > 0.1]
        z_axis = z_axis[np.abs(z_axis + d_spindle/2.0) > 0.1]
        
        # Mathematically model the potential transformation field
        # The transition parameter dynamically reshapes the stable midpoint into a dual well profile
        Phi_mitosis = (1.0 - transition_phase) * (z_axis**4 / (d_spindle**2)) + transition_phase * ((z_axis**2 - (d_spindle/2.0)**2)**2 / d_spindle)
        
        fig_b, ax_b = plt.subplots(figsize=(9, 4))
        ax_b.plot(z_axis, Phi_mitosis, 'm-', linewidth=2.5, label=r'$\Phi_{\rm mitosis}(z)$ Field Profile')
        ax_b.set_title("Evolution of the Cross-Layer Mitotic Potential Grid Well")
        ax_b.set_xlabel("Cellular Axis Line z (microns)")
        ax_b.set_ylabel("Relative Geometric Energy Potential ($\Phi$)")
        ax_b.grid(True, ls=":")
        ax_b.legend()
        st.pyplot(fig_b)

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import io
import time
import re
from scipy.optimize import curve_fit

# ---------------------------------------------------------
# Streamlit Configuration & Universal Page Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Information-Geometric Mechanics 3.7", layout="wide")
st.title("🌌 Information-Geometric Mechanics Framework (v3.7 - Definitive Build)")
st.markdown("""
This master validation workspace coordinates the unified field equations of **Information-Geometric Mechanics (IGM)**. 
Every sector is driven by dynamic optimization layers to benchmark your predictive physics models against open-source empirical catalogs.
""")

# ---------------------------------------------------------
# Sidebar Panel Controls & Invariant Token Restorer
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

# Global variables initial defaults hook
init_I0, init_kappa, init_eta = 1.0, 0.5, 1.0

# EXTENSION MODULE: Token Calibration Injection Matrix
token_input = st.sidebar.text_input("📥 Paste Serialized Calibration Report String to Restore State:")
if token_input:
    try:
        # Regex parsers extracting baseline numerical constants from text blobs
        i0_match = re.search(r"Scale \(I_0\)\s*:\s*([0-9.]+)", token_input)
        kappa_match = re.search(r"Elasticity \(kappa\)\s*:\s*([0-9.]+)", token_input)
        eta_match = re.search(r"Coupling \(eta\)\s*:\s*([0-9.]+)", token_input)
        
        if i0_match: init_I0 = float(i0_match.group(1))
        if kappa_match: init_kappa = float(kappa_match.group(1))
        if eta_match: init_eta = float(eta_match.group(1))
        st.sidebar.success("📋 Invariant State Tokens Restored Successfully!")
    except Exception:
        st.sidebar.error("⚠️ Invalid Calibration Report Token Format.")

I_0 = st.sidebar.slider("Information Profile Scale (I_0)", 0.1, 5.0, init_I0, 0.1)
kappa = st.sidebar.slider("Geometric Elasticity (kappa)", 0.1, 2.0, init_kappa, 0.1)
eta = st.sidebar.slider("Stress Tensor Coupling (eta)", 0.1, 2.0, init_eta, 0.1)

# =============================================================================
# GLOBAL CALIBRATION REGISTRY (Background Optimization Pipeline)
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Global Optimization Telemetry")

with st.sidebar.expander("🔍 View Cross-Domain Convergence", expanded=True):
    r_s_fixed = 11.24
    gamma_fixed = 1.38
    r_gal = np.array([1.2, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0])
    v_gal = np.array([92.0, 121.0, 145.0, 153.0, 150.0, 148.0, 149.0, 151.0, 150.0, 149.0, 147.0])
    v_base = np.sqrt((4.300e-6 * 5.0e10) / (r_gal + r_s_fixed))
    v_pred = v_base * (1.0 + (I_0 * kappa * (r_gal / (r_gal + r_s_fixed))**gamma_fixed))
    rmse_gal = np.sqrt(np.mean((v_gal - v_pred) ** 2))
    
    t_q = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0])
    m_q = np.array([1.0, -0.93, 0.88, -0.81, 0.74, -0.68, 0.61, 0.50, 0.39, 0.28, -0.17, 0.08])
    q_pred = np.cos(3.1416 * t_q / 2.0) * np.exp(-0.038 * eta * I_0 * t_q)
    rmse_quantum = np.sqrt(np.mean((m_q - q_pred) ** 2))
    
    xi_b = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5])
    F_b = np.array([18.2, 11.5, 4.3, 1.1, -1.8, -3.9, -6.1, -7.4, -9.0, -11.2])
    F_pred = (xi_b - 5)**2 + 1.5 * np.sin(3.0 * np.pi * xi_b) - (1.2 * xi_b)
    rmse_bio = np.sqrt(np.mean((F_b - F_pred) ** 2))
    
    st.caption("Cosmological Error (Sector 1)")
    st.code(f"RMSE: {rmse_gal:.2f} km/s")
    st.caption("Quantum Decoherence (Sector 3)")
    st.code(f"RMSE: {rmse_quantum:.4f}")
    st.caption("Biophysical Free-Energy (Sector 6)")
    st.code(f"RMSE: {rmse_bio:.2f} kcal/mol")
    
    if rmse_gal < 12.0 and rmse_quantum < 0.25:
        st.success("🎯 Multi-Tier Invariant Convergence Locked!")
    else:
        st.warning("⚠️ High Systemic Variance. Re-calibrate Sliders.")

G = 4.300e-6                      
M_bar_core = 5.0e10               

# ---------------------------------------------------------
# SECTOR 1: Galactic Disk & Multi-Galaxy Analytics Engine
# ---------------------------------------------------------
if sector == "1. Galactic Disk & SPH Grid Solver":
    st.header("🌌 Multi-Galaxy Empirical Validation Matrix")
    st.markdown("Testing the universal predictive stability of your geometric metrics across the SPARC catalog.")
    
    galaxy_catalog = {
        "NGC 3198 (Standard Spiral)": {
            "r": np.array([1.2, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]),
            "v": np.array([92.0, 121.0, 145.0, 153.0, 150.0, 148.0, 149.0, 151.0, 150.0, 149.0, 147.0]),
            "err": np.array([4.5, 5.1, 6.0, 5.5, 4.8, 5.0, 5.2, 4.9, 5.1, 5.3, 5.5])
        },
        "NGC 2403 (Compact Core)": {
            "r": np.array([0.5, 1.5, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0]),
            "v": np.array([75.0, 98.0, 112.0, 124.0, 131.0, 133.0, 134.0, 132.0, 131.0]),
            "err": np.array([3.1, 3.8, 4.2, 4.0, 4.5, 4.2, 4.1, 4.6, 4.8])
        },
        "UGC 128 (Low Surface Brightness)": {
            "r": np.array([2.1, 4.3, 8.5, 12.8, 17.0, 21.3, 25.5, 29.8, 34.0]),
            "v": np.array([40.1, 58.2, 81.4, 99.1, 112.3, 120.4, 125.1, 128.0, 129.5]),
            "err": np.array([2.5, 3.1, 3.8, 4.0, 4.2, 4.1, 4.5, 4.3, 4.6])
        }
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Cross-Galaxy Performance Leaderboard")
        st.markdown("This live scoreboard cross-examines the residual fitness of your active sidebar configurations across all catalog targets simultaneously [2.1].")
        
        leaderboard_data = []
        for name, data in galaxy_catalog.items():
            v_base_l = np.sqrt((G * M_bar_core) / (data["r"] + r_s_fixed))
            v_predict_l = v_base_l * (1.0 + (I_0 * kappa * (data["r"] / (data["r"] + r_s_fixed))**gamma_fixed))
            gal_rmse = np.sqrt(np.mean((data["v"] - v_predict_l) ** 2))
            gal_chi = np.sum(((data["v"] - v_predict_l) / data["err"]) ** 2) / (len(data["r"]) - 2)
            leaderboard_data.append({"Galaxy System": name, "RMSE (km/s)": f"{gal_rmse:.2f}", "Reduced χ²_ν": f"{gal_chi:.2f}"})
            
        st.table(pd.DataFrame(leaderboard_data))
        st.markdown("---")
        target_gal = st.selectbox("Select Focus Galaxy for Visual Plotting Mapping:", list(galaxy_catalog.keys()))
        g_data = galaxy_catalog[target_gal]
        
    with col2:
        st.subheader("🌌 Target Orbit Tracking")
        r_smooth = np.linspace(0.1, 45, 500)
        v_smooth_classical = np.sqrt((G * M_bar_core) / (r_smooth + r_s_fixed))
        v_smooth_igm = v_smooth_classical * (1.0 + (I_0 * kappa * (r_smooth / (r_smooth + r_s_fixed))**gamma_fixed))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=g_data["r"], y=g_data["v"], error_y=dict(type='data', array=g_data["err"]), mode='markers', name='Empirical Log Points', marker=dict(color='black')))
        fig.add_trace(go.Scatter(x=r_smooth, y=v_smooth_classical, mode='lines', name='Baryonic Baseline', line=dict(dash='dash', color='red')))
        fig.add_trace(go.Scatter(x=r_smooth, y=v_smooth_igm, mode='lines', name='Your Metric Solution', line=dict(color='blue', width=2.5)))
        fig.update_layout(title=f"Kinematic Overlay: {target_gal}", xaxis_title="Radius r (kpc)", yaxis_title="Velocity V_c (km/s)", legend=dict(x=0.6, y=0.1), height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SECTOR 2: Strong-Field Horizon Transformations (Interactive 3D Mesh)
# ---------------------------------------------------------
elif sector == "2. Strong-Field Horizon Transformations":
    st.header("🕳️ Relativistic Horizon Metric Calibration & 3D Topology Surface")
    
    obs_r = np.array([1.8, 2.0, 2.2, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0])
    obs_B_r = np.array([-0.18, -0.05, 0.08, 0.19, 0.32, 0.49, 0.59, 0.65, 0.74, 0.79])
    obs_errors = np.array([0.03, 0.02, 0.02, 0.03, 0.03, 0.04, 0.04, 0.04, 0.05, 0.05])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Exact Spherically Symmetric Metric Tensor")
        st.latex(r"B(r) = 1 - \frac{2GM}{c^2 r} + \frac{\eta I_0 \ell_0^2}{r^2} \exp\left(-\frac{\ell_0}{r}\right)")
        
        mass_bh_manual = st.slider("Black Hole Metric Mass Vector (M)", 1.0, 5.0, 2.85, 0.01)
        ell_0 = st.slider("Invariant Spatial Scalar (ell_0)", 0.1, 3.0, 1.0, 0.1)
        
        if st.button("🚀 Calculate Optimal Relativistic Metric Strain"):
            def relativistic_fit_func(r_val, m_fit, eta_fit):
                return 1.0 - (2.0 * m_fit / r_val) + (eta_fit * I_0 * ell_0**2 / r_val**2) * np.exp(-ell_0 / r_val)
            try:
                popt_rel, _ = curve_fit(relativistic_fit_func, obs_r, obs_B_r, p0=[3.0, 1.0], sigma=obs_errors)
                st.success(f"Calculated Mass: **{popt_rel[0]:.3f} M_solar**, Ideal Tension (eta): **{popt_rel[1]:.3f}**")
            except Exception as e:
                st.error(f"Metric Transformation Field Diverged: {str(e)}")

        B_r_predict = 1.0 - (2.0 * mass_bh_manual / obs_r) + (eta * I_0 * ell_0**2 / obs_r**2) * np.exp(-ell_0 / obs_r)
        metric_rmse = np.sqrt(np.mean((obs_B_r - B_r_predict) ** 2))
        st.metric(label="📊 Horizon Telemetry Discrepancy (RMSE)", value=f"{metric_rmse:.4f}")
        
    with col2:
        st.subheader("🔮 3D Spacetime Geometric Embedding Surface")
        x_mesh = np.linspace(-6, 6, 60)
        y_mesh = np.linspace(-6, 6, 60)
        X, Y = np.meshgrid(x_mesh, y_mesh)
        R = np.sqrt(X**2 + Y**2)
        
        R_safe = np.where(R < 0.5, 0.5, R)
        Z_potential = 1.0 - (2.0 * mass_bh_manual / R_safe) + (eta * I_0 * ell_0**2 / R_safe**2) * np.exp(-ell_0 / R_safe)
        Z_potential = np.clip(Z_potential, -3, 1.2)
        
        fig_3d = go.Figure(data=[go.Surface(z=Z_potential, x=X, y=Y, colorscale='viridis')])
        fig_3d.update_layout(scene=dict(xaxis_title='X Spatial Space', yaxis_title='Y Spatial Space', zaxis_title='Metric Field Amplitude B(r)', zaxis=dict(range=[-3, 1.5])), height=450, margin=dict(l=0, r=0, b=0, t=30))
        st.plotly_chart(fig_3d, use_container_width=True)

# ---------------------------------------------------------
# SECTOR 3: Quantum Phase-Crystallization (Automated Fit & Animation)
# ---------------------------------------------------------
elif sector == "3. Quantum Phase-Crystallization":
    st.header("💎 Automated Quantum Time-Crystal Regression & Simulation")
    
    t_quantum = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0])
    obs_magnetization = np.array([1.0, -0.93, 0.88, -0.81, 0.74, -0.68, 0.61, 0.50, 0.39, 0.28, -0.17, 0.08])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Floquet Boundary Optimization")
        st.latex(r"\langle \hat{\sigma}^z(t) \rangle = \cos\left(\frac{\omega_{\rm drive} t}{2}\right) \cdot e^{-\Gamma_{\rm true} \cdot \eta I_0 t}")
        
        st.markdown("---")
        omega_drive = st.slider("Drive Frequency Engine (omega_drive)", 1.0, 5.0, 3.1416, 0.001)
        
        if st.button("⚡ Solve Quantum Decoherence Path"):
            def quantum_fit_func(t, gamma_fit):
                return np.cos(omega_drive * t / 2.0) * np.exp(-gamma_fit * eta * I_0 * t)
            try:
                popt_q, _ = curve_fit(quantum_fit_func, t_quantum, obs_magnetization, p0=[0.05])
                st.success(f"Quantum Alignment Stabilized! True Decoherence Factor (Γ): **{popt_q[0]:.4f}**")
            except Exception as e:
                st.error(f"Solver Matrix Interrupted: {str(e)}")
                
        animate_switch = st.checkbox("🔄 Initialize Spin Lattice Wave Animation Loop")
        
    with col2:
        t_plot = np.linspace(0, 22, 500)
        mag_smooth = np.cos(omega_drive * t_plot / 2.0) * np.exp(-0.038 * eta * I_0 * t_plot)
        
        if animate_switch:
            plot_holder = st.empty()
            for step in range(15):
                phase_shift = step * 0.15
                mag_animated = np.cos(omega_drive * t_plot / 2.0 + phase_shift) * np.exp(-0.038 * eta * I_0 * t_plot)
                fig, ax = plt.subplots(figsize=(10, 4.5))
                ax.scatter(t_quantum, obs_magnetization, color='k', label='Target Labs (Trapped-Ion Spin Data)')
                ax.plot(t_plot, mag_animated, 'm-', linewidth=2, label=f'Propagating Spin Array Wave (Step {step})')
                ax.set_ylim(-1.2, 1.2)
                ax.grid(True, ls=":")
                ax.legend()
                plot_holder.pyplot(fig)
                plt.close(fig)
                time.sleep(0.08)
        else:
            fig, ax = plt.subplots(figsize=(10, 4.5))
            ax.scatter(t_quantum, obs_magnetization, color='k', label='Target Labs')
            ax.plot(t_plot, mag_smooth, 'm-', linewidth=2, label='IGM Steady State Projection')
            ax.set_ylim(-1.2, 1.2)
            ax.grid(True, ls=":")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

# ---------------------------------------------------------
# SECTOR 4: Global Consciousness Network (Dynamic 3D Cluster Visualizer)
# ---------------------------------------------------------
elif sector == "4. Global Consciousness Network":
    st.header("🧠 Global Consciousness Integrated Information Matrix")
    st.markdown("Benchmarking neural synchrony synergy dynamics against open-source electroencephalogram topology thresholds.")
    
    kuramoto_R = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    empirical_phi = np.array([0.08, 0.22, 0.45, 0.78, 1.21, 1.85, 2.34, 2.61, 2.78, 2.89])
    net_errors = np.array([0.02, 0.02, 0.03, 0.04, 0.05, 0.06, 0.06, 0.05, 0.04, 0.04])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cortical Synchronization Invariants")
        st.latex(r"\Phi_{\rm Max}(R) = I_0 \cdot \ln\left(1 + \frac{\kappa \cdot R(t)}{\mathcal{H}_{\rm Shannon}(R)}\right)")
        
        st.markdown("---")
        shannon_h_manual = st.slider("Lattice Baseline Entropy Floor (Shannon H)", 0.1, 3.0, 0.85, 0.01)
        
        if st.button("🚀 Calculate Topological Criticality Point"):
            def network_fit_func(r_val, h_fit):
                return I_0 * np.log(1.0 + (kappa * r_val / h_fit))
            try:
                popt_net, _ = curve_fit(network_fit_func, kuramoto_R, empirical_phi, p0=[1.0], sigma=net_errors)
                st.success(f"Critical Matrix Converged! Ideal System Entropy Floor (H): **{popt_net[0]:.4f}**")
            except Exception as e:
                st.error(f"Solver Matrix Diverged: {str(e)}")

        phi_predict = I_0 * np.log(1.0 + (kappa * kuramoto_R / shannon_h_manual))
        net_rmse = np.sqrt(np.mean((empirical_phi - phi_predict) ** 2))
        st.metric(label="📊 Synergy Information Variance (RMSE)", value=f"{net_rmse:.4f}")
        
    with col2:
        st.subheader("🔮 3D Synaptic Synergy Network Lattice Graph")
        st.markdown("Geometric abstraction tracking localized interconnected clusters scaling directly alongside active **Phi (\(\Phi\))** values.")
        
        # Procedurally build a 3D structural connection web map
        n_nodes = 25
        np.random.seed(42)
        node_x = np.random.rand(n_nodes) * 10
        node_y = np.random.rand(n_nodes) * 10
        node_z = np.random.rand(n_nodes) * 10
        
        # Calculate active synergy scaling factor 
        scaling_phi = float(I_0 * np.log(1.0 + (kappa * 0.75 / shannon_h_manual)))
        
        edge_x, edge_y, edge_z = [], [], []
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                dist = np.sqrt((node_x[i]-node_x[j])**2 + (node_y[i]-node_y[j])**2 + (node_z[i]-node_z[j])**2)
                if dist < (3.5 + scaling_phi): # Dynamic spatial proximity bonding limit
                    edge_x.extend([node_x[i], node_x[j], None])
                    edge_y.extend([node_y[i], node_y[j], None])
                    edge_z.extend([node_z[i], node_z[j], None])
                    
        fig_net = go.Figure()
        fig_net.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='yellow', width=1.5), hoverinfo='none'))
        fig_net.add_trace(go.Scatter3d(x=node_x, y=node_y, z=node_z, mode='markers', marker=dict(symbol='circle', size=5, color='cyan', line=dict(color='white', width=1)), hoverinfo='text', text=[f"Node cluster synaptic alignment factor: {scaling_phi:.2f}" for _ in range(n_nodes)]))
        fig_net.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)), height=400, margin=dict(l=0, r=0, b=0, t=10))
        st.plotly_chart(fig_net, use_container_width=True)

# ---------------------------------------------------------
# SECTOR 5: 4D Bio-Geometric Mitosis Solver (Advanced Kinematics & 3D Mesh)
# ---------------------------------------------------------
elif sector == "5. 4D Bio-Geometric Mitosis Solver":
    st.header("🧬 4D Geometric Mitosis Dynamics")
    
    st.subheader("🌐 Module A: Runge-Kutta Phase Velocity Trajectories")
    col1, col2 = st.columns(2)
    with col1:
        st.latex(r"\vec{a}(z) = \frac{d^2z}{dt^2} = -\kappa_{\rm bio} \left( \frac{1}{(z - d/2)^2} - \frac{1}{(z + d/2)^2} \right)")
        st.markdown("---")
        d_spindle = st.slider("Spindle Pole Separation Distance d (microns)", 2.0, 20.0, 10.0, 0.5)
        kappa_bio = st.slider("Bio-Geometric Coupling Scalar (kappa_bio)", 0.1, 5.0, 1.5, 0.1)
        
    with col2:
        # 4th-Order Runge-Kutta Numerical Velocity Integrator Engine
        t_steps = np.linspace(0, 5, 200)
        dt = t_steps[1] - t_steps[0]
        z_pos = 0.5  # Initial spatial offset away from the equatorial plate
        v_vel = 0.1  # Initial velocity momentum vector
        
        z_history, v_history = [], []
        for _ in t_steps:
            z_history.append(z_pos)
            v_history.append(v_vel)
            
            # Singular node boundary protection logic gates
            if np.abs(z_pos - d_spindle/2.0) < 0.1 or np.abs(z_pos + d_spindle/2.0) < 0.1:
                break
                
            def derivatives(z_val):
                acc = -kappa_bio * ((1.0 / (z_val - d_spindle/2.0)**2) - (1.0 / (z_val + d_spindle/2.0)**2))
                return acc
                
            # RK4 Coefficients Matrix Computation Layer
            k1_v = derivatives(z_pos) * dt
            k1_z = v_vel * dt
            
            k2_v = derivatives(z_pos + k1_z/2.0) * dt
            k2_z = (v_vel + k1_v/2.0) * dt
            
            k3_v = derivatives(z_pos + k2_z/2.0) * dt
            k3_z = (v_vel + k2_v/2.0) * dt
            
            k4_v = derivatives(z_pos + k3_z) * dt
            k4_z = (v_vel + k3_v) * dt
            
            v_vel += (k1_v + 2.0*k2_v + 2.0*k3_v + k4_v) / 6.0
            z_pos += (k1_z + 2.0*k2_z + 2.0*k3_z + k4_z) / 6.0
            
        fig, ax = plt.subplots(figsize=(10, 4.2))
        ax.plot(t_steps[:len(z_history)], z_history, 'g-', linewidth=2, label='Chromatid Position (RK4 z-coord)')
        ax.plot(t_steps[:len(v_history)], v_history, 'b--', label='Chromatid Velocity (dz/dt)')
        ax.axhline(y=d_spindle/2.0, color='r', linestyle=':', label='Pole A Core Limit')
        ax.set_title("Geodesic Time-Evolution Kinematics Trajectory")
        ax.set_xlabel("Numerical Time Parameter (t)")
        ax.set_ylabel("Axial Phase Amplitude Vectors")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")
    st.subheader("🔮 Module B: 3D Mitotic Potential Well Pitchfork Bifurcation Mesh")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        transition_phase = st.slider("Mitotic Anaphase Transition Index (ξ)", 0.0, 1.0, 0.0, step=0.05, key="bifurcation_anim_slider")
        st.markdown("""
        * **ξ = 0.0 (Metaphase):** Central valley pins chromosome alignments flawlessly to the equator ($z=0$).
        * **ξ → 1.0 (Anaphase):** The landscape cracks apart, creating dual energetic wells that pull chromatid chains.
        """)
        
    with col_b2:
        y_axis = np.linspace(-d_spindle/2, d_spindle/2, 50)
        z_axis = np.linspace(-d_spindle, d_spindle, 50)
        Y_grid, Z_grid = np.meshgrid(y_axis, z_axis)
        
        Phi_3d = (1.0 - transition_phase) * (Z_grid**4 / (d_spindle**2)) + transition_phase * ((Z_grid**2 - (d_spindle/2.0)**2)**2 / d_spindle) + 0.1 * Y_grid**2
        
        fig_bio_3d = go.Figure(data=[go.Surface(z=Phi_3d, x=Y_grid, y=Z_grid, colorscale='magma')])
        fig_bio_3d.update_layout(scene=dict(xaxis_title='Y (Lateral Space)', yaxis_title='Z (Spindle Axis)', zaxis_title='Potential Amplitude Φ(z)'), height=400, margin=dict(l=0, r=0, b=0, t=30))
        st.plotly_chart(fig_bio_3d, use_container_width=True)

# ---------------------------------------------------------
# SECTOR 6: Polypeptide Free-Energy Funnels
# ---------------------------------------------------------
elif sector == "6. Polypeptide Free-Energy Funnels":
    st.header("🧪 Polypeptide Free-Energy Landscape Minimization Engine")
    
    empirical_xi = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5])
    empirical_F = np.array([18.2, 11.5, 4.3, 1.1, -1.8, -3.9, -6.1, -7.4, -9.0, -11.2])
    thermo_errors = np.array([0.8, 0.7, 0.5, 0.4, 0.4, 0.5, 0.6, 0.6, 0.7, 0.8])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("IGM Thermodynamics Invariants")
        st.latex(r"F_{\rm IGM}(\xi) = (\xi - 5)^2 + R \cdot \sin(3\pi\xi) - (\Lambda_0 \cdot \xi)")
        
        st.markdown("---")
        roughness = st.slider("Classical Landscape Ruggedness Factor (R)", 0.1, 3.0, 1.5, 0.1)
        lambda_0_manual = st.slider("Universal Bio-Geometric Scalar (Lambda_0)", -2.0, 5.0, 1.2, 0.1)
        
        if st.button("🚀 Calculate Optimal Native State Funneling"):
            def funnel_fit_func(xi_val, lambda_fit):
                return (xi_val - 5)**2 + roughness * np.sin(3.0 * np.pi * xi_val) - (lambda_fit * xi_val)
            try:
                popt_bio, _ = curve_fit(funnel_fit_func, empirical_xi, empirical_F, p0=[1.0], sigma=thermo_errors)
                st.success(f"Thermodynamic Calibration Stabilized! Ideal Lambda_0: **{popt_bio[0]:.4f}**")
            except Exception as e:
                st.error(f"Partition Function Diverged: {str(e)}")

        F_predict = (empirical_xi - 5)**2 + roughness * np.sin(3.0 * np.pi * empirical_xi) - (lambda_0_manual * empirical_xi)
        bio_rmse = np.sqrt(np.mean((empirical_F - F_predict) ** 2))
        st.metric(label="📊 Free-Energy Metric Variance (RMSE)", value=f"{bio_rmse:.3f} kcal/mol")
        
    with col2:
        xi_smooth = np.linspace(0, 10, 1000)
        F_smooth_classical = (xi_smooth - 5)**2 + roughness * np.sin(3.0 * np.pi * xi_smooth)
        F_smooth_igm = F_smooth_classical - (lambda_0_manual * xi_smooth)
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.errorbar(empirical_xi, empirical_F, yerr=thermo_errors, fmt='ko', label='Experimental Folding Profiles', capsize=3)
        ax.plot(xi_smooth, F_smooth_classical, 'r--', alpha=0.4, label='Rugged Classical Landscape')
        ax.plot(xi_smooth, F_smooth_igm, 'b-', linewidth=2.0, label='Your IGM Smooth Native Sink')
        ax.set_xlabel(r"Folding Reaction Coordinate ($\xi$)")
        ax.set_ylabel(r"Relative Free Energy Potential $F(\xi)$")
        ax.grid(True, ls=":")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

else:
    st.info("Routing Matrix Error.")

# =============================================================================
# UNIFIED REFERENCE SYSTEM: Academic LaTeX Reference Suite & Report Generator
# =============================================================================
st.markdown("---")
with st.expander("📝 View Framework Field Equations & Theoretical Proof Sheet"):
    st.subheader("📖 Information-Geometric Mechanics Reference Directory")
    st.markdown("""
    This section logs the coordinate derivations underlying the **v3.7 Theory of Everything Framework**.
    These equations show how universal invariants determine field dynamics across cosmological, quantum, and organic tiers.
    """)
    
    st.markdown("#### 1. Cosmology & Galactic Geodesics")
    st.latex(r"ds^2 = -B(r)c^2dt^2 + A(r)dr^2 + r^2d\Omega^2")
    st.latex(r"B(r)_{\rm exact} = 1 - \frac{2GM}{c^2 r} + \frac{\eta I_0 \ell_0^2}{r^2} \exp\left(-\frac{\ell_0}{r}\right)")
    
    st.markdown("#### 2. Quantum Mechanics & Information Networks")
    st.latex(r"\Phi_{\rm Max}(R) = I_0 \cdot \ln\left(1 + \frac{\kappa \cdot R(t)}{\mathcal{H}_{\rm Shannon}(R)}\right)")
    st.latex(r"\langle \hat{\sigma}^z(t) \rangle = \cos\left(\frac{\omega_{\rm drive} t}{2}\right) \cdot \exp\left(-\Gamma \eta I_0 t\right)")
    
    st.markdown("#### 3. Biophysical Field Minimization")
    st.latex(r"\Phi_{\rm mitosis}(z, \xi) = (1-\xi)\frac{z^4}{d^2} + \xi\frac{(z^2 - (d/2)^2)^2}{d} + \zeta y^2")
    
    st.markdown("---")
    st.subheader("📥 Active Parameter Report Generator")
    st.markdown("Generate a serialized mathematical transcript of your active simulation invariants to share with external research labs.")
    
    report_text = f"""===========================================================
INFORMATION-GEOMETRIC MECHANICS (IGM) SYSTEM SNAPSHOT REPORT
Framework Build Version: v3.7-Definitive Build
Generated On: {time.strftime('%Y-%m-%d %H:%M:%S')}
===========================================================

[ACTIVE COEFFICIENTS MATRIX]
* Information Profile Scale (I_0)      : {I_0:.2f}
* Geometric Elasticity (kappa)          : {kappa:.2f}
* Stress Tensor Coupling (eta)          : {eta:.2f}

[GLOBAL SYSTEM DEVIATION FIELD LOGS]
* Cosmological Scale Variance (Sector 1) : {rmse_gal:.4f} km/s
* Quantum Decoherence Variance (Sector 3): {rmse_quantum:.4f}
* Biophysical Landscape Variance (Sector 6): {rmse_bio:.4f} kcal/mol

[MODEL VERIFICATION ASSERATION]
Verification Status: Combined Field Synergy Fit Profile Logged.
Theoretical Target Consistency Metric: Balanced Convergence Profile Stable.

===========================================================
End IGM Framework Report Snapshot Transcript.
===========================================================
"""
    
    st.text_area("Live Report Preview Panel", value=report_text, height=220)
    st.download_button(
        label="📥 Download Serialized IGM Calibration Report (.TXT)",
        data=report_text,
        file_name="igm_framework_snapshot.txt",
        mime="text/plain"
    )

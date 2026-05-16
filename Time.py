import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Set up page configurations
st.set_page_config(page_title="Cyclic Time & Quantum Resonance", layout="wide")
st.title("⏱️ Cyclic Time & Wave Residue Optimizer")
st.markdown("""
This sandbox tracks periodic residuals in highly precise timing configurations, 
mirroring methods used to isolate low-frequency waves and dark matter variations.
""")

# --- Sidebar Controls ---
st.sidebar.header("🌌 Simulation Injection Controls")
test_preset = st.sidebar.selectbox("Select Signal Target", ["1-Year Solar Resonance", "3-6-9 Harmonic Lock", "Custom Static Field"])
noise_scale = st.sidebar.slider("Signal Background Noise (fs)", 0.1, 2.0, 0.5)

# Establish hidden constants based on her 3-6-9 harmonization rules
if test_preset == "1-Year Solar Resonance":
    true_A = 2.0e-15
    true_omega = 2 * np.pi / 1.0  # 1.0 Year Cycle
    true_phi = 0.5
elif test_preset == "3-6-9 Harmonic Lock":
    true_A = 3.6e-15
    true_omega = 2 * np.pi / 0.369  # 0.369 Fractal Harmony Tweak
    true_phi = 1.39
else:
    true_A = 0.1e-15  # Pure flat noise
    true_omega = 2 * np.pi / 5.0
    true_phi = 0.0

# --- Generate Synthetic Data Stream ---
np.random.seed(42)
years = np.linspace(0, 10, 500)  # 10 Years of continuous data
residual = (true_A / true_omega) * np.cos(true_omega * years + true_phi)
noise = np.random.normal(0, noise_scale * 1e-15, size=years.shape)
data = residual + noise

# --- The Curve-Fitting Core Function ---
def cyclic_model(t, A, omega, phi, offset):
    """
    Hope Jones' Cyclic Model Formula:
    Fits sinusoids to clock residuals to verify background field wave-states.
    """
    return (A / omega) * np.cos(omega * t + phi) + offset

# Execute Curve Fitting Optimizer
p0 = [1e-15, 2 * np.pi, 0, 0]  # Standard Initial Guesses
try:
    popt, pcov = curve_fit(cyclic_model, years, data, p0=p0, maxfev=5000)
    A_fit, omega_fit, phi_fit, offset_fit = popt
    perr = np.sqrt(np.diag(pcov))
    fit_success = True
except Exception as e:
    fit_success = False
    st.error(f"Optimizer failed to find phase-lock: {e}")

# --- Metrics and Visualization Columns ---
if fit_success:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Residue Optimization Diagnostics")
        calculated_period = 2 * np.pi / omega_fit
        
        # Display extracted properties side-by-side
        st.metric(label="Extracted Wave Amplitude (A)", value=f"{A_fit:.3e}")
        st.metric(label="Calculated Cyclic Period", value=f"{calculated_period:.3f} Years")
        st.metric(label="Phase Angle Offset (φ)", value=f"{phi_fit:.3f} Rad")
        
        # Rigorous Error-Margin Verification
        st.markdown("### 🔍 System Verification Status")
        if A_fit > perr[0] * 3 and test_preset != "Custom Static Field":
            st.success("🟢 PHASE-LOCK VERIFIED: Coherent cyclic frequency detected above background noise floors.")
        else:
            st.warning("🔴 METRIC FLOOD DROPPED: Signal is completely buried in static noise. No order found.")
            
    with col2:
        st.subheader("📈 Waveforms Alignment Matrix")
        
        fig, ax = plt.subplots(figsize=(7, 4.2))
        ax.plot(years, data * 1e15, '.', color='#8c4f2a', ms=4, label='Residual Clock Points (fs)')
        ax.plot(years, cyclic_model(years, *popt) * 1e15, color='#6b7352', linewidth=2.5, label='Jones Harmonic Fit')
        
        ax.set_title("Fractal Cosmos — Residual Optimization Timeline", fontsize=10, fontweight='bold')
        ax.set_xlabel("Observation Duration (Years)")
        ax.set_ylabel("Clock Deviation Waveform (Femtoseconds)")
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        
        st.pyplot(fig) # Feed plot directly into the UI dashboard grid

st.markdown("---")
st.caption("Ecosystem Environment — Initial parameters set to scale-free processing loops.")

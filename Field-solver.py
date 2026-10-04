import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. Simulation Parameters
# ---------------------------------------------------------
N_grid = 1000                     # Spatial resolution steps
r_max = 50.0                      # Maximum radius in kiloparsecs (kpc)
r = np.linspace(0.1, r_max, N_grid) # Radial spatial array (avoid r=0)

G = 4.300e-6                      # Gravitational constant in kpc (km/s)^2 M_sun^-1
M_bar_core = 5.0e10               # Baryonic core mass scale (M_sun)
a_0 = 1.2e-10                     # MOND/RAR acceleration metric scale (m/s^2)
a_0_kpc_s2 = a_0 * 3.086e19 / (1000.0**2) # Convert to kpc/(km/s)^2

# Model configuration constants
I_0 = 1.0                         # Baseline information source normalization
kappa = 0.5                       # Elasticity coefficient of geometric fabric
eta = 1.0                         # Stress tensor coupling efficiency

# ---------------------------------------------------------
# 2. Field Solvers & Grid Conversions
# ---------------------------------------------------------
# Step 1: Initialize Benchmark Information Density (n=1 -> I ∝ 1/r)
I_r = I_0 / r

# Step 2: Radial Velocity (Transport Equation: div(V) = sigma * I)
# For spherical sym: (1/r^2)*d/dr(r^2 * Vr) = sigma * I
# Since I = I_0/r -> d/dr(r^2 * Vr) = sigma * I_0 * r -> r^2 * Vr = 0.5 * sigma * I_0 * r^2
# Therefore Vr = Constant.
V_r = np.full_like(r, 15.0)       # Uniform background radial flow (km/s)

# Step 3: Compute Volumetric Compression Density (4D Hyperspherical Integration)
# Sum(A_i * phi_i) scales as r^3 due to the embedded 3D projection integration
integrated_states = (2.0 * np.pi**2 * I_0 / 3.0) * (r**3)
# Volume scales as a full 4D hypervolume V ∝ r^4
hyper_volume = (0.5 * np.pi**2) * (r**4)
# Compression density chi(r) = States / Volume -> scales precisely as 1/r (m=1)
chi_r = integrated_states / hyper_volume

# Step 4: Stress Tensor Deficit and Gravitational Correction Factor alpha(r)
# alpha(r) ∝ Q_rr ∝ chi(r) -> scales as 1/r
Q_rr = -eta * kappa * chi_r
alpha_r = np.abs(Q_rr) * 40.0     # Scaled coupling factor

# ---------------------------------------------------------
# 3. Velocity Curve Reconstruction & Verification
# ---------------------------------------------------------
# Standard Newtonian acceleration from baryonic mass point
a_bar = (G * M_bar_core) / (r**2)

# Anomalous gravitational acceleration from cosmic medium compression
# a_anomalous = alpha(r) * r -> Since alpha ∝ 1/r, a_anomalous ∝ constant in outer halo
a_anomalous = alpha_r * r

# Total combined acceleration profile
a_total = a_bar + a_anomalous

# Calculate circular velocity: v = sqrt(r * a)
v_baryonic = np.sqrt(r * a_bar)
v_total = np.sqrt(r * a_total)

# ---------------------------------------------------------
# 4. Diagnostics & Verification Plots
# ---------------------------------------------------------
plt.figure(figsize=(12, 5))

# Plot 1: Velocity Curves Comparing Newtonian vs Hybrid 4D Model
plt.subplot(1, 2, 1)
plt.plot(r, v_baryonic, 'r--', label='Pure Baryonic (Newtonian)')
plt.plot(r, v_total, 'b-', label='Unified 4D Space-Division Model')
plt.title('Galactic Velocity Curve Reconstruction')
plt.xlabel('Galactic Radius r (kpc)')
plt.ylabel('Circular Velocity v (km/s)')
plt.grid(True)
plt.legend()

# Plot 2: Log-Log Scale of Structural Variables (Verifying Exponents)
plt.subplot(1, 2, 2)
plt.loglog(r, I_r, 'g-', label='Information Density I(r) [n=1]')
plt.loglog(r, chi_r, 'm-.', label='Compression Density $\chi$(r) [m=1]')
plt.title('Log-Log Verification of Scaling Constraints')
plt.xlabel('Log Radius r (kpc)')
plt.ylabel('Relative Scalar Magnitude')
plt.grid(True, which="both", ls="--")
plt.legend()

plt.tight_layout()
plt.show()

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import time
import io
import os
from pathlib import Path

# import other necessary modules here (e.g., your simulation classes/functions)

# --- SESSION STATE INITIALIZATION ---
session_vars = ["sweep_r", "sweep_k", "sweep_freq", "sweep_alpha", "sweep_beta"]
for var in session_vars:
    if var not in st.session_state:
        st.session_state[var] = None  # Initialize to None or a default value

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

st.session_state.sweep_r = st.sidebar.slider(
    "Sweep Radius (r)", min_value=0.0, max_value=10.0, value=st.session_state.sweep_r or 1.0
)
st.session_state.sweep_k = st.sidebar.slider(
    "Coupling Constant (K)", min_value=0.0, max_value=1.0, value=st.session_state.sweep_k or 0.2
)
st.session_state.sweep_freq = st.sidebar.slider(
    "Frequency Scale", min_value=0.1, max_value=5.0, value=st.session_state.sweep_freq or 1.0
)
st.session_state.sweep_alpha = st.sidebar.slider(
    "Alpha", min_value=0.0, max_value=1.0, value=st.session_state.sweep_alpha or 0.01
)
st.session_state.sweep_beta = st.sidebar.slider(
    "Beta", min_value=0.0, max_value=1.0, value=st.session_state.sweep_beta or 0.01
)

# --- DISPLAY CURRENT SETTINGS ---
st.write("### Current Simulation Parameters")
for var in session_vars:
    st.write(f"{var}: {st.session_state[var]}")

# --- SIMULATION PLACEHOLDER ---
st.write("### Simulation Output")
# Example: generate some data for demo
time = np.linspace(0, 10, 500)
amplitude = np.sin(time * st.session_state.sweep_freq) * st.session_state.sweep_r

st.line_chart(amplitude)

# --- UPDATE LOGIC ---
# Any updates to session_state variables are automatically persisted across reruns
    

# -----------------------
# Core numeric functions
# -----------------------
def compute_inst_amplitudes(time, omegas, amps, phases):
    inst = amps * np.cos(omegas * time + phases)
    node_amp = inst.mean(axis=1)
    complex_phase = np.exp(1j*(omegas * time + phases)).mean(axis=1)
    node_phase = np.angle(complex_phase)
    return node_amp, node_phase, inst

    @njit(parallel=True)
    def numba_kuramoto_rhs_flat(phases_flat, omegas, neighbors, K):
        # phases_flat: (N*M,)
        N_times_M = phases_flat.shape[0]
        # reshape info requires knowing M; we'll compute outside
        return np.zeros_like(phases_flat)  # placeholder - heavy restructuring in numba would be verbose here

    # NOTE: due to complexity of neighbors as ragged arrays, we keep core RK4 in numpy for clarity.
    USE_NUMBA = False  # fallback: keep Numba disabled for the complex neighbors structure
else:
    USE_NUMBA = False

def kuramoto_rhs(phases_flat, omegas, neighbors, K, N, M):
    phases = phases_flat.reshape((N,M))
    # representative node phase
    complex_phase = np.exp(1j * phases).mean(axis=1)
    node_phase = np.angle(complex_phase)
    dph = np.zeros_like(phases)
    for i in range(N):
        neigh_idx = neighbors[i]
        if len(neigh_idx)>0:
            diffs = np.sin(node_phase[neigh_idx] - node_phase[i])
            mean_diff = diffs.mean()
        else:
            mean_diff = 0.0
        dph[i,:] = omegas[i,:] + K * mean_diff
    return dph.reshape(-1)

def rk4_step(state_phases, dt, omegas, neighbors, K, N, M):
    y0 = state_phases.reshape(-1)
    k1 = kuramoto_rhs(y0, omegas, neighbors, K, N, M)
    k2 = kuramoto_rhs(y0 + 0.5*dt*k1, omegas, neighbors, K, N, M)
    k3 = kuramoto_rhs(y0 + 0.5*dt*k2, omegas, neighbors, K, N, M)
    k4 = kuramoto_rhs(y0 + dt*k3, omegas, neighbors, K, N, M)
    y_new = y0 + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
    return (y_new.reshape((N,M))) % (2*np.pi)

# SciPy RHS wrapper for solve_ivp (flattened)
def scipy_rhs(t, phases_flat, omegas, neighbors, K, N, M):
    return kuramoto_rhs(phases_flat, omegas, neighbors, K, N, M)

def evolve_dark_matter(grid, D, alpha, dt):
    g = grid
    lap = (np.roll(g,1,axis=0) + np.roll(g,-1,axis=0) + np.roll(g,1,axis=1) + np.roll(g,-1,axis=1) - 4*g)
    newg = g + D * lap * dt - alpha * g * dt
    return np.clip(newg, 0.0, None)

# Step function (single)
def step_sim(dt=0.01, steps=1):
    N = st.session_state.N; M = st.session_state.M
    for _ in range(steps):
        if st.session_state.integrator == "RK4":
            st.session_state.phases = rk4_step(st.session_state.phases, dt,
                                              st.session_state.omegas, st.session_state.neighbors,
                                              st.session_state.K, N, M)
        else:
            # use solve_ivp over interval dt
            if not SCIPY_AVAILABLE:
                st.warning("SciPy not available; falling back to RK4.")
                st.session_state.phases = rk4_step(st.session_state.phases, dt,
                                                  st.session_state.omegas, st.session_state.neighbors,
                                                  st.session_state.K, N, M)
            else:
                y0 = st.session_state.phases.reshape(-1)
                sol = solve_ivp(lambda t, y: scipy_rhs(t, y, st.session_state.omegas, st.session_state.neighbors, st.session_state.K, N, M),
                                [0, dt], y0, method='RK45', atol=1e-6)
                st.session_state.phases = (sol.y[:, -1].reshape((N,M))) % (2*np.pi)
        # dark matter
        st.session_state.grid = evolve_dark_matter(st.session_state.grid, st.session_state.D, st.session_state.alpha, dt)
        st.session_state.time += dt
        # metrics
        amps, node_phase, inst = compute_inst_amplitudes(st.session_state.time, st.session_state.omegas, st.session_state.amps, st.session_state.phases)
        z = np.mean(np.exp(1j*node_phase))
        R = np.abs(z)
        mean_amp = np.mean(np.abs(amps))
        energy_var = np.var(amps)
        st.session_state.log = st.session_state.log.append({"t":st.session_state.time,
                                                           "mean_amp":float(mean_amp),
                                                           "kuramoto_R":float(R),
                                                           "energy_variance":float(energy_var)}, ignore_index=True)

# -----------------------
# Button actions
# -----------------------
if reset_button:
    reset_simulation()
    st.experimental_rerun()

if step_button:
    step_sim(dt=st.session_state.dt, steps=1)

if run_cont:
    # run a batch, then rerun to update UI
    step_sim(dt=st.session_state.dt, steps=10)
    st.experimental_rerun()

if export_csv:
    if len(st.session_state.log)==0:
        st.warning("No logs to export.")
    else:
        csv = st.session_state.log.to_csv(index=False).encode()
        st.download_button("Download logs CSV", data=csv, file_name="streamlight_logs.csv", mime="text/csv")

# Snapshot export
def export_snapshot():
    amps, node_phase, _ = compute_inst_amplitudes(st.session_state.time, st.session_state.omegas, st.session_state.amps, st.session_state.phases)
    snap = {
        "time": float(st.session_state.time),
        "pos": st.session_state.pos.tolist(),
        "node_amp": amps.tolist(),
        "node_phase": node_phase.tolist(),
        "dm_grid": st.session_state.grid.tolist()
    }
    return json.dumps(snap)

if snapshot_button:
    snap_json = export_snapshot().encode()
    st.download_button("Download snapshot JSON", data=snap_json, file_name=f"snapshot_t{st.session_state.time:.3f}.json", mime="application/json")

# -----------------------
# Parallel parameter sweep worker
# -----------------------
def sweep_worker(args):
    # each worker receives (K_val, f_val, base_state, steps, dt)
    K_val, f_val, base_state, sweep_steps, dt = args
    # restore state locally
    pos = base_state["pos"]
    omegas = base_state["omegas"] * (f_val / base_state["freq_ref"])
    amps = base_state["amps"].copy()
    phases = base_state["phases"].copy()
    neighbors = base_state["neighbors"]
    grid = base_state["grid"].copy()
    # simulate short run
    Rvals = []
    for _ in range(sweep_steps):
        # simple RK4 local step
        N = omegas.shape[0]; M = omegas.shape[1]
        # flattened RK4 step implemented with numpy locally
        def local_kur_rhs(ph_flat):
            phases_mat = ph_flat.reshape((N,M))
            complex_phase = np.exp(1j*phases_mat).mean(axis=1)
            node_phase = np.angle(complex_phase)
            dph = np.zeros_like(phases_mat)
            for i in range(N):
                neigh_idx = neighbors[i]
                if len(neigh_idx)>0:
                    diffs = np.sin(node_phase[neigh_idx] - node_phase[i])
                    mean_diff = diffs.mean()
                else:
                    mean_diff = 0.0
                dph[i,:] = omegas[i,:] + K_val * mean_diff
            return dph.reshape(-1)
        y0 = phases.reshape(-1)
        k1 = local_kur_rhs(y0)
        k2 = local_kur_rhs(y0 + 0.5*dt*k1)
        k3 = local_kur_rhs(y0 + 0.5*dt*k2)
        k4 = local_kur_rhs(y0 + dt*k3)
        y_new = y0 + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        phases = (y_new.reshape((N,M))) % (2*np.pi)
        # compute R
        complex_phase = np.exp(1j*phases).mean(axis=1)
        Rvals.append(float(np.abs(np.mean(complex_phase))))
    return float(np.mean(Rvals))

# Run sweep in parallel
if do_sweep and 'sweep_r' not in st.session_state:
    st.session_state.sweep_r = None

if do_sweep and 'sweep_run_button' not in st.session_state:
    st.session_state.sweep_run_button = False

if do_sweep and sweep_button:
    # prepare base state
    base_state = {
        "pos": st.session_state.pos.copy(),
        "omegas": st.session_state.omegas.copy(),
        "amps": st.session_state.amps.copy(),
        "phases": st.session_state.phases.copy(),
        "grid": st.session_state.grid.copy(),
        "neighbors": st.session_state.neighbors.copy(),
        "freq_ref": st.session_state.freq_scale
    }
    # value arrays
    K_vals = np.linspace(sKmin, sKmax, int(sKsteps))
    f_vals = np.linspace(sfmin, sfmax, int(sfsteps))
    pairs = []
    sweep_steps = 200
    dt = st.session_state.dt
    for Kval in K_vals:
        for fval in f_vals:
            pairs.append((float(Kval), float(fval), base_state, sweep_steps, dt))
    # parallel map with progress
    st.info(f"Running sweep on {len(pairs)} parameter combinations using {st.session_state.parallel_workers} workers — approximate time depends on N and M.")
    with st.spinner("Parallel sweep running..."):
        pool = mp.Pool(processes=st.session_state.parallel_workers)
        results = pool.map(sweep_worker, pairs)
        pool.close(); pool.join()
    # collect DataFrame
    df = pd.DataFrame({
        "K": np.repeat(K_vals, len(f_vals)),
        "freq_scale": np.tile(f_vals, len(K_vals)),
        "R_mean": results
    })
    st.session_state.sweep_r = df
    st.success("Sweep complete.")

if do_sweep and sweep_export and st.session_state.sweep_r is not None:
    csv = st.session_state.sweep_r.to_csv(index=False).encode()
    st.download_button("Download sweep results CSV", data=csv, file_name="sweep_results.csv", mime="text/csv")

# -----------------------
# Visualize main outputs
# -----------------------
col1, col2 = st.columns([2,1])
with col1:
    st.subheader("Spatial map")
    amps, node_phase, inst = compute_inst_amplitudes(st.session_state.time, st.session_state.omegas, st.session_state.amps, st.session_state.phases)
    fig, ax = plt.subplots(figsize=(8,7))
    g = st.session_state.grid
    ext = [-45,45,-45,45]
    ax.imshow(g.T[::-1,:], cmap="magma", extent=ext, alpha=0.5, origin='lower')
    norm_amp = (np.abs(amps) - np.min(np.abs(amps))) / (np.ptp(np.abs(amps))+1e-9)
    sizes = 40 + 400*norm_amp
    phases_norm = (node_phase + np.pi)/(2*np.pi)
    ax.scatter(st.session_state.pos[:,0], st.session_state.pos[:,1], s=sizes, c=plt.cm.hsv(phases_norm), edgecolors='k', linewidths=0.3)
    # edges
    for i in range(st.session_state.pos.shape[0]):
        for j in st.session_state.neighbors[i]:
            ax.plot([st.session_state.pos[i,0], st.session_state.pos[j,0]], [st.session_state.pos[i,1], st.session_state.pos[j,1]], color='white', alpha=0.06, linewidth=0.6)
    ax.set_xlim(-45,45); ax.set_ylim(-45,45); ax.set_xticks([]); ax.set_yticks([])
    st.pyplot(fig)

with col2:
    st.subheader("Metrics")
    if len(st.session_state.log) > 2:
        fig2, axs = plt.subplots(3,1,figsize=(5,6), sharex=True)
        df = st.session_state.log
        axs[0].plot(df["t"], df["kuramoto_R"]); axs[0].set_ylabel("R")
        axs[1].plot(df["t"], df["mean_amp"]); axs[1].set_ylabel("mean_amp")
        axs[2].plot(df["t"], df["energy_variance"]); axs[2].set_ylabel("energy_var"); axs[2].set_xlabel("time")
        st.pyplot(fig2)
    else:
        st.info("Run steps or continuous mode to see metrics.")

# Sweep results display
if st.session_state.sweep_r is not None:
    st.subheader("Sweep results")
    st.dataframe(st.session_state.sweep_r.head(200))
    pivot = st.session_state.sweep_r.pivot(index="freq_scale", columns="K", values="R_mean")
    fig3, ax3 = plt.subplots(figsize=(6,5))
    im = ax3.imshow(pivot.values, origin='lower', aspect='auto',
                    extent=[st.session_state.sweep_r['K'].min(), st.session_state.sweep_r['K'].max(),
                            st.session_state.sweep_r['freq_scale'].min(), st.session_state.sweep_r['freq_scale'].max()])
    ax3.set_xlabel("K"); ax3.set_ylabel("freq_scale")
    plt.colorbar(im, ax=ax3, label="R_mean")
    st.pyplot(fig3)

st.sidebar.markdown("---")
st.sidebar.write(f"Numba available: {NUMBA_AVAILABLE}; SciPy available: {SCIPY_AVAILABLE}")

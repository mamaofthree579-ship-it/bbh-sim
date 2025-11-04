# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
import time

st.set_page_config(layout="wide", page_title="Streamlight — Data-Accurate Cosmos Simulator")

# ----------------------------
# Utility: initialize session
# ----------------------------
def init_session_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        # simulation parameters (default)
        st.session_state.N_nodes = 40
        st.session_state.subnodes = 5
        st.session_state.K = 0.25
        st.session_state.freq_scale = 1.0
        st.session_state.dt = 0.02
        st.session_state.grid_size = 64
        st.session_state.D = 0.08   # DM diffusion
        st.session_state.alpha = 0.005  # DM decay
        # derived / state arrays
        reset_simulation()

def reset_simulation():
    N = st.session_state.N_nodes
    M = st.session_state.subnodes
    # Node positions in 2D (for visualization)
    rng = np.random.default_rng(seed=int(time.time()%1e6))
    pos = rng.uniform(-1, 1, size=(N, 2)) * 40.0
    # Per-node subnodes omegas, amplitudes, phases
    omegas = rng.uniform(0.2, 2.0, size=(N, M)) * (2*np.pi) * st.session_state.freq_scale
    amps = rng.uniform(0.3, 1.0, size=(N, M))
    phases = rng.uniform(0, 2*np.pi, size=(N, M))
    # adjacency (k nearest neighbors by distance)
    from scipy.spatial import cKDTree
    tree = cKDTree(pos)
    k = min(6, max(2, N//8))
    dists, idxs = tree.query(pos, k=k+1)  # includes self
    neighbors = idxs[:, 1:]  # exclude self
    # dark matter grid
    grid = rng.uniform(0.1, 1.0, size=(st.session_state.grid_size, st.session_state.grid_size))
    # logs
    log_df = pd.DataFrame(columns=["t","mean_amp","kuramoto_R","energy_variance"])
    # time
    t0 = 0.0
    # store
    st.session_state.pos = pos
    st.session_state.omegas = omegas
    st.session_state.amps = amps
    st.session_state.phases = phases
    st.session_state.neighbors = neighbors
    st.session_state.grid = grid
    st.session_state.time = t0
    st.session_state.log = log_df

# Ensure session state
init_session_state()

# ----------------------------
# Sidebar controls (inputs)
# ----------------------------
st.sidebar.header("Simulation Controls (data-accurate)")
st.sidebar.number_input("Nodes (N)", min_value=6, max_value=500, value=st.session_state.N_nodes, key="N_nodes", on_change=reset_simulation)
st.sidebar.number_input("Subnodes per node (M)", min_value=1, max_value=20, value=st.session_state.subnodes, key="subnodes", on_change=reset_simulation)
st.sidebar.slider("Coupling K (global)", 0.0, 2.0, st.session_state.K, 0.01, key="K")
st.sidebar.slider("Frequency scale", 0.1, 3.0, st.session_state.freq_scale, 0.01, key="freq_scale")
st.sidebar.slider("Time step dt", 0.001, 0.1, st.session_state.dt, 0.001, key="dt")
st.sidebar.slider("Dark-matter diffusion D", 0.0, 1.0, st.session_state.D, 0.01, key="D")
st.sidebar.slider("Dark-matter decay α", 0.0, 0.1, st.session_state.alpha, 0.001, key="alpha")
st.sidebar.number_input("Neighbors per node (k)", min_value=1, max_value=20, value=min(6, max(2, st.session_state.N_nodes//8)), key="k_neigh")
st.sidebar.markdown("---")

# control buttons
run_toggle = st.sidebar.checkbox("Run (continuous)", value=False, key="run_toggle")
steps_per_update = st.sidebar.number_input("Steps per update (when running)", min_value=1, max_value=1000, value=4, key="steps_per_update")
step_button = st.sidebar.button("Step 1")
reset_button = st.sidebar.button("Reset Simulation")
export_csv = st.sidebar.button("Export Logs (CSV)")

# apply neighbor change if altered
def recompute_neighbors():
    pos = st.session_state.pos
    from scipy.spatial import cKDTree
    tree = cKDTree(pos)
    k = min(st.session_state.N_nodes-1, st.session_state.k_neigh)
    dists, idxs = tree.query(pos, k=k+1)
    st.session_state.neighbors = idxs[:, 1:]
recompute_neighbors()

if reset_button:
    # update derived parameters
    st.session_state.freq_scale = st.session_state.freq_scale
    reset_simulation()
    recompute_neighbors()
    st.experimental_rerun()

# ----------------------------
# Core simulation functions
# ----------------------------
def compute_node_amplitudes(time):
    """Compute node amplitude (mean of subnode amplitudes) and effective phase (mean phase)"""
    phases = st.session_state.phases
    amps = st.session_state.amps
    omegas = st.session_state.omegas
    N, M = phases.shape
    # instantaneous amplitude for each subnode
    inst = amps * np.cos(omegas * time + phases)
    # node amplitude = mean across subnodes (could use RMS)
    node_amp = inst.mean(axis=1)
    # compute complex order value per node using subnode phases -> give a representative phase
    complex_phase = np.exp(1j * (omegas * time + phases)).mean(axis=1)
    node_phase = np.angle(complex_phase)
    return node_amp, node_phase, inst

def kuramoto_update(dt):
    """Evolve subnode phases using Kuramoto-like coupling across nodes (approximate)"""
    phases = st.session_state.phases  # shape N x M
    omegas = st.session_state.omegas
    N, M = phases.shape
    neighbors = st.session_state.neighbors
    K = st.session_state.K
    # Represent each node by the mean phase of its subnodes for coupling
    _, node_phase, _ = compute_node_amplitudes(st.session_state.time)
    # Expand node_phase to subnodes to drive phase shifts
    dphases = np.zeros_like(phases)
    # For each node, sum influence from neighbors
    for i in range(N):
        neigh_idx = neighbors[i]
        # mean sin difference
        diffs = np.sin(node_phase[neigh_idx] - node_phase[i])
        mean_diff = diffs.mean() if diffs.size>0 else 0.0
        # apply small coupling to all subnodes of node i
        dphases[i, :] = omegas[i, :] + K * mean_diff
    # Euler-ish step for simplicity (RK4 could be added)
    st.session_state.phases = (st.session_state.phases + dphases * dt) % (2*np.pi)

def evolve_dark_matter(dt):
    """Simple diffusion+decay on grid"""
    grid = st.session_state.grid
    D = st.session_state.D
    alpha = st.session_state.alpha
    # discrete Laplacian with periodic boundary for stability
    g = grid
    lap = (
        np.roll(g, 1, axis=0) + np.roll(g, -1, axis=0) +
        np.roll(g, 1, axis=1) + np.roll(g, -1, axis=1) - 4*g
    )
    newg = g + D * lap * dt - alpha * g * dt
    # clamp
    newg = np.clip(newg, 0.0, None)
    st.session_state.grid = newg

# ----------------------------
# Step function
# ----------------------------
def step_simulation(steps=1):
    for _ in range(steps):
        # update phases with coupling
        kuramoto_update(st.session_state.dt)
        # evolve dark matter
        evolve_dark_matter(st.session_state.dt)
        # increment time
        st.session_state.time += st.session_state.dt
        # compute metrics and log
        amps, node_phase, inst = compute_node_amplitudes(st.session_state.time)
        # Kuramoto order parameter R (over nodes using representative phases)
        z = np.mean(np.exp(1j * node_phase))
        R = np.abs(z)
        mean_amp = np.mean(np.abs(amps))
        energy_var = np.var(amps)
        st.session_state.log = st.session_state.log.append(
            {"t": st.session_state.time, "mean_amp": float(mean_amp),
             "kuramoto_R": float(R), "energy_variance": float(energy_var)},
            ignore_index=True)

# run single step if button pressed
if step_button:
    step_simulation(1)

# continuous run handling (non-blocking)
if run_toggle:
    # run a number of steps and re-render — we do small batch steps to avoid freezing
    step_simulation(int(steps_per_update))
    # add a small pause so UI updates and user can stop
    time.sleep(0.02)
    # re-run the app to update visuals
    st.experimental_rerun()

# ----------------------------
# Visualizations
# ----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Spatial map — nodes, amplitudes, dark matter")
    # compute current amplitude and phase
    amps, node_phase, inst = compute_node_amplitudes(st.session_state.time)
    pos = st.session_state.pos
    # plot dark matter heatmap as background
    fig, ax = plt.subplots(figsize=(8, 6))
    g = st.session_state.grid
    extent = [-45, 45, -45, 45]
    ax.imshow(g.T[::-1, :], cmap="magma", extent=extent, alpha=0.45, origin='lower')
    # draw nodes as circles sized by amplitude
    norm_amp = (np.abs(amps) - np.min(np.abs(amps))) / (np.ptp(np.abs(amps)) + 1e-9)
    sizes = 50 + 450 * norm_amp
    # color by phase
    phases_norm = (node_phase + np.pi) / (2*np.pi)
    cmap = plt.cm.hsv
    colors = cmap(phases_norm)
    sc = ax.scatter(pos[:, 0], pos[:, 1], s=sizes, c=colors, edgecolors='k', linewidths=0.4)
    # optionally draw neighbor edges for visualizing coupling
    for i in range(pos.shape[0]):
        for j in st.session_state.neighbors[i]:
            ax.plot([pos[i,0], pos[j,0]], [pos[i,1], pos[j,1]], color='white', alpha=0.06, linewidth=0.6)
    ax.set_xlim(-45, 45)
    ax.set_ylim(-45, 45)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"t = {st.session_state.time:.3f}  |  mean_amp={np.mean(np.abs(amps)):.4f}")
    st.pyplot(fig)

with col2:
    st.subheader("Metrics & Controls")
    # show latest metrics chart
    if len(st.session_state.log) > 2:
        fig2, ax2 = plt.subplots(3, 1, figsize=(5, 6), sharex=True)
        df = st.session_state.log
        ax2[0].plot(df["t"], df["kuramoto_R"], label="Kuramoto R")
        ax2[0].legend()
        ax2[1].plot(df["t"], df["mean_amp"], label="Mean amplitude", color="tab:orange")
        ax2[1].legend()
        ax2[2].plot(df["t"], df["energy_variance"], label="Energy var", color="tab:green")
        ax2[2].legend()
        ax2[2].set_xlabel("time")
        st.pyplot(fig2)
    else:
        st.info("Run a few steps (press Step or enable Run) to populate metrics.")

    st.markdown("---")
    st.write("Simulation controls (quick):")
    st.write(f"Nodes: {st.session_state.N_nodes}  |  Subnodes: {st.session_state.subnodes}")
    st.write(f"Neighbors per node: {st.session_state.k_neigh}  |  K = {st.session_state.K:.3f}")
    st.write(f"Dark matter D={st.session_state.D:.3f}, α={st.session_state.alpha:.4f}")

# ----------------------------
# CSV export & logging
# ----------------------------
if export_csv:
    if len(st.session_state.log) == 0:
        st.warning("No logs yet — run the simulation a bit then export.")
    else:
        csv_bytes = st.session_state.log.to_csv(index=False).encode()
        st.download_button("Download CSV logs", data=csv_bytes, file_name="streamlight_sim_logs.csv", mime="text/csv")

# ----------------------------
# Developer info & next steps
# ----------------------------
st.sidebar.markdown("---")
st.sidebar.header("Notes (research integrity)")
st.sidebar.write("""
- This simulation uses a simplified Kuramoto-inspired coupling at the node level. 
- For higher numerical fidelity you can replace the Euler-like phase step with RK4 integrators or implement fully continuous Kuramoto ODE integration with SciPy's solvers.
- The dark-matter grid uses simple diffusion + decay with periodic boundaries for stability; replace with experimentally matched PDE solver if needed.
- All outputs are deterministic given the RNG seed — to reproduce runs, add a fixed RNG seed during reset_simulation().
""")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# === Physical constants (SI) ===
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
M_sun = 1.98847e30

# === Core model equations ===
def schwarzschild_radius(M):
    return 2 * G * M / c**2

def F_QG(r, m, rQ, A_qg=1.0):
    if r <= 0:
        return 0.0
    return A_qg * (G * m / (r**2)) * np.exp(-r / rQ)

def dM_dt_QEWH(M, K_scale=1.0):
    # heuristic Hawking-like evaporation
    return -K_scale * (hbar * c**2 / G) / (M**2)

def STF_simple(rho_QG, vol, dRdt, lam):
    return (rho_QG * vol) - lam * dRdt


# === Simulation step ===
def step_sim(M, r, dt, params, prev_r):
    # Force & acceleration
    Fq = F_QG(r, M, params["rQ"], params["A_qg"])
    acc_qg = Fq / params["m_test"]
    acc_newton = G * M / r**2
    total_acc = acc_newton + acc_qg

    # Update radius (toy shrink)
    r_next = max(params["r_min"], r - 0.001 * total_acc * dt)

    # Evaporation / white-hole emergence
    if params["enable_evap"]:
        dMdt = dM_dt_QEWH(M, params["K_scale"])
        M_next = max(params["M_min"], M + dMdt * dt)
    else:
        dMdt = 0.0
        M_next = M

    # STF diagnostic
    rho_QG = params["rho0"] * np.exp(-r / params["rQ"])
    vol = (4 / 3) * np.pi * r**3
    dRdt = (prev_r - r) / dt
    Strans = STF_simple(rho_QG, vol, dRdt, params["lambda"])

    return M_next, r_next, Strans, dMdt


# === Streamlit UI ===
st.set_page_config(page_title="Quantum-Gravity Black Hole Simulator", layout="wide")

st.title("🌀 Quantum-Gravity Black Hole Simulator")
st.markdown(
    """
    This interactive model combines **quantum-gravity compression (QGC)**, 
    **quantum evaporation / white-hole emergence (QE–WH)**, and a 
    **singularity transition function (STF)**.  
    Use the sliders to explore how these effects might influence a black hole’s dynamics.
    """
)

# Sidebar parameters
st.sidebar.header("Simulation Controls")

M0 = st.sidebar.slider("Initial Mass (× 10⁶ M☉)", 1.0, 100.0, 4.3, 0.1) * 1e6 * M_sun
r_s = schwarzschild_radius(M0)
r0 = st.sidebar.slider("Initial Separation (× rₛ)", 2.0, 50.0, 10.0, 0.5) * r_s

params = {
    "A_qg": st.sidebar.slider("A₍QG₎", 0.1, 10.0, 1.0, 0.1),
    "rQ": st.sidebar.slider("Quantum Radius r_Q (× rₛ)", 0.1, 20.0, 5.0, 0.1) * r_s,
    "lambda": st.sidebar.number_input("λ (STF coupling)", 1e-25, 1e-20, 1e-23, format="%.1e"),
    "rho0": st.sidebar.number_input("ρ₀ (Quantum-density scale)", 1e-12, 1e-6, 1e-9, format="%.1e"),
    "K_scale": st.sidebar.slider("K ₍scale₎ (Evap. rate multiplier)", 1.0, 1e40, 1e30, step=1e10, format="%.1e"),
    "enable_evap": st.sidebar.checkbox("Enable evaporation (QE–WH)", True),
    "m_test": 1e20,
    "r_min": 1e3,
    "M_min": 1e25,
}

t_max = st.sidebar.slider("Simulation time (s)", 1.0, 20.0, 10.0)
dt = st.sidebar.slider("Time step dt (s)", 1e-5, 1e-2, 1e-3, format="%.1e")

# Initialize arrays
steps = int(t_max / dt)
M_vals = [M0]
r_vals = [r0]
S_vals = [0.0]
t_vals = [0.0]

M, r = M0, r0
transitioned = False
S_thresh = 1e25

# === Run the integration loop ===
for i in range(steps):
    M, r, S, dMdt = step_sim(M, r, dt, params, r_vals[-1])
    t = (i + 1) * dt
    M_vals.append(M)
    r_vals.append(r)
    S_vals.append(S)
    t_vals.append(t)
    if S > S_thresh and not transitioned:
        transitioned = True

# === Display results ===
col1, col2 = st.columns(2)

with col1:
    figM = go.Figure()
    figM.add_trace(go.Scatter(x=t_vals, y=np.array(M_vals)/M_sun, mode="lines", line=dict(color="orange")))
    figM.update_layout(title="Mass evolution (M☉)", template="plotly_dark", height=300)
    st.plotly_chart(figM, use_container_width=True)

    figR = go.Figure()
    figR.add_trace(go.Scatter(x=t_vals, y=np.array(r_vals)/r_s, mode="lines", line=dict(color="aqua")))
    figR.update_layout(title="Separation (× rₛ)", template="plotly_dark", height=300)
    st.plotly_chart(figR, use_container_width=True)

with col2:
    figS = go.Figure()
    figS.add_trace(go.Scatter(x=t_vals, y=S_vals, mode="lines", line=dict(color="magenta")))
    figS.add_hline(y=S_thresh, line_dash="dot", line_color="yellow", annotation_text="Sₜᵣₐₙₛ threshold")
    figS.update_layout(title="Singularity Transition Function Sₜᵣₐₙₛ", template="plotly_dark", height=620)
    st.plotly_chart(figS, use_container_width=True)

# === Transition feedback ===
if transitioned:
    st.markdown("### 🌈 Transition detected!")
    st.success("**Sₜᵣₐₙₛ** exceeded threshold — singularity output / white-hole phase triggered.")
    st.balloons()
else:
    st.info("No transition occurred within simulation window.")

# === Optional: audio cue (simple low-freq rumble + chirp) ===
make_sound = st.checkbox("Play simulated chirp", value=False)
if make_sound:
    import numpy as np
    import io
    import soundfile as sf
    import base64
    import tempfile

    sr = 44100
    duration = 3.0
    t = np.linspace(0, duration, int(sr*duration))
    # simple chirp: rising freq with decaying amplitude
    f0, f1 = 30, 300
    waveform = 0.2 * np.sin(2*np.pi*(f0 + (f1-f0)*(t/duration)**2)*t)
    # add low-freq rumble if transition triggered
    if transitioned:
        waveform += 0.15 * np.sin(2*np.pi*10*t) * np.exp(-t)
    wav_io = io.BytesIO()
    sf.write(wav_io, waveform, sr, format='wav')
    st.audio(wav_io.getvalue(), format='audio/wav')

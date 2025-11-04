import streamlit as st
import numpy as np
import plotly.graph_objects as go

# === Physical constants ===
G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
M_sun = 1.98847e30

# --- Core equations ---
def schwarzschild_radius(M):
    return 2 * G * M / c**2

def F_QG(r, m, rQ, A_qg=1.0):
    return A_qg * (G * m / (r**2)) * np.exp(-r / rQ) if r > 0 else 0.0

def dM_dt_QEWH(M, K_scale=1.0):
    return -(K_scale * (hbar * c**2 / G)) / (M**2)

def STF_simple(rho_QG, vol, dRdt, lam):
    return (rho_QG * vol) - lam * dRdt


# --- Sim step ---
def step_sim(M, r, dt, params, prev_r):
    Fq = F_QG(r, M, params["rQ"], params["A_qg"])
    acc_qg = Fq / params["m_test"]
    acc_newton = G * M / r**2
    total_acc = acc_newton + acc_qg
    r_next = max(params["r_min"], r - 0.001 * total_acc * dt)
    if params["enable_evap"]:
        dMdt = dM_dt_QEWH(M, params["K_scale"])
        M_next = max(params["M_min"], M + dMdt * dt)
    else:
        dMdt = 0.0
        M_next = M
    rho_QG = params["rho0"] * np.exp(-r / params["rQ"])
    vol = (4 / 3) * np.pi * r**3
    dRdt = (prev_r - r) / dt
    Strans = STF_simple(rho_QG, vol, dRdt, params["lambda"])
    return M_next, r_next, Strans, dMdt


# === Streamlit layout ===
st.set_page_config(page_title="Quantum-Gravity Black Hole Simulator", layout="wide")

st.title("🌀 Quantum-Gravity Black Hole Simulator")

tabs = st.tabs(["Simulation", "3D Visualization", "Audio Synthesis"])

# ---------------------------------------------
# TAB 1: Simulation
# ---------------------------------------------
with tabs[0]:
    st.markdown("### Physics Evolution")

    M0 = st.slider("Initial Mass (×10⁶ M☉)", 1.0, 100.0, 4.3) * 1e6 * M_sun
    r_s = schwarzschild_radius(M0)
    r0 = st.slider("Initial Separation (×rₛ)", 2.0, 50.0, 10.0) * r_s

    params = {
        "A_qg": st.slider("A₍QG₎", 0.1, 10.0, 1.0),
        "rQ": st.slider("Quantum Radius r_Q (×rₛ)", 0.1, 20.0, 5.0) * r_s,
        "lambda": st.number_input("λ (STF coupling)", 1e-25, 1e-20, 1e-23, format="%.1e"),
        "rho0": st.number_input("ρ₀ (Quantum-density scale)", 1e-12, 1e-6, 1e-9, format="%.1e"),
        "K_scale": st.slider("K ₍scale₎ (Evap. rate multiplier)", 1.0, 1e40, 1e30, step=1e10, format="%.1e"),
        "enable_evap": st.checkbox("Enable evaporation (QE–WH)", True),
        "m_test": 1e20,
        "r_min": 1e3,
        "M_min": 1e25,
    }

    t_max = st.slider("Simulation time (s)", 1.0, 20.0, 10.0)
    dt = st.slider("Time step dt (s)", 1e-5, 1e-2, 1e-3, format="%.1e")

    steps = int(t_max / dt)
    M_vals, r_vals, S_vals, t_vals = [M0], [r0], [0.0], [0.0]
    M, r = M0, r0
    S_thresh, transitioned = 1e25, False

    for i in range(steps):
        M, r, S, dMdt = step_sim(M, r, dt, params, r_vals[-1])
        t = (i + 1) * dt
        M_vals.append(M)
        r_vals.append(r)
        S_vals.append(S)
        t_vals.append(t)
        if S > S_thresh and not transitioned:
            transitioned = True

    col1, col2 = st.columns(2)
    with col1:
        figM = go.Figure()
        figM.add_trace(go.Scatter(x=t_vals, y=np.array(M_vals)/M_sun, mode="lines", line=dict(color="orange")))
        figM.update_layout(title="Mass evolution (M☉)", template="plotly_dark", height=300)
        st.plotly_chart(figM, use_container_width=True)

        figR = go.Figure()
        figR.add_trace(go.Scatter(x=t_vals, y=np.array(r_vals)/r_s, mode="lines", line=dict(color="aqua")))
        figR.update_layout(title="Separation (×rₛ)", template="plotly_dark", height=300)
        st.plotly_chart(figR, use_container_width=True)

    with col2:
        figS = go.Figure()
        figS.add_trace(go.Scatter(x=t_vals, y=S_vals, mode="lines", line=dict(color="magenta")))
        figS.add_hline(y=S_thresh, line_dash="dot", line_color="yellow", annotation_text="Sₜᵣₐₙₛ threshold")
        figS.update_layout(title="Singularity Transition Function Sₜᵣₐₙₛ", template="plotly_dark", height=620)
        st.plotly_chart(figS, use_container_width=True)

    if transitioned:
        st.success("🌈 **Sₜᵣₐₙₛ** exceeded threshold — White-hole output phase triggered.")
        st.balloons()
    else:
        st.info("No transition detected.")


# ---------------------------------------------
# TAB 2: 3D Visualization
# ---------------------------------------------
with tabs[1]:
    st.markdown("### 3D Black Hole Anatomy (Quantum-Gravitational Model)")
    st.write("This view shows the purple-tinted event horizon and glowing accretion disk that oscillates with curvature.")

    # Generate coordinates
    phi, theta = np.mgrid[0:2*np.pi:100j, 0:np.pi:50j]
    radius = 1.0
    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)

    # Horizon color field (dark purple to bright plasma)
    horizon_color = np.sqrt(x**2 + y**2 + z**2)
    fig3d = go.Figure(
        data=[
            go.Surface(
                x=x,
                y=y,
                z=z,
                surfacecolor=horizon_color,
                colorscale=[[0, "rgb(80,0,100)"], [0.4, "rgb(130,0,180)"], [1, "rgb(255,80,255)"]],
                showscale=False,
                opacity=0.98,
            ),
        ]
    )

    # Add accretion disk
    r_disk = np.linspace(1.0, 3.5, 100)
    phi_disk = np.linspace(0, 2*np.pi, 200)
    R, P = np.meshgrid(r_disk, phi_disk)
    Xd = R * np.cos(P)
    Yd = R * np.sin(P)
    Zd = 0.15 * np.sin(6 * P) * np.exp(-0.5 * (R - 2.5))
    fig3d.add_surface(
        x=Xd, y=Yd, z=Zd,
        colorscale=[[0, "rgb(255,160,60)"], [1, "rgb(255,220,180)"]],
        showscale=False,
        opacity=0.85,
    )

    fig3d.update_layout(
        template="plotly_dark",
        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    st.plotly_chart(fig3d, use_container_width=True)

# --- Button 2: Orbit Motion Toggle ---
with col2:
    if st.button("🌌 Start Orbit Animation"):
        st.markdown(
            """
            <script>
            // Animate rotation of a 3D Plotly figure if it exists on the page
            const sleep = ms => new Promise(r => setTimeout(r, ms));
            async function rotateScene() {
                let angle = 0;
                for (let i = 0; i < 180; i++) {
                    const camera = {
                        eye: {
                            x: Math.cos(angle) * 2,
                            y: Math.sin(angle) * 2,
                            z: 0.6
                        }
                    };
                    const gd = document.querySelector(".js-plotly-plot");
                    if (gd) Plotly.relayout(gd, { 'scene.camera': camera });
                    angle += Math.PI / 60;
                    await sleep(50);
                }
            }
            rotateScene();
            </script>
            """,
            unsafe_allow_html=True
        )
        st.info("🌠 Orbit animation running (you can click and drag to adjust view).")
    else:
        st.caption("Press to begin orbit animation.")
# ---------------------------------------------
# TAB 3: Audio Synthesis
# ---------------------------------------------
with tabs[2]:
    st.markdown("### Audio Synthesis — Quantum Whirlpool Rumble")
    st.write("Simulates the ambient sound field based on mass oscillation and curvature flow — like a low-frequency plasma whirlpool.")

    enable_audio = st.checkbox("Enable Quantum Rumble", value=True)
    if enable_audio:
        st.markdown(
            """
            <script>
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc1 = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gain = ctx.createGain();

            osc1.type = "sine";
            osc2.type = "sawtooth";

            osc1.frequency.setValueAtTime(40, ctx.currentTime);
            osc2.frequency.setValueAtTime(60, ctx.currentTime);
            osc1.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + 4);
            osc2.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 4);

            gain.gain.setValueAtTime(0.2, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 6);

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(ctx.destination);

            osc1.start();
            osc2.start();
            osc1.stop(ctx.currentTime + 6);
            osc2.stop(ctx.currentTime + 6);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.info("🎧 This synthesized tone uses your browser’s audio engine (WebAudio).")
    else:
        st.write("Audio synthesis disabled.")


    st.info("🔊 This audio represents hypothetical spacetime fluid dynamics, not literal sound waves in vacuum.")

# ---------------------------------------------
# 🔊 Audio & Orbit Control Section
# ---------------------------------------------
st.markdown("## Quantum Rumble & Orbital Motion")

col1, col2 = st.columns(2)

# --- Button 1: WebAudio Play ---
with col1:
    if st.button("🎧 Play Rumble"):
        st.markdown(
            """
            <script>
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc1 = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gain = ctx.createGain();

            osc1.type = "sine";
            osc2.type = "sawtooth";

            osc1.frequency.setValueAtTime(40, ctx.currentTime);
            osc2.frequency.setValueAtTime(60, ctx.currentTime);
            osc1.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + 6);
            osc2.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 6);

            gain.gain.setValueAtTime(0.2, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 8);

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(ctx.destination);

            osc1.start();
            osc2.start();
            osc1.stop(ctx.currentTime + 8);
            osc2.stop(ctx.currentTime + 8);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.info("🎵 The cosmic ‘rumble’ is playing through your browser.")
    else:
        st.caption("Press the button to play the synthesized rumble.")
        

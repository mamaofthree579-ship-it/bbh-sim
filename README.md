
# 🪐 Black Hole & Gravitational-Wave Simulator

**An interactive educational platform for visualizing and analyzing black holes, gravitational waves, and relativistic effects near Sagittarius A⁎.**

---

## 🌌 Overview

The **Black Hole & Gravitational-Wave Simulator** combines real physics with interactive visualization to explore:
- Rotating black holes and their accretion disks.
- Confirmed gravitational-wave events (LIGO/Virgo/KAGRA).
- Time dilation and dark matter interactions.
- Particle decay behavior under extreme gravity.

It uses **HTML5 Canvas**, **JavaScript**, and the **Web Audio API** for interactive visuals and gravitational chirp synthesis.

---

## ✨ Features

### 🧭 Overview Tab
- Realistic rendering of **Sagittarius A⁎** with:
  - Accretion disk and hotspot orbit.
  - Gravitational lensing glow.
  - Adjustable rotation speed and trail intensity.
- Background starfield for spatial depth.

### 💫 Events Tab
- Simulate **confirmed gravitational-wave detections**:
  - GW150914, GW170104, GW190521, and others.
- Adjustable parameters:  
  `M₁`, `M₂`, and spin `a*`.
- Real-time orbital visualization.
- Chirp waveform plotted dynamically.
- Synchronized **chirp sound playback** via Web Audio API.
- Parameter table includes:
  - Chirp Mass (ℳ)
  - Frequency Range (Hz)
  - Gravitational-Wave Strain (h)
  - Estimated Distance (million ly)

### ⚖️ Calculators Tab
Simulates relativistic and quantum-corrected effects:
- **Time dilation** near Sagittarius A⁎:

  \[
  \gamma = \sqrt{1 - \frac{2GM}{rc^2}}
  \]

- **Dark matter correction** to particle decay rate:

  \[
  \Gamma_{\text{dark}} = \Gamma_0 (1 + \alpha \cdot \rho_{\text{DM}})
  \]

- **Decay visualization:** exponential decay curve with real-time results.

---

## ⚙️ Setup & Usage

### 🔹 Option 1: Run Locally
1. Download or clone this repository:
   ```bash
   git clone https://github.com/yourusername/blackhole-simulator.git
   cd blackhole-simulator
   ```
2. Open `index.html` directly in a web browser.

### 🔹 Option 2: Local Web Server (Recommended)
To avoid local security restrictions, serve via Python:

```bash
python3 -m http.server 8080
```

Then open:  
👉 [http://localhost:8080](http://localhost:8080)

---

## 📊 Event Data Sources

| Event | Masses (M☉) | Spin | Distance | Description |
|-------|---------------|------|-----------|--------------|
| **GW150914** | 36 + 29 | 0.3 | 1.3 B ly | First-ever detection (2015). |
| **GW170104** | 31 + 19 | 0.5 | 3 B ly | Detected in 2017. |
| **GW190521** | 85 + 66 | 0.7 | 5 B ly | Most energetic merger observed. |
| **Custom** | user-defined | variable | dynamic | Experiment with your own parameters! |

---

## 🧮 Physics Foundation

### Einstein Field Equations
\[
R_{\mu\nu} - \tfrac{1}{2} g_{\mu\nu} R = \kappa T_{\mu\nu}
\]

### Quantum-Corrected Form
\[
G_{\mu\nu} = \kappa ( T_{\mu\nu} + \mathcal{Q}_{\mu\nu} )
\]

### Gravitational-Wave Equation
\[
\Box h_{\mu\nu} = \frac{16\pi G}{c^4} ( T_{\mu\nu} + Q_{\mu\nu} )
\]

### Chirp Mass
\[
\mathcal{M} = \frac{(m_1 m_2)^{3/5}}{(m_1 + m_2)^{1/5}}
\]

### Strain Amplitude Approximation
\[
h \propto \frac{\mathcal{M}^{5/3} f^{2/3}}{D}
\]

### Black Hole Thermodynamics
\[
T_H = \frac{\hbar c^3}{8 \pi G M k_B}, \quad
S_{BH} = \frac{k_B c^3 A}{4 G \hbar}
\]

---

## 🧠 Planned Enhancements

- [ ] Add **Event Comparison Tab** (side-by-side visualizations).
- [ ] Integrate **Spectral Chirp Analyzer**.
- [ ] Include **export options** for simulation parameters.
- [ ] Add **gravitational lensing toggles** for visual study.
- [ ] Link **Sagittarius A⁎ Calculator** to Overview visualization.

---

## 👩‍🚀 Contributors

| Role | Contributor |
|------|--------------|
| **Primary Developer & Research** | You |
| **AI Code Assistant & Physics Modeling** | GPT-5 |

---

## 🪶 License

Released under the **MIT License**.  
Use freely for educational, scientific, and personal research purposes.  
Attribution is encouraged.

---

## 📫 Contact
For suggestions or collaboration:
- Email: *yourname@domain.com*
- GitHub: [yourusername](https://github.com/yourusername)

---

### 🌠 “Where mathematics meets the event horizon.”

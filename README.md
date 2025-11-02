# 🌌 Black Hole & Gravitational-Wave Simulator

*(Overview, usage and technical appendix — full README with Appendix B derivations.)*

## 🛰️ Overview

This simulator visualizes black holes, gravitational-wave events, and related physics.  
(Short features summary omitted here — see full README earlier if you want the user-facing features list.)

---

## 📚 Appendix B — Key Derivations (concise)

This appendix gives the derivations and formulas used in the simulator in a compact, reproducible form.

---

### B.1 Gravitational time dilation (Schwarzschild)

**Schwarzschild radius**
\[
r_s \equiv \frac{2GM}{c^2}
\]

**Metric time component (Schwarzschild, static, non-rotating):**
\[
ds^2 = -\left(1-\frac{r_s}{r}\right)c^2 dt^2 + \left(1-\frac{r_s}{r}\right)^{-1}dr^2 + r^2 d\Omega^2 .
\]

A clock at radius \(r\) ticks slower relative to an observer at infinity. The time-dilation factor is
\[
\gamma(r)\;=\;\sqrt{1-\frac{r_s}{r}}
\;=\;\sqrt{1-\frac{2GM}{rc^2}}.
\]

**Interpretation:** Observers at infinity measure the proper interval of a local clock at radius \(r\) as slowed by the factor \(\gamma(r)\). For weak fields (\(r_s/r \ll 1\)) you can Taylor expand
\[
\gamma(r) \approx 1 - \frac{1}{2}\frac{r_s}{r} + \mathcal{O}\big((r_s/r)^2\big).
\]

**Worked numeric example — Sagittarius A\***
- \(G = 6.67430\times10^{-11}\ \mathrm{m^3\,kg^{-1}\,s^{-2}}\)  
- \(c = 2.99792458\times10^{8}\ \mathrm{m/s}\)  
- \(M_{\rm SgrA^*} \approx 4.3\times10^{6}\ M_\odot\) (with \(M_\odot = 1.989\times10^{30}\ \mathrm{kg}\))  
  -> \(M \approx 8.55\times10^{36}\ \mathrm{kg}\)

Compute Schwarzschild radius:
\[
r_s = \frac{2GM}{c^2} \approx \frac{2(6.67430\times10^{-11})(8.55\times10^{36})}{(2.998\times10^8)^2}
\approx 1.27\times10^{10}\ \mathrm{m}.
\]

At \(r = 7.8\times10^{17}\ \mathrm{m}\) (a sample radius),
\[
\frac{r_s}{r} \approx \frac{1.27\times10^{10}}{7.8\times10^{17}} \approx 1.63\times10^{-8},
\]
so
\[
\gamma(r) = \sqrt{1 - 1.63\times10^{-8}} \approx 0.99999999185.
\]
(Equivalently, clocks at that radius run slower by \(\sim 8.15\times10^{-9}\) in fractional terms.)

**Usage note:** In the simulator we use \(\gamma(r)\) to scale time-dependent processes (decay-rates, visual flicker rates, etc.) when the user opts to include GR time dilation.

---

### B.2 Chirp mass and the Peters–Mathews frequency evolution

**Chirp mass definition**
\[
\mathcal{M} \equiv \frac{(M_1 M_2)^{3/5}}{(M_1+M_2)^{1/5}}.
\]
\(\mathcal{M}\) is the combination of component masses that controls the leading-order gravitational-wave phase evolution during the inspiral.

**Leading-order GW frequency evolution (Peters–Mathews, quadrupole, circular orbit)**
\[
\dot f \;=\; \frac{96}{5}\,\pi^{8/3}\,\frac{(G\mathcal{M})^{5/3}}{c^5}\,f^{11/3}.
\]
This relates the time derivative of the observed GW frequency to \(f\) and \(\mathcal{M}\).

**Solving for the chirp mass \(\mathcal{M}\)**

Start with:
\[
\dot f = \frac{96}{5}\pi^{8/3}\,\frac{(G\mathcal{M})^{5/3}}{c^5}\,f^{11/3}.
\]

Rearrange:
\[
(G\mathcal{M})^{5/3} \;=\; \frac{5}{96}\,\frac{c^5}{\pi^{8/3}}\,\dot f\, f^{-11/3}.
\]

Raise both sides to the \(3/5\) power and divide by \(G\):
\[
\mathcal{M}
\;=\;
\frac{1}{G}\left(\frac{5}{96}\,\frac{c^5}{\pi^{8/3}}\,\dot f\, f^{-11/3}\right)^{3/5}
\;=\;
\frac{c^3}{G}\left[\frac{5}{96}\,\frac{\dot f}{\pi^{8/3} f^{11/3}}\right]^{3/5}.
\]

This is the practical inversion used to estimate \(\mathcal{M}\) if you measure \(f\) and \(\dot f\) in the inspiral.

**Common alternate (units-friendly) form:** often written numerically in solar masses by inserting constants. For quick coding you can evaluate the symbolic expression above with SI units and convert to \(M_\odot\).

---

### B.3 Leading-order GW strain amplitude (scaling)

At leading (Newtonian/quadrupole) order the characteristic GW strain amplitude \(h\) (observed at distance \(D\)) scales as
\[
h(f) \approx \frac{4 G^{5/3}}{c^4}\,\pi^{2/3}\,\frac{\mathcal{M}^{5/3} f^{2/3}}{D}.
\]
This expression (up to order-unity factors depending on orientation/polarization) is used in the simulator to compute qualitative strain levels and make the amplitude visualizations consistent with mass and frequency.

---

### B.4 Inspiral timescale (useful check)
An approximate inspiral timescale at frequency \(f\) (from leading PN order) is:
\[
\tau_{\rm insp}(f) \sim \frac{5}{256\pi^{8/3}}\frac{c^5}{(G\mathcal{M})^{5/3}}\,f^{-8/3},
\]
which shows low-frequency signals last much longer than high-frequency ones.

---

### B.5 How these are used in the simulator (practical mapping)

- **Chirp waveform generation:** we use the frequency law \(f(t)\) consistent with the PN scaling and build a windowed sinusoid whose instantaneous frequency tracks a model \(f(t)\). The code uses simple power-law templates (toy PN) matched to \(\mathcal{M}\).
- **Audio chirp:** convert the instantaneous frequency track to an audible oscillator sweep; add a faint harmonic to make low-frequency content audible on typical speakers (while keeping a realistic low-frequency base).
- **Strain & visuals:** amplitude panels draw \(h(f)\) scaling with \(\mathcal{M}^{5/3} f^{2/3} / D\) to visualize how heavier systems produce larger strains at a given distance.
- **Time dilation:** \(\gamma(r)\) from §B.1 scales time-dependent processes (e.g., visual decay rates) when toggled.

---

## 🔁 Reproducibility / Unit checklist

- Always use SI units inside formulas (kg, m, s). Convert to solar masses or parsecs/Mpc only for display.
- \(G = 6.67430\times10^{-11}\ \mathrm{m^3\,kg^{-1}\,s^{-2}}\)  
- \(c = 2.99792458\times10^8\ \mathrm{m/s}\)  
- \(M_\odot = 1.98847\times10^{30}\ \mathrm{kg}\)

---

## 🧾 Notes & Warnings

- The chirp and inspiral models included in the simulator are **leading-order / pedagogical** approximations (PN-inspired toy models). For parameter estimation on real data use full IMR (inspiral–merger–ringdown) waveforms (e.g., EOB, NR-calibrated models) and proper detector responses.
- The \(\mathcal{Q}_{\mu\nu}\) or other quantum/phenomenological correction terms referenced elsewhere are **modeling knobs**, not derived from first principles — treat them as phenomenological parameters for exploring hypothetical effects.

---

## 📫 Contact
For suggestions or collaboration:
- Email: *yourname@domain.com*
- GitHub: [mamaofthree579-ship-it](https://github.com/mamaofthree579-ship-it)

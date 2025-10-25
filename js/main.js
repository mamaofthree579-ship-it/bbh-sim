let loadedEvents = [];
let currentEvent = null;

// Load known gravitational events
fetch("data/events.json")
  .then(res => res.json())
  .then(data => {
    loadedEvents = data.events;
    const select = document.getElementById("eventSelect");
    data.events.forEach(ev => {
      const opt = document.createElement("option");
      opt.value = ev.id;
      opt.textContent = `${ev.name} (${ev.date})`;
      select.appendChild(opt);
    });

    document.getElementById("loadEvent").onclick = () => {
      const id = select.value;
      currentEvent = data.events.find(e => e.id === id);
      if (currentEvent) {
        showFacts(currentEvent);
        plotWaveform(currentEvent);
      }
    };
  });

// Toggle custom form
document.getElementById("simulateCustom").onclick = () => {
  const form = document.getElementById("customForm");
  form.classList.toggle("hidden");
};

// Slider updates
["mass1", "mass2", "duration"].forEach(id => {
  const slider = document.getElementById(id);
  const label = document.getElementById(id === "mass1" ? "m1Val" : id === "mass2" ? "m2Val" : "durVal");
  slider.oninput = () => (label.textContent = slider.value);
});

// Run custom simulation
document.getElementById("runSim").onclick = () => {
  const m1 = parseFloat(document.getElementById("mass1").value);
  const m2 = parseFloat(document.getElementById("mass2").value);
  const dur = parseFloat(document.getElementById("duration").value);

  const chirpMass = Math.pow((m1 * m2) ** (3/5) / Math.pow(m1 + m2, 1/5), 1);
  const t = Array.from({length: 1000}, (_, i) => (i / 1000) * dur * 10);
  const freq = 0.05 * chirpMass ** 0.3;
  const hPlus = t.map(tt => Math.sin(freq * tt) * Math.exp(-tt / (dur * 5)));

  plotCustomWaveform(t, hPlus, {m1, m2, dur});

  if (currentEvent) {
    overlayComparison(t, hPlus, currentEvent);
  }
};

// Save custom simulation parameters
document.getElementById("saveSim").onclick = () => {
  const m1 = parseFloat(document.getElementById("mass1").value);
  const m2 = parseFloat(document.getElementById("mass2").value);
  const dur = parseFloat(document.getElementById("duration").value);
  const blob = new Blob([JSON.stringify({m1, m2, dur}, null, 2)], {type: "application/json"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "custom_simulation.json";
  link.click();
};

// Show event facts
function showFacts(event) {
  const facts = document.getElementById("quickFacts");
  document.getElementById("eventName").textContent = `🌀 ${event.name}`;
  document.getElementById("eventDate").textContent = `📅 Date: ${event.date}`;
  document.getElementById("eventDesc").textContent = `📖 ${event.desc}`;
  facts.classList.remove("hidden");
}

// Plot real event
function plotWaveform(event) {
  const t = Array.from({length: 1000}, (_, i) => i / 50);
  const h = t.map(tt => Math.sin(tt * event.freq * 0.02) * Math.exp(-tt / 40));

  Plotly.newPlot("waveformPlot", [{
    x: t,
    y: h,
    type: "scatter",
    mode: "lines",
    line: {color: "#00e5ff"},
    name: event.name
  }], {
    title: `${event.name} — Gravitational Strain`,
    xaxis: {title: "Time [s]"},
    yaxis: {title: "Strain h(t)"}
  });

  Plotly.newPlot("freqPlot", [{
    x: [event.freq],
    y: [event.amplitude],
    mode: "markers",
    marker: {size: 12, color: "#ff4081"},
    name: "Frequency peak"
  }], {
    title: "Frequency Spectrum",
    xaxis: {title: "Frequency [Hz]"},
    yaxis: {title: "Amplitude"}
  });
}

// Plot simulated waveform
function plotCustomWaveform(t, hPlus, params) {
  Plotly.newPlot("waveformPlot", [
    {x: t, y: hPlus, mode: "lines", name: "h₊", line: {color: "#00e5ff"}}
  ], {
    title: `Simulated BBH: m₁=${params.m1} M☉, m₂=${params.m2} M☉`,
    xaxis: {title: "Time [M]"},
    yaxis: {title: "Strain"}
  });

  const f = 0.05 * Math.pow((params.m1 * params.m2) / (params.m1 + params.m2), 0.3);
  Plotly.newPlot("freqPlot", [{
    x: [f],
    y: [Math.max(...hPlus)],
    mode: "markers",
    marker: {size: 10, color: "#ffc107"},
    name: "Peak frequency"
  }], {
    title: "Approximate Frequency Estimate",
    xaxis: {title: "Frequency [Hz]"},
    yaxis: {title: "Amplitude"}
  });
}

// Overlay comparison between simulated and real event
function overlayComparison(t, simH, event) {
  const realT = Array.from({length: 1000}, (_, i) => i / 50);
  const realH = realT.map(tt => Math.sin(tt * event.freq * 0.02) * Math.exp(-tt / 40));

  Plotly.newPlot("waveformPlot", [
    {x: t, y: simH, mode: "lines", name: "Simulated", line: {color: "#00e5ff"}},
    {x: realT, y: realH, mode: "lines", name: event.name, line: {color: "#ff4081", dash: "dot"}}
  ], {
    title: `Comparison: Simulated vs ${event.name}`,
    xaxis: {title: "Time [s]"},
    yaxis: {title: "Strain h(t)"}
  });
}

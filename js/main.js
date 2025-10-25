// Load events
let loadedEvents = [];
let currentEvent = null;

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
  });

// Info modal (robust mobile-safe version)
const infoBtn = document.getElementById("infoBtn");
const infoModal = document.getElementById("infoModal");
const closeInfo = document.getElementById("closeInfo");

// Ensure starts hidden
infoModal.style.display = "none";

infoBtn.addEventListener("click", () => {
  infoModal.style.display = "flex";
});

closeInfo.addEventListener("click", () => {
  infoModal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === infoModal) {
    infoModal.style.display = "none";
  }
});

// Load selected event
document.getElementById("loadEvent").onclick = () => {
  const id = document.getElementById("eventSelect").value;
  currentEvent = loadedEvents.find(e => e.id === id);
  if (currentEvent) {
    showFacts(currentEvent);
    plotWaveform(currentEvent);
  }
};

// Toggle custom simulation form
document.getElementById("simulateCustom").onclick = () => {
  document.getElementById("customForm").classList.toggle("hidden");
};

// Update sliders
["mass1", "mass2", "duration"].forEach(id => {
  const slider = document.getElementById(id);
  const label = document.getElementById(id === "mass1" ? "m1Val" : id === "mass2" ? "m2Val" : "durVal");
  slider.oninput = () => (label.textContent = slider.value);
});

// Run simulation
document.getElementById("runSim").onclick = () => {
  const m1 = +document.getElementById("mass1").value;
  const m2 = +document.getElementById("mass2").value;
  const dur = +document.getElementById("duration").value;

  const chirpMass = Math.pow((m1 * m2) ** (3/5) / Math.pow(m1 + m2, 1/5), 1);
  const t = Array.from({length: 1000}, (_, i) => (i / 1000) * dur * 10);
  const freq = 0.05 * chirpMass ** 0.3;
  const hPlus = t.map(tt => Math.sin(freq * tt) * Math.exp(-tt / (dur * 5)));

  plotCustomWaveform(t, hPlus, {m1, m2, dur});
  if (currentEvent) overlayComparison(t, hPlus, currentEvent);
};

// Save custom parameters
document.getElementById("saveSim").onclick = () => {
  const m1 = +document.getElementById("mass1").value;
  const m2 = +document.getElementById("mass2").value;
  const dur = +document.getElementById("duration").value;
  const blob = new Blob([JSON.stringify({m1, m2, dur}, null, 2)], {type: "application/json"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "custom_simulation.json";
  link.click();
};

// Display event info
function showFacts(ev) {
  const facts = document.getElementById("quickFacts");
  document.getElementById("eventName").textContent = `🌀 ${ev.name}`;
  document.getElementById("eventDate").textContent = `📅 Date: ${ev.date}`;
  document.getElementById("eventDesc").textContent = `📖 ${ev.desc}`;
  facts.classList.remove("hidden");
}

// Plot functions (same as before)
function plotWaveform(event) { /* same as previous version */ }
function plotCustomWaveform(t, hPlus, params) { /* same as previous version */ }
function overlayComparison(t, simH, event) { /* same as previous version */ }

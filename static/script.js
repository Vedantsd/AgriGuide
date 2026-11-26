const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("submit-btn");
const submitLabel = document.getElementById("submit-label");
const errorMsg = document.getElementById("error-msg");
const resultsCard = document.getElementById("results-card");
const placeholderCard = document.getElementById("placeholder-card");
const topMatchEl = document.getElementById("top-match");
const alternativesEl = document.getElementById("alternatives");
const profileEl = document.getElementById("profile");
const reportInput = document.getElementById("report-file");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const dropzone = document.getElementById("dropzone");
const filePickerLabel = document.getElementById("file-picker-label");
const fileNameEl = document.getElementById("file-name");
const sampleBtn = document.getElementById("sample-btn");
const resetBtn = document.getElementById("reset-btn");

const FIELD_IDS = [
  "ph", "moisture", "temperature", "rainfall",
  "soil_type", "location", "nitrogen", "phosphorus", "potassium",
];

const FIELD_NAMES = {
  ph: "pH", moisture: "moisture", temperature: "temperature", rainfall: "rainfall",
  soil_type: "soil type", location: "climate zone",
  nitrogen: "N", phosphorus: "P", potassium: "K",
};

const SAMPLE_VALUES = {
  ph: 6.4,
  moisture: 74,
  temperature: 27,
  rainfall: 140,
  soil_type: "Sandy Loam",
  location: "Tropical",
  nitrogen: 110,
  phosphorus: 25,
  potassium: 135,
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function fillSelect(selectId, values) {
  const select = document.getElementById(selectId);
  values.forEach((value) => {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = value;
    select.appendChild(opt);
  });
}

async function loadOptions() {
  try {
    const res = await fetch("/api/options");
    if (!res.ok) return;
    const data = await res.json();
    fillSelect("soil_type", data.soil_types);
    fillSelect("location", data.locations);
  } catch (err) {
    console.error("Could not load dropdown options:", err);
  }
}

function fieldValue(id) {
  const val = document.getElementById(id).value;
  return val === "" ? null : val;
}

function setField(id, value) {
  const input = document.getElementById(id);
  if (input.tagName === "SELECT") {
    const match = Array.from(input.options).find(
      (o) => o.value.toLowerCase() === String(value).toLowerCase()
    );
    if (!match) return false;
    input.value = match.value;
    return true;
  }
  input.value = value;
  return true;
}

function describe(ids) {
  return ids.map((id) => FIELD_NAMES[id]).join(", ");
}

function syncSelectedFile() {
  const file = reportInput.files[0];
  if (file) {
    const sizeKb = Math.max(1, Math.round(file.size / 1024));
    fileNameEl.textContent = `${file.name} (${sizeKb} KB)`;
    filePickerLabel.classList.add("has-file");
  } else {
    fileNameEl.textContent = "Choose PDF file…";
    filePickerLabel.classList.remove("has-file");
  }
}

reportInput.addEventListener("change", () => {
  syncSelectedFile();
  uploadStatus.textContent = "";
  uploadStatus.classList.remove("error");
});

if (dropzone) {
  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("drag-over");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("drag-over");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (!file) return;
    const dt = new DataTransfer();
    dt.items.add(file);
    reportInput.files = dt.files;
    syncSelectedFile();
    uploadBtn.click();
  });
}

if (sampleBtn) {
  sampleBtn.addEventListener("click", () => {
    Object.entries(SAMPLE_VALUES).forEach(([id, val]) => setField(id, val));
    errorMsg.textContent = "";
  });
}

if (resetBtn) {
  resetBtn.addEventListener("click", () => {
    form.reset();
    reportInput.value = "";
    syncSelectedFile();
    uploadStatus.textContent = "";
    uploadStatus.classList.remove("error");
    errorMsg.textContent = "";
    resultsCard.hidden = true;
    placeholderCard.hidden = false;
  });
}

uploadBtn.addEventListener("click", async () => {
  uploadStatus.classList.remove("error");
  const file = reportInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Choose a PDF file first.";
    uploadStatus.classList.add("error");
    return;
  }

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Reading…";
  const body = new FormData();
  body.append("report", file);

  try {
    const res = await fetch("/api/upload-report", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not read the report.");

    const filled = FIELD_IDS.filter((id) => {
      const value = data.values[id];
      return value !== null && value !== undefined && setField(id, value);
    });
    const missing = FIELD_IDS.filter((id) => !filled.includes(id));

    let message = `Auto-filled ${filled.length} field(s): ${describe(filled) || "none"}.`;
    if (missing.length) message += ` Not found in report: ${describe(missing)}.`;
    uploadStatus.textContent = message;
  } catch (err) {
    uploadStatus.textContent = err.message;
    uploadStatus.classList.add("error");
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Auto-fill";
  }
});

function createMatchRing(percent) {
  const clamped = Math.max(0, Math.min(100, Number(percent) || 0));
  const r = 32;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - clamped / 100);

  const ring = el("div", "match-ring");
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", "0 0 76 76");
  svg.setAttribute("aria-hidden", "true");

  const bg = document.createElementNS(svgNS, "circle");
  bg.setAttribute("class", "match-ring-bg");
  bg.setAttribute("cx", "38");
  bg.setAttribute("cy", "38");
  bg.setAttribute("r", String(r));

  const fill = document.createElementNS(svgNS, "circle");
  fill.setAttribute("class", "match-ring-fill");
  fill.setAttribute("cx", "38");
  fill.setAttribute("cy", "38");
  fill.setAttribute("r", String(r));
  fill.setAttribute("stroke-dasharray", circumference.toFixed(2));
  fill.setAttribute("stroke-dashoffset", offset.toFixed(2));

  svg.append(bg, fill);

  const textWrap = el("div", "match-ring-text");
  textWrap.append(
    el("span", "match-ring-val", `${clamped.toFixed(1)}%`),
    el("span", "match-ring-lbl", "Match")
  );

  ring.append(svg, textWrap);
  return ring;
}

function renderTopMatch(crop) {
  const head = el("div", "top-match-head");
  const titleBox = el("div");
  titleBox.append(
    el("span", "top-badge", "Top recommendation"),
    el("p", "crop-name", crop.crop_name),
    el("p", "match-subtitle", `${crop.soil_type} soil · ${crop.location} zone`)
  );
  head.append(titleBox, createMatchRing(crop.match_percent));

  const metrics = [
    ["Ideal pH", crop.ph_range],
    ["Ideal moisture", crop.moisture_range],
    ["Ideal temperature", crop.temperature_range],
    ["Ideal rainfall", crop.rainfall_range],
    ["Soil type", crop.soil_type],
    ["Climate zone", crop.location],
    ["Typical N / P / K", crop.npk],
    ["Planting window", crop.planting_window],
  ];

  const grid = el("div", "top-match-grid");
  metrics.forEach(([label, val]) => {
    const tile = el("div", "metric-tile");
    tile.append(
      el("span", "metric-tile-label", label),
      el("span", "metric-tile-val", val)
    );
    grid.appendChild(tile);
  });

  topMatchEl.replaceChildren(head, grid);
}

function renderAlternatives(alts) {
  alternativesEl.replaceChildren();
  alts.forEach((crop, idx) => {
    const card = el("div", "alt-card");

    const top = el("div", "alt-top");
    const titleWrap = el("div", "alt-title-wrap");
    titleWrap.append(
      el("span", "alt-rank", `#${idx + 2}`),
      el("span", "alt-name", crop.crop_name)
    );

    const scoreWrap = el("div", "alt-score-wrap");
    const bar = el("div", "alt-bar");
    const barFill = el("div", "alt-bar-fill");
    barFill.style.width = `${Math.max(0, Math.min(100, crop.match_percent))}%`;
    bar.appendChild(barFill);

    scoreWrap.append(bar, el("div", "alt-score", `${crop.match_percent}%`));
    top.append(titleWrap, scoreWrap);

    const meta = el("div", "alt-meta");
    meta.append(
      el("span", "", `${crop.soil_type} · ${crop.location}`),
      el("span", "", `pH ${crop.ph_range}`),
      el("span", "", `${crop.temperature_range}`),
      el("span", "", crop.planting_window)
    );

    card.append(top, meta);
    alternativesEl.appendChild(card);
  });
}

function renderProfile(profile) {
  profileEl.replaceChildren();
  if (!profile || !profile.length) return;
  profileEl.appendChild(el("p", "profile-title", "Your field profile"));

  const chips = el("div", "chips");
  profile.forEach((item) => {
    const chip = el("span", "chip");
    chip.append(
      el("span", "chip-label", `${item.label}:`),
      document.createTextNode(` ${item.category}`)
    );
    chips.appendChild(chip);
  });
  profileEl.appendChild(chips);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorMsg.textContent = "";
  submitBtn.disabled = true;
  submitLabel.textContent = "Scoring crops…";

  const payload = {};
  FIELD_IDS.forEach((id) => { payload[id] = fieldValue(id); });

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      errorMsg.textContent = data.error || "Something went wrong. Please try again.";
      return;
    }

    placeholderCard.hidden = true;
    resultsCard.hidden = false;
    renderProfile(data.profile);
    renderTopMatch(data.top_match);
    renderAlternatives(data.alternatives);
  } catch (err) {
    errorMsg.textContent = "Could not reach the server. Is the Flask app running?";
    console.error(err);
  } finally {
    submitBtn.disabled = false;
    submitLabel.textContent = "Predict best crop";
  }
});

loadOptions();

const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("submit-btn");
const errorMsg = document.getElementById("error-msg");
const resultsCard = document.getElementById("results-card");
const placeholderCard = document.getElementById("placeholder-card");
const topMatchEl = document.getElementById("top-match");
const alternativesEl = document.getElementById("alternatives");
const reportInput = document.getElementById("report-file");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");

const FIELD_IDS = [
  "ph", "moisture", "temperature", "rainfall",
  "soil_type", "location", "nitrogen", "phosphorus", "potassium",
];

const FIELD_NAMES = {
  ph: "pH", moisture: "moisture", temperature: "temperature", rainfall: "rainfall",
  soil_type: "soil type", location: "climate zone",
  nitrogen: "N", phosphorus: "P", potassium: "K",
};

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
  const el = document.getElementById(id);
  if (el.tagName === "SELECT") {
    const match = Array.from(el.options).find(
      (o) => o.value.toLowerCase() === String(value).toLowerCase()
    );
    if (!match) return false;
    el.value = match.value;
    return true;
  }
  el.value = value;
  return true;
}

function describe(ids) {
  return ids.map((id) => FIELD_NAMES[id]).join(", ");
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

    let message = `Filled ${filled.length} field(s): ${describe(filled) || "none"}.`;
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

function renderTopMatch(crop) {
  topMatchEl.innerHTML = `
    <p class="crop-name">${crop.crop_name}</p>
    <p class="match-percent">${crop.match_percent}% match to your conditions</p>
    <dl>
      <dt>Ideal pH</dt><dd>${crop.ph_range}</dd>
      <dt>Ideal moisture</dt><dd>${crop.moisture_range}</dd>
      <dt>Ideal temperature</dt><dd>${crop.temperature_range}</dd>
      <dt>Ideal rainfall</dt><dd>${crop.rainfall_range}</dd>
      <dt>Soil type</dt><dd>${crop.soil_type}</dd>
      <dt>Climate zone</dt><dd>${crop.location}</dd>
      <dt>Typical N/P/K</dt><dd>${crop.npk}</dd>
      <dt>Planting window</dt><dd>${crop.planting_window}</dd>
    </dl>
  `;
}

function renderAlternatives(alts) {
  alternativesEl.innerHTML = "";
  alts.forEach((crop) => {
    const div = document.createElement("div");
    div.className = "alt-card";
    div.innerHTML = `
      <div>
        <div class="alt-name">${crop.crop_name}</div>
        <div class="alt-meta">${crop.soil_type} soil &middot; ${crop.location}</div>
      </div>
      <div class="alt-score">${crop.match_percent}%</div>
    `;
    alternativesEl.appendChild(div);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorMsg.textContent = "";
  submitBtn.disabled = true;
  submitBtn.textContent = "Predicting…";

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
    renderTopMatch(data.top_match);
    renderAlternatives(data.alternatives);
  } catch (err) {
    errorMsg.textContent = "Could not reach the server. Is the Flask app running?";
    console.error(err);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Predict best crop";
  }
});

loadOptions();
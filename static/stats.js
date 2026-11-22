const LABELS = {
  nitrogen: "Nitrogen (N)",
  phosphorus: "Phosphorus (P)",
  potassium: "Potassium (K)",
  ph_avg: "Avg. pH",
  moisture_avg: "Avg. moisture (%)",
  temp_avg: "Avg. temperature (°C)",
  rainfall_avg: "Avg. rainfall (mm)",
  location: "Climate zone",
  soil_type: "Soil type",
  const: "Intercept",
  custom: "Agronomic categories",
  equal_width: "Equal-width bins",
  quantile: "Quantile bins",
};

const $ = (id) => document.getElementById(id);
const label = (key) => LABELS[key] || key;

function fmt(x, digits = 3) {
  return x === null || x === undefined ? "–" : Number(x).toFixed(digits);
}

function fmtP(p) {
  if (p === null || p === undefined) return "–";
  return p < 0.001 ? "< 0.001" : p.toFixed(4);
}

function makeTable(headers, rows) {
  const table = document.createElement("table");
  table.className = "stats-table";
  const headRow = table.createTHead().insertRow();
  headers.forEach((h) => {
    const th = document.createElement("th");
    th.textContent = h;
    headRow.appendChild(th);
  });
  const body = table.createTBody();
  rows.forEach((row) => {
    const tr = body.insertRow();
    row.forEach((cell) => { tr.insertCell().textContent = cell; });
  });
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  wrap.appendChild(table);
  return wrap;
}

function makeHeading(text) {
  const p = document.createElement("p");
  p.className = "stats-sub";
  p.textContent = text;
  return p;
}

function makeInterpretation(text) {
  const p = document.createElement("p");
  p.className = "interpretation";
  p.textContent = text;
  return p;
}

function fillSelect(select, values) {
  select.innerHTML = "";
  values.forEach((value) => {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = label(value);
    select.appendChild(opt);
  });
}

async function getJSON(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed.");
  return data;
}

async function runCard(button, errorEl, outEl, url, render) {
  errorEl.textContent = "";
  button.disabled = true;
  try {
    const data = await getJSON(url);
    outEl.replaceChildren(...render(data));
  } catch (err) {
    outEl.replaceChildren();
    errorEl.textContent = err.message;
  } finally {
    button.disabled = false;
  }
}

function groupRows(groups) {
  return groups.map((g) => [g.name, g.n, fmt(g.mean, 2), fmt(g.std, 2)]);
}

function renderRegression(d) {
  return [
    makeTable(
      ["Observations", "R²", "Adj. R²", "F-statistic", "df", "F p-value"],
      [[d.n, fmt(d.r2), fmt(d.adj_r2), fmt(d.f_stat, 2),
        `${d.df_model}, ${d.df_resid}`, fmtP(d.f_p_value)]]
    ),
    makeHeading("Coefficients (t-tests)"),
    makeTable(
      ["Term", "Coef.", "Std. error", "t", "p-value", "95% CI"],
      d.coefficients.map((c) => [
        label(c.term), fmt(c.coef), fmt(c.std_err), fmt(c.t_stat, 2),
        fmtP(c.p_value), `${fmt(c.ci_low, 2)} to ${fmt(c.ci_high, 2)}`,
      ])
    ),
    makeInterpretation(d.interpretation),
  ];
}

function renderTTest(d) {
  const t = d.t_test;
  const f = d.variance_f_test;
  return [
    makeTable(["Group", "n", "Mean", "Std. dev."], groupRows(d.groups)),
    makeHeading(t.method),
    makeTable(
      ["t", "df", "p-value", "Mean diff.", "95% CI of diff."],
      [[fmt(t.t_stat), fmt(t.df, 1), fmtP(t.p_value), fmt(t.mean_diff, 2),
        `${fmt(t.ci_low, 2)} to ${fmt(t.ci_high, 2)}`]]
    ),
    makeHeading("Variance ratio F-test"),
    makeTable(
      ["F", "df (num, den)", "p-value"],
      [[fmt(f.f_stat), `${f.df_num}, ${f.df_den}`, fmtP(f.p_value)]]
    ),
    makeInterpretation(d.interpretation),
  ];
}

function renderAnova(d) {
  return [
    makeTable(
      ["F", "df (between, within)", "p-value", "Eta squared"],
      [[fmt(d.f_stat), `${d.df_between}, ${d.df_within}`, fmtP(d.p_value), fmt(d.eta_squared)]]
    ),
    makeHeading("Group summary"),
    makeTable(["Group", "n", "Mean", "Std. dev."], groupRows(d.groups)),
    makeInterpretation(d.interpretation),
  ];
}

function makeBars(rows) {
  const wrap = document.createElement("div");
  wrap.className = "bars";
  rows.forEach((r) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    const name = document.createElement("span");
    name.className = "bar-name";
    name.textContent = r.bin;
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = `${r.percent}%`;
    track.appendChild(fill);
    const value = document.createElement("span");
    value.className = "bar-val";
    value.textContent = `${r.count} (${r.percent}%)`;
    row.append(name, track, value);
    wrap.appendChild(row);
  });
  return wrap;
}

function renderBinning(d) {
  const nodes = [
    makeBars(d.rows),
    makeTable(
      ["Bin", "Range", "Count", "Percent"],
      d.rows.map((r) => [r.bin, r.range, r.count, `${r.percent}%`])
    ),
  ];
  if (d.crosstab) {
    const ct = d.crosstab;
    nodes.push(makeHeading(`Bins by ${label(ct.group_col).toLowerCase()}`));
    nodes.push(makeTable(
      ["Bin", ...ct.columns, "Total"],
      ct.rows.map((r) => [r.bin, ...r.counts, r.counts.reduce((a, b) => a + b, 0)])
    ));
  }
  nodes.push(makeInterpretation(d.interpretation));
  return nodes;
}

function refreshGroups(prefix, groups) {
  const values = groups[$(`${prefix}-col`).value] || [];
  fillSelect($("t-a"), values);
  fillSelect($("t-b"), values);
  if (values.length > 1) $("t-b").value = values[1];
}

async function init() {
  let meta;
  try {
    meta = await getJSON("/api/stats/meta");
  } catch (err) {
    $("reg-error").textContent = err.message;
    return;
  }

  const groupCols = Object.keys(meta.groups);
  fillSelect($("reg-target"), meta.targets);
  fillSelect($("t-var"), meta.variables);
  fillSelect($("t-col"), groupCols);
  fillSelect($("a-var"), meta.variables);
  fillSelect($("a-col"), groupCols);
  refreshGroups("t", meta.groups);
  $("t-col").addEventListener("change", () => refreshGroups("t", meta.groups));

  $("reg-run").addEventListener("click", () => runCard(
    $("reg-run"), $("reg-error"), $("reg-out"),
    `/api/stats/regression?target=${encodeURIComponent($("reg-target").value)}`,
    renderRegression
  ));

  $("t-run").addEventListener("click", () => {
    const params = new URLSearchParams({
      variable: $("t-var").value,
      group_col: $("t-col").value,
      group_a: $("t-a").value,
      group_b: $("t-b").value,
    });
    runCard($("t-run"), $("t-error"), $("t-out"), `/api/stats/ttest?${params}`, renderTTest);
  });

  $("a-run").addEventListener("click", () => {
    const params = new URLSearchParams({
      variable: $("a-var").value,
      group_col: $("a-col").value,
    });
    runCard($("a-run"), $("a-error"), $("a-out"), `/api/stats/anova?${params}`, renderAnova);
  });

  fillSelect($("b-var"), meta.variables);
  fillSelect($("b-method"), meta.bin_methods);
  fillSelect($("b-col"), groupCols);
  $("b-col").prepend(new Option("None", ""));
  $("b-col").value = "";
  const syncBins = () => { $("b-bins").disabled = $("b-method").value === "custom"; };
  $("b-method").addEventListener("change", syncBins);
  syncBins();

  $("b-run").addEventListener("click", () => {
    const params = new URLSearchParams({
      variable: $("b-var").value,
      method: $("b-method").value,
      bins: $("b-bins").value,
      group_col: $("b-col").value,
    });
    runCard($("b-run"), $("b-error"), $("b-out"), `/api/stats/binning?${params}`, renderBinning);
  });
}

init();
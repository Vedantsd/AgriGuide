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

const ALPHA = 0.05;
const $ = (id) => document.getElementById(id);
const label = (key) => LABELS[key] || key;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function fmt(x, digits = 3) {
  return x === null || x === undefined ? "–" : Number(x).toFixed(digits);
}

function fmtP(p) {
  if (p === null || p === undefined) return "–";
  return p < 0.001 ? "< 0.001" : p.toFixed(4);
}

function makeSigBadge(p) {
  if (p === null || p === undefined) return null;
  const sig = p < ALPHA;
  return el("span", `sig-badge ${sig ? "is-sig" : "not-sig"}`, sig ? "Significant" : "Not sig.");
}

function makeKpiGrid(items) {
  const grid = el("div", "kpi-grid");
  items.forEach(({ name, value, badge }) => {
    const tile = el("div", "kpi-tile");
    tile.appendChild(el("span", "kpi-label", name));
    const row = el("div", "kpi-value-row");
    row.appendChild(el("span", "kpi-value", String(value)));
    if (badge) row.appendChild(badge);
    tile.appendChild(row);
    grid.appendChild(tile);
  });
  return grid;
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
    row.forEach((cell) => {
      const td = tr.insertCell();
      if (cell instanceof Node) {
        td.appendChild(cell);
      } else {
        td.textContent = cell;
      }
    });
  });
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  wrap.appendChild(table);
  return wrap;
}

function makeHeading(text) {
  return el("p", "stats-sub", text);
}

function makeInterpretation(text) {
  return el("p", "interpretation", text);
}

function makeBars(rows) {
  const wrap = el("div", "bars");
  rows.forEach((r) => {
    const row = el("div", "bar-row");
    const name = el("span", "bar-name", r.label);
    const track = el("div", "bar-track");
    const fill = el("div", "bar-fill");
    fill.style.width = `${Math.max(0, Math.min(100, r.percent))}%`;
    track.appendChild(fill);
    const value = el("span", "bar-val", r.valText);
    row.append(name, track, value);
    wrap.appendChild(row);
  });
  return wrap;
}

function makeGroupMeanBars(groups) {
  const maxMean = Math.max(...groups.map((g) => Math.abs(g.mean || 0)), 1e-6);
  return makeBars(
    groups.map((g) => ({
      label: g.name,
      percent: (Math.max(0, g.mean || 0) / maxMean) * 100,
      valText: `${fmt(g.mean, 2)} (n=${g.n})`,
    }))
  );
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
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "Running…";
  try {
    const data = await getJSON(url);
    outEl.replaceChildren(...render(data));
  } catch (err) {
    outEl.replaceChildren();
    errorEl.textContent = err.message;
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

function groupRows(groups) {
  return groups.map((g) => [g.name, g.n, fmt(g.mean, 2), fmt(g.std, 2)]);
}

function renderRegression(d) {
  return [
    makeKpiGrid([
      { name: "Observations", value: d.n },
      { name: "R²", value: fmt(d.r2) },
      { name: "Adjusted R²", value: fmt(d.adj_r2) },
      { name: `Overall F (${d.df_model}, ${d.df_resid})`, value: fmt(d.f_stat, 2) },
      { name: "Overall p-value", value: fmtP(d.f_p_value), badge: makeSigBadge(d.f_p_value) },
    ]),
    makeHeading("Coefficients (t-tests)"),
    makeTable(
      ["Term", "Coef.", "Std. error", "t", "p-value", "95% CI", "Status"],
      d.coefficients.map((c) => [
        label(c.term),
        fmt(c.coef),
        fmt(c.std_err),
        fmt(c.t_stat, 2),
        fmtP(c.p_value),
        `${fmt(c.ci_low, 2)} to ${fmt(c.ci_high, 2)}`,
        c.term === "const" ? "–" : makeSigBadge(c.p_value),
      ])
    ),
    makeInterpretation(d.interpretation),
  ];
}

function renderTTest(d) {
  const t = d.t_test;
  const f = d.variance_f_test;
  return [
    makeKpiGrid([
      { name: "Mean difference", value: fmt(t.mean_diff, 2) },
      { name: "Welch's t", value: fmt(t.t_stat) },
      { name: "t-Test p-value", value: fmtP(t.p_value), badge: makeSigBadge(t.p_value) },
      { name: "Variance F-test p", value: fmtP(f.p_value), badge: makeSigBadge(f.p_value) },
    ]),
    makeHeading("Group means"),
    makeGroupMeanBars(d.groups),
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
    makeKpiGrid([
      { name: `F (${d.df_between}, ${d.df_within})`, value: fmt(d.f_stat) },
      { name: "p-value", value: fmtP(d.p_value), badge: makeSigBadge(d.p_value) },
      { name: "Eta squared (η²)", value: fmt(d.eta_squared) },
      { name: "Groups compared", value: d.groups.length },
    ]),
    makeHeading("Group mean comparison"),
    makeGroupMeanBars(d.groups),
    makeHeading("Group summary"),
    makeTable(["Group", "n", "Mean", "Std. dev."], groupRows(d.groups)),
    makeInterpretation(d.interpretation),
  ];
}

function renderBinning(d) {
  const topBin = d.rows.reduce((best, r) => (r.count > best.count ? r : best), d.rows[0]);
  const nodes = [
    makeKpiGrid([
      { name: "Total crops", value: d.total },
      { name: "Bins created", value: d.rows.length },
      { name: "Largest bin", value: topBin ? `${topBin.bin} (${topBin.percent}%)` : "–" },
    ]),
    makeBars(
      d.rows.map((r) => ({
        label: r.bin,
        percent: r.percent,
        valText: `${r.count} (${r.percent}%)`,
      }))
    ),
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

function triggerRegression() {
  return runCard(
    $("reg-run"), $("reg-error"), $("reg-out"),
    `/api/stats/regression?target=${encodeURIComponent($("reg-target").value)}`,
    renderRegression
  );
}

function triggerTTest() {
  const params = new URLSearchParams({
    variable: $("t-var").value,
    group_col: $("t-col").value,
    group_a: $("t-a").value,
    group_b: $("t-b").value,
  });
  return runCard($("t-run"), $("t-error"), $("t-out"), `/api/stats/ttest?${params}`, renderTTest);
}

function triggerAnova() {
  const params = new URLSearchParams({
    variable: $("a-var").value,
    group_col: $("a-col").value,
  });
  return runCard($("a-run"), $("a-error"), $("a-out"), `/api/stats/anova?${params}`, renderAnova);
}

function triggerBinning() {
  const params = new URLSearchParams({
    variable: $("b-var").value,
    method: $("b-method").value,
    bins: $("b-bins").value,
    group_col: $("b-col").value,
  });
  return runCard($("b-run"), $("b-error"), $("b-out"), `/api/stats/binning?${params}`, renderBinning);
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

  $("reg-run").addEventListener("click", triggerRegression);
  $("t-run").addEventListener("click", triggerTTest);
  $("a-run").addEventListener("click", triggerAnova);

  fillSelect($("b-var"), meta.variables);
  fillSelect($("b-method"), meta.bin_methods);
  fillSelect($("b-col"), groupCols);
  $("b-col").prepend(new Option("None", ""));
  $("b-col").value = "";
  const syncBins = () => { $("b-bins").disabled = $("b-method").value === "custom"; };
  $("b-method").addEventListener("change", syncBins);
  syncBins();

  $("b-run").addEventListener("click", triggerBinning);

  await Promise.all([
    triggerRegression(),
    triggerTTest(),
    triggerAnova(),
    triggerBinning(),
  ]);
}

init();

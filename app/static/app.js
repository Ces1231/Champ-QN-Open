// CHAMP-QN Crypto Readiness Scanner — browser UI logic.
// No external dependencies. All user-controlled text is rendered via
// textContent (never innerHTML) to avoid script injection from
// attacker-controlled inventory content (asset IDs, algorithm strings, notes).

let lastBlob = null;
let lastFilename = "inventory";
let lastMode = null; // "upload" | "sample"

const statusMsg = document.getElementById("statusMsg");
const resultsPanel = document.getElementById("resultsPanel");
const resultsSummary = document.getElementById("resultsSummary");
const resultsAssets = document.getElementById("resultsAssets");

function setStatus(text, isError) {
  statusMsg.textContent = text;
  statusMsg.style.color = isError ? "#b91c1c" : "";
}

function clearChildren(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

function el(tag, opts) {
  const node = document.createElement(tag);
  if (opts) {
    if (opts.text !== undefined) node.textContent = opts.text;
    if (opts.className) node.className = opts.className;
  }
  return node;
}

async function postForAssessment(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`HTTP ${resp.status}: ${body}`);
  }
  return resp.json();
}

function renderResults(result) {
  clearChildren(resultsSummary);
  clearChildren(resultsAssets);

  const summary = el("div", { className: "summary" });
  summary.appendChild(el("p", { text: `Overall score: ${result.overall_score} / 100` }));
  summary.appendChild(el("p", { text: `Overall classification: ${result.overall_classification}` }));
  summary.appendChild(el("p", { text: `Assets assessed: ${result.asset_count}` }));
  summary.appendChild(el("p", { text: `Findings identified: ${result.finding_count}` }));
  resultsSummary.appendChild(summary);

  for (const asset of result.assets) {
    const card = el("div", { className: "asset-card" });
    const heading = el("h3", { text: asset.asset_id });
    card.appendChild(heading);
    card.appendChild(
      el("p", {
        className: "muted",
        text: `Score: ${asset.asset_score}/100 · Classification: ${asset.asset_classification}`,
      })
    );

    if (asset.findings.length === 0) {
      card.appendChild(el("p", { className: "muted", text: "No algorithms listed." }));
    } else {
      const table = el("table");
      const thead = el("thead");
      const headRow = el("tr");
      ["Detected value", "Matched algorithm", "Classification", "Guidance"].forEach((h) => {
        headRow.appendChild(el("th", { text: h }));
      });
      thead.appendChild(headRow);
      table.appendChild(thead);

      const tbody = el("tbody");
      for (const finding of asset.findings) {
        const row = el("tr");
        row.appendChild(el("td", { text: finding.raw_value }));
        row.appendChild(el("td", { text: finding.matched_name }));
        row.appendChild(el("td", { text: finding.classification }));
        row.appendChild(el("td", { text: finding.guidance }));
        tbody.appendChild(row);
      }
      table.appendChild(tbody);
      card.appendChild(table);
    }
    resultsAssets.appendChild(card);
  }

  resultsPanel.hidden = false;
}

async function runUpload(blob, filename) {
  setStatus("Assessing…", false);
  const formData = new FormData();
  formData.append("file", blob, filename);
  try {
    const result = await postForAssessment("/api/v1/assess/upload?format=json", {
      method: "POST",
      body: formData,
    });
    lastBlob = blob;
    lastFilename = filename;
    lastMode = "upload";
    renderResults(result);
    setStatus("Assessment complete.", false);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function runSample() {
  setStatus("Assessing sample inventory…", false);
  try {
    const result = await postForAssessment("/api/v1/assess/sample?format=json", {
      method: "POST",
    });
    lastMode = "sample";
    renderResults(result);
    setStatus("Assessment complete.", false);
  } catch (err) {
    setStatus(String(err), true);
  }
}

document.getElementById("uploadBtn").addEventListener("click", () => {
  const input = document.getElementById("fileInput");
  if (!input.files || input.files.length === 0) {
    setStatus("Choose a file first.", true);
    return;
  }
  const file = input.files[0];
  runUpload(file, file.name);
});

document.getElementById("sampleBtn").addEventListener("click", () => {
  runSample();
});

document.getElementById("pasteBtn").addEventListener("click", () => {
  const text = document.getElementById("pasteInput").value;
  if (!text.trim()) {
    setStatus("Paste some JSON or YAML first.", true);
    return;
  }
  const blob = new Blob([text], { type: "text/plain" });
  runUpload(blob, "pasted-inventory.json");
});

async function downloadReport(format) {
  if (!lastMode) {
    setStatus("Run an assessment first.", true);
    return;
  }
  try {
    let url;
    let options;
    if (lastMode === "sample") {
      url = `/api/v1/assess/sample?format=${format}`;
      options = { method: "POST" };
    } else {
      const formData = new FormData();
      formData.append("file", lastBlob, lastFilename);
      url = `/api/v1/assess/upload?format=${format}`;
      options = { method: "POST", body: formData };
    }
    const resp = await fetch(url, options);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const blob = await resp.blob();
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = format === "markdown" ? "champ-qn-report.md" : "champ-qn-report.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(downloadUrl);
  } catch (err) {
    setStatus(String(err), true);
  }
}

document.getElementById("downloadJson").addEventListener("click", () => downloadReport("json"));
document.getElementById("downloadMarkdown").addEventListener("click", () => downloadReport("markdown"));

const requirementsEl = document.getElementById("requirements");
const codeContextEl = document.getElementById("codeContext");
const inputTypeEl = document.getElementById("inputType");
const techniqueEl = document.getElementById("technique");
const modelEl = document.getElementById("model");
const tempEl = document.getElementById("temperature");
const promptEl = document.getElementById("promptVersion");
const outputEl = document.getElementById("output");
const statusEl = document.getElementById("status");
const buttonEl = document.getElementById("generateBtn");

function syncInputVisibility() {
  const inputType = inputTypeEl?.value || "requirements";
  if (!requirementsEl || !codeContextEl) return;

  const isReq = inputType === "requirements";
  requirementsEl.style.display = isReq ? "block" : "none";
  codeContextEl.style.display = isReq ? "none" : "block";
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#ffb4b4" : "#b6bed9";
}

inputTypeEl?.addEventListener("change", () => {
  syncInputVisibility();
  setStatus("");
});

syncInputVisibility();

function formatDecisionTable(dt) {
  if (!dt.rules || !Array.isArray(dt.rules) || dt.rules.length === 0) {
    return "";
  }
  const conditions = dt.conditions || [];
  const actions = dt.actions || [];
  const colWidths = [];

  for (const c of conditions) {
    const id = c.id || "";
    const desc = c.description || "";
    colWidths.push(Math.max(id.length, desc.length, 8));
  }
  for (const a of actions) {
    const id = a.id || "";
    const desc = a.description || "";
    colWidths.push(Math.max(id.length, desc.length, 8));
  }

  const separator = "+" + colWidths.map(w => "-".repeat(w + 2)).join("+") + "+";
  const headerRow = "|" + conditions.map((c, i) => " " + (c.id || "").padEnd(colWidths[i]) + " ").join("|") + "|" + actions.map((a, i) => " " + (a.id || "").padEnd(colWidths[conditions.length + i]) + " ").join("|") + "|";

  const rows = [];
  for (const rule of dt.rules) {
    const entries = [...(rule.condition_entries || []), ...(rule.action_entries || [])];
    const row = "|" + entries.map((v, i) => " " + String(v || "-").padEnd(colWidths[i]) + " ").join("|") + "|";
    rows.push(row);
  }

  return separator + "\n" + headerRow + "\n" + separator + "\n" + rows.join("\n" + separator + "\n") + "\n" + separator;
}

function formatDecisionTables(data) {
  if (!data.decision_tables || !Array.isArray(data.decision_tables) || data.decision_tables.length === 0) {
    return "";
  }
  const lines = [];
  for (const dt of data.decision_tables) {
    const name = dt.name || "Decision Table";
    lines.push("=== " + name + " ===");
    const table = formatDecisionTable(dt);
    if (table) {
      lines.push(table);
    }
    if (dt.test_cases && Array.isArray(dt.test_cases) && dt.test_cases.length > 0) {
      lines.push("\nTest Cases:");
      for (const tc of dt.test_cases) {
        const inputs = tc.inputs ? JSON.stringify(tc.inputs) : "{}";
        lines.push("  " + (tc.id || "TC?") + ": " + inputs + " => " + (tc.expected || ""));
      }
    }
    lines.push("");
  }
  return lines.join("\n");
}

function formatOutput(data, technique) {
  if (technique === "decision_table" && data.decision_tables) {
    const lines = [];
    for (const dt of data.decision_tables) {
      const name = dt.name || "Decision Table";
      lines.push("=== " + name + " ===");

      if (dt.conditions && dt.conditions.length > 0) {
        lines.push("Conditions:");
        for (const c of dt.conditions) {
          lines.push("  " + (c.id || "?") + ": " + (c.description || "") + " (" + JSON.stringify(c.values || []) + ")");
        }
      }

      if (dt.actions && dt.actions.length > 0) {
        lines.push("Actions:");
        for (const a of dt.actions) {
          lines.push("  " + (a.id || "?") + ": " + (a.description || ""));
        }
      }

      if (dt.rules && dt.rules.length > 0) {
        lines.push("Rules:");
        for (const r of dt.rules) {
          lines.push("  " + (r.rule_id || "?") + ": " + (r.description || ""));
          lines.push("    conditions: " + JSON.stringify(r.condition_entries || []));
          lines.push("    actions: " + JSON.stringify(r.action_entries || []));
        }
      }

      if (dt.test_cases && dt.test_cases.length > 0) {
        lines.push("Test Cases:");
        for (const tc of dt.test_cases) {
          lines.push("  " + (tc.id || "?") + ": " + JSON.stringify(tc.inputs || {}) + " => " + (tc.expected || ""));
        }
      }
      lines.push("");
    }
    data._formatted = lines.join("\n");
  }
  return data;
}

function displayOutput(data, technique) {
  const formatted = formatOutput(data, technique);
  if (formatted._formatted) {
    outputEl.textContent = formatted._formatted;
  } else {
    outputEl.textContent = JSON.stringify(data, null, 2);
  }
}

buttonEl.addEventListener("click", async () => {
  const requirements = (requirementsEl?.value || "").trim();
  const codeContext = (codeContextEl?.value || "").trim();
  const inputType = inputTypeEl?.value || "requirements";
  const technique = techniqueEl?.value || "ep_bva";

  if (inputType === "requirements" && !requirements) {
    setStatus("Please paste requirements before generating.", true);
    return;
  }
  if (inputType === "codebase" && !codeContext) {
    setStatus("Please paste code/docs context before generating.", true);
    return;
  }

  const payload = {
    requirements,
    code_context: codeContext,
    input_type: inputType,
    technique,
    model: modelEl.value.trim() || "gpt-4o-mini",
    temperature: parseFloat(tempEl.value || "0.2"),
    prompt_version: promptEl.value,
  };

  setStatus("Streaming JSON...", false);
  buttonEl.disabled = true;
  outputEl.textContent = "";

  try {
    const response = await fetch("/api/generate-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Request failed");
    }

    if (!response.body) {
      throw new Error("Streaming not supported by the browser");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        const lines = part.split("\n");
        let eventType = "message";
        let dataText = "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.replace("event:", "").trim();
          } else if (line.startsWith("data:")) {
            dataText += line.replace("data:", "").trim();
          }
        }

        if (!dataText) continue;
        const payload = JSON.parse(dataText);

        if (eventType === "chunk") {
          outputEl.textContent += payload.text;
        } else if (eventType === "done") {
          setStatus("Done.");
        } else if (eventType === "error") {
          throw new Error(payload.error || "Streaming error");
        }
      }
    }
  } catch (error) {
    outputEl.textContent = "{}";
    setStatus(`Error: ${error.message}`, true);
  } finally {
    buttonEl.disabled = false;
  }
});

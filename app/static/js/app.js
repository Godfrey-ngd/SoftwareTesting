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
          outputEl.textContent = JSON.stringify(payload.data, null, 2);
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

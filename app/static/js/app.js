const requirementsEl = document.getElementById("requirements");
const modelEl = document.getElementById("model");
const tempEl = document.getElementById("temperature");
const promptEl = document.getElementById("promptVersion");
const outputEl = document.getElementById("output");
const statusEl = document.getElementById("status");
const buttonEl = document.getElementById("generateBtn");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#ffb4b4" : "#b6bed9";
}

buttonEl.addEventListener("click", async () => {
  const requirements = requirementsEl.value.trim();
  if (!requirements) {
    setStatus("Please paste requirements before generating.", true);
    return;
  }

  const payload = {
    requirements,
    model: modelEl.value.trim() || "gpt-4o-mini",
    temperature: parseFloat(tempEl.value || "0.2"),
    prompt_version: promptEl.value,
  };

  setStatus("Generating JSON...", false);
  buttonEl.disabled = true;

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Request failed");
    }

    const data = await response.json();
    outputEl.textContent = JSON.stringify(data, null, 2);
    setStatus("Done.");
  } catch (error) {
    outputEl.textContent = "{}";
    setStatus(`Error: ${error.message}`, true);
  } finally {
    buttonEl.disabled = false;
  }
});

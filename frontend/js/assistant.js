const chatWindow = document.getElementById("chatWindow");

function appendMessage(role, text, sources = []) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.textContent = text;

  if (sources.length > 0) {
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "chat-sources";
    sourcesEl.textContent = `Sources: ${[...new Set(sources.map((s) => s.document))].join(", ")}`;
    bubble.appendChild(sourcesEl);
  }

  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

document.getElementById("chatForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("chatInput");
  const question = input.value.trim();
  if (!question) return;

  appendMessage("user", question);
  input.value = "";

  const loadingBubble = document.createElement("div");
  loadingBubble.className = "chat-bubble assistant";
  loadingBubble.textContent = "Thinking...";
  chatWindow.appendChild(loadingBubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const response = await Api.askAssistant(question);
    loadingBubble.remove();
    appendMessage("assistant", response.answer, response.sources);
  } catch (error) {
    loadingBubble.remove();
    appendMessage("assistant", `Error: ${error.message}`);
  }
});

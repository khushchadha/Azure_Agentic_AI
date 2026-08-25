// Flask backend from server.py
const API_BASE = "http://127.0.0.1:5000";

const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const send = document.getElementById("send");
const status = document.getElementById("status");

/* ---------- composer behaviour ---------- */
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
});
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});
chat.addEventListener("click", e => {
  if (e.target.classList.contains("chip")) {
    input.value = e.target.textContent;
    form.requestSubmit();
  }
});

/* ---------- rendering helpers ---------- */
function addMsg(cls, text) {
  const el = document.createElement("div");
  el.className = "msg " + cls;
  el.textContent = text || "";
  chat.appendChild(el);
  scrollDown();
  return el;
}

function addPill(kind, text) {
  let row = chat.lastElementChild;
  if (!row || !row.classList.contains("events")) {
    row = document.createElement("div");
    row.className = "events";
    chat.appendChild(row);
  }
  const p = document.createElement("span");
  p.className = "pill " + kind;
  p.textContent = text;
  row.appendChild(p);
  scrollDown();
}

function scrollDown() {
  chat.scrollTop = chat.scrollHeight;
}

/* ---------- SSE stream ---------- */
form.addEventListener("submit", async e => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message || send.disabled) return;

  const empty = document.getElementById("empty");
  if (empty) empty.remove();

  addMsg("user", message);
  input.value = "";
  input.style.height = "auto";
  send.disabled = true;
  status.textContent = "streaming...";

  let bubble = null;

  try {
    const res = await fetch(API_BASE + "/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
    if (!res.ok) throw new Error("server returned " + res.status);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split("\n\n");
      buffer = parts.pop();

      for (const part of parts) {
        const line = part.split("\n").find(l => l.startsWith("data: "));
        if (!line) continue;
        const ev = JSON.parse(line.slice(6));

        if (ev.type === "token") {
          if (!bubble) {
            bubble = addMsg("bot");
            bubble.classList.add("caret");
          }
          bubble.textContent += ev.text;
          scrollDown();
        } else if (ev.type === "agent") {
          addPill("agent", "\u{1F916} " + ev.name);
          bubble = null;
        } else if (ev.type === "tool") {
          addPill("tool", "\u{1F6E0} " + ev.name);
          bubble = null;
        } else if (ev.type === "tool_output") {
          addPill("tool", "✓ tool result");
        } else if (ev.type === "error") {
          if (bubble) bubble.classList.remove("caret");
          addMsg("error", "⚠ " + ev.message);
        } else if (ev.type === "done") {
          if (bubble) bubble.classList.remove("caret");
          else if (ev.output) addMsg("bot", ev.output);
        }
      }
    }
  } catch (err) {
    addMsg("error", "⚠ " + err.message + " — is the backend running on " + API_BASE + "?");
  } finally {
    if (bubble) bubble.classList.remove("caret");
    send.disabled = false;
    status.textContent = "idle";
    input.focus();
  }
});

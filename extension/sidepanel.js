const API_URL = "http://localhost:8000";
let videoUrl = null;
const status = document.querySelector("#video-status");
const messages = document.querySelector("#messages");
const question = document.querySelector("#question");
const send = document.querySelector("#send");
const summarize = document.querySelector("#summarize");

function addMessage(text, type) {
  const item = document.createElement("div");
  item.className = `message ${type}`;
  item.textContent = text;
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
}

function setReady(ready) {
  question.disabled = !ready;
  send.disabled = !ready;
  summarize.disabled = !ready;
}

async function loadVideo() {
  const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  if (!tab?.url?.includes("youtube.com/watch") && !tab?.url?.includes("youtu.be/") && !tab?.url?.includes("youtube.com/shorts/")) {
    status.textContent = "Open a YouTube video, then return here.";
    return;
  }
  videoUrl = tab.url;
  status.textContent = tab.title || "YouTube video ready";
  setReady(true);
}

async function ask(endpoint, userText) {
  if (!videoUrl) return;
  if (userText) addMessage(userText, "user");
  setReady(false);
  addMessage("Reading captions and thinking…", "assistant");
  const placeholder = messages.lastElementChild;
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(endpoint === "/chat" ? { video_url: videoUrl, question: userText } : { video_url: videoUrl })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "The backend returned an error.");
    placeholder.textContent = data.answer;
  } catch (error) {
    placeholder.textContent = `Could not answer: ${error.message}. Make sure the backend is running at ${API_URL}.`;
  } finally { setReady(true); }
}

document.querySelector("#chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = question.value.trim();
  if (!text) return;
  question.value = "";
  await ask("/chat", text);
});
summarize.addEventListener("click", () => ask("/summarize"));
loadVideo();

let mode = "chat";
let isProcessing = false;
let currentTrainingQuestion = null;
let currentLang = localStorage.getItem("lang") || "fr";

const translations = {
  en: {
    placeholder: "What can I help you with?",
    training: "Training",
    asking: "Asking",
    language_toggle: "FR",
    input_placeholder: "Type your message..."
  },
  fr: {
    placeholder: "Comment puis-je vous aider ?",
    training: "Entraînement",
    asking: "Demander",
    language_toggle: "EN",
    input_placeholder: "Tapez votre message..."
  }
};

const trainingBtn = document.getElementById("training-btn");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const messageList = document.getElementById("message-list");
const themeToggle = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");
const langBtn = document.getElementById("lang-btn");

themeToggle.addEventListener("click", () => {
  const isLight = document.body.classList.contains("light-theme");
  document.body.classList.toggle("light-theme", !isLight);
  document.body.classList.toggle("dark-theme", isLight);
  themeIcon.textContent = isLight ? "🌙" : "☀️";
});

function applyTranslations() {
  const t = translations[currentLang];
  if (!t) return;

  const placeholder = document.getElementById("placeholder");
  if (placeholder) placeholder.textContent = t.placeholder;
  trainingBtn.textContent = mode === "chat" ? t.training : t.asking;
  langBtn.textContent = t.language_toggle;
  userInput.placeholder = t.input_placeholder;
}

langBtn.addEventListener("click", () => {
  currentLang = currentLang === "en" ? "fr" : "en";
  localStorage.setItem("lang", currentLang);
  applyTranslations();
});

userInput.addEventListener("input", function () {
  this.style.height = "auto";
  const minHeight = 40;
  this.style.height = Math.max(this.scrollHeight, minHeight) + "px";
  this.style.overflowY = this.scrollHeight > 200 ? "scroll" : "hidden";
});

userInput.addEventListener("keydown", function (e) {
  if (isProcessing) {
    e.preventDefault();
    return;
  }
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
  }
});

function addMessage(text, sender = "bot") {
  const placeholder = document.getElementById("placeholder");
  if (placeholder) placeholder.remove();

  const p = document.createElement("p");
  p.className = "message " + sender;
  p.innerHTML = sender === "bot" && text.includes("<") ? text : text.replace(/\n/g, "<br>");
  messageList.appendChild(p);
  messageList.scrollTop = messageList.scrollHeight;
}

function addSeparator() {
  const hr = document.createElement("hr");
  hr.style.width = "100%";
  hr.style.border = "none";
  hr.style.borderTop = "1px solid #999";
  hr.style.margin = "20px 0";
  messageList.appendChild(hr);
}

function getTrainingQuestion() {
  if (mode !== "training") return;

  isProcessing = true;
  userInput.disabled = true;

  fetch(`http://localhost:5000/training?lang=${currentLang}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        addMessage(data.error, "bot");
        mode = "chat";
        applyTranslations();
      } else {
        currentTrainingQuestion = data;
        const { question, choices } = data;
        addMessage(
          `QCM:\n${question}\n\n` +
            `A) ${choices.A}\nB) ${choices.B}\nC) ${choices.C}\nD) ${choices.D}\n\n` +
            (currentLang === "fr"
              ? "Veuillez répondre par A, B, C ou D."
              : "Please answer A, B, C or D."),
          "bot"
        );
      }
    })
    .catch((err) => {
      addMessage(`${err}`, "bot");
      mode = "chat";
      applyTranslations();
    })
    .finally(() => {
      isProcessing = false;
      userInput.disabled = false;
    });
}

trainingBtn.addEventListener("click", () => {
  if (isProcessing) return;

  addSeparator();
  if (mode === "training") {
    mode = "chat";
    currentTrainingQuestion = null;
  } else {
    mode = "training";
    getTrainingQuestion();
  }
  applyTranslations();
});

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (isProcessing) return;

  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = "";
  userInput.style.height = "auto";

  try {
    isProcessing = true;
    userInput.disabled = true;

    if (mode === "chat") {
      const res = await fetch(`http://127.0.0.1:5000/ask?lang=${currentLang}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text, lang: currentLang })
      });
      const data = await res.json();
      addMessage(data.response || "No response", "bot");

    } else if (mode === "training" && currentTrainingQuestion?.question_id) {
      const res = await fetch(`http://127.0.0.1:5000/training_answer?lang=${currentLang}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_id: currentTrainingQuestion.question_id,
          answer: text.toUpperCase(),
          lang: currentLang
        })
      });
      const data = await res.json();
      if (data.error) {
        addMessage(data.error, "bot");
      } else {
        const tag = data.correct
          ? "<span style='color:green;'>✔ Correct!</span>"
          : "<span style='color:red;'>✘ Incorrect.</span>";
        addMessage(`${tag}<br>${data.explanation}`, "bot");

        setTimeout(() => {
          addSeparator();
          currentTrainingQuestion = null;
          getTrainingQuestion();
        }, 5000);
      }
    }
  } catch (err) {
    console.error(err);
    addMessage("Error occurred, please try again.", "bot");
  } finally {
    isProcessing = false;
    userInput.disabled = false;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
});
/* Noetfield institutional assistant — pro UI, backend-only API */
(function () {
  "use strict";

  var QUICK_PROMPTS = [
    "What is Noetfield?",
    "Trust Brief pricing",
    "Bank Pilot scope",
    "How do we engage?",
  ];

  function apiBase() {
    var host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return "http://127.0.0.1:8001";
    }
    if (
      host === "www.noetfield.com" ||
      host === "noetfield.com" ||
      host.indexOf(".vercel.app") > 0
    ) {
      return "";
    }
    var script = document.querySelector("script[data-api-base]");
    if (script && script.getAttribute("data-api-base")) {
      return String(script.getAttribute("data-api-base")).replace(/\/$/, "");
    }
    var meta = document.querySelector('meta[name="nf-chat-api-base"]');
    if (meta && meta.content) return String(meta.content).replace(/\/$/, "");
    if (host.indexOf("platform.") === 0) return window.location.origin;
    return "https://platform.noetfield.com";
  }

  function sessionId() {
    var key = "nf_chat_sid";
    try {
      var existing = localStorage.getItem(key);
      if (existing) return existing;
      var sid = "c-" + Math.random().toString(36).slice(2, 12);
      localStorage.setItem(key, sid);
      return sid;
    } catch (_) {
      return "c-anon";
    }
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  function appendMsg(log, role, text, extraClass) {
    var cls = "nfChatMsg " + role + (extraClass ? " " + extraClass : "");
    var msg = el("div", cls, text);
    log.appendChild(msg);
    log.scrollTop = log.scrollHeight;
    return msg;
  }

  function removeEl(node) {
    if (node && node.parentNode) node.parentNode.removeChild(node);
  }

  function sendMessage(log, input, sendBtn, text) {
    var t = (text || "").trim();
    if (!t) return;
    input.value = "";
    appendMsg(log, "user", t);
    sendBtn.disabled = true;
    var typing = appendMsg(log, "bot", "Thinking", "typing");
    typing.classList.add("nfChatTypingDots");

    fetch((apiBase() || "") + "/api/public/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: t, session_id: sessionId() }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (result) {
        removeEl(typing);
        if (result.ok && result.data && result.data.reply) {
          appendMsg(log, "bot", result.data.reply);
          return;
        }
        var detail =
          (result.data && result.data.detail) ||
          "Assistant is unavailable. Use /trust-brief/intake/ or email operations@noetfield.com.";
        appendMsg(log, "bot", String(detail));
      })
      .catch(function () {
        removeEl(typing);
        appendMsg(
          log,
          "bot",
          "Could not reach the assistant. Email operations@noetfield.com or visit /trust-brief/intake/."
        );
      })
      .finally(function () {
        sendBtn.disabled = false;
        input.focus();
      });
  }

  function mount() {
    if (document.getElementById("nfChatFab")) return;

    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/assets/noetfield-chat.css?v=2";
    document.head.appendChild(link);

    var fab = el("button", "nfChatFab", "✦");
    fab.id = "nfChatFab";
    fab.type = "button";
    fab.setAttribute("aria-label", "Open Noetfield assistant");

    var panel = el("div", "nfChatPanel");
    panel.id = "nfChatPanel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Noetfield assistant");

    var head = el("div", "nfChatHead");
    var mark = el("div", "nfChatHeadMark", "N");
    var headText = document.createElement("div");
    headText.className = "nfChatHeadText";
    headText.innerHTML =
      "<strong>Noetfield Assistant</strong><span>Governance · Offerings · Intake</span>";
    var closeBtn = el("button", "nfChatClose", "×");
    closeBtn.type = "button";
    closeBtn.setAttribute("aria-label", "Close");
    head.appendChild(mark);
    head.appendChild(headText);
    head.appendChild(closeBtn);

    var quick = el("div", "nfChatQuick");
    QUICK_PROMPTS.forEach(function (prompt) {
      var b = el("button", "", prompt);
      quick.appendChild(b);
    });

    var log = el("div", "nfChatLog");
    log.id = "nfChatLog";

    var note = el("div", "nfChatNote");
    note.textContent =
      "Institutional Q&A from public product sources. Not legal advice. Engagements: operations@noetfield.com";

    var form = el("form", "nfChatForm");
    var input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Ask about Trust Brief, Copilot, Bank Pilot…";
    input.autocomplete = "off";
    input.maxLength = 2000;
    input.setAttribute("aria-label", "Your question");
    var send = el("button", "", "Send");
    send.type = "submit";
    form.appendChild(input);
    form.appendChild(send);

    panel.appendChild(head);
    panel.appendChild(quick);
    panel.appendChild(log);
    panel.appendChild(note);
    panel.appendChild(form);
    document.body.appendChild(fab);
    document.body.appendChild(panel);

    appendMsg(
      log,
      "bot",
      "Welcome. I can help with Noetfield offerings, governance evaluation, and how to request a Governance Brief."
    );

    function setOpen(open) {
      panel.classList.toggle("open", open);
      fab.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) input.focus();
    }

    fab.addEventListener("click", function () {
      setOpen(!panel.classList.contains("open"));
    });
    closeBtn.addEventListener("click", function () {
      setOpen(false);
    });

    quick.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        sendMessage(log, input, send, btn.textContent || "");
      });
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      sendMessage(log, input, send, input.value);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();

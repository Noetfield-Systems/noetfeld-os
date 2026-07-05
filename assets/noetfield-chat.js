/* Noetfield institutional assistant — pro UI, backend-only API */
(function () {
  "use strict";

  var QUICK_PROMPTS = [
    "What does Noetfield do for my business?",
    "I want a Diagnostic Sprint — what's involved?",
    "We're evaluating vendors",
    "Investor diligence materials",
    "Is this channel confidential?",
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

  function track(eventName, metadata) {
    try {
      if (window.NFAnalytics && window.NFAnalytics.track) {
        window.NFAnalytics.track(eventName, Object.assign({ component: "chat" }, metadata || {}));
      }
    } catch (_) {}
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  var CITATION_LABELS = {
    "/pricing/": "Pricing",
    "/intelligence/intake/": "Diagnostic Sprint",
    "/gel/": "GEL overview",
    "/copilot/pilot/": "Copilot Governance Pack",
    "/trust-brief/": "Trust Brief",
    "/trust-brief/intake/": "Apply for Trust Brief",
    "/investors/diligence/": "Investor diligence",
    "/start/": "Free sandbox",
    "/copilot/": "Copilot overview",
  };

  function citationLabel(href) {
    var key = String(href || "").trim();
    if (CITATION_LABELS[key]) return CITATION_LABELS[key];
    return key.replace(/^\/+|\/+$/g, "").replace(/-/g, " ").replace(/\//g, " · ") || key;
  }
    return (
      href.indexOf("/") === 0 ||
      href.indexOf("https://www.noetfield.com/") === 0 ||
      href.indexOf("https://noetfield.com/") === 0 ||
      href.indexOf("mailto:operations@noetfield.com") === 0
    );
  }

  function publicHref(value) {
    var text = String(value || "").trim();
    if (!text) return "";
    if (/^operations@noetfield\.com$/i.test(text)) return "mailto:operations@noetfield.com";
    if (/^https:\/\/(www\.)?noetfield\.com\//i.test(text)) return text;
    if (/^\/[a-z0-9/_?=&.#-]*$/i.test(text)) return text;
    return "";
  }

  function appendSafeLink(parent, label, href) {
    if (!isSafeHref(href)) {
      parent.appendChild(document.createTextNode(label));
      return;
    }
    var a = document.createElement("a");
    a.href = href;
    a.textContent = label;
    if (href.indexOf("http") === 0) {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    }
    parent.appendChild(a);
  }

  function renderRichText(parent, text) {
    var source = String(text || "");
    var pattern =
      /(https:\/\/(?:www\.)?noetfield\.com\/[^\s)]+|operations@noetfield\.com|\/[a-z0-9][a-z0-9/_?=&.#-]*(?:\/)?)/gi;
    var last = 0;
    source.replace(pattern, function (match, _m, offset) {
      if (offset > last) parent.appendChild(document.createTextNode(source.slice(last, offset)));
      appendSafeLink(parent, match, publicHref(match));
      last = offset + match.length;
      return match;
    });
    if (last < source.length) parent.appendChild(document.createTextNode(source.slice(last)));
  }

  function appendCitations(msg, citations) {
    var publicCitations = (citations || [])
      .map(function (citation) {
        return String(citation || "").trim();
      })
      .filter(function (citation) {
        return publicHref(citation);
      })
      .slice(0, 4);
    if (!publicCitations.length) return;
    var wrap = el("div", "nfChatCitations");
    var label = el("span", "nfChatCitationsLabel", "Suggested links");
    wrap.appendChild(label);
    publicCitations.forEach(function (citation) {
      var chip = document.createElement("a");
      chip.href = publicHref(citation);
      chip.textContent = citationLabel(citation);
      wrap.appendChild(chip);
    });
    msg.appendChild(wrap);
  }

  function appendMsg(log, role, text, extraClass, citations) {
    var cls = "nfChatMsg " + role + (extraClass ? " " + extraClass : "");
    var msg = el("div", cls);
    if (role === "bot") {
      renderRichText(msg, text);
      appendCitations(msg, citations);
    } else {
      msg.textContent = text || "";
    }
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
    track("chat_message_sent", { length: t.length });

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
          appendMsg(log, "bot", result.data.reply, "", result.data.citations || []);
          track("chat_response_received", {
            provider: result.data.provider || "",
            citations: result.data.citations || [],
            reply_length: String(result.data.reply || "").length,
          });
          return;
        }
        var detail =
          (result.data && result.data.detail) ||
          "I’m having trouble reaching the live assistant. Try again in a moment, or use /trust-brief/intake/ if you want to share context.";
        appendMsg(log, "bot", String(detail));
        track("chat_response_error", { detail: String(detail).slice(0, 160) });
      })
      .catch(function () {
        removeEl(typing);
        appendMsg(
          log,
          "bot",
          "I couldn’t reach the live assistant. Try again in a moment, or use /trust-brief/intake/ if this is time-sensitive."
        );
        track("chat_response_error", { detail: "network_error" });
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
    link.href = "/assets/noetfield-chat.css?v=6";
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
      "<strong>Noetfield Assistant</strong><span>Executive Q&A · Governance · Intake</span>";
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
    input.placeholder = "What are you working on?";
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
      "Hi — one moment…",
      "typing"
    );
    fetch((apiBase() || "") + "/api/public/chat", { method: "GET", headers: { Accept: "application/json" } })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        var host = log.querySelector(".nfChatMsg.bot");
        if (host) removeEl(host);
        if (data && data.greeting && data.greeting.indexOf("Ask naturally") === -1) {
          appendMsg(log, "bot", data.greeting, "", data.citations || []);
          return;
        }
        appendMsg(log, "bot", "Hi — what are you working on?", "", ["/pricing/"]);
      })
      .catch(function () {
        var host = log.querySelector(".nfChatMsg.bot");
        if (host) removeEl(host);
        appendMsg(log, "bot", "Hi — what are you working on?", "", ["/pricing/"]);
      });

    function setOpen(open) {
      panel.classList.toggle("open", open);
      fab.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        track("chat_opened", {});
        input.focus();
      }
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

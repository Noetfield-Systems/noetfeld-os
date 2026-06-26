/* /assets/noetfield-shell.js — v3.0
   Noetfield Shell:
   - Inject header/footer partials
   - Burger menu (with iOS-safe scroll lock + focus handling)
   - Active links
   - Footer year
   - Feedback tab
   - RID: generate/store/display/copy + propagate to tagged links + inject into forms
   - Emits: window.__nf + event "nf:shell:ready"
   Version: 2025.12.19.2
*/
(function () {
  "use strict";

  var SHELL_VERSION = "2026.06.26.v21";
  var PARTIALS_BASE = "/assets/partials";
  var RID_KEY = "nf_rid";

  function normPath(p) {
    if (!p) return "/";
    p = String(p).split("?")[0].split("#")[0];
    if (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1);
    return p.toLowerCase();
  }

  function safeQueryAll(sel) {
    try { return document.querySelectorAll(sel); } catch (_) { return []; }
  }

  function toInternalPath(href) {
    if (!href) return null;
    if (href.startsWith("http")) {
      try {
        var u = new URL(href, window.location.origin);
        if (u.origin !== window.location.origin) return null;
        return u.pathname || "/";
      } catch (_) { return null; }
    }
    if (!href.startsWith("/")) return null;
    return href;
  }

  function setYear() {
    var y = document.getElementById("y");
    if (y) y.textContent = String(new Date().getFullYear());
  }

  function sanitizeRID(x) {
    x = (x || "").trim();
    if (!x) return "";
    x = x.replace(/[^a-zA-Z0-9\-_]/g, "").slice(0, 64);
    if (x.length < 6) return "";
    return x;
  }

  function buildUrlWithRID(href, rid) {
    try {
      var u = new URL(href, window.location.origin);
      if (u.origin !== window.location.origin) return null;
      u.searchParams.set("rid", rid);
      var qs = u.searchParams.toString();
      return u.pathname + (qs ? ("?" + qs) : "") + (u.hash || "");
    } catch (_) {
      return null;
    }
  }

  function generateRID() {
    return (
      "RID-" +
      Date.now().toString(36) +
      "-" +
      Math.random().toString(36).slice(2, 8)
    ).toUpperCase();
  }

  function getOrCreateRID() {
    var url;
    try { url = new URL(window.location.href); } catch (_) { url = null; }

    var ridFromUrl = "";
    if (url) ridFromUrl = sanitizeRID(url.searchParams.get("rid"));

    if (ridFromUrl) {
      try { localStorage.setItem(RID_KEY, ridFromUrl); } catch (_) {}
      return ridFromUrl;
    }

    var stored = "";
    try { stored = sanitizeRID(localStorage.getItem(RID_KEY)); } catch (_) {}
    if (stored) return stored;

    var rid = sanitizeRID(generateRID()) || generateRID();
    try { localStorage.setItem(RID_KEY, rid); } catch (_) {}
    return rid;
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { return true; }).catch(function () { return false; });
    }
    return new Promise(function (resolve) {
      try {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand("copy");
        document.body.removeChild(ta);
        resolve(!!ok);
      } catch (_) {
        resolve(false);
      }
    });
  }

  function applyRID(rid) {
    safeQueryAll("[data-rid]").forEach(function (el) {
      el.textContent = rid;
    });

    safeQueryAll("[data-copy-rid]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        copyText(rid).then(function (ok) {
          if (!ok) return;
          btn.setAttribute("data-copied", "1");
          setTimeout(function () { btn.removeAttribute("data-copied"); }, 900);
        });
      });
    });

    safeQueryAll("a[data-rid-link]").forEach(function (a) {
      var href = (a.getAttribute("href") || "").trim();
      if (!href) return;
      var out = buildUrlWithRID(href, rid);
      if (out) a.setAttribute("href", out);
    });

    safeQueryAll("form").forEach(function (form) {
      var ridInput = form.querySelector('input[name="rid"]');
      var reqInput = form.querySelector('input[name="request_id"]');

      if (!ridInput) {
        ridInput = document.createElement("input");
        ridInput.type = "hidden";
        ridInput.name = "rid";
        form.appendChild(ridInput);
      }
      ridInput.value = rid;

      if (!reqInput) {
        reqInput = document.createElement("input");
        reqInput.type = "hidden";
        reqInput.name = "request_id";
        form.appendChild(reqInput);
      }
      reqInput.value = rid;
    });
  }

  function setActiveLinks() {
    var current = normPath(window.location.pathname);

    var selectors = [
      "#nfHeader .menuPrimary a",
      "#nfHeader .menuActions a",
      "#nfHeader .mobileGrid a",
      "#nfFooter .footerMiniNav a"
    ].join(", ");

    safeQueryAll(selectors).forEach(function (a) {
      var hrefRaw = a.getAttribute("href") || "";
      var href = toInternalPath(hrefRaw);
      if (!href) return;

      var target = normPath(href);
      var isActive =
        (target === "/" && current === "/") ||
        (target !== "/" && (current === target || current.startsWith(target + "/")));

      if (isActive) {
        a.classList.add("active");
        a.setAttribute("aria-current", "page");
      } else {
        a.classList.remove("active");
        a.removeAttribute("aria-current");
      }
    });
  }

  // ===== iOS-safe scroll lock + focus handling =====
  var __scrollY = 0;
  function lockScroll() {
    try {
      __scrollY = window.scrollY || window.pageYOffset || 0;
      document.body.style.position = "fixed";
      document.body.style.top = "-" + __scrollY + "px";
      document.body.style.left = "0";
      document.body.style.right = "0";
      document.body.style.width = "100%";
      document.body.classList.add("navOpen");
    } catch (_) {
      document.body.classList.add("navOpen");
    }
  }
  function unlockScroll() {
    try {
      document.body.classList.remove("navOpen");
      document.body.style.position = "";
      document.body.style.top = "";
      document.body.style.left = "";
      document.body.style.right = "";
      document.body.style.width = "";
      window.scrollTo(0, __scrollY || 0);
    } catch (_) {
      document.body.classList.remove("navOpen");
    }
  }

  function trapFocus(container, e) {
    if (!container) return;
    if (e.key !== "Tab") return;

    var focusables = container.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (!focusables || !focusables.length) return;

    var first = focusables[0];
    var last = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function initBurger() {
    var burger = document.getElementById("burger");
    var panel = document.getElementById("mobilePanel");
    if (!burger || !panel) return;

    var lastFocus = null;

    function openPanel() {
      lastFocus = document.activeElement || burger;
      burger.setAttribute("aria-expanded", "true");
      panel.hidden = false;
      lockScroll();

      // focus first item for accessibility
      setTimeout(function () {
        var firstLink = panel.querySelector("a, button");
        if (firstLink && firstLink.focus) firstLink.focus();
      }, 0);
    }

    function closePanel() {
      burger.setAttribute("aria-expanded", "false");
      panel.hidden = true;
      unlockScroll();

      // restore focus
      setTimeout(function () {
        if (lastFocus && lastFocus.focus) lastFocus.focus();
      }, 0);
    }

    function toggle() {
      var isOpen = burger.getAttribute("aria-expanded") === "true";
      if (isOpen) closePanel(); else openPanel();
    }

    burger.setAttribute("aria-expanded", "false");
    panel.hidden = true;

    burger.addEventListener("click", function (e) {
      e.preventDefault();
      toggle();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && burger.getAttribute("aria-expanded") === "true") closePanel();
      if (burger.getAttribute("aria-expanded") === "true") trapFocus(panel, e);
    });

    document.addEventListener("click", function (e) {
      if (burger.getAttribute("aria-expanded") !== "true") return;
      var withinHeader = !!(e.target && e.target.closest && e.target.closest("#nfHeader"));
      if (!withinHeader) closePanel();
    });

    panel.addEventListener("click", function (e) {
      var a = e.target && e.target.closest ? e.target.closest("a") : null;
      if (a) closePanel();
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1140 && burger.getAttribute("aria-expanded") === "true") closePanel();
    });
  }

  function isGovernanceLanePath(p) {
    if (!p || p === "/") return false;
    if (p === "/intelligence" || p.startsWith("/intelligence/")) return false;
    var prefixes = [
      "/governance", "/copilot", "/trust-brief", "/bank-pilot", "/enterprise",
      "/federal", "/msp", "/ai-automation", "/trust-ledger", "/trust/",
      "/gate", "/console", "/docs/api"
    ];
    return prefixes.some(function (pre) {
      return p === pre || p.startsWith(pre + "/");
    });
  }

  function applyBodyLaneClass() {
    var p = normPath(window.location.pathname);
    document.body.classList.remove("nf-lane-intelligence", "nf-lane-governance");
    if (p === "/" || p.startsWith("/intelligence")) {
      document.body.classList.add("nf-lane-intelligence");
    } else if (isGovernanceLanePath(p)) {
      document.body.classList.add("nf-lane-governance");
    }
  }

  function normalizeFooterCTA() {
    /* Intelligence 613: footer CTAs live in footer.html partial — do not strip */
  }

  async function loadEcosystem() {
    try {
      var url =
        "/assets/noetfield-ecosystem.json?v=" + encodeURIComponent(SHELL_VERSION);
      var res = await fetch(url, { credentials: "same-origin", cache: "no-store" });
      if (!res.ok) return {};
      return await res.json();
    } catch (_) {
      return {};
    }
  }

  function applyChatApiMeta(eco) {
    var base = eco && eco.chat_api_base;
    if (!base) return;
    var meta =
      document.querySelector('meta[name="nf-chat-api-base"]') ||
      document.createElement("meta");
    meta.setAttribute("name", "nf-chat-api-base");
    meta.setAttribute("content", String(base).replace(/\/$/, ""));
    if (!meta.parentNode) document.head.appendChild(meta);
  }

  function enhanceFooterChannels(eco) {
    var footer = document.getElementById("nfFooter");
    if (!footer || footer.querySelector(".nfConnectCol")) return;

    var email = (eco && eco.intake_email) || "operations@noetfield.com";
    var tg = eco && eco.telegram_bot_username;
    var tgUser = tg ? String(tg).replace(/^@/, "") : "";

    var col = document.createElement("div");
    col.className = "fcol nfConnectCol";
    var title = document.createElement("div");
    title.className = "fTitle";
    title.textContent = "Assistant";
    var links = document.createElement("div");
    links.className = "fLinks";

    var chatBtn = document.createElement("button");
    chatBtn.type = "button";
    chatBtn.className = "nfLinkBtn";
    chatBtn.textContent = "Web chat";
    chatBtn.addEventListener("click", function () {
      var fab = document.getElementById("nfChatFab");
      if (fab) fab.click();
      else window.location.href = "/faq/#assistant";
    });
    links.appendChild(chatBtn);

    if (tgUser) {
      var tgA = document.createElement("a");
      tgA.href = "https://t.me/" + encodeURIComponent(tgUser);
      tgA.target = "_blank";
      tgA.rel = "noopener";
      tgA.textContent = "Telegram @" + tgUser;
      links.appendChild(tgA);
    }

    var mail = document.createElement("a");
    mail.href = "mailto:" + email;
    mail.textContent = email;
    links.appendChild(mail);

    col.appendChild(title);
    col.appendChild(links);
    var top = footer.querySelector(".footerTop");
    if (top) top.appendChild(col);
  }

  function ensureFeedbackTab(rid, eco) {
    var p = normPath(window.location.pathname);
    if (p === "/feedback" || p.startsWith("/feedback/")) return;
    if (document.querySelector(".feedbackTab")) return;

    var a = document.createElement("a");
    a.className = "feedbackTab";
    a.href = "/contact/?topic=feedback#contact-form";
    a.setAttribute("aria-label", "Send feedback");

    var spark = document.createElement("span");
    spark.className = "spark";
    spark.setAttribute("aria-hidden", "true");

    a.appendChild(spark);
    a.appendChild(document.createTextNode("Feedback"));
    document.body.appendChild(a);
  }

  async function injectOne(targetId, partialName) {
    var el = document.getElementById(targetId);
    if (!el) return;
    if (el.children && el.children.length > 0) return;

    var url = PARTIALS_BASE + "/" + partialName + "?v=" + encodeURIComponent(SHELL_VERSION);

    try {
      var res = await fetch(url, { credentials: "same-origin", cache: "reload" });
      if (!res.ok) return;
      var html = await res.text();
      el.innerHTML = html;
    } catch (_) {}
  }

  async function injectOfferingsStrip() {
    var header = document.getElementById("nfHeader");
    if (!header || document.querySelector(".nfOfferStrip")) return;
    var mount = document.createElement("div");
    mount.id = "nfOfferStripMount";
    header.insertAdjacentElement("afterend", mount);
    await injectOne("nfOfferStripMount", "offerings-strip.html");
    var inner = mount.querySelector(".nfOfferStrip");
    if (inner) {
      mount.replaceWith(inner);
    } else {
      mount.remove();
    }
  }

  async function injectLaneRail() {
    if (!isGovernanceLanePath(normPath(window.location.pathname))) return;
    if (document.querySelector(".nf-lane-rail")) return;
    var header = document.getElementById("nfHeader");
    if (!header) return;
    var mount = document.createElement("div");
    mount.id = "nfLaneRailMount";
    var strip = document.querySelector(".nfOfferStrip");
    if (strip) {
      strip.insertAdjacentElement("afterend", mount);
    } else {
      header.insertAdjacentElement("afterend", mount);
    }
    await injectOne("nfLaneRailMount", "intelligence-rail.html");
    var inner = mount.querySelector(".nf-lane-rail");
    if (inner) {
      mount.replaceWith(inner);
    } else {
      mount.remove();
    }
  }

  async function injectShell() {
    await injectOne("nfHeader", "header.html");
    await injectOfferingsStrip();
    await injectLaneRail();
    await injectOne("nfFooter", "footer.html");
  }

  function emitReady(rid) {
    try {
      window.__nf = { rid: rid, version: SHELL_VERSION };
      var ev = new CustomEvent("nf:shell:ready", { detail: { rid: rid, version: SHELL_VERSION } });
      window.dispatchEvent(ev);
    } catch (_) {
      window.__nf = window.__nf || {};
      window.__nf.rid = rid;
      window.__nf.version = SHELL_VERSION;
    }
  }

  function loadPublicChat() {
    if (document.querySelector('script[data-nf-chat]')) return;
    var s = document.createElement("script");
    s.src = "/assets/noetfield-chat.js";
    s.defer = true;
    s.setAttribute("data-nf-chat", "1");
    document.body.appendChild(s);
  }

  async function boot() {
    var eco = await loadEcosystem();
    window.__nfEcosystem = eco;

    await injectShell();

    applyBodyLaneClass();
    var rid = getOrCreateRID();
    applyRID(rid);

    applyChatApiMeta(eco);
    enhanceFooterChannels(eco);
    setYear();
    setActiveLinks();
    initBurger();
    normalizeFooterCTA();
    ensureFeedbackTab(rid, eco);
    loadPublicChat();

    emitReady(rid);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { boot(); });
  } else {
    boot();
  }
})();

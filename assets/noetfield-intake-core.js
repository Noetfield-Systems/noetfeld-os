/** Shared async intake — POST /api/intake, RID threading, ops webhook (background). */
(function (global) {
  "use strict";

  var INTAKE_EMAIL = "operations@noetfield.com";

  function apiBase() {
    var host = global.location && global.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return "http://127.0.0.1:8001";
    }
    if (
      host === "www.noetfield.com" ||
      host === "noetfield.com" ||
      (host && host.indexOf(".vercel.app") > 0)
    ) {
      return "";
    }
    var meta = document.querySelector('meta[name="nf-chat-api-base"]');
    if (meta && meta.content) return String(meta.content).replace(/\/$/, "");
    return "https://platform.noetfield.com";
  }

  function intakeUrl(path) {
    var base = apiBase();
    return (base ? base : "") + path;
  }

  function skuFromVector(vector) {
    var v = (vector || "").toLowerCase();
    if (v.indexOf("copilot-governance") >= 0 || v === "copilot-governance") return "copilot";
    if (v.indexOf("copilot") >= 0) return "copilot";
    if (v.indexOf("bank") >= 0) return "bank_pilot";
    if (v.indexOf("work-with-us") >= 0) return "general";
    if (v.indexOf("trust") >= 0) return "trust_brief";
    return "general";
  }

  function getRid() {
    try {
      if (global.__nf && global.__nf.rid) return global.__nf.rid;
      var fromField = document.querySelector("[data-rid-field]");
      if (fromField && fromField.value) return fromField.value;
      return localStorage.getItem("nf_rid") || "";
    } catch (_) {
      return "";
    }
  }

  function enc(v) {
    return encodeURIComponent(v || "");
  }

  function postIntake(payload) {
    return fetch(intakeUrl("/api/intake"), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
      credentials: "omit",
      keepalive: true,
    }).then(function (res) {
      if (!res.ok) {
        return res
          .json()
          .catch(function () {
            return { detail: res.statusText };
          })
          .then(function (body) {
            var err = new Error(body.detail || "Intake failed");
            err.status = res.status;
            throw err;
          });
      }
      return res.json();
    });
  }

  function checkHealth() {
    return fetch(intakeUrl("/api/intake/health"), {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "omit",
    })
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .catch(function () {
        return null;
      });
  }

  function mailtoFallback(subject, body) {
    if (global.noetfieldIntakeMailto) {
      return global.noetfieldIntakeMailto(subject, body, "intake-fallback");
    }
    return (
      "mailto:" +
      enc(INTAKE_EMAIL) +
      "?subject=" +
      enc(subject) +
      "&body=" +
      enc(body || "")
    );
  }

  function renderSuccess(container, data, opts) {
    if (!container) return;
    var rid = (data && data.request_id) || getRid() || "—";
    var intakeId = (data && data.intake_id) || "—";
    var headline = (opts && opts.headline) || "Application recorded";
    var detail =
      (opts && opts.detail) ||
      "Your intake was saved instantly. Operations is notified asynchronously — expect a reply within one business day.";
    container.hidden = false;
    container.className = "nf-intake-async-status nf-intake-async-status--ok";
    container.innerHTML =
      "<p><strong>" +
      headline +
      "</strong></p>" +
      "<p>" +
      detail +
      "</p>" +
      '<p class="nf-intake-async-meta">Intake <code>' +
      intakeId +
      "</code> · RID <code>" +
      rid +
      "</code> · async ops notify</p>" +
      ((opts && opts.extraHtml) || "");
  }

  function renderError(container, err, opts) {
    if (!container) return;
    var subject = (opts && opts.mailSubject) || "Noetfield — Intake (API fallback)";
    var body = (opts && opts.mailBody) || "Intake API unavailable. Please follow up manually.\n";
    container.hidden = false;
    container.className = "nf-intake-async-status nf-intake-async-status--err";
    container.innerHTML =
      "<p><strong>Could not reach intake API</strong></p>" +
      "<p>" +
      (err && err.message ? err.message : "Network error") +
      "</p>" +
      '<p><a class="btn btn-secondary" href="' +
      mailtoFallback(subject, body) +
      '">Email operations</a></p>';
  }

  function setButtonState(btn, state, labels) {
    if (!btn) return;
    labels = labels || {};
    if (state === "loading") {
      btn.disabled = true;
      btn.dataset.nfPrevLabel = btn.textContent;
      btn.textContent = labels.loading || "Submitting…";
    } else if (state === "done") {
      btn.disabled = true;
      btn.textContent = labels.done || "Submitted";
    } else if (state === "idle") {
      btn.disabled = false;
      btn.textContent = labels.idle || btn.dataset.nfPrevLabel || "Submit";
    }
  }

  /**
   * options: { organization, contact_email, contact_name, message, request_id,
   *            sku, vector, metadata, submitBtn, statusEl, labels, onSuccess, onError }
   */
  function submitAsync(options) {
    options = options || {};
    var btn = options.submitBtn;
    setButtonState(btn, "loading", options.labels);

    if (options.statusEl) {
      options.statusEl.hidden = true;
      options.statusEl.className = "nf-intake-async-status";
    }

    var payload = {
      organization: options.organization,
      contact_email: options.contact_email,
      contact_name: options.contact_name || null,
      message: options.message,
      request_id: options.request_id || getRid() || null,
      sku: options.sku || skuFromVector(options.vector),
      vector: options.vector || "web-intake",
      source: "web",
      metadata: options.metadata || { page: global.location.pathname },
    };

    return postIntake(payload)
      .then(function (data) {
        setButtonState(btn, "done", options.labels);
        renderSuccess(options.statusEl, data, options.successCopy);
        if (typeof options.onSuccess === "function") options.onSuccess(data);
        checkHealth().then(function (h) {
          if (h && h.enabled && options.statusEl) {
            var meta = options.statusEl.querySelector(".nf-intake-async-meta");
            if (meta) meta.textContent += " · intake API online";
          }
        });
        return data;
      })
      .catch(function (err) {
        setButtonState(btn, "idle", options.labels);
        renderError(options.statusEl, err, options.errorCopy);
        if (typeof options.onError === "function") options.onError(err);
        throw err;
      });
  }

  global.NFIntakeCore = {
    apiBase: apiBase,
    skuFromVector: skuFromVector,
    getRid: getRid,
    postIntake: postIntake,
    checkHealth: checkHealth,
    submitAsync: submitAsync,
    renderSuccess: renderSuccess,
    renderError: renderError,
    INTAKE_EMAIL: INTAKE_EMAIL,
  };
})(window);

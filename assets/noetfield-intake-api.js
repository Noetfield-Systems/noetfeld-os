/* Primary intake: POST /api/intake (Formspree removed). Mailto fallback on failure. */
(function () {
  "use strict";

  function apiBase() {
    var meta = document.querySelector('meta[name="nf-chat-api-base"]');
    if (meta && meta.content) return String(meta.content).replace(/\/$/, "");
    var host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") return "http://127.0.0.1:8001";
    return "https://platform.noetfield.com";
  }

  function skuFromVector(vector) {
    var v = (vector || "").toLowerCase();
    if (v.indexOf("copilot") >= 0) return "copilot";
    if (v.indexOf("bank") >= 0) return "bank_pilot";
    if (v.indexOf("trust") >= 0) return "trust_brief";
    return "general";
  }

  function postIntake(payload) {
    return fetch(apiBase() + "/api/intake", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "omit",
    }).then(function (res) {
      if (!res.ok) {
        return res.json().catch(function () {
          return { detail: res.statusText };
        }).then(function (body) {
          var err = new Error(body.detail || "Intake failed");
          err.status = res.status;
          throw err;
        });
      }
      return res.json();
    });
  }

  function wireForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();

      var ridEl = form.querySelector("[data-rid-field]");
      var rid = ridEl && ridEl.value ? ridEl.value : "";
      var org = (document.getElementById("tb_org") || {}).value || "";
      var email = (document.getElementById("tb_email") || {}).value || "";
      var name = (document.getElementById("tb_name") || {}).value || "";
      var notes = (document.getElementById("tb_notes") || {}).value || "";
      var vectorEl = document.getElementById("tb_intake_vector");
      var vector = vectorEl && vectorEl.value ? vectorEl.value : "trust-brief-intake";

      if (!org || !email) {
        alert("Organization and work email are required.");
        return;
      }

      var summary = "";
      try {
        if (typeof buildSummary === "function") {
          var s = buildSummary();
          if (s && s.text) summary = s.text;
          if (s && s.body) summary = s.body;
        }
      } catch (_) {}

      var message = notes || summary || "Trust Brief intake form submitted.";
      var submitBtn = form.querySelector('button[type="submit"]');
      var okWrap = document.getElementById("tbOk");
      var errWrap = document.getElementById("tbIntakeErr");

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }
      if (errWrap) errWrap.style.display = "none";

      postIntake({
        organization: org,
        contact_email: email,
        contact_name: name || null,
        message: message,
        request_id: rid || null,
        sku: skuFromVector(vector),
        vector: vector,
        source: "web",
        metadata: { page: window.location.pathname },
      })
        .then(function () {
          if (okWrap) okWrap.style.display = "block";
          if (submitBtn) submitBtn.textContent = "Sent";
          form.scrollIntoView({ behavior: "smooth", block: "end" });
        })
        .catch(function (err) {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Send intake";
          }
          if (errWrap) {
            errWrap.style.display = "block";
            errWrap.textContent =
              "Could not reach the intake API. Use Email operations or try again. (" +
              (err.message || "error") +
              ")";
          } else {
            alert("Intake API unavailable. Use Email operations@noetfield.com with your Request ID.");
          }
        });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      wireForm("tbIntakeForm");
    });
  } else {
    wireForm("tbIntakeForm");
  }
})();

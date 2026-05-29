/* Mirror trust-brief intake to platform API (Formspree remains primary). */
(function () {
  "use strict";

  function apiBase() {
    var meta = document.querySelector('meta[name="nf-chat-api-base"]');
    if (meta && meta.content) return String(meta.content).replace(/\/$/, "");
    var host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") return "http://127.0.0.1:8001";
    return "https://platform.noetfield.com";
  }

  function postIntake(payload) {
    return fetch(apiBase() + "/api/intake", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "omit",
      keepalive: true,
    }).catch(function () {
      return null;
    });
  }

  function wireForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", function () {
      var ridEl = form.querySelector("[data-rid-field]");
      var rid = ridEl && ridEl.value ? ridEl.value : "";
      var org = (document.getElementById("tb_org") || {}).value || "";
      var email = (document.getElementById("tb_email") || {}).value || "";
      var name = (document.getElementById("tb_name") || {}).value || "";
      var notes = (document.getElementById("tb_notes") || {}).value || "";
      var vectorEl = document.getElementById("tb_intake_vector");
      var vector = vectorEl && vectorEl.value ? vectorEl.value : "trust-brief-intake";

      var summary = "";
      try {
        if (typeof buildSummary === "function") {
          var s = buildSummary();
          if (s && s.text) summary = s.text;
        }
      } catch (_) {}

      var message = notes || summary || "Trust Brief intake form submitted.";
      if (!org || !email) return;

      postIntake({
        organization: org,
        contact_email: email,
        contact_name: name || null,
        message: message,
        request_id: rid || null,
        sku: "trust_brief",
        vector: vector,
        source: "web",
        metadata: { page: window.location.pathname },
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

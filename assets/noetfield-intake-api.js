/* Primary intake: POST /api/intake via NFIntakeCore (async ops notify). */
(function () {
  "use strict";

  function buildMetadata(vector) {
    var meta = { page: window.location.pathname, async: true };
    var role = (document.getElementById("tb_role") || {}).value || "";
    var band = (document.getElementById("tb_pilot_band") || {}).value || "";
    var region = (document.getElementById("tb_pilot_region") || {}).value || "";
    try {
      var sp = new URLSearchParams(window.location.search);
      if (!role && sp.get("role")) role = sp.get("role");
    } catch (_) {}

    if (window.NFIntakePilot && window.NFIntakePilot.isPilotIntake()) {
      meta.pilot_band = band || "readiness";
      if (role) meta.buyer_role = role;
    }
    if (window.NFIntakeEcosystem && window.NFIntakeEcosystem.isEcosystemIntake()) {
      meta.program_lane = role || "partner";
      if (region) meta.region = region;
    }
    if (vector) meta.vector = vector;
    return meta;
  }

  function wireForm(formId) {
    var form = document.getElementById(formId);
    if (!form || !window.NFIntakeCore) return;

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();

      var ridEl = form.querySelector("[data-rid-field]");
      var rid = ridEl && ridEl.value ? ridEl.value : window.NFIntakeCore.getRid();
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
          if (s && s.body) summary = s.body;
          else if (s && s.text) summary = s.text;
        }
      } catch (_) {}

      var isPilot = window.NFIntakePilot && window.NFIntakePilot.isPilotIntake();
      var isEco = window.NFIntakeEcosystem && window.NFIntakeEcosystem.isEcosystemIntake();
      var message =
        notes || summary ||
        (isPilot
          ? "Copilot Governance Pack pilot application submitted."
          : isEco
          ? "Work with Noetfield ecosystem application submitted."
          : "Trust Brief intake form submitted.");

      var submitBtn = form.querySelector('button[type="submit"]');
      var okWrap = document.getElementById("tbOk");
      var errWrap = document.getElementById("tbIntakeErr");

      if (errWrap) {
        errWrap.style.display = "none";
        errWrap.textContent = "";
      }
      if (okWrap) okWrap.style.display = "none";

      window.NFIntakeCore.submitAsync({
        organization: org,
        contact_email: email,
        contact_name: name || null,
        message: message,
        request_id: rid || null,
        vector: vector,
        sku: window.NFIntakeCore.skuFromVector(vector),
        metadata: buildMetadata(vector),
        submitBtn: submitBtn,
        statusEl: null,
        labels: {
          idle: isPilot
            ? "Submit pilot application"
            : isEco
            ? "Submit application"
            : "Send intake",
          loading: "Submitting…",
          done: "Submitted ✓",
        },
        successCopy: {
          headline: "Intake recorded — async ops notify",
          detail:
            "Your intake was saved instantly. Operations is notified asynchronously and replies within one business day at operations@noetfield.com.",
        },
        onSuccess: function (data) {
          if (okWrap) {
            okWrap.style.display = "block";
            var idEl = document.getElementById("tbIntakeId");
            if (idEl && data && data.intake_id) {
              idEl.textContent = data.intake_id;
            } else if (idEl) {
              idEl.textContent = "confirmation pending";
            }
          }
          form.scrollIntoView({ behavior: "smooth", block: "end" });
        },
        onError: function (err) {
          if (errWrap) {
            errWrap.style.display = "block";
            errWrap.textContent =
              "Could not reach the intake API. Use Email operations or try again. (" +
              (err.message || "error") +
              ")";
          } else {
            alert(
              "Intake API unavailable. Use operations@noetfield.com with your Request ID."
            );
          }
        },
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

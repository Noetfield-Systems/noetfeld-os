/** Status page — live intake delivery health from GET /api/intake/health */
(function () {
  "use strict";

  function badge(label, state) {
    var cls = "nf-signal-badge nf-signal-badge--" + state;
    return (
      '<div class="nf-trust-signal"><span class="nf-trust-signal-label">' +
      label +
      '</span><span class="' +
      cls +
      '">' +
      (state === "available" ? "Ready" : state === "orientation" ? "Partial" : "Pending") +
      "</span></div>"
    );
  }

  function render(host, h) {
    if (!host || !h) return;
    var www = h.www_email_configured === true;
    var platform = h.platform_intake_enabled === true;
    var enabled = h.enabled === true;
    var mode = h.delivery_mode || "unconfigured";

    host.innerHTML =
      badge("Form intake API", enabled ? "available" : "orientation") +
      badge("WWW email (Resend)", www ? "available" : "orientation") +
      badge("Platform intake store", platform ? "available" : "orientation") +
      badge("Auto-ack to submitter", h.auto_ack_enabled ? "available" : "na") +
      '<p class="nf-section-lead" style="margin-top:12px">Delivery mode: <code>' +
      mode +
      "</code> · Inbox: <code>" +
      (h.intake_email || "operations@noetfield.com") +
      "</code></p>";
  }

  function init() {
    var host = document.querySelector("[data-intake-health-host]");
    if (!host || !window.NFIntakeCore) return;
    host.innerHTML =
      badge("Form intake API", "orientation") +
      badge("WWW email (Resend)", "orientation") +
      badge("Platform intake store", "orientation") +
      badge("Auto-ack to submitter", "orientation");
    window.NFIntakeCore.checkHealth().then(function (h) {
      render(host, h);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

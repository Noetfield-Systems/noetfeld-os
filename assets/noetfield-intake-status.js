/** Status + /next/ — live intake health + ops status (factory-first law) */
(function () {
  "use strict";

  function badge(label, state) {
    var cls =
      "nf-signal-badge nf-signal-badge--" +
      (state === "deferred" ? "roadmap" : state);
    var text =
      state === "available"
        ? "Ready"
        : state === "deferred" || state === "roadmap"
          ? "Deferred"
          : state === "orientation"
            ? "Partial"
            : state === "na"
              ? "N/A"
              : "Pending";
    return (
      '<div class="nf-trust-signal"><span class="nf-trust-signal-label">' +
      label +
      '</span><span class="' +
      cls +
      '">' +
      text +
      "</span></div>"
    );
  }

  function opsNextSteps(wwwReady) {
    if (wwwReady) {
      return (
        '<aside class="nf-callout nf-callout--urgency" style="margin-top:16px">' +
        "<p><strong>Intake email live.</strong> Forms notify operations@noetfield.com · Reply-To = submitter.</p>" +
        "</aside>"
      );
    }
    return (
      '<aside class="nf-callout" style="margin-top:16px">' +
      "<p><strong>Google Workspace inbox is live.</strong> Direct email to operations@noetfield.com works. " +
      "WWW form auto-send (Resend) is <strong>deferred until after factory</strong> — not the current P0. " +
      '<a href="/next/#next-ops">Ops status →</a></p>' +
      "</aside>"
    );
  }

  function render(host, h) {
    if (!host || !h) return;
    var www = h.www_email_configured === true;
    var platform = h.platform_intake_enabled === true;
    var enabled = h.enabled === true;
    var mode = h.delivery_mode || "unconfigured";

    host.innerHTML =
      badge("Google Workspace inbox", "available") +
      badge("Form intake API", enabled ? "available" : "orientation") +
      badge("WWW form email (Resend)", www ? "available" : "deferred") +
      badge("Platform intake store", platform ? "available" : "orientation") +
      badge("Auto-ack to submitter", h.auto_ack_enabled ? "available" : "na") +
      '<p class="nf-section-lead" style="margin-top:12px">Delivery mode: <code>' +
      mode +
      "</code> · Inbox: <code>" +
      (h.intake_email || "operations@noetfield.com") +
      "</code></p>" +
      opsNextSteps(www || enabled);
  }

  function initHost(host) {
    if (!host || !window.NFIntakeCore) return;
    host.innerHTML =
      badge("Google Workspace inbox", "available") +
      badge("Form intake API", "orientation") +
      badge("WWW form email (Resend)", "deferred") +
      badge("Platform intake store", "orientation") +
      badge("Auto-ack to submitter", "na");
    window.NFIntakeCore.checkHealth().then(function (h) {
      render(host, h);
    });
  }

  function init() {
    document.querySelectorAll("[data-intake-health-host]").forEach(initHost);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

/** Status + /next/ — live intake + sandbox health (www spine law) */
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

  function opsNextSteps(h) {
    var www = h && h.www_email_configured === true;
    var enabled = h && h.enabled === true;
    if (www && enabled) {
      return (
        '<aside class="nf-callout nf-callout--urgency" style="margin-top:16px">' +
        "<p><strong>Form intake live.</strong> Submissions notify " +
        (h.intake_email || "operations@noetfield.com") +
        " via Resend · Reply-To = submitter · auto-ack when enabled.</p>" +
        "</aside>"
      );
    }
    if (enabled) {
      return (
        '<aside class="nf-callout" style="margin-top:16px">' +
        "<p><strong>Form intake API ready.</strong> Direct email to " +
        (h.intake_email || "operations@noetfield.com") +
        " always works. " +
        '<a href="/next/#next-ops">Ops checklist →</a></p>' +
        "</aside>"
      );
    }
    return (
      '<aside class="nf-callout" style="margin-top:16px">' +
      "<p><strong>Google Workspace inbox is live.</strong> Email " +
      (h && h.intake_email ? h.intake_email : "operations@noetfield.com") +
      " directly. Form delivery is being verified — " +
      '<a href="/next/#next-ops">Ops status →</a></p>' +
      "</aside>"
    );
  }

  function renderIntake(host, h) {
    if (!host || !h) return;
    var www = h.www_email_configured === true;
    var platform = h.platform_intake_enabled === true;
    var enabled = h.enabled === true;
    var mode = h.delivery_mode || "unconfigured";

    host.innerHTML =
      badge("Google Workspace inbox", "available") +
      badge("Form intake API", enabled ? "available" : "orientation") +
      badge("WWW form email (Resend)", www ? "available" : "orientation") +
      badge("Platform intake store", platform ? "available" : "orientation") +
      badge("Platform spine", h.platform_reachable ? "available" : "orientation") +
      badge("Auto-ack to submitter", h.auto_ack_enabled ? "available" : "na") +
      '<p class="nf-section-lead" style="margin-top:12px">Delivery mode: <code>' +
      mode +
      "</code> · Inbox: <code>" +
      (h.intake_email || "operations@noetfield.com") +
      "</code></p>" +
      opsNextSteps(h);
  }

  function initIntakeHost(host) {
    if (!host || !window.NFIntakeCore) return;
    host.innerHTML =
      badge("Google Workspace inbox", "available") +
      badge("Form intake API", "orientation") +
      badge("WWW form email (Resend)", "orientation") +
      badge("Platform intake store", "orientation") +
      badge("Platform spine", "orientation") +
      badge("Auto-ack to submitter", "na");
    window.NFIntakeCore.checkHealth().then(function (h) {
      renderIntake(host, h);
    });
  }

  function renderSandbox(host, healthOk, evalOk, rid) {
    if (!host) return;
    host.innerHTML =
      badge("WWW liveness (/api/health)", healthOk ? "available" : "orientation") +
      badge("Sandbox evaluate (POST /evaluate)", evalOk ? "available" : "orientation") +
      badge("Decision record ID", rid ? "available" : "na") +
      '<p class="nf-section-lead" style="margin-top:12px">' +
      (evalOk
        ? "Sandbox spine responds on www — trial evaluate returns a Request ID."
        : "Sandbox evaluate check pending or unavailable — contact operations@noetfield.com for pilot API keys.") +
      (rid ? ' Last RID: <code>' + rid + "</code>" : "") +
      "</p>";
  }

  function initSandboxHost(host) {
    if (!host) return;
    host.innerHTML =
      badge("WWW liveness", "orientation") +
      badge("Sandbox evaluate", "orientation") +
      badge("Decision record ID", "orientation");

    var healthOk = false;
    var evalOk = false;
    var rid = "";

    fetch("/api/health", { headers: { Accept: "application/json" } })
      .then(function (r) {
        healthOk = r.ok;
        return r.json().catch(function () {
          return {};
        });
      })
      .then(function () {
        var payload = JSON.stringify({
          actor: "status-widget",
          action: "health-check",
          context: "www status page",
          metadata: {},
        });
        return fetch("/evaluate", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: payload,
        }).then(function (r) {
          evalOk = r.ok;
          return r.json().catch(function () {
            return {};
          });
        });
      })
      .then(function (data) {
        rid = (data && data.rid) || "";
        renderSandbox(host, healthOk, evalOk, rid);
      })
      .catch(function () {
        renderSandbox(host, healthOk, false, "");
      });
  }

  function init() {
    document.querySelectorAll("[data-intake-health-host]").forEach(initIntakeHost);
    document.querySelectorAll("[data-sandbox-health-host]").forEach(initSandboxHost);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

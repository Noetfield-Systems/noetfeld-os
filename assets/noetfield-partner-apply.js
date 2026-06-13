/** Work with Noetfield — async ecosystem apply (no redirect). */
(function () {
  "use strict";

  function roleLabel(role) {
    var map = {
      connector: "Connector",
      facilitator: "Facilitator",
      "co-partner": "Co-partner",
      partner: "Partner · MSP / SI / advisory",
      investor: "Investor · capital / strategic",
    };
    return map[role] || role || "Ecosystem partner";
  }

  function buildMessage(fields) {
    return (
      "Noetfield — Work With Us (async application)\n" +
      "Program lane: " +
      roleLabel(fields.role) +
      "\n" +
      "Organization: " +
      fields.org +
      "\n" +
      "Work email: " +
      fields.email +
      "\n" +
      "Geography: " +
      (fields.region || "—") +
      "\n" +
      "Notes: " +
      (fields.notes || "—") +
      "\n" +
      "Commercial attach: Copilot Governance Pack · $2k–10k\n" +
      "Disclosure: Non-confidential · final partner agreement after review.\n"
    );
  }

  function bind() {
    var form = document.getElementById("nfPartnerApplyForm");
    if (!form || !window.NFIntakeCore) return;

    var statusEl = document.getElementById("nfPartnerApplyStatus");

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var email = (form.querySelector('[name="email"]') || {}).value || "";
      var org = (form.querySelector('[name="org"]') || {}).value || "";
      var role = (form.querySelector('[name="role"]') || {}).value || "";
      var region = (form.querySelector('[name="region"]') || {}).value || "";
      var notes = (form.querySelector('[name="notes"]') || {}).value || "";

      if (!email || !org || !role) {
        if (statusEl) {
          statusEl.hidden = false;
          statusEl.className = "nf-intake-async-status nf-intake-async-status--err";
          statusEl.innerHTML =
            "<p><strong>Missing fields</strong></p><p>Work email, organization, and program lane are required.</p>";
        }
        return;
      }

      var msg = buildMessage({ email: email, org: org, role: role, region: region, notes: notes });

      window.NFIntakeCore.submitAsync({
        organization: org,
        contact_email: email,
        message: msg,
        vector: "work-with-us",
        sku: "general",
        metadata: {
          page: window.location.pathname,
          program_lane: role,
          region: region,
          async: true,
        },
        submitBtn: form.querySelector('button[type="submit"]'),
        statusEl: statusEl,
        labels: {
          idle: "Submit application",
          loading: "Submitting…",
          done: "Submitted ✓",
        },
        successCopy: {
          headline: "Application recorded — async handoff to operations",
          detail:
            fields.role === "investor"
              ? "Your investor inquiry was saved instantly. We share the Land · Expand · Channel brief and follow up within one business day."
              : "Your ecosystem application was saved instantly. Partner review and enablement orientation follow within one business day.",
          extraHtml:
            (fields.role === "investor"
              ? '<p class="nf-section-lead" style="margin-top:10px"><a href="/investors/">Investor brief</a> · <a href="/copilot/demo/">5-minute demo</a>'
              : '<p class="nf-section-lead" style="margin-top:10px"><a href="/copilot/demo/">5-minute demo</a> · <a href="/start/">Try sandbox</a>') +
            ' · <a href="/trust-brief/intake/?interest=partner&amp;vector=work-with-us&amp;role=' +
            encodeURIComponent(role) +
            "&amp;email=" +
            encodeURIComponent(email) +
            "&amp;org=" +
            encodeURIComponent(org) +
            '">Add scope details</a></p>',
        },
        errorCopy: {
          mailSubject: "Noetfield — Work with us application",
          mailBody: msg,
        },
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();

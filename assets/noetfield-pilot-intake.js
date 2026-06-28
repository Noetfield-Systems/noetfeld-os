/** Copilot Governance Pack — async pilot apply (no redirect). */
(function () {
  "use strict";

  function roleLabel(role) {
    var map = {
      ciso: "CISO / Security",
      grc: "GRC / Compliance",
      legal: "Legal / Procurement",
      board: "Board / Risk committee",
      it: "IT / Copilot owner",
    };
    return map[role] || role || "—";
  }

  function bandLabel(band) {
    var map = {
      quickscan: "QuickScan · $2k–$3.5k · 4 weeks",
      readiness: "Readiness Pilot · $5k–10k · 90 days",
    };
    return map[band] || band || "Readiness Pilot";
  }

  function track(eventName, metadata) {
    try {
      if (window.NFAnalytics && window.NFAnalytics.track) {
        window.NFAnalytics.track(eventName, metadata || {});
      }
    } catch (_) {}
  }

  function buildMessage(fields) {
    return (
      "Noetfield — Copilot Governance Pack (async pilot application)\n" +
      "Organization: " +
      fields.org +
      "\n" +
      "Work email: " +
      fields.email +
      "\n" +
      "Role: " +
      roleLabel(fields.role) +
      "\n" +
      "Pilot band: " +
      bandLabel(fields.band) +
      "\n" +
      "Timeline: " +
      (fields.timeline || "—") +
      "\n" +
      "Evidence readiness: " +
      (fields.evidence || "—") +
      "\n" +
      "Success meeting: " +
      (fields.success_meeting || "—") +
      "\n" +
      "Notes: " +
      (fields.notes || "—") +
      "\n" +
      "Success signal: board PDF in a real governance meeting.\n"
    );
  }

  function bind() {
    var form = document.getElementById("nfPilotApplyForm");
    if (!form || !window.NFIntakeCore) return;

    var statusEl = document.getElementById("nfPilotApplyStatus");
    var vector =
      (form.getAttribute("data-vector") || "copilot-governance").trim();

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var email = (form.querySelector('[name="email"]') || {}).value || "";
      var org = (form.querySelector('[name="org"]') || {}).value || "";
      var role = (form.querySelector('[name="role"]') || {}).value || "";
      var band = (form.querySelector('[name="band"]') || {}).value || "readiness";
      var timeline = (form.querySelector('[name="timeline"]') || {}).value || "";
      var evidence = (form.querySelector('[name="evidence"]') || {}).value || "";
      var successMeeting = (form.querySelector('[name="success_meeting"]') || {}).value || "";
      var notes = (form.querySelector('[name="notes"]') || {}).value || "";

      if (!email || !org) {
        if (statusEl) {
          statusEl.hidden = false;
          statusEl.className = "nf-intake-async-status nf-intake-async-status--err";
          statusEl.innerHTML =
            "<p><strong>Missing fields</strong></p><p>Work email and organization are required.</p>";
        }
        return;
      }

      var msg = buildMessage({
        email: email,
        org: org,
        role: role,
        band: band,
        timeline: timeline,
        evidence: evidence,
        success_meeting: successMeeting,
        notes: notes,
      });
      var intakeUrl =
        form.getAttribute("data-intake") ||
        "/trust-brief/intake/?interest=pilot&vector=copilot-governance";

      window.NFIntakeCore.submitAsync({
        organization: org,
        contact_email: email,
        message: msg,
        vector: vector,
        sku: "copilot",
        metadata: {
          page: window.location.pathname,
          pilot_band: band,
          buyer_role: role,
          timeline: timeline,
          evidence_readiness: evidence,
          success_meeting: successMeeting,
          contact_email: email,
          organization: org,
          vector: vector,
          async: true,
        },
        submitBtn: form.querySelector('button[type="submit"]'),
        statusEl: statusEl,
        labels: {
          idle: "Submit pilot intake",
          loading: "Submitting…",
          done: "Submitted ✓",
        },
        successCopy: {
          headline: "Pilot application recorded — async ops notify",
          detail:
            "Your Copilot Governance Pack application was saved instantly. Operations follows up within one business day with kickoff and M365 scoping.",
          extraHtml:
            '<p class="nf-section-lead" style="margin-top:10px"><a href="/copilot/demo/">5-minute demo</a> · <a href="/start/">Start sandbox</a> · <a href="' +
            intakeUrl +
            "&email=" +
            encodeURIComponent(email) +
            "&org=" +
            encodeURIComponent(org) +
            "&role=" +
            encodeURIComponent(role) +
            "&band=" +
            encodeURIComponent(band) +
            '">Complete full intake</a></p>',
        },
        errorCopy: {
          mailSubject: "Noetfield — Copilot Governance Pack pilot application",
          mailBody: msg,
        },
        onSuccess: function () {
          track("form_submit", {
            component: "form",
            form_id: form.id || "",
            vector: vector,
            sku: "copilot",
            page: window.location.pathname,
            contact_email: email,
            organization: org,
            role: role,
            pilot_band: band,
            timeline: timeline,
            evidence_readiness: evidence,
            success_meeting: successMeeting,
          });
        },
        onError: function (err) {
          track("form_submit_error", {
            component: "form",
            form_id: form.id || "",
            vector: vector,
            sku: "copilot",
            page: window.location.pathname,
            status: err && err.status ? err.status : 0,
          });
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

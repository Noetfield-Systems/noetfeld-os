/** Site-wide form wiring — every public form → POST /api/intake (async ops notify). */
(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function rid() {
    if (window.NFIntakeCore) return window.NFIntakeCore.getRid();
    try {
      return localStorage.getItem("nf_rid") || "";
    } catch (_) {
      return "";
    }
  }

  function field(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    return el && el.value ? String(el.value).trim() : "";
  }

  function statusEl(form) {
    return (
      form.querySelector("[data-nf-intake-status]") ||
      document.getElementById(form.getAttribute("data-status-id") || "")
    );
  }

  function markBound(form) {
    form.dataset.nfIntakeBound = "1";
  }

  function isBound(form) {
    return form.dataset.nfIntakeBound === "1" && form.dataset.nfIntakeCustom !== "1";
  }

  function fireIntake(opts) {
    if (!window.NFIntakeCore) return;
    window.NFIntakeCore.submitAsync(opts).catch(function () {});
  }

  function bindGenericForm(form) {
    if (!form || isBound(form)) return;
    if (form.id === "tbIntakeForm") return;
    if (form.id === "nfPartnerApplyForm" || form.id === "nfPilotApplyForm") return;
    if (form.id === "nfLiveProofForm" || form.id === "nfTrialEvaluateForm") return;

    markBound(form);

    form.addEventListener("submit", function (ev) {
      if (!window.NFIntakeCore) return;
      ev.preventDefault();

      var email = field(form, "email") || field(form, "contact_email");
      var org = field(form, "org") || field(form, "organization");
      var name = field(form, "name") || field(form, "contact_name");
      var notes = field(form, "notes") || field(form, "message");
      var topic = field(form, "topic") || field(form, "role") || field(form, "subject");
      var role = field(form, "role");

      if (!email || email.indexOf("@") < 1) {
        var st = statusEl(form);
        if (st) {
          st.hidden = false;
          st.className = "nf-intake-async-status nf-intake-async-status--err";
          st.innerHTML = "<p><strong>Work email required</strong></p>";
        } else {
          alert("Work email is required.");
        }
        return;
      }

      if (!org) org = topic || "Web inquiry";

      var vector = form.getAttribute("data-intake-vector") || "web-intake";
      var sku = form.getAttribute("data-intake-sku") || window.NFIntakeCore.skuFromVector(vector);
      var headline = form.getAttribute("data-intake-headline") || "Message recorded — async ops notify";
      var detail =
        form.getAttribute("data-intake-detail") ||
        "Your message was saved instantly. Operations replies within one business day.";

      var message =
        notes ||
        "Noetfield — web form submission\n" +
          "Page: " +
          location.pathname +
          "\n" +
          (topic ? "Topic: " + topic + "\n" : "") +
          (name ? "Name: " + name + "\n" : "") +
          "Organization: " +
          org +
          "\n" +
          "Email: " +
          email +
          "\n";

      fireIntake({
        organization: org,
        contact_email: email,
        contact_name: name || null,
        message: message,
        request_id: rid() || null,
        vector: vector,
        sku: sku,
        metadata: {
          page: location.pathname,
          form_id: form.id || "",
          topic: topic || "",
          role: role || topic || "",
          async: true,
        },
        submitBtn: form.querySelector('button[type="submit"]'),
        statusEl: statusEl(form),
        labels: {
          idle: form.getAttribute("data-submit-label") || "Submit",
          loading: "Submitting…",
          done: "Submitted ✓",
        },
        successCopy: { headline: headline, detail: detail },
        errorCopy: {
          mailSubject: "Noetfield — " + (topic || "Contact"),
          mailBody: message,
        },
      });
    });
  }

  function bindSandboxLead(form) {
    if (!form || form.dataset.nfLeadBound === "1") return;
    form.dataset.nfLeadBound = "1";

    form.addEventListener(
      "submit",
      function () {
        if (!window.NFIntakeCore) return;
        var email = field(form, "email");
        if (!email || email.indexOf("@") < 1) return;
        var org = field(form, "org") || "Sandbox signup";
        fireIntake({
          organization: org,
          contact_email: email,
          message:
            "Noetfield — Sandbox / developer access signup\nPage: " +
            location.pathname +
            "\nOrganization: " +
            org +
            "\n",
          vector: "sandbox-signup",
          sku: "general",
          metadata: { page: location.pathname, form_id: form.id, async: true },
          submitBtn: null,
          statusEl: null,
        });
      },
      true
    );
  }

  function bindAll() {
    document.querySelectorAll("[data-nf-intake-form]").forEach(bindGenericForm);
    bindSandboxLead(document.getElementById("nfSandboxForm"));
    bindSandboxLead(document.getElementById("nfTrialAccountForm"));

    try {
      var sp = new URLSearchParams(location.search);
      var topic = sp.get("topic");
      var form = document.getElementById("nfContactForm");
      if (topic && form) {
        var sel = form.querySelector('[name="topic"]');
        if (sel) sel.value = topic;
      }
    } catch (_) {}
  }

  ready(function () {
    bindAll();
    window.addEventListener("nf:shell:ready", bindAll);
  });
})();

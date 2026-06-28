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

  function track(eventName, metadata) {
    try {
      if (window.NFAnalytics && window.NFAnalytics.track) {
        window.NFAnalytics.track(eventName, metadata || {});
      }
    } catch (_) {}
  }

  function formMeta(form, step) {
    return {
      component: "form",
      form_id: form.id || "",
      vector: form.getAttribute("data-intake-vector") || form.getAttribute("data-vector") || "web-intake",
      sku: form.getAttribute("data-intake-sku") || "",
      page: location.pathname,
      step_index: step ? step.index : undefined,
      step_id: step ? step.id : undefined,
      step_label: step ? step.label : undefined,
    };
  }

  function bindMultiStepForm(form) {
    if (!form || form.dataset.nfMultiStepBound === "1") return;
    var panels = Array.prototype.slice.call(form.querySelectorAll("[data-nf-form-step]"));
    if (panels.length < 2) return;
    form.dataset.nfMultiStepBound = "1";

    var current = 0;
    var progress = Array.prototype.slice.call(form.querySelectorAll("[data-nf-step-target]"));

    function stepInfo(index) {
      var panel = panels[index];
      return {
        index: index + 1,
        id: panel ? panel.getAttribute("data-nf-form-step") || String(index + 1) : "",
        label: panel ? panel.getAttribute("data-step-label") || "" : "",
      };
    }

    function setStep(index, reason) {
      current = Math.max(0, Math.min(index, panels.length - 1));
      panels.forEach(function (panel, panelIndex) {
        var active = panelIndex === current;
        panel.hidden = !active;
        panel.setAttribute("aria-hidden", active ? "false" : "true");
        Array.prototype.slice.call(panel.querySelectorAll("input, select, textarea, button")).forEach(function (fieldEl) {
          if (fieldEl.hasAttribute("data-nf-step-back") || fieldEl.hasAttribute("data-nf-step-next")) return;
          fieldEl.disabled = !active;
        });
      });
      progress.forEach(function (item, itemIndex) {
        item.classList.toggle("is-active", itemIndex === current);
        item.classList.toggle("is-complete", itemIndex < current);
        item.setAttribute("aria-current", itemIndex === current ? "step" : "false");
      });
      track("form_step_view", Object.assign(formMeta(form, stepInfo(current)), { reason: reason || "init" }));
    }

    function validateCurrentStep() {
      var fields = Array.prototype.slice.call(panels[current].querySelectorAll("input, select, textarea"));
      for (var i = 0; i < fields.length; i += 1) {
        if (!fields[i].checkValidity()) {
          fields[i].reportValidity();
          return false;
        }
      }
      return true;
    }

    form.addEventListener("click", function (ev) {
      var next = ev.target.closest("[data-nf-step-next]");
      var back = ev.target.closest("[data-nf-step-back]");
      if (next) {
        ev.preventDefault();
        if (!validateCurrentStep()) return;
        track("form_step_complete", formMeta(form, stepInfo(current)));
        setStep(current + 1, "next");
      }
      if (back) {
        ev.preventDefault();
        setStep(current - 1, "back");
        track("form_step_back", formMeta(form, stepInfo(current)));
      }
    });

    form.addEventListener("submit", function (ev) {
      if (current < panels.length - 1) {
        ev.preventDefault();
        if (!validateCurrentStep()) return;
        track("form_step_complete", formMeta(form, stepInfo(current)));
        setStep(current + 1, "submit-next");
        return;
      }
      track("form_step_complete", Object.assign(formMeta(form, stepInfo(current)), { final: true }));
    }, true);

    setStep(0, "init");
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
      var engagement = field(form, "engagement");
      var dealStage = field(form, "deal_stage");
      var targetContext = field(form, "target_context");

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
      if (topic === "investor-diligence") vector = "investor-diligence";
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
          (engagement ? "Engagement: " + engagement + "\n" : "") +
          (dealStage ? "Deal stage: " + dealStage + "\n" : "") +
          (targetContext ? "Target context: " + targetContext + "\n" : "") +
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
          engagement: engagement || "",
          deal_stage: dealStage || "",
          target_context: targetContext || "",
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
      track("form_submit", {
        component: "form",
        form_id: form.id || "",
        vector: vector,
        sku: sku,
        topic: topic || "",
        page: location.pathname,
        contact_email: email,
        organization: org,
        contact_name: name || "",
        engagement: engagement || "",
        deal_stage: dealStage || "",
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
        track("form_submit", {
          component: "form",
          form_id: form.id || "",
          vector: "sandbox-signup",
          sku: "general",
          page: location.pathname,
          contact_email: email,
          organization: org,
        });
      },
      true
    );
  }

  function bindAll() {
    document.querySelectorAll("[data-nf-multistep-form]").forEach(bindMultiStepForm);
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

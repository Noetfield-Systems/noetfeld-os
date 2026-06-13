/** Work-with-us / ecosystem partner intake — ?interest=partner&vector=work-with-us */
(function (global) {
  "use strict";

  var ROLE_LABELS = {
    connector: "Connector",
    facilitator: "Facilitator",
    "co-partner": "Co-partner",
    partner: "Partner · MSP / SI / advisory",
  };

  function queryParams() {
    try {
      return new URLSearchParams(location.search);
    } catch (_) {
      return new URLSearchParams();
    }
  }

  function isEcosystemIntake() {
    var sp = queryParams();
    var vector = (sp.get("vector") || "").toLowerCase();
    return vector === "work-with-us";
  }

  function roleLabel(key) {
    return ROLE_LABELS[key] || "Ecosystem partner";
  }

  function buildEcosystemSummary(ctx) {
    var sp = queryParams();
    var role = sp.get("role") || "partner";
    var rid = (ctx && ctx.rid) || "—";
    var org = (document.getElementById("tb_org") || {}).value || sp.get("org") || "";
    var email = (document.getElementById("tb_email") || {}).value || sp.get("email") || "";
    var name = (document.getElementById("tb_name") || {}).value || "";
    var notes = (document.getElementById("tb_notes") || {}).value || "";
    var vector = (ctx && ctx.intakeVector) ? ctx.intakeVector() : "work-with-us";

    var line =
      "Work with Noetfield · " +
      roleLabel(role) +
      " · Copilot Governance Pack ecosystem attach";

    var body =
      "Noetfield — Work With Us (Ecosystem Intake)\n" +
      "Request ID: " +
      rid +
      "\n" +
      (name ? "Name: " + name + "\n" : "") +
      (email ? "Work email: " + email + "\n" : "") +
      (org ? "Organization: " + org + "\n" : "") +
      "Program lane: " +
      roleLabel(role) +
      "\n" +
      "Source vector: " +
      vector +
      "\n" +
      "Commercial attach: Copilot Governance Pack · $2k–10k pilot referrals / co-delivery\n" +
      "Notes (high-level): " +
      (notes || "—") +
      "\n" +
      "Disclosure: Non-confidential intake only. Final partner agreement confirmed after review.\n";

    return {
      rid: rid,
      tierName: "Work with Noetfield · " + roleLabel(role),
      priceLabel: "Program review",
      line: line,
      body: body,
    };
  }

  function applyDomMode() {
    if (!isEcosystemIntake()) return false;
    if (global.NFIntakePilot && global.NFIntakePilot.isPilotIntake()) return false;

    document.body.classList.add("intake-ecosystem-mode");
    document.title = "Noetfield — Work With Us Application";

    var tbHero = document.getElementById("intakeHeroTrustBrief");
    var ecoHero = document.getElementById("intakeHeroEcosystem");
    if (tbHero) tbHero.hidden = true;
    if (ecoHero) ecoHero.hidden = false;

    var pkg = document.querySelector('#tbIntakeForm input[name="package"]');
    if (pkg) pkg.value = "work-with-us";

    var vec = document.getElementById("tb_intake_vector");
    if (vec) vec.value = "work-with-us";

    var sticky = document.getElementById("intakeStickyCta");
    if (sticky) sticky.hidden = true;

    var prepareTb = document.getElementById("tbPrepareTrustBrief");
    var prepareEco = document.getElementById("tbPrepareEcosystem");
    if (prepareTb) prepareTb.hidden = true;
    if (prepareEco) prepareEco.hidden = false;

    var trustEstimator = document.querySelector(".tb-estimator-fields");
    var pilotScope = document.querySelector(".pilot-scope-fields");
    if (trustEstimator) trustEstimator.hidden = true;
    if (pilotScope) pilotScope.hidden = true;

    var formTitle = document.getElementById("tbFormTitle");
    var formLead = document.getElementById("tbFormLead");
    if (formTitle) formTitle.textContent = "Ecosystem application";
    if (formLead) {
      formLead.textContent =
        "Tell us how you connect, facilitate, co-deliver, or partner on Copilot Governance Pack programs.";
    }

    var submitBtn = document.querySelector('#tbIntakeForm button[type="submit"]');
    if (submitBtn) submitBtn.textContent = "Submit application";

    var tierLabel = document.getElementById("tbTierLabel");
    if (tierLabel) tierLabel.textContent = "Program lane";
    var tierRailTitle = document.getElementById("tbTierRailTitle");
    if (tierRailTitle) tierRailTitle.textContent = "Application summary";
    var tierRailLead = document.getElementById("tbTierRailLead");
    if (tierRailLead) {
      tierRailLead.textContent = "Connector · facilitator · co-partner · partner paths.";
    }

    var routingCopy = document.getElementById("tbRoutingCopy");
    if (routingCopy) {
      routingCopy.textContent =
        "Operations reviews ecosystem applications within one business day. Include your Request ID in email follow-ups.";
    }

    var tbRouting = document.getElementById("tbRoutingActionsTrustBrief");
    var ecoRouting = document.getElementById("tbRoutingActionsEcosystem");
    if (tbRouting) tbRouting.hidden = true;
    if (ecoRouting) ecoRouting.hidden = false;

    var formTbActions = document.getElementById("tbFormActionsTrustBrief");
    if (formTbActions) formTbActions.hidden = true;

    var backLink = document.getElementById("tbBackLink");
    if (backLink) {
      backLink.textContent = "Back to Work with us";
      backLink.href = "/work-with-us/";
    }

    var nextStep = document.getElementById("tbNextStepNotice");
    if (nextStep) {
      nextStep.innerHTML =
        "<strong>Next step:</strong> partner review → enablement orientation → first attached Copilot Governance Pack pilot or intro.";
    }

    prefillFromQuery();
    return true;
  }

  function prefillFromQuery() {
    var sp = queryParams();
    var map = [
      ["email", "tb_email"],
      ["org", "tb_org"],
      ["organization", "tb_org"],
      ["name", "tb_name"],
    ];
    map.forEach(function (pair) {
      var val = sp.get(pair[0]);
      if (!val) return;
      var el = document.getElementById(pair[1]);
      if (el) el.value = val;
    });
    try {
      var raw = sessionStorage.getItem("nf_partner_intake_notes");
      if (raw) {
        var data = JSON.parse(raw);
        if (data.email && document.getElementById("tb_email")) {
          document.getElementById("tb_email").value = data.email;
        }
        if (data.org && document.getElementById("tb_org")) {
          document.getElementById("tb_org").value = data.org;
        }
        if (data.notes && document.getElementById("tb_notes")) {
          document.getElementById("tb_notes").value = data.notes;
        }
      }
    } catch (_) {}
  }

  global.NFIntakeEcosystem = {
    isEcosystemIntake: isEcosystemIntake,
    buildEcosystemSummary: buildEcosystemSummary,
    applyDomMode: applyDomMode,
    roleLabel: roleLabel,
  };
})(window);

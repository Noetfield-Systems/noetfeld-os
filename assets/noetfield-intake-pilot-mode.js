/** Copilot Governance Pack intake mode — ?interest=pilot&vector=copilot-governance */
(function (global) {
  "use strict";

  var PILOT_BANDS = {
    quickscan: {
      name: "Copilot Governance Pack · QuickScan",
      priceLabel: "$2,000 CAD",
      priceMid: 2000,
      line: "4-week scope · evaluate orientation · sample TLE · export walkthrough",
    },
    readiness: {
      name: "Copilot Governance Pack · Readiness Pilot",
      priceLabel: "$5,000 – $10,000 CAD",
      priceMid: 7500,
      line: "90 days · production tenant · live TLE · board PDF in governance meeting",
    },
    unsure: {
      name: "Copilot Governance Pack · scope TBD",
      priceLabel: "$2,000 – $10,000 CAD",
      priceMid: 5000,
      line: "Scoping call · QuickScan or Readiness band confirmed at kickoff",
    },
  };

  function queryParams() {
    try {
      return new URLSearchParams(location.search);
    } catch (_) {
      return new URLSearchParams();
    }
  }

  function isPilotIntake() {
    var sp = queryParams();
    var interest = (sp.get("interest") || "").toLowerCase();
    var vector = (sp.get("vector") || "").toLowerCase();
    return interest === "pilot" || vector === "copilot-governance";
  }

  function fmtCAD(n) {
    try {
      return new Intl.NumberFormat("en-CA", {
        style: "currency",
        currency: "CAD",
        maximumFractionDigits: 0,
      }).format(n);
    } catch (_) {
      return "$" + Math.round(n) + " CAD";
    }
  }

  function pilotBandKey() {
    var el = document.getElementById("tb_pilot_band");
    var v = el && el.value ? el.value : "readiness";
    return PILOT_BANDS[v] ? v : "readiness";
  }

  function buildPilotSummary(ctx) {
    var rid = (ctx && ctx.rid) || "—";
    var org = (document.getElementById("tb_org") || {}).value || "";
    var email = (document.getElementById("tb_email") || {}).value || "";
    var name = (document.getElementById("tb_name") || {}).value || "";
    var role = (document.getElementById("tb_role") || {}).value || "";
    var driver = (document.getElementById("tb_driver") || {}).value || "";
    var start = (document.getElementById("tb_start") || {}).value || "";
    var notes = (document.getElementById("tb_notes") || {}).value || "";
    var band = pilotBandKey();
    var meta = PILOT_BANDS[band];
    var vector = (ctx && ctx.intakeVector) ? ctx.intakeVector() : "copilot-governance";

    var line =
      meta.name +
      " • " +
      meta.line +
      (driver ? " • Driver: " + driver : "") +
      (start ? " • Start: " + start : "");

    var body =
      "Noetfield — Copilot Governance Pack (Pilot Intake)\n" +
      "Request ID: " +
      rid +
      "\n" +
      (name ? "Name: " + name + "\n" : "") +
      (email ? "Work email: " + email + "\n" : "") +
      (org ? "Organization: " + org + "\n" : "") +
      (role ? "Role: " + role + "\n" : "") +
      "Program: " +
      meta.name +
      "\n" +
      "Pilot band: " +
      band +
      "\n" +
      "Typical fee guidance: " +
      meta.priceLabel +
      "\n" +
      (driver ? "Primary driver: " + driver + "\n" : "") +
      (start ? "Desired start window: " + start + "\n" : "") +
      "Source vector: " +
      vector +
      "\n" +
      "Success signal: board PDF used in a real governance meeting.\n" +
      "Notes (high-level): " +
      (notes || "—") +
      "\n" +
      "Disclosure: Guidance only; final SOW confirmed after kickoff. Public intake is non-confidential.\n";

    return {
      rid: rid,
      tierName: meta.name,
      total: meta.priceMid,
      priceLabel: meta.priceLabel,
      line: line,
      body: body,
    };
  }

  function setText(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function prefillFromQuery() {
    var sp = queryParams();
    var map = [
      ["email", "tb_email"],
      ["org", "tb_org"],
      ["organization", "tb_org"],
      ["role", "tb_role"],
      ["band", "tb_pilot_band"],
      ["name", "tb_name"],
    ];
    map.forEach(function (pair) {
      var val = sp.get(pair[0]);
      if (!val) return;
      var el = document.getElementById(pair[1]);
      if (el) el.value = val;
    });
    try {
      var raw = sessionStorage.getItem("nf_pilot_intake_notes");
      if (raw) {
        var data = JSON.parse(raw);
        if (data.email && document.getElementById("tb_email")) {
          document.getElementById("tb_email").value = data.email;
        }
        if (data.org && document.getElementById("tb_org")) {
          document.getElementById("tb_org").value = data.org;
        }
        if (data.role && document.getElementById("tb_role")) {
          document.getElementById("tb_role").value = data.role;
        }
        if (data.band && document.getElementById("tb_pilot_band")) {
          document.getElementById("tb_pilot_band").value = data.band;
        }
        if (data.notes && document.getElementById("tb_notes")) {
          document.getElementById("tb_notes").value = data.notes;
        }
      }
    } catch (_) {}
  }

  function relaxTrustBriefRequired() {
    [
      "tb_usecases",
      "tb_teams",
      "tb_risk",
      "tb_evidence",
      "tb_proc",
      "tb_driver",
      "tb_start",
    ].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.removeAttribute("required");
    });
  }

  function applyDomMode() {
    if (!isPilotIntake()) return false;

    document.body.classList.add("intake-pilot-mode");
    document.title = "Noetfield — Copilot Governance Pack Intake";

    var tbHero = document.getElementById("intakeHeroTrustBrief");
    var pilotHero = document.getElementById("intakeHeroPilot");
    if (tbHero) tbHero.hidden = true;
    if (pilotHero) pilotHero.hidden = false;

    var pkg = document.querySelector('#tbIntakeForm input[name="package"]');
    if (pkg) pkg.value = "copilot-governance-pack";

    var vec = document.getElementById("tb_intake_vector");
    if (vec) vec.value = "copilot-governance";

    var trustEstimator = document.querySelector(".tb-estimator-fields");
    var pilotScope = document.querySelector(".pilot-scope-fields");
    if (trustEstimator) trustEstimator.hidden = true;
    if (pilotScope) pilotScope.hidden = false;

    var formTitle = document.getElementById("tbFormTitle");
    var formLead = document.getElementById("tbFormLead");
    if (formTitle) formTitle.textContent = "Pilot application";
    if (formLead) {
      formLead.textContent =
        "Non-confidential intake for Copilot Governance Pack ($2k–10k). Operations replies within one business day.";
    }

    var submitBtn = document.querySelector('#tbIntakeForm button[type="submit"]');
    if (submitBtn) submitBtn.textContent = "Submit pilot application";

    var tierLabel = document.getElementById("tbTierLabel");
    if (tierLabel) tierLabel.textContent = "Locked program";
    var tierRailTitle = document.getElementById("tbTierRailTitle");
    if (tierRailTitle) tierRailTitle.textContent = "Program direction";
    var tierRailLead = document.getElementById("tbTierRailLead");
    if (tierRailLead) {
      tierRailLead.textContent = "Copilot Governance Pack — fixed-fee pilot bands.";
    }

    var routingCopy = document.getElementById("tbRoutingCopy");
    if (routingCopy) {
      routingCopy.textContent =
        "Submit this form or email operations@noetfield.com with your Request ID. No purchase hub required for pilot intake.";
    }

    var tbRouting = document.getElementById("tbRoutingActionsTrustBrief");
    var pilotRouting = document.getElementById("tbRoutingActionsPilot");
    if (tbRouting) tbRouting.hidden = true;
    if (pilotRouting) pilotRouting.hidden = false;

    var stickyText = document.getElementById("tbStickyText");
    if (stickyText) {
      stickyText.innerHTML =
        "<strong>Copilot Governance Pack</strong> — $2k–10k pilot intake · non-confidential · board PDF success signal.";
    }
    var stickyTrust = document.getElementById("tbStickyActionsTrustBrief");
    var stickyPilot = document.getElementById("tbStickyActionsPilot");
    if (stickyTrust) stickyTrust.hidden = true;
    if (stickyPilot) stickyPilot.hidden = false;

    var driver = document.getElementById("tb_driver");
    if (driver && !driver.value) {
      for (var i = 0; i < driver.options.length; i++) {
        if (driver.options[i].text.indexOf("Copilot") >= 0) {
          driver.selectedIndex = i;
          break;
        }
      }
    }

    relaxTrustBriefRequired();
    prefillFromQuery();
    return true;
  }

  global.NFIntakePilot = {
    isPilotIntake: isPilotIntake,
    buildPilotSummary: buildPilotSummary,
    fmtCAD: fmtCAD,
    applyDomMode: applyDomMode,
    pilotBandKey: pilotBandKey,
    PILOT_BANDS: PILOT_BANDS,
  };
})(window);

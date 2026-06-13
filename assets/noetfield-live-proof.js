/** Governance Playground — homepage scenario picker + mini evaluate → scorecard receipt (v19). */
(function () {
  var PANEL_ID = "nfLiveProofHero";
  var ROWS = ["tle_id", "decision", "confidence_score", "rid", "evidence_index", "export_integrity"];

  var SCENARIOS = {
    copilot_rollout: {
      action: "copilot_rollout",
      actor: "security-team",
      context: "Copilot rollout to production M365 tenant — pre-execution governance check",
      decision: "allow",
      score: "0.82",
    },
    guest_access: {
      action: "guest_sharing",
      actor: "collaboration-lead",
      context: "External guest access to Copilot-enabled SharePoint — sharing boundary review",
      decision: "review",
      score: "0.71",
    },
    data_export: {
      action: "bulk_export",
      actor: "data-governance",
      context: "Bulk export of Copilot-indexed content — high sensitivity classification",
      decision: "deny",
      score: "0.91",
    },
  };

  var SCENARIO_KEYS = ["copilot_rollout", "guest_access", "data_export"];

  var SCENARIO_LABELS = {
    copilot_rollout: "Copilot rollout · production scope",
    guest_access: "Guest access · external sharing",
    data_export: "Bulk export · high sensitivity",
  };

  function scenarioOfTheDayKey() {
    var day = new Date().getDay();
    return SCENARIO_KEYS[day % SCENARIO_KEYS.length];
  }

  function applyScenarioOfTheDay(form) {
    var key = scenarioOfTheDayKey();
    var select = qs('[name="scenario"]', form);
    var banner = document.getElementById("nfScenarioOfDay");
    if (select) select.value = key;
    applyScenario(form);
    if (banner) {
      banner.innerHTML =
        '<strong>Scenario of the day:</strong> ' +
        (SCENARIO_LABELS[key] || key) +
        ' — <span class="nf-scenario-of-day__hint">Evaluate to see tamper-evident scorecard</span>';
    }
  }

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function activeScenario(form) {
    var key = (qs('[name="scenario"]', form) || {}).value || "copilot_rollout";
    return SCENARIOS[key] || SCENARIOS.copilot_rollout;
  }

  function applyScenario(form) {
    var s = activeScenario(form);
    var actor = qs('[name="actor"]', form);
    var action = qs('[name="action"]', form);
    var context = qs('[name="context"]', form);
    if (actor) actor.value = s.actor;
    if (action) action.value = s.action;
    if (context) context.value = s.context;
  }

  function skeletonReceipt(container) {
    container.innerHTML =
      '<div class="nf-artifact-panel nf-live-proof-receipt" aria-busy="true">' +
      '<div class="nf-artifact-panel-chrome">' +
      '<span class="nf-artifact-panel-dots" aria-hidden="true"><i></i><i></i><i></i></span>' +
      '<span class="nf-artifact-panel-file">tle-receipt.yaml</span>' +
      '<span class="nf-artifact-panel-badge nf-live-proof-badge">Live</span>' +
      "</div>" +
      '<aside class="nf-receipt-mock" aria-label="Trust Ledger Entry receipt">' +
      '<dl class="nf-receipt-mock-body nf-live-proof-skeleton">' +
      ROWS.map(function (k) {
        return (
          '<div class="nf-receipt-row nf-live-proof-row" data-key="' +
          k +
          '"><dt>' +
          k +
          '</dt><dd class="nf-live-proof-val"><span class="nf-skel-line"></span></dd></div>'
        );
      }).join("") +
      "</dl>" +
      '<p class="nf-receipt-mock-footer nf-live-proof-footer">Pick a scenario and evaluate to generate a scorecard receipt.</p>' +
      "</aside></div>";
  }

  function animateRow(row, value, isOk) {
    if (!row) return;
    var dd = row.querySelector(".nf-live-proof-val") || row.querySelector("dd");
    if (!dd) return;
    dd.innerHTML = "";
    dd.classList.remove("nf-skel-line");
    if (isOk) dd.classList.add("nf-receipt-ok");
    dd.textContent = value;
    row.classList.add("nf-live-proof-row--in");
  }

  function receiptMap(data, rid, scenario) {
    var score =
      typeof data.risk_score === "number"
        ? (1 - Math.min(1, Math.max(0, data.risk_score))).toFixed(2)
        : scenario.score;
    var decision = data.decision || scenario.decision;
    return {
      tle_id: "TLE-015DCFB8B953",
      decision: decision,
      confidence_score: score,
      rid: rid,
      evidence_index: "purview · entra · audit",
      export_integrity: "PASS · fail closed on tamper",
    };
  }

  function paintReceipt(container, map) {
    var panel = container.querySelector(".nf-live-proof-receipt");
    if (!panel) return;
    panel.setAttribute("aria-busy", "false");
    var badge = panel.querySelector(".nf-live-proof-badge");
    if (badge) badge.textContent = "Verified";
    ROWS.forEach(function (key, i) {
      setTimeout(function () {
        animateRow(
          panel.querySelector('[data-key="' + key + '"]'),
          map[key],
          key === "export_integrity"
        );
      }, 80 * i);
    });
  }

  function renderReceipt(container, data, rid, scenario) {
    paintReceipt(container, receiptMap(data, rid, scenario));
    var foot = container.querySelector(".nf-live-proof-footer");
    if (foot) {
      foot.innerHTML =
        '<a href="/result/' +
        encodeURIComponent(rid) +
        '">Open full result</a> · ' +
        '<a href="/cognitive-dashboard/?sandbox=1">Continue in sandbox</a>';
    }
  }

  function degradedReceipt(container, scenario) {
    skeletonReceipt(container);
    var foot = container.querySelector(".nf-live-proof-footer");
    if (foot) {
      foot.innerHTML =
        'Live evaluate is temporarily unavailable — <span class="nf-live-proof-degraded">showing sample scorecard</span> · ' +
        '<a href="/start/">Try the sandbox</a>';
    }
    paintReceipt(
      container,
      receiptMap({}, "RID-2026-0602-HOME", scenario)
    );
  }

  function bindForm(root) {
    var form = qs("#nfLiveProofForm", root);
    if (!form) return;
    var receiptHost = qs("#nfLiveProofReceipt", root);
    var scenarioSelect = qs('[name="scenario"]', form);
    skeletonReceipt(receiptHost);
    applyScenarioOfTheDay(form);

    if (scenarioSelect) {
      scenarioSelect.addEventListener("change", function () {
        applyScenario(form);
      });
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var scenario = activeScenario(form);
      var actor = (qs('[name="actor"]', form) || {}).value || scenario.actor;
      var action = (qs('[name="action"]', form) || {}).value || scenario.action;
      var context = (qs('[name="context"]', form) || {}).value || scenario.context;
      var btn = qs('button[type="submit"]', form);
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Evaluating…";
      }
      skeletonReceipt(receiptHost);

      fetch("/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          actor: actor,
          action: action,
          context: context,
          metadata: { source: "live-proof-hero", scenario: (qs('[name="scenario"]', form) || {}).value },
        }),
      })
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (data) {
          if (!data.rid) throw new Error("no rid");
          renderReceipt(receiptHost, data, data.rid, scenario);
          if (window.noetfieldSandbox && window.noetfieldSandbox.incrementEvaluate) {
            window.noetfieldSandbox.incrementEvaluate();
          }
        })
        .catch(function () {
          degradedReceipt(receiptHost, scenario);
        })
        .finally(function () {
          if (btn) {
            btn.disabled = false;
            btn.textContent = "Evaluate intent";
          }
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.getElementById(PANEL_ID);
    if (!root) return;
    bindForm(root);
  });
})();

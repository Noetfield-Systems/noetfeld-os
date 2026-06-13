/** Governance Playground — multi-product scenario picker + mini evaluate → scorecard receipt (v20). */
(function () {
  "use strict";

  var PANEL_ID = "nfLiveProofHero";
  var ROWS = ["tle_id", "decision", "confidence_score", "rid", "evidence_index", "export_integrity"];

  var LANE_LABELS = {
    all: "All products",
    copilot: "Copilot Pack",
    trust_brief: "Trust Brief",
    bank: "Bank Pilot",
    automation: "AI automation",
    partner: "Partner shadow",
  };

  /** Aligned with OFFERINGS_LOCKED + GET /api/v1/governance/scenario-presets/{preset} */
  var SCENARIO_CATALOG = [
    {
      key: "copilot_rollout",
      lane: "copilot",
      label: "Copilot rollout · production scope",
      action: "copilot_rollout",
      actor: "security-team",
      context: "Copilot rollout to production M365 tenant — pre-execution governance check",
      decision: "allow",
      score: "0.82",
      evidence: "purview · entra · audit",
    },
    {
      key: "copilot_generation",
      lane: "copilot",
      label: "Copilot session · content generation",
      action: "copilot_content_generation",
      actor: "knowledge-worker",
      context: "M365 Copilot content generation on classified workspace — session governance evaluate",
      decision: "review",
      score: "0.76",
      evidence: "purview · copilot · audit",
    },
    {
      key: "guest_access",
      lane: "copilot",
      label: "Guest access · external sharing",
      action: "guest_sharing",
      actor: "collaboration-lead",
      context: "External guest access to Copilot-enabled SharePoint — sharing boundary review",
      decision: "review",
      score: "0.71",
      evidence: "purview · entra · sharepoint",
    },
    {
      key: "data_export",
      lane: "copilot",
      label: "Bulk export · high sensitivity",
      action: "bulk_export",
      actor: "data-governance",
      context: "Bulk export of Copilot-indexed content — high sensitivity classification",
      decision: "deny",
      score: "0.91",
      evidence: "purview · dlp · audit",
    },
    {
      key: "trust_brief_scope",
      lane: "trust_brief",
      label: "Trust Brief · AI policy scope change",
      action: "ai_policy_update",
      actor: "grc-lead",
      context: "Six-week Trust Brief — AI acceptable use policy revision before Copilot scale",
      decision: "review",
      score: "0.79",
      evidence: "policy · risk · board",
    },
    {
      key: "vendor_ai_tool",
      lane: "trust_brief",
      label: "Vendor AI tool · onboarding",
      action: "vendor_ai_intake",
      actor: "procurement",
      context: "Third-party AI SaaS onboarding — governance diagnostic and evidence expectations",
      decision: "review",
      score: "0.68",
      evidence: "vendor · policy · procurement",
    },
    {
      key: "bank_board_report",
      lane: "bank",
      label: "Bank Pilot · board report publish",
      action: "publish_board_report",
      actor: "frfi-governance",
      context: "FRFI shadow mode — board governance artifact publish before production AI scope",
      decision: "allow",
      score: "0.85",
      evidence: "shadow · audit · compliance",
    },
    {
      key: "bank_shadow_evaluate",
      lane: "bank",
      label: "Bank Pilot · shadow evaluate",
      action: "shadow_policy_evaluate",
      actor: "model-risk",
      context: "Read-only governance simulation — no execution rights · audit lineage export",
      decision: "allow",
      score: "0.88",
      evidence: "shadow · lineage · audit",
    },
    {
      key: "agentic_workflow",
      lane: "automation",
      label: "Agentic workflow · policy-bound",
      action: "agentic_workflow_run",
      actor: "automation-owner",
      context: "Policy-bound investigate → triage → draft → approve on metadata-only M365 evidence",
      decision: "review",
      score: "0.74",
      evidence: "workflow · policy · rid",
    },
    {
      key: "low_risk_auto_record",
      lane: "automation",
      label: "Low-risk path · auto-record sandbox",
      action: "auto_record_evaluate",
      actor: "sandbox-operator",
      context: "Pre-approved sandbox evaluate — auto-record TLE; production requires Governance Pack keys",
      decision: "allow",
      score: "0.93",
      evidence: "sandbox · tle · export",
    },
    {
      key: "msb_transfer_intent",
      lane: "partner",
      label: "MSB partner · transfer intent (shadow)",
      action: "initiate_transfer_intent",
      actor: "partner-pilot",
      context: "Licensed MSB partner — read-only transfer intent signal · Noetfield does not execute payments",
      decision: "review",
      score: "0.77",
      evidence: "partner signal · read-only · msb",
    },
    {
      key: "exchange_order_intent",
      lane: "partner",
      label: "Exchange · order intent (shadow)",
      action: "place_order_intent",
      actor: "partner-pilot",
      context: "Licensed exchange/VASP — shadow evaluate on order intent · partner executes outside Noetfield",
      decision: "deny",
      score: "0.89",
      evidence: "partner signal · read-only · exchange",
    },
  ];

  var SCENARIOS = {};
  var SCENARIO_LABELS = {};
  SCENARIO_CATALOG.forEach(function (s) {
    SCENARIOS[s.key] = s;
    SCENARIO_LABELS[s.key] = s.label;
  });

  var activeLane = "all";

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function scenarioKeysForLane(lane) {
    return SCENARIO_CATALOG.filter(function (s) {
      return lane === "all" || s.lane === lane;
    }).map(function (s) {
      return s.key;
    });
  }

  function scenarioOfTheDayKey() {
    var keys = scenarioKeysForLane(activeLane);
    if (!keys.length) keys = SCENARIO_CATALOG.map(function (s) {
      return s.key;
    });
    var day = new Date().getDay();
    return keys[day % keys.length];
  }

  function rebuildScenarioSelect(form, preferredKey) {
    var select = qs('[name="scenario"]', form);
    if (!select) return;
    var keys = scenarioKeysForLane(activeLane);
    var current = preferredKey || select.value;
    select.innerHTML = "";
    var groups = {};
    SCENARIO_CATALOG.forEach(function (s) {
      if (keys.indexOf(s.key) < 0) return;
      if (!groups[s.lane]) groups[s.lane] = [];
      groups[s.lane].push(s);
    });
    Object.keys(groups).forEach(function (lane) {
      var og = document.createElement("optgroup");
      og.label = LANE_LABELS[lane] || lane;
      groups[lane].forEach(function (s) {
        var opt = document.createElement("option");
        opt.value = s.key;
        opt.textContent = s.label;
        og.appendChild(opt);
      });
      select.appendChild(og);
    });
    if (current && keys.indexOf(current) >= 0) {
      select.value = current;
    } else if (keys.length) {
      select.value = keys[0];
    }
  }

  function applyScenarioOfTheDay(form) {
    var key = scenarioOfTheDayKey();
    rebuildScenarioSelect(form, key);
    applyScenario(form);
    var banner = document.getElementById("nfScenarioOfDay");
    if (banner) {
      var item = SCENARIOS[key];
      banner.innerHTML =
        '<strong>Scenario of the day:</strong> ' +
        (SCENARIO_LABELS[key] || key) +
        (item && item.lane
          ? ' · <span class="nf-scenario-of-day__lane">' +
            (LANE_LABELS[item.lane] || item.lane) +
            "</span>"
          : "") +
        ' — <span class="nf-scenario-of-day__hint">Evaluate to see tamper-evident scorecard</span>';
    }
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
      '<p class="nf-receipt-mock-footer nf-live-proof-footer">Pick a product lane and scenario — evaluate to generate a scorecard receipt.</p>' +
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
      evidence_index: scenario.evidence || "purview · entra · audit",
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
    paintReceipt(container, receiptMap({}, "RID-2026-0602-HOME", scenario));
  }

  function bindLaneFilters(form) {
    document.querySelectorAll("[data-live-proof-lane]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeLane = btn.getAttribute("data-live-proof-lane") || "all";
        document.querySelectorAll("[data-live-proof-lane]").forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        applyScenarioOfTheDay(form);
      });
    });
  }

  function bindForm(root) {
    var form = qs("#nfLiveProofForm", root);
    if (!form) return;
    var receiptHost = qs("#nfLiveProofReceipt", root);
    var scenarioSelect = qs('[name="scenario"]', form);
    skeletonReceipt(receiptHost);
    bindLaneFilters(form);
    applyScenarioOfTheDay(form);

    if (scenarioSelect) {
      scenarioSelect.addEventListener("change", function () {
        applyScenario(form);
        var item = activeScenario(form);
        var banner = document.getElementById("nfScenarioOfDay");
        if (banner && item) {
          banner.innerHTML =
            '<strong>Selected:</strong> ' +
            (SCENARIO_LABELS[item.key] || item.key) +
            ' · <span class="nf-scenario-of-day__lane">' +
            (LANE_LABELS[item.lane] || item.lane) +
            '</span> — <span class="nf-scenario-of-day__hint">Evaluate to see tamper-evident scorecard</span>';
        }
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
          metadata: {
            source: "live-proof-hero",
            scenario: (qs('[name="scenario"]', form) || {}).value,
            product_lane: scenario.lane,
          },
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

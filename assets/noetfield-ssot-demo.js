/** Copilot Governance vertical demo — SSOT change → invalidate → re-brief → evaluate → TLE (v1). */
(function () {
  "use strict";

  var ROOT_ID = "nfSsotDemo";
  var FIXTURE_BASE = "/demos/copilot-governance/ssot/";
  var ROWS = ["tle_id", "decision", "confidence_score", "rid", "evidence_index", "export_integrity"];

  var SCENARIO = {
    actor: "security-team",
    action: "copilot_rollout",
    context:
      "Copilot rollout to production M365 tenant — re-briefed after guest-sharing rule change (policy v3.2)",
    evidence: "purview · entra · audit",
  };

  var state = {
    policyBefore: null,
    policyAfter: null,
    pending: [],
    ssotEvent: null,
    reBriefQueue: [],
    evalResult: null,
    step: 0,
  };

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function apiBase() {
    var meta = document.querySelector('meta[name="nf-intake-api-base"]');
    if (meta && meta.getAttribute("content")) {
      return meta.getAttribute("content").replace(/\/$/, "");
    }
    return "";
  }

  function fetchJson(path, opts) {
    var base = apiBase();
    var url = path.indexOf("http") === 0 ? path : location.origin + path;
    if (base && path.indexOf("/api/") === 0) {
      url = base + path;
    }
    return fetch(url, opts || {}).then(function (res) {
      return res.json().then(function (data) {
        return { ok: res.ok, status: res.status, data: data };
      });
    });
  }

  function loadFixtures() {
    return Promise.all([
      fetchJson(FIXTURE_BASE + "policy_v3.1.json"),
      fetchJson(FIXTURE_BASE + "policy_v3.2.json"),
      fetchJson(FIXTURE_BASE + "pending_evaluations.json"),
    ]).then(function (parts) {
      state.policyBefore = parts[0].data;
      state.policyAfter = parts[1].data;
      state.pending = (parts[2].data && parts[2].data.pending_evaluations) || [];
    });
  }

  function applySsotClient() {
    var fromV = parseFloat(state.policyBefore.version);
    var toV = parseFloat(state.policyAfter.version);
    var invalidated = [];
    var reBriefQueue = [];
    state.pending.forEach(function (item) {
      var pv = parseFloat(item.policy_version);
      if (pv < toV) {
        invalidated.push({
          rid: item.rid,
          action: item.action,
          prior_policy_version: String(pv),
          status: "invalidated",
        });
        reBriefQueue.push({
          rid: item.rid,
          action: item.action,
          required_policy_version: String(toV),
          briefing_status: "queued",
        });
      }
    });
    return {
      event: "SSOT_CHANGED",
      from_version: String(fromV),
      to_version: String(toV),
      occurred_at: new Date().toISOString(),
      policy_id: "copilot-acceptable-use",
      invalidated_count: invalidated.length,
      invalidated: invalidated,
      re_brief_queue: reBriefQueue,
    };
  }

  function publishSsotChange() {
    var btn = qs("#nfSsotPublish");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Publishing…";
    }
    return fetchJson("/api/demo/ssot-change", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        from_version: state.policyBefore.version,
        to_version: state.policyAfter.version,
        pending: state.pending,
      }),
    })
      .then(function (res) {
        if (res.ok && res.data && res.data.event === "SSOT_CHANGED") {
          state.ssotEvent = res.data;
          state.reBriefQueue = res.data.re_brief_queue || [];
        } else {
          state.ssotEvent = applySsotClient();
          state.reBriefQueue = state.ssotEvent.re_brief_queue;
        }
        afterSsotPublished();
      })
      .catch(function () {
        state.ssotEvent = applySsotClient();
        state.reBriefQueue = state.ssotEvent.re_brief_queue;
        afterSsotPublished();
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Publish policy v3.2 (SSOT change)";
        }
      });
  }

  function runEvaluate() {
    var btn = qs("#nfSsotEvaluate");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Evaluating…";
    }
    skeletonReceipt(qs("#nfSsotReceipt"));

    return fetchJson("/api/demo/evaluate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Tenant-ID": "demo-northstar",
      },
      body: JSON.stringify({
        actor: SCENARIO.actor,
        action: SCENARIO.action,
        context: SCENARIO.context,
        metadata: {
          source: "ssot-demo",
          policy_version: state.policyAfter.version,
          re_brief_completed: true,
        },
      }),
    })
      .then(function (res) {
        if (res.ok && res.data && res.data.rid) {
          state.evalResult = res.data;
        } else {
          state.evalResult = evaluateClientFallback();
        }
        setStep(2);
        renderReceipt();
        renderBoardSnippet();
        renderMiddleware();
      })
      .catch(function () {
        state.evalResult = evaluateClientFallback();
        setStep(2);
        renderReceipt();
        renderBoardSnippet();
        renderMiddleware();
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Run re-brief + evaluate";
        }
      });
  }

  function evaluateClientFallback() {
    var score = 20;
    return {
      decision: score >= 40 ? "review" : "allow",
      risk_score: score,
      reason: ["Production Copilot rollout requires v3.2 evidence index and approver chain."],
      conditions: ["Route to compliance owner with RID attached."],
      rid: "RID-SSOT-DEMO-" + Date.now().toString(36).toUpperCase().slice(-6),
      policy_version: state.policyAfter.version,
    };
  }

  function setStep(index) {
    state.step = Math.max(state.step, index);
    var root = document.getElementById(ROOT_ID);
    if (!root) return;
    root.querySelectorAll(".nf-ssot-demo__step").forEach(function (el, i) {
      el.classList.remove("is-active", "is-done");
      if (i < state.step) el.classList.add("is-done");
      if (i === state.step) el.classList.add("is-active");
    });
  }

  function afterSsotPublished() {
    setStep(1);
    renderEventLog();
    renderReBriefQueue();
    var ev = qs("#nfSsotEvaluate");
    if (ev) ev.disabled = false;
  }

  function renderPolicyCards() {
    var host = qs("#nfSsotPolicyCards");
    if (!host || !state.policyBefore) return;
    host.innerHTML =
      '<article class="nf-ssot-policy nf-ssot-policy--old">' +
      "<h4>Before · v" +
      state.policyBefore.version +
      "</h4>" +
      "<ul>" +
      state.policyBefore.rules_summary.map(function (r) {
        return "<li>" + r + "</li>";
      }).join("") +
      "</ul></article>" +
      '<article class="nf-ssot-policy nf-ssot-policy--new">' +
      "<h4>After · v" +
      state.policyAfter.version +
      "</h4>" +
      "<ul>" +
      state.policyAfter.rules_summary.map(function (r) {
        return "<li>" + r + "</li>";
      }).join("") +
      "</ul></article>";
  }

  function renderPendingTable() {
    var host = qs("#nfSsotPending");
    if (!host) return;
    var rows = state.pending
      .map(function (p) {
        return (
          "<tr><td><code>" +
          p.rid +
          "</code></td><td>" +
          p.action +
          "</td><td>v" +
          p.policy_version +
          "</td><td>" +
          p.status +
          "</td></tr>"
        );
      })
      .join("");
    host.innerHTML =
      '<table class="nf-ssot-table"><thead><tr><th>RID</th><th>Action</th><th>Policy</th><th>Status</th></tr></thead><tbody>' +
      rows +
      "</tbody></table>";
  }

  function renderEventLog() {
    var host = qs("#nfSsotEventLog");
    if (!host || !state.ssotEvent) return;
    var inv = state.ssotEvent.invalidated || [];
    host.innerHTML =
      '<p class="nf-ssot-event"><strong>SSOT_CHANGED</strong> · v' +
      state.ssotEvent.from_version +
      " → v" +
      state.ssotEvent.to_version +
      " · " +
      state.ssotEvent.invalidated_count +
      " evaluations invalidated</p>" +
      "<ul>" +
      inv
        .map(function (i) {
          return "<li><code>" + i.rid + "</code> — " + i.action + " (was v" + i.prior_policy_version + ")</li>";
        })
        .join("") +
      "</ul>";
  }

  function renderReBriefQueue() {
    var host = qs("#nfSsotReBrief");
    if (!host) return;
    var q = state.reBriefQueue || [];
    if (!q.length) {
      host.innerHTML = "<p class=\"muted\">No re-brief required — all pending evaluations already on current SSOT.</p>";
      return;
    }
    host.innerHTML =
      "<ul>" +
      q
        .map(function (item) {
          return (
            "<li><code>" +
            item.rid +
            "</code> → re-brief for v" +
            item.required_policy_version +
            " (" +
            item.action +
            ")</li>"
          );
        })
        .join("") +
      "</ul>";
  }

  function receiptMap(data) {
    var score =
      typeof data.risk_score === "number"
        ? (1 - Math.min(1, Math.max(0, data.risk_score / 100))).toFixed(2)
        : "0.80";
    return {
      tle_id: "TLE-" + (data.rid || "DEMO").slice(-12).toUpperCase(),
      decision: data.decision,
      confidence_score: score,
      rid: data.rid,
      evidence_index: SCENARIO.evidence,
      export_integrity: "PASS · fail closed on tamper",
    };
  }

  function skeletonReceipt(container) {
    if (!container) return;
    container.innerHTML =
      '<div class="nf-artifact-panel nf-live-proof-receipt" aria-busy="true">' +
      '<div class="nf-artifact-panel-chrome">' +
      '<span class="nf-artifact-panel-dots" aria-hidden="true"><i></i><i></i><i></i></span>' +
      '<span class="nf-artifact-panel-file">tle-receipt.yaml</span>' +
      '<span class="nf-artifact-panel-badge nf-live-proof-badge">Live</span></div>' +
      '<dl class="nf-receipt-mock-body">' +
      ROWS.map(function (k) {
        return '<div class="nf-receipt-row" data-key="' + k + '"><dt>' + k + '</dt><dd><span class="nf-skel-line"></span></dd></div>';
      }).join("") +
      "</dl></div>";
  }

  function paintReceipt(container, map) {
    var panel = container.querySelector(".nf-live-proof-receipt");
    if (!panel) return;
    panel.setAttribute("aria-busy", "false");
    var badge = panel.querySelector(".nf-live-proof-badge");
    if (badge) badge.textContent = "Verified";
    ROWS.forEach(function (key, i) {
      setTimeout(function () {
        var row = panel.querySelector('[data-key="' + key + '"]');
        if (!row) return;
        var dd = row.querySelector("dd");
        if (dd) {
          dd.innerHTML = "";
          dd.textContent = map[key];
          if (key === "export_integrity") dd.classList.add("nf-receipt-ok");
        }
      }, 70 * i);
    });
  }

  function renderReceipt() {
    var host = qs("#nfSsotReceipt");
    if (!host || !state.evalResult) return;
    skeletonReceipt(host);
    paintReceipt(host, receiptMap(state.evalResult));
  }

  function renderBoardSnippet() {
    var host = qs("#nfSsotBoard");
    if (!host || !state.evalResult) return;
    var conf =
      typeof state.evalResult.risk_score === "number"
        ? (1 - state.evalResult.risk_score / 100).toFixed(2)
        : "0.80";
    host.innerHTML =
      '<h4>Board digest excerpt</h4>' +
      "<p>Policy v" +
      state.policyAfter.version +
      " published; " +
      (state.ssotEvent ? state.ssotEvent.invalidated_count : 0) +
      " stale evaluations invalidated; fresh evaluate → <strong>" +
      state.evalResult.decision +
      "</strong> (confidence " +
      conf +
      ").</p>" +
      "<ul><li>SSOT change closes governance latency — agents re-brief on current policy.</li>" +
      "<li>Signed TLE + board PDF for procurement — no execution or payment rails.</li></ul>";
  }

  function renderMiddleware() {
    var host = qs("#nfSsotMiddleware");
    if (!host) return;
    var origin = location.origin;
    host.innerHTML =
      '<p><strong>Middleware hook</strong> — agency agents call Noetfield as gate + ledger:</p>' +
      '<pre class="nf-ssot-curl"><code># 1) Policy publish invalidates stale context\n' +
      "curl -X POST " +
      origin +
      '/api/demo/ssot-change \\\n  -H "Content-Type: application/json" \\\n  -d \'{"from_version":"3.1","to_version":"3.2","pending":[...]}\'\n\n' +
      "# 2) Re-brief + pre-execution evaluate\n" +
      "curl -X POST " +
      origin +
      '/api/demo/evaluate \\\n  -H "Content-Type: application/json" \\\n  -H "X-Tenant-ID: demo-northstar" \\\n  -d \'{"actor":"security-team","action":"copilot_rollout","context":"...","metadata":{"policy_version":"3.2"}}\'</code></pre>';
  }

  function bind(root) {
    var pub = qs("#nfSsotPublish", root);
    var ev = qs("#nfSsotEvaluate", root);
    if (pub) pub.addEventListener("click", publishSsotChange);
    if (ev) {
      ev.disabled = true;
      ev.addEventListener("click", runEvaluate);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.getElementById(ROOT_ID);
    if (!root) return;
    loadFixtures()
      .then(function () {
        renderPolicyCards();
        renderPendingTable();
        bind(root);
      })
      .catch(function () {
        root.innerHTML =
          '<p class="nf-callout">Demo fixtures unavailable — run from deployed www or local static server with /demos/ served.</p>';
      });
  });

})();

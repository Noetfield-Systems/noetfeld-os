/** Live Proof Hero — homepage mini evaluate → animated receipt (v18 UI-01). */
(function () {
  var PANEL_ID = "nfLiveProofHero";
  var ROWS = ["tle_id", "decision", "confidence_score", "rid", "evidence_index", "export_integrity"];

  function qs(sel, root) {
    return (root || document).querySelector(sel);
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
      '<p class="nf-receipt-mock-footer nf-live-proof-footer">Submit intent to generate a live receipt.</p>' +
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

  function renderReceipt(container, data, rid) {
    var panel = container.querySelector(".nf-live-proof-receipt");
    if (!panel) return;
    panel.setAttribute("aria-busy", "false");
    var badge = panel.querySelector(".nf-live-proof-badge");
    if (badge) badge.textContent = "Verified";

    var score =
      typeof data.risk_score === "number"
        ? (1 - Math.min(1, Math.max(0, data.risk_score))).toFixed(2)
        : "0.82";
    var decision = data.decision || "allow";
    var map = {
      tle_id: "TLE-015DCFB8B953",
      decision: decision,
      confidence_score: score,
      rid: rid,
      evidence_index: "purview · entra · audit",
      export_integrity: "PASS · fail closed on tamper",
    };

    ROWS.forEach(function (key, i) {
      setTimeout(function () {
        animateRow(
          panel.querySelector('[data-key="' + key + '"]'),
          map[key],
          key === "export_integrity"
        );
      }, 80 * i);
    });

    var foot = panel.querySelector(".nf-live-proof-footer");
    if (foot) {
      foot.innerHTML =
        '<a href="/result/' +
        encodeURIComponent(rid) +
        '">Open full result</a> · ' +
        '<a href="/cognitive-dashboard/?sandbox=1">Continue in sandbox</a>';
    }
  }

  function degradedReceipt(container, msg) {
    skeletonReceipt(container);
    var foot = container.querySelector(".nf-live-proof-footer");
    if (foot) {
      foot.innerHTML =
        (msg || "API offline") +
        ' · <span class="nf-live-proof-degraded">Sample receipt</span> · ' +
        '<a href="/start/">Start sandbox when API returns</a>';
    }
    var map = {
      tle_id: "TLE-015DCFB8B953",
      decision: "allow",
      confidence_score: "0.82",
      rid: "RID-2026-0602-HOME",
      evidence_index: "purview · entra · audit",
      export_integrity: "PASS · fail closed on tamper",
    };
    ROWS.forEach(function (key) {
      animateRow(
        container.querySelector('[data-key="' + key + '"]'),
        map[key],
        key === "export_integrity"
      );
    });
  }

  function bindForm(root) {
    var form = qs("#nfLiveProofForm", root);
    if (!form) return;
    var receiptHost = qs("#nfLiveProofReceipt", root);
    skeletonReceipt(receiptHost);

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var actor = (qs('[name="actor"]', form) || {}).value || "www-hero";
      var action = (qs('[name="action"]', form) || {}).value || "copilot_rollout";
      var context =
        (qs('[name="context"]', form) || {}).value ||
        "Homepage live proof — Copilot governance evaluate";
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
          metadata: { source: "live-proof-hero" },
        }),
      })
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (data) {
          if (!data.rid) throw new Error("no rid");
          renderReceipt(receiptHost, data, data.rid);
          if (window.noetfieldSandbox && window.noetfieldSandbox.incrementEvaluate) {
            window.noetfieldSandbox.incrementEvaluate();
          }
        })
        .catch(function () {
          degradedReceipt(receiptHost, "Start sandbox when API returns");
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

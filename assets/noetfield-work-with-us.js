/** Work with Noetfield — lane pills, URL prefill, dynamic notes placeholder. */
(function () {
  "use strict";

  var NOTE_PLACEHOLDERS = {
    connector:
      "Warm intro network · regulated EU/US sectors · typical intro fee expectations · unclassified only",
    facilitator:
      "Workshop formats · Copilot kickoff experience · geographies · unclassified only",
    "co-partner":
      "Joint delivery scope · SOW experience · Governance Pack bands · unclassified only",
    partner:
      "MSP/SI practice · Purview readiness · tenant count · Phase 2 attach model · unclassified only",
    investor:
      "Fund stage · thesis fit · Land · Expand · Channel questions · intro path · unclassified only",
  };

  function queryRole() {
    try {
      return new URLSearchParams(window.location.search).get("role") || "";
    } catch (_) {
      return "";
    }
  }

  function setLane(lane, scroll) {
    var select = document.getElementById("nfPartnerRole");
    var notes = document.getElementById("nfPartnerNotes");
    if (!select || !lane) return;

    select.value = lane;
    select.dispatchEvent(new Event("change", { bubbles: true }));

    document.querySelectorAll(".nf-wwu-lane-pill").forEach(function (btn) {
      var active = btn.getAttribute("data-wwu-lane") === lane;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });

    if (notes && NOTE_PLACEHOLDERS[lane]) {
      notes.placeholder = NOTE_PLACEHOLDERS[lane];
    }

    if (scroll) {
      var target = document.getElementById("partner-apply");
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function bindPills() {
    document.querySelectorAll(".nf-wwu-lane-pill").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setLane(btn.getAttribute("data-wwu-lane"), false);
      });
    });

    document.querySelectorAll("[data-wwu-pick]").forEach(function (link) {
      link.addEventListener("click", function (ev) {
        ev.preventDefault();
        setLane(link.getAttribute("data-wwu-pick"), true);
      });
    });

    var select = document.getElementById("nfPartnerRole");
    if (select) {
      select.addEventListener("change", function () {
        if (select.value) setLane(select.value, false);
      });
    }
  }

  function init() {
    bindPills();
    var fromUrl = queryRole();
    if (fromUrl) setLane(fromUrl, window.location.hash === "#partner-apply");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

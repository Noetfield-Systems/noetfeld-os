/** Design-partner pilot apply — Sumsub-class inline intake → trust-brief router */
(function () {
  "use strict";

  function enc(v) {
    return encodeURIComponent(v || "");
  }

  function bind() {
    var form = document.getElementById("nfPilotApplyForm");
    if (!form) return;

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var base = form.getAttribute("data-intake") || "/trust-brief/intake/?interest=pilot&vector=copilot-governance";
      var email = (form.querySelector('[name="email"]') || {}).value || "";
      var org = (form.querySelector('[name="org"]') || {}).value || "";
      var role = (form.querySelector('[name="role"]') || {}).value || "";
      var band = (form.querySelector('[name="band"]') || {}).value || "";
      var notes = (form.querySelector('[name="notes"]') || {}).value || "";

      if (!email || !org) {
        alert("Work email and organization are required.");
        return;
      }

      var url = base;
      if (url.indexOf("?") === -1) url += "?";
      else if (url.slice(-1) !== "&" && url.slice(-1) !== "?") url += "&";

      url +=
        "email=" +
        enc(email) +
        "&org=" +
        enc(org) +
        "&role=" +
        enc(role) +
        "&band=" +
        enc(band);

      if (notes) {
        try {
          sessionStorage.setItem(
            "nf_pilot_intake_notes",
            JSON.stringify({ email: email, org: org, notes: notes, band: band, role: role })
          );
        } catch (_) {}
      }

      window.location.href = url;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();

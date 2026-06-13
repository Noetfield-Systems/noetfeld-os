/** Work with Noetfield — ecosystem apply form → trust-brief intake router */
(function () {
  "use strict";

  function enc(v) {
    return encodeURIComponent(v || "");
  }

  function bind() {
    var form = document.getElementById("nfPartnerApplyForm");
    if (!form) return;

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var base =
        form.getAttribute("data-intake") ||
        "/trust-brief/intake/?interest=partner&vector=work-with-us";
      var email = (form.querySelector('[name="email"]') || {}).value || "";
      var org = (form.querySelector('[name="org"]') || {}).value || "";
      var role = (form.querySelector('[name="role"]') || {}).value || "";
      var region = (form.querySelector('[name="region"]') || {}).value || "";
      var notes = (form.querySelector('[name="notes"]') || {}).value || "";

      if (!email || !org || !role) {
        alert("Work email, organization, and program lane are required.");
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
        "&region=" +
        enc(region);

      if (notes) {
        try {
          sessionStorage.setItem(
            "nf_partner_intake_notes",
            JSON.stringify({ email: email, org: org, role: role, region: region, notes: notes })
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

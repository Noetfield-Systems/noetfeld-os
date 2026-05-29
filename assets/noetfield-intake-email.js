/* Canonical intake email — single operational inbox for Gmail monitor loop */
(function (g) {
  "use strict";

  var CANONICAL = "operations@noetfield.com";

  function enc(s) {
    return encodeURIComponent(s || "");
  }

  function intakeVector() {
    try {
      var sp = new URLSearchParams(g.location.search);
      return (
        sp.get("vector") ||
        sp.get("interest") ||
        sp.get("source") ||
        ""
      ).trim();
    } catch (_) {
      return "";
    }
  }

  function mailto(subject, body, vector) {
    var v = (vector || intakeVector() || "trust-brief-intake").trim();
    var subj = subject || "Noetfield — Intake";
    if (v && subj.indexOf("[vector:") === -1) {
      subj = "[vector:" + v + "] " + subj;
    }
    var fullBody =
      (body || "") +
      (v ? "\n\nSource vector: " + v + "\nAlert destination: " + CANONICAL + "\n" : "");
    return "mailto:" + CANONICAL + "?subject=" + enc(subj) + "&body=" + enc(fullBody);
  }

  function rewriteLegacyMailtos(root) {
    var scope = root || document;
    var legacy =
      /^(contact|procurement|sales|support|feedback|engagements|billing|trust|legal)@noetfield\.com$/i;
    try {
      scope.querySelectorAll('a[href^="mailto:"]').forEach(function (a) {
        var href = a.getAttribute("href") || "";
        var m = href.match(/^mailto:([^?]+)/i);
        if (!m) return;
        var addr = decodeURIComponent(m[1]).trim();
        if (legacy.test(addr) || addr.toLowerCase() === CANONICAL.toLowerCase()) {
          var rest = href.indexOf("?") >= 0 ? href.slice(href.indexOf("?")) : "";
          if (rest) {
            a.setAttribute("href", "mailto:" + CANONICAL + rest);
          } else {
            a.setAttribute("href", mailto("Noetfield — Intake", "", intakeVector()));
          }
        }
      });
    } catch (_) {}
  }

  g.NOETFIELD_CANONICAL_INTAKE_EMAIL = CANONICAL;
  g.noetfieldIntakeMailto = mailto;
  g.noetfieldRewriteLegacyMailtos = rewriteLegacyMailtos;

  function boot() {
    rewriteLegacyMailtos(document);
  }

  g.addEventListener("nf:shell:ready", boot);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);

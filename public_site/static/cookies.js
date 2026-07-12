(function () {
  "use strict";

  var STORAGE_KEY = "noos_cookie_consent_v1";
  var banner = document.getElementById("cookie-banner");
  var modal = document.getElementById("cookie-preferences");
  if (!banner) return;

  function readConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_err) {
      return null;
    }
  }

  function writeConsent(consent) {
    consent.updatedAt = new Date().toISOString();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(consent));
    applyConsent(consent);
    hideBanner();
    hideModal();
    document.dispatchEvent(new CustomEvent("noos:cookie-consent", { detail: consent }));
  }

  function defaultConsent(essential, analytics) {
    return {
      version: 1,
      essential: essential !== false,
      analytics: !!analytics,
    };
  }

  function applyConsent(consent) {
    document.documentElement.dataset.analytics = consent.analytics ? "granted" : "denied";
    if (consent.analytics) {
      /* Hook for future analytics — no third-party scripts loaded by default */
    }
  }

  function showBanner() {
    banner.hidden = false;
    banner.setAttribute("aria-hidden", "false");
  }

  function hideBanner() {
    banner.hidden = true;
    banner.setAttribute("aria-hidden", "true");
  }

  function showModal() {
    if (!modal) return;
    modal.hidden = false;
    modal.setAttribute("aria-hidden", "false");
    var first = modal.querySelector("input, button");
    if (first) first.focus();
  }

  function hideModal() {
    if (!modal) return;
    modal.hidden = true;
    modal.setAttribute("aria-hidden", "true");
  }

  function syncModalFromConsent(consent) {
    if (!modal) return;
    var analytics = modal.querySelector("#cookie-analytics");
    if (analytics) analytics.checked = !!(consent && consent.analytics);
  }

  banner.querySelector("[data-cookie-accept]")?.addEventListener("click", function () {
    writeConsent(defaultConsent(true, true));
  });

  banner.querySelector("[data-cookie-reject]")?.addEventListener("click", function () {
    writeConsent(defaultConsent(true, false));
  });

  banner.querySelector("[data-cookie-customize]")?.addEventListener("click", function () {
    syncModalFromConsent(readConsent() || defaultConsent(true, false));
    showModal();
  });

  document.querySelector("[data-cookie-manage]")?.addEventListener("click", function (event) {
    event.preventDefault();
    syncModalFromConsent(readConsent() || defaultConsent(true, false));
    showModal();
  });

  modal?.querySelector("[data-cookie-save]")?.addEventListener("click", function () {
    var analytics = modal.querySelector("#cookie-analytics");
    writeConsent(defaultConsent(true, analytics && analytics.checked));
  });

  modal?.querySelector("[data-cookie-cancel]")?.addEventListener("click", function () {
    hideModal();
  });

  modal?.querySelector("[data-cookie-modal-backdrop]")?.addEventListener("click", function () {
    hideModal();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal && !modal.hidden) hideModal();
  });

  var existing = readConsent();
  if (existing && typeof existing.essential === "boolean") {
    applyConsent(existing);
    hideBanner();
  } else {
    showBanner();
  }
})();

(function () {
  "use strict";

  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  var main = document.getElementById("main-content");
  if (main && !main.hasAttribute("tabindex")) {
    main.setAttribute("tabindex", "-1");
  }

  document.querySelector(".skip-link")?.addEventListener("click", function () {
    if (main) main.focus({ preventScroll: false });
  });
})();

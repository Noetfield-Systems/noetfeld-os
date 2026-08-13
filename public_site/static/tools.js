(function () {
  var LOAD = 1.3;
  var WEEKS = 48;
  var HOBBY = 3000;
  var NOTICE = "Nothing is posted. Nothing is stored.";

  function money(n) {
    var v = Number.isFinite(n) && n > 0 ? n : 0;
    return new Intl.NumberFormat("en-CA", {
      style: "currency",
      currency: "CAD",
      maximumFractionDigits: 0,
    }).format(Math.round(v));
  }

  function num(form, name) {
    return Number(form.elements[name] && form.elements[name].value ? form.elements[name].value : 0);
  }

  function sel(form, name) {
    var el = form.elements[name];
    return el ? String(el.value || "") : "";
  }

  function checked(form, name) {
    var el = form.elements[name];
    return !!(el && el.checked);
  }

  function processCost(touches, minutes, rate, people) {
    return Number(touches) * (Number(minutes) / 60) * Number(rate) * LOAD * Number(people) * WEEKS;
  }

  var CTAS = {
    app: { href: "https://app.noetfield.com/", label: "Open the app" },
    readiness: { href: "https://www.noetfield.com/copilot/pilot/", label: "Copilot pilot" },
    brief: { href: "https://www.noetfield.com/trust-brief/", label: "Trust Brief" },
    intake: { href: "https://www.noetfield.com/trust-brief/intake/", label: "Trust Brief intake" },
    calculator: { href: "https://sourcea.app/calculator", label: "Full process-cost calculator" },
    tools: { href: "/tools/", label: "See the other checks" },
  };

  function compute(tool, form) {
    if (tool === "quiet-leak") {
      var cost = processCost(num(form, "touches"), num(form, "minutes"), num(form, "rate"), num(form, "people"));
      if (cost < HOBBY) {
        return {
          kind: "leave",
          amount: money(cost) + " / year",
          headline: "Leave it alone.",
          body: "Under $3,000 a year, automating this is a hobby, not an investment. The page says that out loud instead of selling you a fix.",
          extra: "Count one real day before you trust the estimate. People undercount touches by about half.",
          cta: "calculator",
        };
      }
      if (cost < 15000) {
        return {
          kind: "look",
          amount: money(cost) + " / year",
          headline: "Real money. Still not a platform.",
          body: "Price one leak first. If the number is real, start with one named goal and a check that can fail.",
          extra: "",
          cta: "app",
        };
      }
      return {
        kind: "act",
        amount: money(cost) + " / year",
        headline: "This leak is large enough to name.",
        body: "Give this process as a goal in the open alpha. Plan, run, check, stop for your decision. Founder-operated. No fake customer logos.",
        extra: "",
        cta: "app",
      };
    }

    if (tool === "ai-spend") {
      var monthly = Math.max(0, num(form, "monthly"));
      var share = Math.min(100, Math.max(0, num(form, "attributed"))) / 100;
      var teams = Math.max(1, num(form, "teams") || 1);
      var named = sel(form, "named") === "yes";
      var annual = monthly * (1 - share) * 12;
      var amount = money(annual) + " / year unattributed";
      if (monthly < 1500 && teams <= 1) {
        return {
          kind: "leave",
          amount: amount,
          headline: "Leave it alone.",
          body: "Under about $1,500 a month and one team, a spreadsheet is enough. Do not buy a governance stack for a hobby.",
          extra: "",
          cta: "tools",
        };
      }
      if (named && share >= 0.2) {
        return {
          kind: "leave",
          amount: amount,
          headline: "You already have the bones.",
          body: "Named workflow and named accepter. Do not buy a platform tour. Tighten the receipt, then stop shopping.",
          extra: "",
          cta: "app",
        };
      }
      if (share < 0.2) {
        return {
          kind: "act",
          amount: amount,
          headline: "The leak is explanation, not tokens.",
          body: "Under 20% attributed, nobody can defend the bill. Name one workflow, one owner, and who accepts output before it leaves.",
          extra: "People count licensed Copilot and forget personal ChatGPT. That unofficial line is often larger.",
          cta: "readiness",
        };
      }
      return {
        kind: "look",
        amount: amount,
        headline: "Attribute more before you buy more.",
        body: "Spend is large enough to care. The next honest step is a named workflow and a named accepter, not another seat.",
        extra: "",
        cta: "app",
      };
    }

    if (tool === "who-accepted") {
      var deliverables = Math.max(0, num(form, "deliverables"));
      var signed = Math.min(100, Math.max(0, num(form, "signed"))) / 100;
      var minutes = Math.max(0, num(form, "minutes"));
      var rate = Math.max(0, num(form, "rate"));
      var replay = sel(form, "replay") === "yes";
      var redo = deliverables * (1 - signed) * (minutes / 60) * rate * LOAD * WEEKS;
      var amount = money(redo) + " / year of unsigned redo";
      if (signed >= 0.9 && replay) {
        return {
          kind: "leave",
          amount: amount,
          headline: "Leave it alone.",
          body: "A named signer and a replayable why. You do not need another copilot. Keep the receipt. Stop shopping.",
          extra: "",
          cta: "tools",
        };
      }
      if (signed < 0.5 || !replay) {
        return {
          kind: "act",
          amount: amount,
          headline: "That is a chat log, not a process.",
          body: "Name who accepts, keep the reason, and let a check fail. One real goal in the open alpha is enough to try that.",
          extra: "The builder must not grade itself. If the model that wrote the draft also marks it done, you have a hope, not a check.",
          cta: "app",
        };
      }
      return {
        kind: "look",
        amount: amount,
        headline: "Close the replay gap.",
        body: "Signing without a why still fails a board question. Record the pass/fail reason before you buy more seats.",
        extra: "",
        cta: "app",
      };
    }

    if (tool === "copilot-seats") {
      var licensed = Math.max(0, num(form, "licensed"));
      var used = Math.min(licensed, Math.max(0, num(form, "used")));
      var hours = Math.max(0, num(form, "hours"));
      var wage = Math.max(0, num(form, "rate"));
      var seat = Math.max(0, num(form, "seat"));
      var unused = Math.max(0, licensed - used);
      var waste = unused * seat;
      var ungoverned = used * hours * wage * LOAD * WEEKS;
      var amount = money(waste) + " unused licenses · " + money(ungoverned) + " ungoverned use / year";
      if (unused < 10 && licensed <= 20) {
        return {
          kind: "leave",
          amount: amount,
          headline: "Fix adoption. Do not buy policy.",
          body: "Unused seats under about 10 is not a governance purchase. Turn unused licenses off, or train the people who have them.",
          extra: "Showing only the unused-license number is how a post stays dishonest. The used-seat line is usually larger.",
          cta: "tools",
        };
      }
      if (used >= 10 && hours >= 2) {
        return {
          kind: "act",
          amount: amount,
          headline: "You are paying for labor with no trail.",
          body: "The used-seat line is the one that matters. Name the workflow, the owner, and who accepts output.",
          extra: "",
          cta: "brief",
        };
      }
      return {
        kind: "look",
        amount: amount,
        headline: "Show both numbers to finance.",
        body: "License waste is visible. Ungoverned use is usually larger and quieter. Do not let a seat-optimization slide hide the second number.",
        extra: "",
        cta: "readiness",
      };
    }

    if (tool === "board-five") {
      var n =
        (checked(form, "workflow") ? 1 : 0) +
        (checked(form, "owner") ? 1 : 0) +
        (checked(form, "spend") ? 1 : 0) +
        (checked(form, "failed") ? 1 : 0) +
        (checked(form, "accepted") ? 1 : 0);
      if (n <= 1) {
        return {
          kind: "leave",
          amount: n + " / 5",
          headline: "Do not buy.",
          body: "You are not ready for a diagnostic. Name the workflow and the owner first. Open the app if you want one real goal with a check that can fail.",
          extra: "",
          cta: "app",
        };
      }
      if (n <= 3) {
        return {
          kind: "look",
          amount: n + " / 5",
          headline: "Procurement may need a file. You do not need a tour.",
          body: "Copilot Readiness is the pack that can be filed. The missing yeses are still the work: spend, last failure, or who accepted.",
          extra: "",
          cta: "readiness",
        };
      }
      return {
        kind: "act",
        amount: n + " / 5",
        headline: "Trust Brief only if you need a board memo.",
        body: "You can already answer the room. Buy a memo if the board needs paper. Do not buy another copilot to feel busy.",
        extra: "",
        cta: "intake",
      };
    }

    return null;
  }

  function applyPreset(form, raw) {
    var data;
    try {
      data = JSON.parse(raw);
    } catch {
      return;
    }
    Object.keys(data).forEach(function (key) {
      var el = form.elements[key];
      if (!el) return;
      if (el.type === "checkbox") el.checked = !!data[key];
      else el.value = data[key];
    });
    if (Object.keys(data).length === 0) {
      Array.prototype.forEach.call(form.elements, function (el) {
        if (el.type === "checkbox") el.checked = false;
      });
    }
  }

  function applyParams(form) {
    var params = new URLSearchParams(window.location.search);
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || !params.has(el.name)) return;
      if (el.type === "checkbox") el.checked = params.get(el.name) === "1" || params.get(el.name) === "true";
      else el.value = params.get(el.name);
    });
  }

  function shareUrl(form) {
    var url = new URL(window.location.href);
    url.searchParams.delete("embed");
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name) return;
      if (el.type === "checkbox") url.searchParams.set(el.name, el.checked ? "1" : "0");
      else url.searchParams.set(el.name, String(el.value || ""));
    });
    return url.toString();
  }

  function flash(btn, text) {
    if (!btn) return;
    var prior = btn.textContent;
    btn.textContent = text;
    setTimeout(function () {
      btn.textContent = prior;
    }, 1600);
  }

  function render(tool, form) {
    var result = compute(tool, form);
    if (!result) return;
    var box = document.getElementById("nf-tools-result");
    var amount = document.querySelector("[data-result-amount]");
    var headline = document.querySelector("[data-result-headline]");
    var body = document.querySelector("[data-result-body]");
    var extra = document.querySelector("[data-result-extra]");
    var cta = document.querySelector("[data-result-cta]");
    if (box) box.setAttribute("data-kind", result.kind);
    if (amount && !amount.hidden) amount.textContent = result.amount;
    if (amount && amount.hidden && tool === "board-five") {
      amount.hidden = false;
      amount.textContent = result.amount;
    }
    if (headline) headline.textContent = result.headline;
    if (body) body.textContent = result.body;
    if (extra) {
      extra.textContent = result.extra || "";
      extra.hidden = !result.extra;
    }
    var dest = CTAS[result.cta] || CTAS.tools;
    if (cta) {
      cta.setAttribute("href", dest.href);
      cta.textContent = dest.label;
    }
  }

  function bootEmbedBlocks() {
    document.querySelectorAll("[data-embed-src]").forEach(function (block) {
      var src = block.getAttribute("data-embed-src");
      var code = '<iframe src="' + src + '" title="Noetfield tool" width="100%" height="740" style="border:0;border-radius:12px" loading="lazy"></iframe>';
      var slot = block.querySelector("code");
      if (slot) slot.textContent = code;
      var btn = block.querySelector("[data-copy-embed]");
      if (btn) {
        btn.addEventListener("click", function () {
          navigator.clipboard.writeText(code).then(function () {
            flash(btn, "Copied");
          }).catch(function () {
            window.prompt("Copy this embed", code);
          });
        });
      }
    });
  }

  function boot() {
    var params = new URLSearchParams(window.location.search);
    if (params.get("embed") === "1") document.body.classList.add("nf-tools--embed");
    bootEmbedBlocks();
    var tool = document.body.getAttribute("data-tool") || "";
    var form = document.getElementById("nf-tools-form");
    if (!form) return;
    applyParams(form);
    render(tool, form);
    form.addEventListener("input", function () {
      render(tool, form);
    });
    form.addEventListener("change", function () {
      render(tool, form);
    });
    form.addEventListener("submit", function (event) {
      event.preventDefault();
    });
    document.querySelectorAll("[data-preset]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyPreset(form, btn.getAttribute("data-preset") || "{}");
        render(tool, form);
      });
    });
    var share = document.getElementById("nf-tools-share");
    if (share) {
      share.addEventListener("click", function () {
        var href = shareUrl(form);
        navigator.clipboard.writeText(href).then(function () {
          flash(share, "Link copied");
        }).catch(function () {
          window.prompt("Copy this link", href);
        });
      });
    }
    var copy = document.getElementById("nf-tools-copy");
    if (copy) {
      copy.addEventListener("click", function () {
        var headline = document.querySelector("[data-result-headline]");
        var body = document.querySelector("[data-result-body]");
        var amount = document.querySelector("[data-result-amount]");
        var text = [amount && amount.textContent, headline && headline.textContent, body && body.textContent, NOTICE, window.location.href]
          .filter(Boolean)
          .join("\n");
        navigator.clipboard.writeText(text).then(function () {
          flash(copy, "Copied");
        });
      });
    }
  }

  window.NF_TOOLS_MATH = { LOAD: LOAD, WEEKS: WEEKS, money: money, processCost: processCost, compute: compute };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();

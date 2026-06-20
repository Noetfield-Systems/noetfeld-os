/** Self-serve developer sandbox + Trial OS wizard (v18 UI-02). */
(function () {
  var STORAGE_KEY = "nf_sandbox_v1";
  var SESSION_ID_KEY = "nf_sandbox_sid_v1";
  var LIMIT_EVALUATES = 50;
  var TRIAL_DAYS = 14;
  var STEPS = ["account", "environment", "connect", "evaluate", "receipt"];

  function useServerApi() {
    return window.NF_SANDBOX_API === 1 || window.NF_SANDBOX_API === "1";
  }

  function apiSessionsUrl() {
    var base = window.NF_SANDBOX_API_BASE || "";
    return base + "/api/v1/sandbox/sessions";
  }

  function readSession() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeSession(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      if (data && data.session_id) {
        localStorage.setItem(SESSION_ID_KEY, data.session_id);
      }
    } catch (e) {}
    if (useServerApi() && data && data.session_id) {
      fetch(apiSessionsUrl() + "/" + encodeURIComponent(data.session_id), {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evaluates_used: data.evaluates_used,
          trial_step: data.trial_step,
          m365_connected: data.m365_connected,
        }),
      }).catch(function () {});
    }
  }

  function serverToClient(data) {
    return {
      session_id: data.session_id,
      email: data.email,
      org: data.org,
      tenant_id: data.tenant_id,
      api_key_preview: data.api_key_preview,
      mode: data.mode || "sandbox",
      evaluates_used: data.evaluates_used || 0,
      evaluates_limit: data.evaluates_limit || LIMIT_EVALUATES,
      created_at: data.created_at,
      expires_at: data.expires_at,
      trial_step: data.trial_step || 0,
      m365_connected: !!data.m365_connected,
    };
  }

  function newTenantId() {
    var hex = "0123456789abcdef";
    var s = "sandbox-";
    for (var i = 0; i < 8; i++) s += hex[Math.floor(Math.random() * 16)];
    return s;
  }

  function daysRemaining(expiresAt) {
    var ms = new Date(expiresAt).getTime() - Date.now();
    return Math.max(0, Math.ceil(ms / 86400000));
  }

  function createSessionLocal(email, org) {
    var now = Date.now();
    var session = {
      email: email,
      org: org || "Sandbox org",
      tenant_id: newTenantId(),
      api_key_preview: "nf_sbx_" + Math.random().toString(36).slice(2, 10),
      mode: "sandbox",
      evaluates_used: 0,
      evaluates_limit: LIMIT_EVALUATES,
      created_at: new Date(now).toISOString(),
      expires_at: new Date(now + TRIAL_DAYS * 86400000).toISOString(),
      trial_step: 0,
      m365_connected: false,
    };
    writeSession(session);
    return session;
  }

  function createSession(email, org, onReady) {
    if (!useServerApi()) {
      var local = createSessionLocal(email, org);
      if (onReady) onReady(local);
      return local;
    }
    fetch(apiSessionsUrl(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, org: org || "Sandbox org" }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("sandbox api");
        return res.json();
      })
      .then(function (data) {
        var session = serverToClient(data);
        writeSession(session);
        if (onReady) onReady(session);
      })
      .catch(function () {
        var fallback = createSessionLocal(email, org);
        if (onReady) onReady(fallback);
      });
    return null;
  }

  function resumeServerSession(onReady) {
    if (!useServerApi()) {
      if (onReady) onReady(readSession());
      return;
    }
    var sid = null;
    try {
      sid = localStorage.getItem(SESSION_ID_KEY);
    } catch (e) {}
    if (!sid) {
      if (onReady) onReady(readSession());
      return;
    }
    fetch(apiSessionsUrl() + "/" + encodeURIComponent(sid))
      .then(function (res) {
        if (!res.ok) throw new Error("resume failed");
        return res.json();
      })
      .then(function (data) {
        var session = serverToClient(data);
        writeSession(session);
        if (onReady) onReady(session);
      })
      .catch(function () {
        if (onReady) onReady(readSession());
      });
  }

  function incrementEvaluate() {
    var session = readSession();
    if (!session) return null;
    session.evaluates_used = Math.min(
      session.evaluates_limit,
      (session.evaluates_used || 0) + 1
    );
    if (session.trial_step < 4) session.trial_step = 4;
    writeSession(session);
    renderUsageChips();
    return session;
  }

  function usageLabel(session) {
    if (!session) return "";
    var days = daysRemaining(session.expires_at);
    return (
      (session.evaluates_used || 0) +
      "/" +
      session.evaluates_limit +
      " evaluates · " +
      days +
      " days left"
    );
  }

  function renderUsageChips() {
    var session = readSession();
    var label = usageLabel(session);
    document.querySelectorAll("[data-nf-usage-chip]").forEach(function (el) {
      if (!session) {
        el.hidden = true;
        return;
      }
      el.hidden = false;
      el.textContent = label;
    });
  }

  function setTrialStep(index) {
    var session = readSession();
    if (session) {
      session.trial_step = Math.max(session.trial_step || 0, index);
      writeSession(session);
    }
    updateTrialUI(index);
  }

  function updateTrialUI(activeIndex) {
    var root = document.getElementById("nfTrialOs");
    if (!root) return;
    var session = readSession();

    root.querySelectorAll(".nf-trial-os__step").forEach(function (el, i) {
      el.classList.remove("is-active", "is-done");
      if (i < activeIndex) el.classList.add("is-done");
      if (i === activeIndex) el.classList.add("is-active");
    });

    root.querySelectorAll(".nf-trial-os__panel").forEach(function (panel, i) {
      panel.classList.toggle("is-active", i === activeIndex);
    });

    var usage = root.querySelector(".nf-trial-os__usage");
    if (usage && session) {
      usage.hidden = false;
      usage.textContent = usageLabel(session);
    }

    var keyEl = root.querySelector("[data-api-key]");
    if (keyEl && session) keyEl.textContent = session.api_key_preview;

    var curlEl = root.querySelector("[data-curl-example]");
    if (curlEl && session) {
      curlEl.textContent =
        'curl -X POST "' +
        location.origin +
        '/evaluate" \\\n  -H "Content-Type: application/json" \\\n  -H "X-Tenant-ID: ' +
        session.tenant_id +
        '" \\\n  -d \'{"actor":"sandbox","action":"copilot_rollout","context":"Trial OS evaluate"}\'';
    }
  }

  function afterSessionReady(session, next) {
    if (!session) return;
    try {
      var u = new URL(next, location.origin);
      u.searchParams.set("tenant", session.tenant_id);
      u.searchParams.set("sandbox", "1");
      location.href = u.pathname + u.search;
    } catch (e) {
      location.href = next;
    }
  }

  function bindLegacyForm(form) {
    if (!form) return;
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var emailEl = form.querySelector('[name="email"]');
      var orgEl = form.querySelector('[name="org"]');
      var email = emailEl && emailEl.value ? emailEl.value.trim() : "";
      if (!email || email.indexOf("@") < 1) {
        alert("Enter a work email to start your sandbox.");
        return;
      }
      var next = form.getAttribute("data-next") || "/cognitive-dashboard/?sandbox=1";
      createSession(email, orgEl && orgEl.value ? orgEl.value.trim() : "", function (session) {
        afterSessionReady(session, next);
      });
    });
  }

  function bindTrialOs(root) {
    if (!root) return;
    resumeServerSession(function (session) {
      var startIndex = session ? Math.min(STEPS.length - 1, session.trial_step || 0) : 0;
      updateTrialUI(startIndex);
      renderUsageChips();
    });

    var accountForm = root.querySelector("#nfTrialAccountForm");
    if (accountForm) {
      accountForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var email = (root.querySelector('[name="email"]') || {}).value || "";
        var org = (root.querySelector('[name="org"]') || {}).value || "";
        if (!email || email.indexOf("@") < 1) {
          alert("Enter a work email.");
          return;
        }
        createSession(email.trim(), org.trim(), function () {
          setTrialStep(1);
        });
      });
    }

    root.querySelectorAll("[data-trial-next]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var step = parseInt(btn.getAttribute("data-trial-next") || "0", 10);
        setTrialStep(step);
      });
    });

    var oauthBtn = root.querySelector("#nfTrialMockOAuth");
    if (oauthBtn) {
      oauthBtn.addEventListener("click", function () {
        var s = readSession();
        if (s) {
          s.m365_connected = true;
          s.trial_step = 3;
          writeSession(s);
        }
        var status = root.querySelector("#nfTrialOAuthStatus");
        if (status) {
          status.hidden = false;
          status.textContent = "Mock OAuth connected · M365 evidence ingested (sandbox simulation)";
        }
        setTrialStep(3);
      });
    }

    var evalForm = root.querySelector("#nfTrialEvaluateForm");
    if (evalForm) {
      evalForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var s = readSession();
        var btn = evalForm.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Evaluating…";
        }
        fetch("/evaluate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Tenant-ID": s ? s.tenant_id : "sandbox",
          },
          body: JSON.stringify({
            actor: "trial-os",
            action: "copilot_rollout",
            context: "Trial OS first evaluate",
            metadata: { source: "trial-os-flow" },
          }),
        })
          .then(function (res) {
            return res.json();
          })
          .then(function (data) {
            incrementEvaluate();
            var ridEl = root.querySelector("[data-trial-rid]");
            if (ridEl && data.rid) ridEl.textContent = data.rid;
            setTrialStep(4);
          })
          .catch(function () {
            alert("Evaluate failed — ensure dev stack is running.");
          })
          .finally(function () {
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Run first evaluate";
            }
          });
      });
    }

    var finishBtn = root.querySelector("#nfTrialFinish");
    if (finishBtn) {
      finishBtn.addEventListener("click", function () {
        var s = readSession();
        var next = "/cognitive-dashboard/?sandbox=1";
        if (s) next += "&tenant=" + encodeURIComponent(s.tenant_id);
        location.href = next;
      });
    }
  }

  function renderStatus(el) {
    if (!el) return;
    var session = readSession();
    if (!session) {
      el.hidden = true;
      return;
    }
    el.hidden = false;
    el.innerHTML =
      "<p><strong>Sandbox active</strong> · tenant <code>" +
      session.tenant_id +
      "</code> · " +
      usageLabel(session) +
      " · mode <strong>sandbox</strong></p>";
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindLegacyForm(document.getElementById("nfSandboxForm"));
    bindTrialOs(document.getElementById("nfTrialOs"));
    resumeServerSession(function () {
      renderStatus(document.getElementById("nfSandboxStatus"));
      renderUsageChips();
      var badge = document.getElementById("nfSandboxBadge");
      if (badge && readSession()) {
        badge.textContent = "Sandbox";
        badge.hidden = false;
      }
    });
  });

  window.noetfieldSandbox = {
    read: readSession,
    create: createSession,
    incrementEvaluate: incrementEvaluate,
    limit: LIMIT_EVALUATES,
    trialDays: TRIAL_DAYS,
    useServerApi: useServerApi,
  };
})();

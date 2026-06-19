/** Self-serve developer sandbox + Trial OS wizard (v2 — server-backed). */
(function () {
  var STORAGE_KEY = "nf_sandbox_v2";
  var TOKEN_KEY = "nf_sandbox_token";
  var API_BASE = (function () {
    var meta = document.querySelector('meta[name="nf-chat-api-base"]');
    return (meta && meta.getAttribute("content")) || "";
  })();

  function apiUrl(path) {
    if (API_BASE) return API_BASE.replace(/\/$/, "") + path;
    return path;
  }

  function readSession() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function readToken() {
    try {
      return localStorage.getItem(TOKEN_KEY) || "";
    } catch (e) {
      return "";
    }
  }

  function writeSession(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      if (data && data.session_token) {
        localStorage.setItem(TOKEN_KEY, data.session_token);
      }
    } catch (e) {}
  }

  function daysRemaining(expiresAt) {
    var ms = new Date(expiresAt).getTime() - Date.now();
    return Math.max(0, Math.ceil(ms / 86400000));
  }

  function normalizeSession(data) {
    if (!data) return null;
    return {
      session_token: data.session_token || readToken(),
      email: data.email,
      org: data.org || "Sandbox org",
      tenant_id: data.tenant_id,
      api_key_preview: data.api_key_preview,
      mode: data.mode || "observe",
      evaluates_used: data.evaluates_used || 0,
      evaluates_limit: data.evaluates_limit || 50,
      created_at: data.created_at,
      expires_at: data.expires_at,
      trial_step: data.trial_step || 0,
      m365_connected: !!data.m365_connected,
      last_rid: data.last_rid || null,
      factory_demos_run: data.factory_demos_run || [],
      upgrade_url: data.upgrade_url || "/trust-brief/intake/?interest=pilot&vector=copilot-governance",
    };
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
      " days left · mode " +
      (session.mode || "observe")
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

  function sandboxHeaders() {
    var token = readToken();
    var headers = { "Content-Type": "application/json" };
    if (token) headers["X-Sandbox-Token"] = token;
    return headers;
  }

  function provisionSession(email, org) {
    return fetch(apiUrl("/api/sandbox/provision"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, org: org || "" }),
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error((data && data.detail) || "Provision failed");
        var session = normalizeSession(data);
        writeSession(session);
        renderUsageChips();
        return session;
      });
    });
  }

  function refreshSession() {
    var token = readToken();
    if (!token) return Promise.resolve(readSession());
    return fetch(apiUrl("/api/sandbox/session"), {
      headers: sandboxHeaders(),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error((data && data.detail) || "Session expired");
          var session = normalizeSession(data);
          writeSession(session);
          renderUsageChips();
          return session;
        });
      })
      .catch(function () {
        return readSession();
      });
  }

  function patchSession(patch) {
    return fetch(apiUrl("/api/sandbox/session"), {
      method: "PATCH",
      headers: sandboxHeaders(),
      body: JSON.stringify(patch),
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error((data && data.detail) || "Update failed");
        var session = normalizeSession(data);
        writeSession(session);
        renderUsageChips();
        return session;
      });
    });
  }

  function setTrialStep(index) {
    var session = readSession();
    if (session && readToken()) {
      patchSession({ trial_step: index }).then(function () {
        updateTrialUI(index);
      });
      return;
    }
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
        (API_BASE || location.origin) +
        '/api/sandbox/evaluate" \\\n  -H "X-Sandbox-Token: ' +
        (session.session_token || readToken()) +
        '"';
    }

    var ridEl = root.querySelector("[data-trial-rid]");
    if (ridEl && session && session.last_rid) ridEl.textContent = session.last_rid;

    var upgradeEl = root.querySelector("[data-sandbox-upgrade]");
    if (upgradeEl && session) {
      var base = session.upgrade_url || "/trust-brief/intake/?interest=pilot&vector=copilot-governance";
      var url = base;
      if (session.last_rid) {
        url += (base.indexOf("?") >= 0 ? "&" : "?") + "request_id=" + encodeURIComponent(session.last_rid);
      }
      upgradeEl.setAttribute("href", url);
    }

    var warnEl = root.querySelector("#nfTrialUsageWarn");
    if (warnEl && session) {
      var warnAt = Math.ceil(session.evaluates_limit * 0.8);
      if (session.evaluates_used >= warnAt) {
        warnEl.hidden = false;
        warnEl.textContent =
          "You've used " +
          session.evaluates_used +
          "/" +
          session.evaluates_limit +
          " evaluates — upgrade to Copilot Readiness Pack for production tenant and enforce mode.";
      } else {
        warnEl.hidden = true;
      }
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
      provisionSession(email, orgEl && orgEl.value ? orgEl.value.trim() : "")
        .then(function (session) {
          var next = form.getAttribute("data-next") || "/cognitive-dashboard/?sandbox=1";
          try {
            var u = new URL(next, location.origin);
            if (session) u.searchParams.set("tenant", session.tenant_id);
            u.searchParams.set("sandbox", "1");
            location.href = u.pathname + u.search;
          } catch (e) {
            location.href = next;
          }
        })
        .catch(function (err) {
          alert(err.message || "Sandbox provision failed — try a work email.");
        });
    });
  }

  function runFactoryDemo(factoryId) {
    return fetch(apiUrl("/api/sandbox/factory-demo"), {
      method: "POST",
      headers: sandboxHeaders(),
      body: JSON.stringify({ factory_id: factoryId }),
    }).then(function (res) {
      return res.json();
    });
  }

  function bindTrialOs(root) {
    if (!root) return;

    refreshSession().then(function (session) {
      var startIndex = session ? Math.min(4, session.trial_step || 0) : 0;
      updateTrialUI(startIndex);
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
        var btn = accountForm.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Provisioning…";
        }
        provisionSession(email.trim(), org.trim())
          .then(function () {
            setTrialStep(1);
          })
          .catch(function (err) {
            alert(err.message || "Provision failed — use a work email address.");
          })
          .finally(function () {
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Continue";
            }
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
        var done = function () {
          var status = root.querySelector("#nfTrialOAuthStatus");
          if (status) {
            status.hidden = false;
            status.textContent =
              "Mock OAuth connected · M365 evidence ingested (sandbox simulation · observe mode)";
          }
          setTrialStep(3);
        };
        if (readToken()) {
          patchSession({ m365_connected: true, trial_step: 3 }).then(done);
        } else {
          done();
        }
      });
    }

    root.querySelectorAll("[data-factory-demo]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var factoryId = btn.getAttribute("data-factory-demo");
        if (!factoryId || !readToken()) return;
        btn.disabled = true;
        runFactoryDemo(factoryId)
          .then(function () {
            btn.textContent = "Demo complete";
          })
          .catch(function () {
            btn.disabled = false;
          });
      });
    });

    var evalForm = root.querySelector("#nfTrialEvaluateForm");
    if (evalForm) {
      evalForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var btn = evalForm.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Evaluating…";
        }
        fetch(apiUrl("/api/sandbox/evaluate"), {
          method: "POST",
          headers: sandboxHeaders(),
        })
          .then(function (res) {
            return res.json().then(function (data) {
              if (!res.ok) throw new Error((data && data.detail) || "Evaluate failed");
              return data;
            });
          })
          .then(function (data) {
            return refreshSession().then(function () {
              var ridEl = root.querySelector("[data-trial-rid]");
              if (ridEl && data.rid) ridEl.textContent = data.rid;
              if (data.usage_warning) {
                var warnEl = root.querySelector("#nfTrialUsageWarn");
                if (warnEl) {
                  warnEl.hidden = false;
                  warnEl.textContent =
                    "Approaching evaluate cap — " +
                    data.evaluates_used +
                    "/" +
                    data.evaluates_limit +
                    " used. Upgrade for production enforce mode.";
                }
              }
              setTrialStep(4);
            });
          })
          .catch(function (err) {
            alert(err.message || "Evaluate failed — ensure API is reachable.");
          })
          .finally(function () {
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Run first evaluate";
            }
          });
      });
    }

    var exportBtn = root.querySelector("#nfTrialExportPdf");
    if (exportBtn) {
      exportBtn.addEventListener("click", function (ev) {
        ev.preventDefault();
        var token = readToken();
        if (!token) {
          alert("Complete sandbox signup before exporting.");
          return;
        }
        exportBtn.disabled = true;
        fetch(apiUrl("/api/sandbox/export/board.pdf"), {
          headers: { "X-Sandbox-Token": token },
        })
          .then(function (res) {
            if (!res.ok) throw new Error("Export failed");
            return res.blob();
          })
          .then(function (blob) {
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = "noetfield-board-sandbox.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
          })
          .catch(function () {
            alert("Board PDF export failed — ensure sandbox session is active.");
          })
          .finally(function () {
            exportBtn.disabled = false;
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
      "</p>";
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindLegacyForm(document.getElementById("nfSandboxForm"));
    bindTrialOs(document.getElementById("nfTrialOs"));
    renderStatus(document.getElementById("nfSandboxStatus"));
    renderUsageChips();
    var badge = document.getElementById("nfSandboxBadge");
    if (badge && readSession()) {
      badge.textContent = "Sandbox";
      badge.hidden = false;
    }
  });

  window.noetfieldSandbox = {
    read: readSession,
    provision: provisionSession,
    refresh: refreshSession,
    apiUrl: apiUrl,
    limit: 50,
    trialDays: 14,
    mode: "observe",
  };
})();

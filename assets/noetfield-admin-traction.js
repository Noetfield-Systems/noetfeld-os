/** Internal traction dashboard client. Requires X-Admin-Secret; no public data without it. */
(function () {
  "use strict";

  var STORAGE_KEY = "nf_admin_secret";
  var state = { data: null, eventFilter: "all", search: "" };

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function secret() {
    try {
      return localStorage.getItem(STORAGE_KEY) || "";
    } catch (_) {
      return "";
    }
  }

  function setSecret(value) {
    try {
      if (value) localStorage.setItem(STORAGE_KEY, value);
      else localStorage.removeItem(STORAGE_KEY);
    } catch (_) {}
  }

  function setStatus(message, kind) {
    var el = $("nfAdminStatus");
    if (!el) return;
    el.hidden = false;
    el.className = "nf-admin-status" + (kind ? " nf-admin-status--" + kind : "");
    el.textContent = message;
  }

  function track(eventName, metadata) {
    try {
      if (window.NFAnalytics && window.NFAnalytics.track) {
        window.NFAnalytics.track(eventName, Object.assign({ component: "admin-traction" }, metadata || {}));
      }
    } catch (_) {}
  }

  function metricCard(label, value, hint) {
    return (
      '<article class="nf-admin-card"><span>' +
      escapeHtml(label) +
      "</span><strong>" +
      escapeHtml(value) +
      "</strong><small>" +
      escapeHtml(hint || "") +
      "</small></article>"
    );
  }

  function matchesSearch(item) {
    if (!state.search) return true;
    return JSON.stringify(item || {}).toLowerCase().indexOf(state.search.toLowerCase()) >= 0;
  }

  function filterEvents(items) {
    return (items || []).filter(function (item) {
      return (state.eventFilter === "all" || item.event_name === state.eventFilter) && matchesSearch(item);
    });
  }

  function filterRows(items) {
    return (items || []).filter(matchesSearch);
  }

  function rows(items, columns) {
    if (!items || !items.length) {
      return '<tr><td colspan="' + columns.length + '">No records match the current filters.</td></tr>';
    }
    return items
      .map(function (item) {
        return (
          "<tr>" +
          columns
            .map(function (col) {
              return "<td>" + escapeHtml(item[col] == null ? "" : item[col]) + "</td>";
            })
            .join("") +
          "</tr>"
        );
      })
      .join("");
  }

  function table(title, items, columns, labels) {
    return (
      '<section class="nf-admin-panel"><h2>' +
      escapeHtml(title) +
      '</h2><div class="nf-admin-table-wrap"><table><thead><tr>' +
      labels
        .map(function (label) {
          return "<th>" + escapeHtml(label) + "</th>";
        })
        .join("") +
      "</tr></thead><tbody>" +
      rows(items, columns) +
      "</tbody></table></div></section>"
    );
  }

  function funnel(items) {
    items = items || [];
    var max = Math.max.apply(
      null,
      items.map(function (item) {
        return Number(item.count || 0);
      }).concat([1])
    );
    return (
      '<section class="nf-admin-panel"><h2>Conversion Funnel</h2><div class="nf-admin-funnel">' +
      items
        .map(function (item) {
          var width = Math.max(4, Math.round((Number(item.count || 0) / max) * 100));
          return (
            '<div class="nf-admin-funnel-row"><span>' +
            escapeHtml(item.stage) +
            '</span><div><i style="width:' +
            width +
            '%"></i></div><strong>' +
            escapeHtml(item.count || 0) +
            "</strong></div>"
          );
        })
        .join("") +
      "</div></section>"
    );
  }

  function eventOptions(data) {
    var names = (data.events_by_name || []).map(function (item) {
      return item.event_name;
    });
    var sel = $("nfEventFilter");
    if (!sel) return;
    var current = sel.value || "all";
    sel.innerHTML =
      '<option value="all">All events</option>' +
      names
        .map(function (name) {
          return '<option value="' + escapeHtml(name) + '">' + escapeHtml(name) + "</option>";
        })
        .join("");
    sel.value = names.indexOf(current) >= 0 ? current : "all";
    state.eventFilter = sel.value;
  }

  function currentExportRows() {
    if (!state.data) return [];
    return {
      totals: state.data.totals || {},
      funnel: state.data.funnel || [],
      recent_events: filterEvents(state.data.recent_events || []),
      recent_leads: filterRows(state.data.recent_leads || []),
      recent_conversions: filterRows(state.data.recent_conversions || []),
    };
  }

  function download(filename, content, type) {
    var blob = new Blob([content], { type: type || "text/plain" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 500);
  }

  function toCsv(rowsIn) {
    var rows = rowsIn || [];
    if (!rows.length) return "";
    var columns = Object.keys(rows[0]);
    return [columns.join(",")]
      .concat(
        rows.map(function (row) {
          return columns
            .map(function (col) {
              return '"' + String(row[col] == null ? "" : row[col]).replace(/"/g, '""') + '"';
            })
            .join(",");
        })
      )
      .join("\n");
  }

  function render(data) {
    state.data = data;
    eventOptions(data);
    var root = $("nfTractionOutput");
    if (!root) return;
    var totals = data.totals || {};
    var filteredEvents = filterEvents(data.recent_events || []);
    root.innerHTML =
      '<section class="nf-admin-grid">' +
      metricCard("Events", totals.events || 0, data.window_days + " day window") +
      metricCard("Sessions", totals.sessions || 0, "visitor_sessions") +
      metricCard("Conversions", totals.conversions || 0, "forms, chat, CTA") +
      metricCard("Leads", totals.leads || 0, "lead_profiles") +
      metricCard("Form submits", totals.form_submits || 0, "high-intent") +
      metricCard("Chat messages", totals.chat_messages || 0, "assistant engagement") +
      metricCard("CTA clicks", totals.cta_clicks || 0, "commercial clicks") +
      "</section>" +
      funnel(data.funnel || []) +
      table("Event Activity", data.events_by_name || [], ["event_name", "count"], ["Event", "Count"]) +
      table("Conversion Types", data.conversions_by_type || [], ["conversion_type", "count"], ["Conversion", "Count"]) +
      table("Top Pages", data.top_pages || [], ["page_path", "count"], ["Page", "Events"]) +
      table("Source Pages", data.source_pages || [], ["landing_page", "count"], ["Landing page", "Sessions"]) +
      table("Recent Leads", filterRows(data.recent_leads || []), ["organization", "primary_email", "status", "lead_score", "last_seen_at"], ["Org", "Email", "Status", "Score", "Last seen"]) +
      table("Recent Conversions", filterRows(data.recent_conversions || []), ["conversion_type", "page_path", "lead_id", "request_id", "created_at"], ["Type", "Page", "Lead", "RID", "Created"]) +
      table("Recent Events", filteredEvents, ["event_name", "page_path", "session_id", "request_id", "created_at"], ["Event", "Page", "Session", "RID", "Created"]);
    $("nfGeneratedAt").textContent = data.generated_at || "";
  }

  function load() {
    var input = $("nfAdminSecret");
    var days = $("nfWindowDays");
    var value = input ? input.value.trim() : "";
    if (!value) {
      setStatus("Enter the admin secret to load traction data.", "err");
      return;
    }
    setSecret(value);
    setStatus("Loading traction summary...", "");
    track("admin_dashboard_load", { window_days: days ? days.value : "30" });
    fetch("/api/admin/traction?days=" + encodeURIComponent(days ? days.value : "30"), {
      headers: { Accept: "application/json", "X-Admin-Secret": value },
      credentials: "omit",
    })
      .then(function (res) {
        return res.json().then(function (body) {
          if (!res.ok) {
            var err = new Error(body.detail || "Traction API failed");
            err.status = res.status;
            throw err;
          }
          return body;
        });
      })
      .then(function (data) {
        render(data);
        setStatus("Loaded traction summary.", "ok");
      })
      .catch(function (err) {
        setStatus((err.status ? "HTTP " + err.status + ": " : "") + err.message, "err");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var input = $("nfAdminSecret");
    if (input) input.value = secret();
    var button = $("nfLoadTraction");
    if (button) button.addEventListener("click", load);
    var clear = $("nfClearSecret");
    if (clear) {
      clear.addEventListener("click", function () {
        setSecret("");
        if (input) input.value = "";
        setStatus("Admin secret cleared from this browser.", "");
      });
    }
    var search = $("nfAdminSearch");
    if (search) search.addEventListener("input", function () {
      state.search = search.value || "";
      if (state.data) render(state.data);
    });
    var eventFilter = $("nfEventFilter");
    if (eventFilter) eventFilter.addEventListener("change", function () {
      state.eventFilter = eventFilter.value || "all";
      if (state.data) render(state.data);
    });
    var exportJson = $("nfExportJson");
    if (exportJson) exportJson.addEventListener("click", function () {
      download("noetfield-traction.json", JSON.stringify(currentExportRows(), null, 2), "application/json");
      track("admin_dashboard_export", { format: "json" });
    });
    var exportCsv = $("nfExportCsv");
    if (exportCsv) exportCsv.addEventListener("click", function () {
      var rowsOut = currentExportRows().recent_events || [];
      download("noetfield-traction-events.csv", toCsv(rowsOut), "text/csv");
      track("admin_dashboard_export", { format: "csv" });
    });
    if (secret()) load();
  });
})();

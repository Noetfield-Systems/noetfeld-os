/** Intake ops notify — Telegram (@noetfield_ops_bot) primary channel for www submissions. */

const DEFAULT_CHAT_ID = "8635650894";

function telegramConfigured() {
  const token = (process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "").trim();
  const chatId = (process.env.TELEGRAM_OPS_CHAT_ID || DEFAULT_CHAT_ID).trim();
  return Boolean(token && chatId);
}

function formatIntakeTelegramText(body, intakeId) {
  const name = String(body.contact_name || "—").trim() || "—";
  const company = String(body.organization || "—").trim() || "—";
  const message = String(body.message || "").trim() || "—";
  const id = String(intakeId || "—").trim() || "—";
  return ["name: " + name, "company: " + company, "message: " + message, "intake ID: " + id].join("\n");
}

async function sendIntakeTelegram(body, intakeId) {
  const token = (process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "").trim();
  const chatId = (process.env.TELEGRAM_OPS_CHAT_ID || DEFAULT_CHAT_ID).trim();
  if (!token || !chatId) {
    return { ok: false, configured: false, error: "missing_telegram_config" };
  }

  const text = formatIntakeTelegramText(body, intakeId);
  const res = await fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text.slice(0, 4096),
      disable_web_page_preview: true,
    }),
  });

  const payload = await res.json().catch(function () {
    return {};
  });
  if (res.ok && payload.ok) {
    return {
      ok: true,
      configured: true,
      message_id: payload.result && payload.result.message_id ? payload.result.message_id : null,
    };
  }

  const err = payload.description || ("http_" + res.status);
  console.error("intake_telegram_failed", err);
  return { ok: false, configured: true, error: err };
}

module.exports = {
  DEFAULT_CHAT_ID,
  telegramConfigured,
  formatIntakeTelegramText,
  sendIntakeTelegram,
};

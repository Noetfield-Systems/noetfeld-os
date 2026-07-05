/** Intake inbox email — Resend delivery to operations@ + submitter ack (www serverless). */

const CANONICAL = "operations@noetfield.com";

function meta(body) {
  return body && typeof body.metadata === "object" && body.metadata ? body.metadata : {};
}

function intakeLabel(body) {
  const m = meta(body);
  const vector = String(body.vector || "").toLowerCase();
  const topic = String(m.topic || m.role || m.program_lane || "").toLowerCase();
  const sku = String(body.sku || "").toLowerCase();
  const formId = String(m.form_id || "").toLowerCase();

  if (vector.indexOf("sandbox") >= 0 || formId === "nfsandboxform" || formId === "nftrialaccountform") {
    return "Sandbox signup";
  }
  if (vector === "investor-diligence" || topic === "investor-diligence") {
    return "Investor diligence vault";
  }
  if (topic === "investor" || (vector === "work-with-us" && topic === "investor")) {
    return "Investor brief";
  }
  if (vector === "work-with-us" || ["connector", "facilitator", "co-partner", "partner"].indexOf(topic) >= 0) {
    return "Work with Noetfield application";
  }
  if (vector.indexOf("copilot") >= 0 || sku === "copilot" || topic === "pilot") {
    return "Governance Pack apply";
  }
  if (vector.indexOf("trust") >= 0 || sku === "trust_brief" || topic === "trust-brief") {
    return "Trust Brief Intake";
  }
  if (vector.indexOf("bank") >= 0 || sku === "bank_pilot" || topic === "bank-pilot") {
    return "Bank Pilot inquiry";
  }
  if (topic === "federal") return "Federal Brief";
  if (topic === "feedback") return "Site feedback";
  if (topic === "partner") return "Partner program";
  if (vector === "contact" && topic) return "Contact — " + topic;
  if (vector === "contact") return "Contact";
  return "Intake";
}

function metaLine(body) {
  const m = meta(body);
  const parts = [];
  const lane = m.program_lane || m.buyer_role || m.role || "";
  const topic = m.topic || "";
  if (lane) parts.push("lane/role: " + lane);
  if (topic && topic !== lane) parts.push("topic: " + topic);
  if (m.pilot_band) parts.push("pilot_band: " + m.pilot_band);
  if (m.engagement) parts.push("engagement: " + m.engagement);
  if (m.page) parts.push("page: " + m.page);
  if (m.form_id) parts.push("form: " + m.form_id);
  if (m.async) parts.push("async web submit");
  return parts.join(" · ");
}

function intakeSubject(body, intakeId) {
  const rid = body.request_id || intakeId;
  const label = intakeLabel(body);
  const vector = String(body.vector || "").trim();
  if (vector && label.indexOf("[vector:") < 0) {
    return "[vector:" + vector + "] Noetfield — " + label + " (" + rid + ")";
  }
  return "Noetfield — " + label + " (" + rid + ")";
}

function opsBodyText(body, intakeId) {
  const m = meta(body);
  const ctx = metaLine(body);
  const lines = [
    "New Noetfield intake — REPLY to this email to reach the submitter.",
    "",
    "Intake ID: " + intakeId,
    "RID: " + (body.request_id || "—"),
    "Organization: " + (body.organization || "—"),
    "Contact: " + (body.contact_name || "—") + " <" + (body.contact_email || "—") + ">",
    "SKU: " + (body.sku || "—"),
    "Vector: " + (body.vector || "—"),
    "Source: " + (body.source || "web"),
  ];
  if (ctx) lines.push("Context: " + ctx);
  lines.push("", "Message:", String(body.message || "").trim(), "");
  return lines.join("\n");
}

function ackBody(body, intakeId) {
  const name = body.contact_name ? " " + body.contact_name : "";
  const rid = body.request_id || intakeId;
  return (
    "Hi" +
    name +
    ",\n\n" +
    "Your message was saved instantly. Operations at Noetfield will follow up within one business day.\n\n" +
    "Reference: " +
    rid +
    "\n" +
    "Intake ID: " +
    intakeId +
    "\n\n" +
    "Reply to this email or write " +
    CANONICAL +
    " — include your Request ID in any follow-up.\n\n" +
    "— Noetfield Operations\n" +
    CANONICAL +
    "\n"
  );
}

async function sendResend({ from, to, subject, text, replyTo, requestId }) {
  const key = (process.env.RESEND_API_KEY || "").trim();
  if (!key) return { ok: false, error: "missing_api_key" };
  const payload = { from, to, subject, text };
  if (replyTo) payload.reply_to = replyTo;
  const rid = String(requestId || "").trim().toUpperCase();
  if (rid) payload.tags = [{ name: "request_id", value: rid }];

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + key,
    },
    body: JSON.stringify(payload),
  });
  if (res.ok) return { ok: true };
  const errBody = await res.text().catch(function () {
    return "";
  });
  console.error("resend_send_failed", res.status, errBody.slice(0, 500));
  return { ok: false, error: errBody.slice(0, 200) };
}

function emailConfigured() {
  return Boolean((process.env.RESEND_API_KEY || "").trim());
}

async function sendIntakeEmails(body, ids) {
  const intakeId = ids.intakeId;
  const from =
    (process.env.INTAKE_EMAIL_FROM || "").trim() ||
    "Noetfield Intake <notifications@noetfield.com>";
  const inbox = (process.env.INTAKE_EMAIL_TO || CANONICAL).trim();
  const autoAck = (process.env.INTAKE_AUTO_ACK_ENABLED || "true").toLowerCase() !== "false";

  if (!emailConfigured()) {
    return { ops: false, ack: false, configured: false };
  }
  if (!body.contact_email || String(body.contact_email).indexOf("@") < 1) {
    return { ops: false, ack: false, configured: true };
  }

  const opsResult = await sendResend({
    from,
    to: [inbox],
    subject: intakeSubject(body, intakeId),
    text: opsBodyText(body, intakeId),
    replyTo: body.contact_email,
    requestId: body.request_id || ids.rid || null,
  });
  const ops = opsResult.ok;

  let ack = false;
  if (autoAck && ops) {
    const ackResult = await sendResend({
      from,
      to: [body.contact_email],
      subject: "Noetfield — message received (" + (body.request_id || intakeId) + ")",
      text: ackBody(body, intakeId),
      replyTo: CANONICAL,
      requestId: body.request_id || ids.rid || null,
    });
    ack = ackResult.ok;
  }

  return { ops, ack, configured: true, resend_error: ops ? null : opsResult.error || null };
}

module.exports = {
  CANONICAL,
  emailConfigured,
  intakeLabel,
  intakeSubject,
  opsBodyText,
  sendIntakeEmails,
};

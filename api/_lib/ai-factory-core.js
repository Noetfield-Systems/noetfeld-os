function hash(value) {
  const s = JSON.stringify(value);
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16).padStart(8, "0");
}

function randomId() {
  if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }
  return "req-" + hash({ t: Date.now(), r: Math.random() });
}

function validateGateRequest(payload) {
  const errors = [];
  for (const field of ["factory_type", "target_user", "output_format", "payload"]) {
    if (payload[field] === undefined || payload[field] === null || payload[field] === "") {
      errors.push({ field, code: "required", message: `${field} is required` });
    }
  }
  if (payload.payload !== undefined && (typeof payload.payload !== "object" || Array.isArray(payload.payload))) {
    errors.push({ field: "payload", code: "invalid_type", message: "payload must be a JSON object" });
  }
  return errors;
}

function policyDecision(payload) {
  const serialized = JSON.stringify(payload).toLowerCase();
  if (serialized.includes("prohibited") || serialized.includes("bypass")) return "BLOCK";
  if (serialized.includes("regulated") || serialized.includes("msb") || serialized.includes("compliance")) return "ESCALATE";
  return "ALLOW";
}

function buildFactoryReceipt(payload) {
  const requestId = payload.request_id || randomId();
  const normalized = {
    request_id: requestId,
    user_id: payload.user_id || "anonymous",
    factory_type: payload.factory_type,
    target_user: payload.target_user,
    output_format: payload.output_format,
    payload: payload.payload || {},
    policy_mode: payload.policy_mode || "ALLOW / BLOCK / ESCALATE"
  };
  const decision = policyDecision(normalized);
  const statusRecord = {
    request_id: requestId,
    request_type: "AI Factory",
    lane: decision === "BLOCK" ? "validation" : "intake",
    next_action: decision === "BLOCK" ? "Revise request scope before design" : "Review generated Factory Spec",
    policy_decision: decision,
    current_node: "receive_request",
    audit_state: "minimal_receipt_created",
    terminal_state: null
  };
  const receipt = {
    request_id: requestId,
    gate_lane: "AI Factory Design",
    status: decision === "BLOCK" ? "partial" : "accepted",
    status_record: statusRecord,
    factory_spec_ref: "/ai-factories/spec/",
    audit: {
      request_id: requestId,
      input_hash: hash(normalized),
      policy_decision: decision,
      execution_trace: ["receive_request", "validate_input", "assign_gate_lane", "create_status_record", "write_minimal_audit_receipt"],
      stateless: true,
      storage: "none_in_runtime",
      created_at: new Date().toISOString()
    },
    adapters: {
      status: { configured: false },
      trust_ledger: { configured: false }
    }
  };
  receipt.audit.final_output_hash = hash(receipt);
  return receipt;
}

function buildStatusPreview(requestId) {
  const lanes = ["intake", "design", "spec_review", "validation", "deployment", "ledger_complete"];
  const digest = hash(requestId);
  const lane = lanes[digest.charCodeAt(0) % lanes.length];
  return {
    request_id: requestId,
    request_type: "AI Factory",
    lane,
    policy_decision: digest.charCodeAt(1) % 5 === 0 ? "ESCALATE" : "ALLOW",
    current_node: lane === "ledger_complete" ? "write_audit_record" : "create_execution_plan",
    audit_state: lane === "ledger_complete" ? "ledger_ready" : "in_progress",
    next_action: lane === "ledger_complete" ? "Review Trust Ledger receipt" : "Continue factory design review",
    stateless_preview: true
  };
}

module.exports = { buildFactoryReceipt, buildStatusPreview, validateGateRequest };

/**
 * @noetfield/gate — fetch wrapper for Noetfield GEL POST /v1/decision
 * UPG-0165 / UPG-0166 scaffold (publish pending legal/npm org)
 */

export interface DecisionRequest {
  applicant_id: string;
  credit_score: number;
  monthly_debt: number;
  monthly_income: number;
  loan_amount: number;
  collateral_value: number;
  employment_history_years: number;
  liquid_reserves_months: number;
  request_id?: string;
  correlation_id?: string;
  rule_set_version?: string;
}

export interface PolicyHashes {
  base: string;
  corridor: string;
  combined: string;
}

export interface DecisionProvenance {
  policy_decision: string;
  corridor_decision: string | null;
  corridor_breaches: string[];
  final_source: string;
}

/** API response + receipt envelope for downstream audit export. */
export interface DecisionReceipt {
  request_id: string;
  applicant_id: string;
  tenant_id: string;
  decision: "APPROVE" | "REVIEW" | "DECLINE" | string;
  composite_score: number;
  score_breakdown: Record<string, number>;
  policy_decision: string;
  corridor_decision: string | null;
  corridor_breaches: string[];
  rule_set_id: string;
  rule_set_version: string;
  policy_hashes: PolicyHashes;
  provenance: DecisionProvenance;
  audit_id: number;
  correlation_id?: string | null;
}

export interface PostDecisionOptions {
  apiUrl?: string;
  apiKey: string;
  signal?: AbortSignal;
}

const DEFAULT_API_URL = "https://api.noetfield.com";

export async function postDecision(
  payload: DecisionRequest,
  options: PostDecisionOptions,
): Promise<DecisionReceipt> {
  const base = (options.apiUrl ?? process.env.NOETFIELD_API_URL ?? DEFAULT_API_URL).replace(
    /\/$/,
    "",
  );
  const res = await fetch(`${base}/v1/decision`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": options.apiKey,
    },
    body: JSON.stringify(payload),
    signal: options.signal,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Noetfield decision API ${res.status}: ${detail}`);
  }
  return (await res.json()) as DecisionReceipt;
}

/** Sample approve-path intent (matches Python SAMPLE_INTENT). */
export const SAMPLE_APPROVE_INTENT: DecisionRequest = {
  applicant_id: "gate-demo-001",
  credit_score: 720,
  monthly_debt: 1200,
  monthly_income: 6000,
  loan_amount: 250000,
  collateral_value: 320000,
  employment_history_years: 4,
  liquid_reserves_months: 6,
};

/** Extreme DTI intent — expect DECLINE from corridor policy. */
export const SAMPLE_DECLINE_INTENT: DecisionRequest = {
  applicant_id: "gate-demo-decline",
  credit_score: 620,
  monthly_debt: 4200,
  monthly_income: 6000,
  loan_amount: 350000,
  collateral_value: 300000,
  employment_history_years: 1,
  liquid_reserves_months: 1,
};

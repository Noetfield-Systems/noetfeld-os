---
id: llm-drift-detection-architecture
status: locked
version: 1
locked_at: 2026-06-06
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
product_scope: noetfield-only
index: GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md
---

# LLM Drift Detection Architecture — Enterprise Blueprint (2026 Edition)

**Status:** LOCKED L2 supplement — Trust Brief / Copilot buyer appendix  
**Mode:** **Cite and record** — Noetfield does not host PSI, embedding monitors, or cost telemetry lakes  
**Defers to:** [GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md](./GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md) Part E  
**Integrates with:** [GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md](./GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md) · [TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md](./TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md)

---

## One sentence

LLM Drift Detection Architecture is a **behavioral and semantic observability layer** on top of LLM systems that continuously monitors quality, behavior, cost, and risk—detecting deviation from baseline, scoring it, and recording actionable governance records.

---

## 1. Architecture layers (overview)

| Layer | Role | Primary output |
|-------|------|----------------|
| **Telemetry & tracing** | Capture raw data from every request | Trace/span with inputs, outputs, metadata |
| **Behavior & quality evaluation** | Measure quality, alignment, safety | Quality scores, hallucination rate, tone, adherence |
| **Drift analytics** | Detect deviation from baseline | Drift signals and alerts |
| **Cost & usage monitoring** | Track spend and usage patterns | Cost drift, token drift, latency tails |
| **Governance & response** | Decide, act, audit | Alerts, rollback, retrain, policy update → Trust Ledger |

This five-layer model aligns with 2026 LLM observability practice: **tracing · evaluation · cost · quality drift**.

---

## 2. Layer 1 — Telemetry & tracing (reality capture)

**Goal:** Every LLM interaction is recorded in structured form.

### Inputs

- Prompt (raw + normalized)
- Context (RAG: retrieved documents, chunk IDs)
- Model ID / version
- System prompt / policy version
- User / session / tenant ID
- Tool definitions available

### Outputs

- Completion (full text)
- Token counts (input / output)
- Latency (P50 / P95 / P99)
- Errors / provider codes
- Tool calls (name, args, results)

### Standards & tooling

- **Tracing:** Langfuse, LangSmith, Helicone, or equivalent + **OpenTelemetry GenAI** conventions (`gen_ai.request.model`, `gen_ai.usage.input_tokens`, etc.)
- Each call → parent span with child spans for retrieval, rerank, tools, guardrails

**Noetfield role:** Ingest customer-owned trace exports as **evidence** cited at TLE decision time—not replace customer observability stack.

---

## 3. Layer 2 — Behavior & quality evaluation

Drift moves from “technical metrics” to **quality and behavior**.

### 3.1 LLM-as-a-judge pipelines

For samples (or stratified subsets), a judge model evaluates:

| Dimension | Metric |
|-----------|--------|
| Factuality / faithfulness (RAG) | Hallucination rate |
| Instruction following | Adherence score ∈ [0,1] |
| Tone / style | Tone consistency score |
| Safety | Toxicity / policy violation rate |
| Task success | Helpfulness / outcome pass rate |

Automated evaluation + pass-rate metrics are standard in 2026 LLM observability guides.

### 3.2 Behavioral drift framework

Research and production experience (2024–2026) show LLMs drift over time in:

- Response verbosity
- Instruction adherence
- Factuality
- Tone and safety behavior

**Required:** Per-dimension rubric + rolling baseline.

---

## 4. Layer 3 — Drift analytics & detection

Classic model drift architecture, extended with **semantic** and **behavioral** dimensions.

### 4.1 Drift types in LLM systems

| Type | Definition | Example signal |
|------|------------|----------------|
| **Data / input drift** | Pₜ(prompt, context) ≠ P_baseline | New domains, languages, longer RAG contexts |
| **Behavioral drift** | Change in instruction-following, tone, verbosity, safety, reasoning patterns | Adherence drop after prompt change |
| **Quality drift** | Decline in factuality, task success, satisfaction | Hallucination rate ↑ over 7-day window |
| **Cost drift** | Spend or token profile change | 4× completion length after minor prompt edit |

### 4.2 Metrics and methods

**Statistical (on distributions):**

- PSI, KL, JS, Hellinger, Wasserstein on: prompt length, completion length, embedding distributions, intent class distributions

**Embedding-based:**

- Embeddings for prompt, response, retrieved context
- Compare windowed distributions (baseline vs current)

**Behavioral:**

- Rolling mean and variance of: `instruction_adherence_score`, `hallucination_rate`, `tone_score`, `policy_violation_rate`

**Quality detection:**

- Sliding windows (e.g., 7 days)
- Alert when Δmetric > threshold for sustained period

---

## 5. Layer 4 — Cost & usage drift

2026 operations emphasis: **silent cost blowouts** and **prompt drift**.

### Metrics

- Tokens per request (avg, P95)
- Completion length drift
- Cost per session / per feature
- Budget burn rate
- Latency tail drift (P95 / P99)

### Common scenarios

| Trigger | Effect |
|---------|--------|
| Small prompt change | 4× response length → 4× cost |
| Model version change (e.g., GPT-4 → 4.1) | Latency and price profile shift |
| RAG strategy change | Longer context → higher token spend |

---

## 6. Layer 5 — Governance, response & replay

Connects to Governance Drift Engine and Trust Ledger.

### 6.1 Alerting & SLOs

Define SLOs for:

- Hallucination rate
- Instruction adherence
- Latency P95
- Cost per 1K requests

Use Prometheus + Grafana (or equivalent) for dashboards and alert rules (e.g., quality drift > X% for Y minutes).

### 6.2 Response playbook

| Phase | Actions |
|-------|---------|
| **Triage** | Real drift vs noise? Which segment (geo, feature, channel)? |
| **Mitigation** | Prompt hotfix · policy update · guardrail tightening · model rollback |
| **Long-term** | Retrain (custom models) · retrieval strategy change · rubric redesign |

### 6.3 Trust Ledger & replay

Every drift event + decision + action → Trust Ledger entry.

Auditor questions enabled:

- *“How did the system behave on date X?”*
- *“Why did quality drop last month and what did you do?”*

---

## 7. End-to-end pipeline (production reference)

```text
1. Instrumentation & tracing     → every call → span + metadata + tokens + latency
2. Storage                     → raw traces + structured events
3. Evaluation jobs               → LLM-as-judge · rule checks · safety filters
4. Drift analytics               → sliding windows · baseline vs current
5. Monitoring & alerting         → dashboards · SLOs · alerts
6. Governance & response         → runbooks · approvals · Trust Ledger entries
```

---

## 8. Productization for Noetfield

### LLM Drift Profile (recommended spec)

A governed artifact defining:

```text
LLMDriftProfile {
  profile_id
  baseline_window
  input_distribution_metrics[]
  behavior_metrics[]
  quality_metrics[]
  cost_metrics[]
  thresholds{}
  escalation_paths[]
}
```

### Drift Contract (recommended)

Formal agreement between:

- Product team (Copilot feature owners)
- Governance (risk / compliance)
- Infra / SRE (observability ownership)

Defines: baseline, metrics, thresholds, escalation, Trust Ledger recording obligations.

**Noetfield GTM honesty:** Shadow-evaluate, rate-limit, record RID — **do not** imply Noetfield is Evidently/Deepchecks. Continuous ML/LLM monitoring stays in customer environment or Trust Brief scope.

---

## 9. External sensor integration (Noetfield)

| Sensor | Drift signal | Noetfield action |
|--------|--------------|------------------|
| Microsoft Purview DSPM/DLP | Copilot posture drift | Evidence ingest → TLE cites snapshot |
| Microsoft AGT | Agent inventory / behavior | Vocabulary for behavioral drift class |
| Customer Langfuse / OTel | Quality / cost drift | Evidence attachment at decision |
| MLOps (Arize, Galileo, etc.) | Model / embedding drift | Customer-owned; TLE cites evaluation ID |

---

## 10. Non-obvious insight

LLM drift is **multi-dimensional decay**: a model can stay “online” while silently degrading on factuality, cost, and safety simultaneously. The architecture must score **vectors**, not single thresholds—and bind every alert to a **replayable evidence snapshot**.

---

## 11. Recommended next specifications

1. **LLM Drift Profile Spec** — fields, metrics, thresholds  
2. **Drift Contract template** for design partners  
3. **Evidence pack extension** — `llm_drift_summary` block (roadmap schema)

---

*Private annex: `ops/private/agent-reference/blueprints/LLM_DRIFT_DETECTION_ARCHITECTURE_2026_LOCKED.md`*

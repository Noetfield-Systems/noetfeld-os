/**
 * Public Service Page: Agentic Cost Governance
 * 
 * This is the live, public-facing service page for Noetfield's ACG offering.
 * 
 * LIVE: Published to www.noetfield.com/services/agentic-cost-governance
 * Published: 2026-07-05
 */

"use client";

import React from "react";

interface ServiceModule {
  title: string;
  tagline: string;
  description: string;
  timeline: string;
  deliverables: string[];
}

const modules: ServiceModule[] = [
  {
    title: "AI Spend Leak Audit",
    tagline: "See the hidden cost surface",
    description: "Discover where your AI spend actually goes. We map all AI consumption across APIs, agents, and embedded models—then show you the leak zones and ROI impact.",
    timeline: "1–2 weeks",
    deliverables: [
      "Spend surface map (all AI APIs, agents, embedded models)",
      "Model usage breakdown by task and workflow",
      "Cost attribution to business outcomes",
      "Leak zone identification (auto-escalations, silent defaults, shared-key bleed)",
      "Margin impact estimate (quantified ROI leakage)"
    ]
  },
  {
    title: "Premium Model Firewall",
    tagline: "Lock in cost-safe defaults",
    description: "Define which models work for which tasks. We help you set cost-safe defaults, approval gates for premium models, and hard budget caps—then integrate with your systems.",
    timeline: "2–4 weeks",
    deliverables: [
      "Cost-safe routing policy (cheap ≠ routine, pay-as-needed for complex)",
      "Premium escalation gates (explicit approval, budget triggers)",
      "Hard budget caps per service, team, and workflow",
      "Graceful fallback policy (retry, circuit-break, or escalate)",
      "API key isolation with audit trail per credential"
    ]
  },
  {
    title: "Automation Cost Ledger",
    tagline: "Every dollar auditable, every decision logged",
    description: "Track real-time AI spend with full visibility. Know why each model was chosen, who approved premium spend, and detect anomalies before they hurt margins.",
    timeline: "Ongoing",
    deliverables: [
      "Real-time cost per automation invocation",
      "Model selection reasoning (policy, fallback, explicit request)",
      "Approval trail (who approved premium escalations, when, why)",
      "Monthly cost summary by automation, model tier, and team",
      "Anomaly detection and spike alerts"
    ]
  },
  {
    title: "Model ROI Router",
    tagline: "Cost-per-outcome, not cost-per-invocation",
    description: "Align model selection to business outcomes, not cost-cutting alone. We recommend the cheapest model that meets your quality bar—then measure if it works.",
    timeline: "4–6 weeks",
    deliverables: [
      "ROI targets per automation task (acceptable cost-per-outcome)",
      "Smart routing algorithm (minimum cost meeting quality bar)",
      "A/B cost analysis (savings from cheaper model variants)",
      "Outcome-to-model correlation (which models drive results?)",
      "Downgrade recommendations (when cheaper models work as well)"
    ]
  },
  {
    title: "Premium Escalation Policy",
    tagline: "Expensive models earn approval, not accidental spend",
    description: "Make premium model spend intentional, not automatic. We define thresholds, approval workflows, and cost-benefit analysis so premium choices are always auditable.",
    timeline: "2–3 weeks",
    deliverables: [
      "Escalation threshold definition (when cheap models fail)",
      "Approval workflow with human + policy gates",
      "Cost-benefit analysis per escalation (ROI of premium vs. baseline)",
      "Spend tracking and escalation rate monitoring",
      "Full governance audit log (who, why, when, outcome)"
    ]
  }
];

const painPoints = [
  "Auto model selection defaults to expensive reasoning models without buyer intent",
  "Premium inference modes activated silently on routine tasks",
  "Long-running background agents consume quota without visibility",
  "Shared API keys break spend attribution across applications",
  "Cheap models fail; expensive models invoked as automatic recovery",
  "GitHub Actions, Copilot, Cursor, Claude, OpenAI all debit same budget",
  "Finance teams cannot tie AI costs to business outcomes or automation tasks"
];

const nonClaims = [
  "Not a payment custody or banking service",
  "Not a PSP or Money Services Business (MSB)",
  "Not a full agentic platform (governance + audit only)",
  "Not a deployment platform (we recommend; you deploy)",
  "Not financial advisory (operational cost control only)",
  "Not a replacement for CFO/Finance teams",
  "Not a substitute for budget authority"
];

export default function ServiceACG() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      {/* Hero Section */}
      <section className="mx-auto max-w-5xl mb-20">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">
          For Enterprise Teams
        </p>
        <h1 className="mt-6 text-6xl font-semibold tracking-tight leading-tight">
          Agentic Cost Governance
        </h1>
        <p className="mt-8 text-2xl font-medium text-emerald-300 max-w-4xl">
          We help companies keep AI automation without letting silent premium-model defaults destroy ROI.
        </p>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <p className="text-sm font-semibold text-slate-400 mb-2">The Problem</p>
            <p className="text-slate-300">
              Background agents, Copilot, Cursor, Claude, and OpenAI automation leak cost silently. Expensive models auto-escalate. Premium defaults activate unknowingly. Finance can't track ROI.
            </p>
          </div>
          <div className="rounded-lg border border-emerald-800 bg-emerald-950/30 p-4">
            <p className="text-sm font-semibold text-emerald-300 mb-2">Our Solution</p>
            <p className="text-emerald-200">
              We audit your spend surface, lock in cost-safe policies, and restore ROI through transparent ledger, approval gates, and outcome correlation.
            </p>
          </div>
        </div>
      </section>

      {/* Buyer Pain Points */}
      <section className="mx-auto max-w-5xl mb-20">
        <h2 className="text-3xl font-semibold mb-8">The Silent Cost Leak</h2>
        <div className="grid gap-4">
          {painPoints.map((point, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 flex gap-4"
            >
              <span className="text-red-400 font-bold flex-shrink-0">•</span>
              <p className="text-slate-300">{point}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="mx-auto max-w-5xl mb-20">
        <h2 className="text-3xl font-semibold mb-4">How We Restore Your AI ROI</h2>
        <p className="text-slate-300 mb-10 max-w-3xl">
          Five modules, delivered sequentially or in parallel. Each builds visibility, enforces governance, and measurably improves cost-per-outcome.
        </p>
        <div className="space-y-8">
          {modules.map((module, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-8 hover:border-cyan-700 hover:bg-slate-900/70 transition"
            >
              {/* Module Header */}
              <div className="flex items-start justify-between gap-6 mb-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl font-bold text-cyan-300">{idx + 1}</span>
                    <div>
                      <h3 className="text-2xl font-semibold text-slate-100">
                        {module.title}
                      </h3>
                      <p className="text-sm text-emerald-300 italic mt-1">{module.tagline}</p>
                    </div>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs uppercase tracking-wider text-slate-500 mb-1">Timeline</p>
                  <p className="text-lg font-semibold text-cyan-300">{module.timeline}</p>
                </div>
              </div>

              {/* Module Description */}
              <p className="text-slate-300 mb-6 leading-relaxed">
                {module.description}
              </p>

              {/* Deliverables */}
              <div>
                <p className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">
                  What You Get
                </p>
                <ul className="space-y-2">
                  {module.deliverables.map((deliverable, didx) => (
                    <li
                      key={didx}
                      className="text-sm text-slate-300 flex gap-3"
                    >
                      <span className="text-emerald-400 font-bold flex-shrink-0">✓</span>
                      <span>{deliverable}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Value Proposition */}
      <section className="mx-auto max-w-5xl mb-20">
        <h2 className="text-3xl font-semibold mb-8">Buyer Value</h2>
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">
                  Before
                </th>
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">
                  After
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-700">
                <td className="py-3 px-4 text-slate-300">
                  Unknown spend: AI costs hidden
                </td>
                <td className="py-3 px-4 text-emerald-300">
                  Transparent ledger: Every $ auditable
                </td>
              </tr>
              <tr className="border-b border-slate-700">
                <td className="py-3 px-4 text-slate-300">
                  Silent premium defaults
                </td>
                <td className="py-3 px-4 text-emerald-300">
                  Cost-safe policies with approval gates
                </td>
              </tr>
              <tr className="border-b border-slate-700">
                <td className="py-3 px-4 text-slate-300">
                  Margin erosion
                </td>
                <td className="py-3 px-4 text-emerald-300">
                  ROI restored and tracked
                </td>
              </tr>
              <tr className="border-b border-slate-700">
                <td className="py-3 px-4 text-slate-300">
                  No attribution to outcomes
                </td>
                <td className="py-3 px-4 text-emerald-300">
                  Cost-per-outcome correlation
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-slate-300">
                  Uncontrollable spend
                </td>
                <td className="py-3 px-4 text-emerald-300">
                  Governed with budget caps
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Governance Boundary Section */}
      <section className="mx-auto max-w-5xl mb-20">
        <h2 className="text-3xl font-semibold mb-8">Clear Scope: What We Are & Aren't</h2>
        <div className="grid md:grid-cols-2 gap-8">
          {/* What We Are NOT */}
          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
            <h3 className="text-lg font-semibold text-slate-300 mb-4">What We're NOT</h3>
            <div className="space-y-3">
              {nonClaims.map((claim, idx) => (
                <div key={idx} className="flex gap-3 text-sm text-slate-400">
                  <span className="text-slate-600 flex-shrink-0 mt-0.5">—</span>
                  <p>{claim}</p>
                </div>
              ))}
            </div>
          </div>

          {/* What We ARE */}
          <div className="rounded-lg border border-emerald-800 bg-emerald-950/30 p-6">
            <h3 className="text-lg font-semibold text-emerald-300 mb-4">What We ARE</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex gap-3 text-emerald-200">
                <span className="text-emerald-400 flex-shrink-0 font-bold mt-0.5">✓</span>
                <span>Governance + audit + policy layer for AI cost control</span>
              </li>
              <li className="flex gap-3 text-emerald-200">
                <span className="text-emerald-400 flex-shrink-0 font-bold mt-0.5">✓</span>
                <span>Operational intelligence (spend surface, attribution, anomalies)</span>
              </li>
              <li className="flex gap-3 text-emerald-200">
                <span className="text-emerald-400 flex-shrink-0 font-bold mt-0.5">✓</span>
                <span>Policy enforcement toolkit (routing, gates, caps)</span>
              </li>
              <li className="flex gap-3 text-emerald-200">
                <span className="text-emerald-400 flex-shrink-0 font-bold mt-0.5">✓</span>
                <span>Transparency and auditability for automation spend</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="mx-auto max-w-5xl mb-20">
        <div className="rounded-lg border border-cyan-800 bg-cyan-950/20 p-8">
          <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Ready to Control Your AI Spend?</h2>
          <p className="text-slate-300 mb-6 max-w-3xl">
            If you're an enterprise team deploying background agents, GitHub Copilot, Cursor, or custom AI automation—and you're concerned about silent cost escalation—let's talk.
          </p>
          <p className="text-sm text-slate-500">
            Contact: operations@noetfield.com
          </p>
        </div>
      </section>

      {/* Footer */}
      <section className="mx-auto max-w-5xl border-t border-slate-800 pt-12 text-center text-slate-500 text-xs">
        <p>Agentic Cost Governance Service</p>
        <p className="mt-2">Published: 2026-07-05</p>
      </section>
    </main>
  );
}

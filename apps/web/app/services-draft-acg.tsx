/**
 * Draft Service Page: Agentic Cost Governance
 * 
 * Status: DRAFT (not published to live site)
 * This page is a draft component prepared for review.
 * Do NOT render to live www.noetfield.com until:
 * - Noetfield repo reconciliation is complete
 * - Vercel live deployment truth is verified
 * - NOOS receives updated lane receipt with service draft
 * - Buyer-audience verification passes
 * - Messaging coordination clears
 * 
 * Created: 2026-07-05
 */

"use client";

import React from "react";

interface ServiceModule {
  title: string;
  description: string;
  timeline: string;
  deliverables: string[];
}

const modules: ServiceModule[] = [
  {
    title: "AI Spend Leak Audit",
    description: "Discover the hidden cost surface. Map all AI consumption, model usage, cost attribution, and ROI leakage.",
    timeline: "1–2 weeks",
    deliverables: [
      "Spend surface map (APIs, agents, embedded models)",
      "Model usage breakdown by task/workflow",
      "Cost attribution to business outcomes",
      "Leak zone identification (auto-escalations, silent defaults)",
      "ROI leakage estimate and margin impact"
    ]
  },
  {
    title: "Premium Model Firewall",
    description: "Lock in cost-safe model routing. Define policies, escalation gates, budget caps, and fallback behavior.",
    timeline: "2–4 weeks",
    deliverables: [
      "Cost-safe model policy per task",
      "Premium escalation gates (approval, budget triggers)",
      "Hard budget caps per service/team/workflow",
      "Graceful fallback degradation policy",
      "API key isolation and audit trail"
    ]
  },
  {
    title: "Automation Cost Ledger",
    description: "Every automation action auditable. Real-time cost tracking, model reasoning logs, approval trails, anomaly detection.",
    timeline: "Ongoing integration",
    deliverables: [
      "Real-time cost per automation invocation",
      "Model selection reasoning log",
      "Approval trail (premium escalations)",
      "Monthly cost summary by automation/model/team",
      "Anomaly detection and spike alerts"
    ]
  },
  {
    title: "Model ROI Router",
    description: "Align model selection to business outcomes. Smart routing, A/B cost comparison, outcome tracking, recommendations.",
    timeline: "4–6 weeks",
    deliverables: [
      "ROI target setting per automation task",
      "Smart model routing (cost vs. quality)",
      "A/B cost comparison analysis",
      "Outcome-to-model correlation tracking",
      "Cost savings recommendations"
    ]
  },
  {
    title: "Premium Escalation Policy",
    description: "Earn the right to expensive models. Thresholds, approval workflows, cost-benefit analysis, governance trails.",
    timeline: "2–3 weeks",
    deliverables: [
      "Escalation threshold definition",
      "Approval workflow (human + policy gates)",
      "Cost-benefit analysis per escalation",
      "Spend tracking and escalation rate monitoring",
      "Full governance audit log"
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

export default function ServiceDraftACG() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      {/* Draft Warning Banner */}
      <div className="mx-auto max-w-5xl mb-8 rounded-lg border border-amber-600 bg-amber-950/30 p-4">
        <p className="text-sm font-semibold text-amber-300">
          ⚠️ DRAFT SERVICE PAGE
        </p>
        <p className="text-xs text-amber-200 mt-2">
          This service offering is in draft stage. Not published to live site. Awaiting reconciliation complete, Vercel verification, and buyer-audience review before publication.
        </p>
      </div>

      {/* Hero Section */}
      <section className="mx-auto max-w-5xl mb-16">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">
          Service Draft
        </p>
        <h1 className="mt-6 text-5xl font-semibold tracking-tight">
          Agentic Cost Governance
        </h1>
        <p className="mt-6 text-xl font-medium text-emerald-300">
          We help companies keep AI automation without letting silent premium-model defaults destroy ROI.
        </p>
        <p className="mt-4 max-w-3xl text-lg text-slate-300">
          Background agents, GitHub Copilot, Cursor, Claude, and custom workflows leak cost silently. We audit the spend surface, enforce policy, and restore ROI.
        </p>
      </section>

      {/* Buyer Pain Points */}
      <section className="mx-auto max-w-5xl mb-16">
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

      {/* Core Modules */}
      <section className="mx-auto max-w-5xl mb-16">
        <h2 className="text-3xl font-semibold mb-8">Five Core Modules</h2>
        <div className="space-y-6">
          {modules.map((module, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-6"
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-cyan-300">
                    {idx + 1}. {module.title}
                  </h3>
                  <p className="text-slate-300 mt-2">{module.description}</p>
                </div>
                <span className="text-sm text-slate-400 whitespace-nowrap">
                  {module.timeline}
                </span>
              </div>
              <div className="ml-0 mt-4">
                <p className="text-sm font-semibold text-slate-400 mb-2">
                  Deliverables:
                </p>
                <ul className="space-y-1">
                  {module.deliverables.map((deliverable, didx) => (
                    <li
                      key={didx}
                      className="text-sm text-slate-300 flex gap-2"
                    >
                      <span className="text-emerald-400 flex-shrink-0">✓</span>
                      {deliverable}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Value Proposition */}
      <section className="mx-auto max-w-5xl mb-16">
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

      {/* Non-Claims */}
      <section className="mx-auto max-w-5xl mb-16">
        <h2 className="text-3xl font-semibold mb-8">What This Service Is NOT</h2>
        <div className="grid gap-3">
          {nonClaims.map((claim, idx) => (
            <div key={idx} className="flex gap-3 text-slate-300">
              <span className="text-slate-500 flex-shrink-0">✗</span>
              {claim}
            </div>
          ))}
        </div>
        <div className="mt-8 rounded-lg border border-emerald-800 bg-emerald-950/30 p-6">
          <p className="text-sm font-semibold text-emerald-300 mb-3">What This Service IS:</p>
          <ul className="space-y-2 text-sm text-emerald-200">
            <li>✓ Governance + audit + policy layer for AI cost control</li>
            <li>✓ Operational intelligence (spend surface, attribution, anomalies)</li>
            <li>✓ Policy enforcement toolkit (routing, gates, caps)</li>
            <li>✓ Transparency and auditability for automation spend</li>
          </ul>
        </div>
      </section>

      {/* Status & Next Steps */}
      <section className="mx-auto max-w-5xl mb-16 rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-xl font-semibold mb-4">Status & Timeline</h2>
        <div className="space-y-3 text-sm text-slate-300">
          <p>✅ <span className="text-emerald-300">Draft stage:</span> Service brief and positioning complete</p>
          <p>⏸️ <span className="text-amber-300">Review stage:</span> Awaiting founder/stakeholder review</p>
          <p>⏸️ <span className="text-amber-300">Integration stage:</span> Awaiting Noetfield reconciliation + Vercel verification</p>
          <p>⏸️ <span className="text-amber-300">Publication stage:</span> After NOOS coordination clear</p>
          <p>⏸️ <span className="text-amber-300">Go-live stage:</span> After buyer-audience verification</p>
        </div>
      </section>

      {/* Footer */}
      <section className="mx-auto max-w-5xl text-center text-slate-500 text-sm">
        <p>Drafted by: [NF-LOCAL-REPO-AGENT]</p>
        <p>Date: 2026-07-05</p>
        <p className="mt-4 text-amber-600 font-semibold">
          DRAFT — Not for publication until reconciliation complete and review approved
        </p>
      </section>
    </main>
  );
}

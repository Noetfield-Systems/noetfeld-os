"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

type AgentCard = {
  id: string;
  column: "investigate" | "triage" | "draft" | "await" | "recorded";
  title: string;
  confidence: number;
  rid?: string;
  tleId?: string;
  elapsed: string;
  status: "running" | "done" | "gate";
};

const COLUMNS: { key: AgentCard["column"]; label: string }[] = [
  { key: "investigate", label: "Investigate" },
  { key: "triage", label: "Triage" },
  { key: "draft", label: "Draft TLE" },
  { key: "await", label: "Await human" },
  { key: "recorded", label: "Recorded" },
];

const SEED: AgentCard[] = [
  {
    id: "a1",
    column: "investigate",
    title: "Purview label gap scan",
    confidence: 0.76,
    elapsed: "12s",
    status: "running",
  },
  {
    id: "a2",
    column: "triage",
    title: "Copilot rollout intent",
    confidence: 0.82,
    rid: "RID-sandbox-demo",
    elapsed: "4s",
    status: "done",
  },
  {
    id: "a3",
    column: "draft",
    title: "TLE draft for prod scope",
    confidence: 0.79,
    tleId: "TLE-015DCFB8B953",
    elapsed: "18s",
    status: "done",
  },
  {
    id: "a4",
    column: "await",
    title: "Board go/no-go approval",
    confidence: 0.71,
    rid: "RID-sandbox-demo",
    elapsed: "—",
    status: "gate",
  },
  {
    id: "a5",
    column: "recorded",
    title: "Sandbox evaluate auto-record",
    confidence: 0.88,
    rid: "RID-sandbox-demo",
    elapsed: "2s",
    status: "done",
  },
];

export function AgentCommandDeck() {
  const [cards, setCards] = useState(SEED);
  const [focusIndex, setFocusIndex] = useState(0);
  const router = useRouter();

  const onKey = useCallback(
    (e: KeyboardEvent) => {
      const deck = document.getElementById("agent-command-deck");
      if (!deck || !deck.contains(document.activeElement)) return;
      if (e.key === "j") {
        e.preventDefault();
        setFocusIndex((i) => Math.min(cards.length - 1, i + 1));
      }
      if (e.key === "k") {
        e.preventDefault();
        setFocusIndex((i) => Math.max(0, i - 1));
      }
    },
    [cards.length],
  );

  useEffect(() => {
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onKey]);

  function approve(id: string) {
    setCards((prev) =>
      prev.map((c) =>
        c.id === id ? { ...c, column: "recorded" as const, status: "done" as const } : c,
      ),
    );
  }

  function reject(id: string) {
    setCards((prev) => prev.filter((c) => c.id !== id));
  }

  function openCard(card: AgentCard) {
    if (card.tleId) router.push(`/workspace/${encodeURIComponent(card.tleId)}`);
    else if (card.rid) router.push(`/evaluate`);
    else router.push("/evaluate");
  }

  return (
    <section
      id="agent-command-deck"
      className="nf-card mb-8 p-5"
      aria-label="Agent command deck"
      tabIndex={0}
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="nf-eyebrow">Agentic governance</p>
          <h3 className="text-lg font-semibold text-text">Agent command deck</h3>
        </div>
        <span className="rounded-full border border-border bg-panel-solid px-3 py-1 text-xs font-medium text-muted">
          sandbox simulation
        </span>
      </div>
      <div className="grid gap-3 overflow-x-auto lg:grid-cols-5">
        {COLUMNS.map((col) => (
          <div key={col.key} className="min-w-[180px] rounded-lg border border-border bg-panel-solid p-3">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">{col.label}</p>
            <ul className="space-y-2">
              {cards
                .filter((c) => c.column === col.key)
                .map((card) => {
                  const idx = cards.indexOf(card);
                  const focused = idx === focusIndex;
                  return (
                    <li key={card.id}>
                      <button
                        type="button"
                        className={`w-full rounded-lg border p-3 text-left text-sm transition ${
                          focused ? "border-accent bg-accent/5" : "border-border bg-white hover:border-accent/30"
                        }`}
                        onClick={() => openCard(card)}
                      >
                        <p className="font-medium text-text">{card.title}</p>
                        <p className="mt-1 text-xs text-muted-2">
                          {(card.confidence * 100).toFixed(0)}% · {card.elapsed}
                        </p>
                        {card.rid && (
                          <p className="mt-1 font-mono text-[10px] text-accent">{card.rid}</p>
                        )}
                        {card.status === "gate" && (
                          <div className="mt-2 flex gap-2">
                            <button
                              type="button"
                              className="nf-btn-primary px-2 py-1 text-xs"
                              onClick={(e) => {
                                e.stopPropagation();
                                approve(card.id);
                              }}
                            >
                              Approve
                            </button>
                            <button
                              type="button"
                              className="nf-btn-secondary px-2 py-1 text-xs"
                              onClick={(e) => {
                                e.stopPropagation();
                                reject(card.id);
                              }}
                            >
                              Reject
                            </button>
                          </div>
                        )}
                      </button>
                    </li>
                  );
                })}
            </ul>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs text-muted-2">
        Focus deck · <kbd className="rounded border px-1">j</kbd>/<kbd className="rounded border px-1">k</kbd>{" "}
        navigate ·{" "}
        <Link href="/copilot/" className="text-accent hover:underline">
          Agentic procurement copy
        </Link>
      </p>
    </section>
  );
}

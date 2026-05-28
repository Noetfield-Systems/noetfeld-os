const runtimeSurfaces = [
  "Async event bus metrics",
  "Replayable governance events",
  "Dead-letter recovery queue",
  "Signal ingestion traces",
  "Graph confidence evolution",
  "Human approval queue",
  "Inspector collaboration runs",
];

export default function RuntimeConsolePage() {
  return (
    <main className="min-h-screen bg-black px-6 py-14 text-zinc-100">
      <section className="mx-auto max-w-6xl">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Runtime Console</p>
        <h1 className="mt-6 text-4xl font-semibold">Living governed intelligence nervous system</h1>
        <p className="mt-5 max-w-3xl text-zinc-300">
          Phase 3 exposes live operational cognition through the backend runtime console at
          <code className="mx-2 rounded bg-zinc-900 px-2 py-1 text-cyan-200">
            /runtime/console
          </code>
          while keeping governance review and veto boundaries explicit.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {runtimeSurfaces.map((surface) => (
            <div key={surface} className="rounded-xl border border-cyan-950 bg-zinc-950 p-5">
              <div className="text-sm text-cyan-300">Live surface</div>
              <div className="mt-2 text-lg">{surface}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

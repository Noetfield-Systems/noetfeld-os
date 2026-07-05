import Link from "next/link";

const principles = [
  "Workflow-first governance",
  "Append-only auditability",
  "Living knowledge graph memory",
  "Human-governed intelligence execution",
];

const services = [
  {
    title: "Agentic Cost Governance",
    description: "Control silent AI spend leakage from background agents, Copilot, and custom automation.",
    href: "/services/agentic-cost-governance",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      <section className="mx-auto max-w-5xl">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Noetfield v3.1</p>
        <h1 className="mt-6 text-5xl font-semibold tracking-tight">
          Autonomous Governed Intelligence Nervous System
        </h1>
        <p className="mt-6 max-w-3xl text-lg text-slate-300">
          Ambient market intelligence infrastructure built around governance memory,
          event-centric orchestration, and human-reviewed AI execution.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {principles.map((principle) => (
            <div key={principle} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              {principle}
            </div>
          ))}
        </div>

        {/* Services Section */}
        <div className="mt-20">
          <h2 className="text-2xl font-semibold mb-6">Services</h2>
          <div className="space-y-4">
            {services.map((service) => (
              <Link key={service.href} href={service.href}>
                <div className="rounded-lg border border-slate-800 bg-slate-900/50 hover:border-cyan-700 hover:bg-slate-900/70 p-5 transition cursor-pointer">
                  <h3 className="font-semibold text-cyan-300">{service.title}</h3>
                  <p className="text-sm text-slate-400 mt-2">{service.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

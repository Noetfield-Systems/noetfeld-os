import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { PageHero } from "@/components/PageHero";

export default function EvaluatePage() {
  return (
    <Shell active="evaluate">
      <PageHero
        eyebrow="Pre-execution"
        title="Submit operational intent"
        lead="Describe who is acting, what they propose, and the operational context. Noetfield returns a governance decision — allow, deny, or review — before any external system executes."
      />
      <EvaluateForm />
    </Shell>
  );
}

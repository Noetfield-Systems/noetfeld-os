import { AppShell, type ShellActive } from "@/components/AppShell";

type ShellProps = {
  children: React.ReactNode;
  active?: ShellActive;
  title?: string;
  proofRid?: string;
};

/** @deprecated Use AppShell — kept for route compatibility (UI-04). */
export function Shell({ children, active, title, proofRid }: ShellProps) {
  return (
    <AppShell active={active} title={title} proofRid={proofRid}>
      {children}
    </AppShell>
  );
}

export { AppShell };

import Link from "next/link";
import type { ReactNode } from "react";

type StatCardProps = {
  label: string;
  title: string;
  description?: string;
  children?: ReactNode;
  href?: string;
  external?: boolean;
};

export function StatCard({
  label,
  title,
  description,
  children,
  href,
  external,
}: StatCardProps) {
  const inner = (
    <>
      <p className="nf-eyebrow">{label}</p>
      <p className="mt-2 text-lg font-semibold text-white">{title}</p>
      {description && <p className="mt-1 text-sm text-muted">{description}</p>}
      {children && <div className="mt-3">{children}</div>}
    </>
  );

  if (!href) {
    return <div className="nf-card p-5">{inner}</div>;
  }

  const className = "nf-card-hover block p-5";
  if (external) {
    return (
      <a href={href} className={className} target="_blank" rel="noopener noreferrer">
        {inner}
      </a>
    );
  }
  return (
    <Link href={href} className={className}>
      {inner}
    </Link>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Noetfield Governance Console",
  description:
    "Pre-execution governance evaluation for operational intent — allow, deny, or review with full audit traceability.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

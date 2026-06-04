import { IBM_Plex_Sans, IBM_Plex_Serif } from "next/font/google";
import type { Metadata, Viewport } from "next";
import "./globals.css";

const ibmSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const ibmSerif = IBM_Plex_Serif({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Noetfield Governance Console",
    template: "%s · Noetfield Governance",
  },
  description:
    "Pre-execution governance evaluation for operational intent — allow, deny, or review with full audit traceability.",
};

export const viewport: Viewport = {
  themeColor: "#07070b",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${ibmSans.variable} ${ibmSerif.variable}`}>
      <body className="min-h-screen font-sans">{children}</body>
    </html>
  );
}

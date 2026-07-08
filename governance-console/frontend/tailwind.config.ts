import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      colors: {
        surface: "rgb(var(--surface-rgb) / <alpha-value>)",
        panel: "rgb(var(--panel-rgb) / <alpha-value>)",
        "panel-solid": "rgb(var(--panel-solid-rgb) / <alpha-value>)",
        border: "rgb(var(--border-rgb) / <alpha-value>)",
        text: "rgb(var(--text-rgb) / <alpha-value>)",
        muted: "rgb(var(--muted-rgb) / <alpha-value>)",
        "muted-2": "rgb(var(--muted-2-rgb) / <alpha-value>)",
        accent: "rgb(var(--gold-rgb) / <alpha-value>)",
        "accent-dim": "rgba(138, 107, 31, 0.12)",
        ok: "rgb(var(--ok-rgb) / <alpha-value>)",
        review: "rgb(var(--review-rgb) / <alpha-value>)",
        deny: "rgb(var(--deny-rgb) / <alpha-value>)",
      },
      boxShadow: {
        panel: "0 4px 24px rgba(15, 17, 23, 0.06)",
        glow: "0 2px 12px rgba(15, 17, 23, 0.04)",
      },
      borderRadius: {
        xl: "var(--radius-xl)",
        lg: "var(--radius-md)",
      },
      maxWidth: {
        content: "1320px",
      },
    },
  },
  plugins: [],
};

export default config;

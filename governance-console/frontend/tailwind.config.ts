import type { Config } from "tailwindcss";
import tokens from "../../packages/ui-tokens/tokens.json";

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
        surface: tokens.colors.surface,
        panel: tokens.colors.panel,
        "panel-solid": "#f8f9fb",
        border: tokens.colors.border,
        text: tokens.colors.text,
        muted: tokens.colors.muted,
        "muted-2": "#6b7280",
        accent: tokens.colors.gold,
        "accent-dim": "rgba(138, 107, 31, 0.12)",
        ok: tokens.colors.ok,
      },
      boxShadow: {
        panel: "0 4px 24px rgba(15, 17, 23, 0.06)",
        glow: "0 2px 12px rgba(15, 17, 23, 0.04)",
      },
      borderRadius: {
        xl: "18px",
        lg: "12px",
      },
      maxWidth: {
        content: "1320px",
      },
    },
  },
  plugins: [],
};

export default config;

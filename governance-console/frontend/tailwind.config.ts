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
        surface: "#07070b",
        panel: "rgba(255,255,255,0.055)",
        "panel-solid": "#14141c",
        border: "rgba(255,255,255,0.11)",
        muted: "#b9bbcf",
        "muted-2": "#8e91ad",
        accent: "#c8a349",
        "accent-dim": "rgba(200,163,73,0.35)",
        ok: "#2de38a",
      },
      boxShadow: {
        panel: "0 28px 80px rgba(0,0,0,0.45)",
        glow: "0 0 40px rgba(200,163,73,0.12)",
      },
      borderRadius: {
        xl: "18px",
        lg: "12px",
      },
    },
  },
  plugins: [],
};

export default config;

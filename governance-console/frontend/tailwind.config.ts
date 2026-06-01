import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0c0c10",
        panel: "#14141c",
        border: "#2a2a36",
        muted: "#9ca3af",
        accent: "#c9a227",
      },
    },
  },
  plugins: [],
};

export default config;

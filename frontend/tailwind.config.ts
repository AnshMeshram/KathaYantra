import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        obsidian: {
          DEFAULT: "#09090D",
          50: "#1A1A22",
          100: "#14141B",
          200: "#0F0F14",
          300: "#0B0B0F",
          400: "#09090D",
          900: "#040406",
        },
        plum: {
          DEFAULT: "#191119",
          hover: "#221722",
          card: "#191119",
        },
        charcoal: {
          wine: "#251820",
          border: "#362530",
        },
        gold: {
          DEFAULT: "#C78B42",
          hover: "#DC9F55",
          muted: "#8C612E",
          glow: "rgba(199, 139, 66, 0.25)",
        },
        blood: {
          DEFAULT: "#E52D35",
          dark: "#991D23",
          glow: "rgba(229, 45, 53, 0.3)",
        },
        ember: {
          DEFAULT: "#FF713B",
          glow: "rgba(255, 113, 59, 0.3)",
        },
        ivory: {
          DEFAULT: "#E9DCC5",
          muted: "#C5B8A2",
          dark: "#998E7D",
        },
        ash: {
          DEFAULT: "#A59AA0",
          dark: "#685F64",
        },
        spectral: {
          DEFAULT: "#2CEAA3",
          glow: "rgba(44, 234, 163, 0.25)",
        },
      },
      fontFamily: {
        gothic: ["var(--font-cormorant)", "Georgia", "serif"],
        serif: ["var(--font-lora)", "Libre Baskerville", "serif"],
        mono: ["var(--font-ibm-plex-mono)", "Courier New", "monospace"],
      },
      backgroundImage: {
        "parchment-vignette":
          "radial-gradient(circle at center, rgba(25, 17, 25, 0.5) 0%, rgba(9, 9, 13, 0.95) 100%)",
        "gold-shimmer":
          "linear-gradient(45deg, rgba(199, 139, 66, 0.15), rgba(255, 113, 59, 0.05), rgba(199, 139, 66, 0.15))",
      },
      boxShadow: {
        "gothic-card": "0 8px 32px 0 rgba(0, 0, 0, 0.7)",
        "gold-glow": "0 0 20px 2px rgba(199, 139, 66, 0.3)",
        "blood-glow": "0 0 20px 2px rgba(229, 45, 53, 0.35)",
        "spectral-glow": "0 0 20px 2px rgba(44, 234, 163, 0.3)",
      },
    },
  },
  plugins: [],
};

export default config;

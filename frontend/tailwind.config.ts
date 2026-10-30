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
        /* Carbon Archival Inks */
        ink: {
          DEFAULT: "#0C0D12",
          deep: "#07080B",
          50: "#1E202B",
          100: "#161720",
          200: "#101117",
          300: "#0C0D12",
          400: "#07080B",
        },
        /* Matte Archival Surfaces */
        parchment: {
          DEFAULT: "#13141B",
          surface: "#13141B",
          elevated: "#1B1D27",
          overlay: "#212431",
        },
        /* Weathered Architectural Borders */
        stone: {
          DEFAULT: "#262937",
          border: "#262937",
          subtle: "rgba(237, 229, 216, 0.09)",
          active: "#D1A75C",
        },
        /* Antique Illuminated Brass */
        brass: {
          DEFAULT: "#D1A75C",
          light: "#E8C88B",
          dark: "#997538",
          dim: "rgba(209, 167, 92, 0.15)",
        },
        /* Cinnabar Lacquer & Wax Seals */
        cinnabar: {
          DEFAULT: "#BA382E",
          dark: "#7C211A",
          seal: "#D44439",
          dim: "rgba(186, 56, 46, 0.16)",
        },
        /* Unbleached Linen Typography */
        linen: {
          DEFAULT: "#EDE5D8",
          muted: "#A39C90",
          faint: "#6E685E",
          dim: "#48433C",
        },
        /* Scholarly Verdigris */
        verdigris: {
          DEFAULT: "#3E7259",
          dim: "rgba(62, 114, 89, 0.2)",
        },

        /* Backward-compatible aliases for Phase 1 transitions */
        obsidian: {
          DEFAULT: "#0C0D12",
          900: "#07080B",
        },
        plum: {
          DEFAULT: "#13141B",
          hover: "#1B1D27",
          card: "#13141B",
        },
        charcoal: {
          wine: "#262937",
          border: "#262937",
        },
        gold: {
          DEFAULT: "#D1A75C",
          hover: "#E8C88B",
          muted: "#997538",
          glow: "rgba(209, 167, 92, 0.2)",
        },
        blood: {
          DEFAULT: "#BA382E",
          dark: "#7C211A",
          glow: "rgba(186, 56, 46, 0.25)",
        },
        ember: {
          DEFAULT: "#C45B38",
          glow: "rgba(196, 91, 56, 0.2)",
        },
        ivory: {
          DEFAULT: "#EDE5D8",
          muted: "#A39C90",
          dark: "#6E685E",
        },
        ash: {
          DEFAULT: "#A39C90",
          dark: "#6E685E",
        },
        spectral: {
          DEFAULT: "#3E7259",
          glow: "rgba(62, 114, 89, 0.25)",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Cormorant Garamond", "Cinzel", "Georgia", "serif"],
        gothic: ["var(--font-gothic)", "UnifrakturCook", "Grenze Gotisch", "serif"],
        serif: ["var(--font-body)", "Lora", "Libre Baskerville", "Georgia", "serif"],
        mono: ["var(--font-mono)", "IBM Plex Mono", "JetBrains Mono", "monospace"],
      },
      boxShadow: {
        editorial: "0 4px 24px rgba(0, 0, 0, 0.65)",
        overlay: "0 16px 48px -8px rgba(0, 0, 0, 0.85)",
        seal: "0 2px 12px rgba(186, 56, 46, 0.35)",
        brass: "0 0 16px rgba(209, 167, 92, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;

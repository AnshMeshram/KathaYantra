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
        /* Exact Five User-Specified Reference Colors */
        burgundy: {
          DEFAULT: "#70191D",
          dark: "#541215",
          light: "#8C2227",
        },
        "chinese-red": {
          DEFAULT: "#970A12",
          dark: "#78060D",
          light: "#B8141E",
        },
        satsuma: {
          DEFAULT: "#D1601F",
          dark: "#AB4C14",
          light: "#E47738",
        },
        "lunar-yellow": {
          DEFAULT: "#FECD6D",
          dark: "#E8B248",
          light: "#FFE09B",
        },
        cobalt: {
          DEFAULT: "#5686BB",
          dark: "#3F6B9D",
          light: "#729ECF",
        },

        /* Supporting Editorial Neutrals */
        parchment: {
          DEFAULT: "#F4EBDD",
          light: "#FAF4EC",
          deep: "#EDE2D0",
          border: "#D8C7B0",
        },
        ink: {
          DEFAULT: "#251D1B",
          deep: "#161110",
          muted: "#766B62",
          faint: "#A59B91",
        },

        /* Semantic Aliases */
        primary: "#70191D",
        accent: "#970A12",
      },
      fontFamily: {
        display: ["var(--font-display)", "Cormorant Garamond", "Cinzel", "Georgia", "serif"],
        gothic: ["var(--font-gothic)", "UnifrakturCook", "Grenze Gotisch", "serif"],
        serif: ["var(--font-body)", "Lora", "Libre Baskerville", "Georgia", "serif"],
        mono: ["var(--font-mono)", "IBM Plex Mono", "JetBrains Mono", "monospace"],
      },
      boxShadow: {
        editorial: "0 4px 18px rgba(37, 29, 27, 0.08)",
        panel: "0 12px 36px -6px rgba(37, 29, 27, 0.14)",
        seal: "0 2px 10px rgba(151, 10, 18, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;

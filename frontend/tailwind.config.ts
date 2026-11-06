import type { Config } from "tailwindcss";
export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: {
    colors: { leaf: { 50:"#f1f8ee",100:"#dcefd5",200:"#b9dfac",300:"#8bc878",400:"#5fae4c",500:"#3f9230",600:"#2f7625",700:"#275c21",800:"#22491e",900:"#143015" },
              grain: { 50:"#fffaf0",100:"#fdf1d6",300:"#f3d58a",500:"#e0a824",700:"#a8740d" },
              soil: { 700:"#5b3a1e", 900:"#2b1b0e" } },
    fontFamily: { sans: ['"Noto Sans Telugu"','"Noto Sans Devanagari"','"Segoe UI"','system-ui','sans-serif'],
                  display: ['"Noto Serif Telugu"','"Noto Serif Devanagari"','Georgia','serif'] },
    keyframes: { ring: { "0%": { transform: "scale(1)", opacity: ".6" }, "100%": { transform: "scale(1.9)", opacity: "0" } } },
    animation: { ring: "ring 1.6s ease-out infinite" } } },
  plugins: [],
} satisfies Config;

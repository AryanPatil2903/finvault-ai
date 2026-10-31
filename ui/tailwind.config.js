/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff", 100: "#e0e7ff", 200: "#c7d2fe", 300: "#a5b4fc",
          400: "#818cf8", 500: "#6366f1", 600: "#4f46e5", 700: "#4338ca",
          800: "#3730a3", 900: "#1e1b4b",
        },
        success: { 100: "#dcfce7", 200: "#bbf7d0", 500: "#22c55e", 600: "#16a34a" },
        danger:  { 100: "#fee2e2", 200: "#fecaca", 500: "#ef4444", 600: "#dc2626" },
        warning: { 100: "#fef3c7", 200: "#fde68a", 500: "#f59e0b", 600: "#d97706" },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
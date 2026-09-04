/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        indigo: {
          950: "#1a1b3a",
          900: "#232461",
          800: "#2d2f7a",
          700: "#383a94",
          600: "#4749ad",
          500: "#5a5cc4",
        },
        amber: {
          500: "#e8a13d",
          400: "#f0b658",
          300: "#f5cb85",
        },
        cream: {
          50: "#faf8f3",
          100: "#f4f0e6",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
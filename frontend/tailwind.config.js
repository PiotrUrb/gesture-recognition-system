/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'industrial-dark': '#1a1a1a',
        'industrial-gray': '#2d2d2d',
        'accent-blue': '#3b82f6',
        'alert-red': '#ef4444',
        'success-green': '#22c55e',
      }
    },
  },
  plugins: [],
}

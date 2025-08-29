/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // 👈 important so React files are scanned
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

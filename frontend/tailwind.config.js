/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          navy: '#0F172A',      // Slate 900
          navyLight: '#1E293B', // Slate 800
          indigo: '#6366F1',    // Indigo 500
          indigoDark: '#4F46E5',  // Indigo 600
          indigoLight: '#818CF8', // Indigo 400
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

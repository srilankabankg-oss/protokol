/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff', 100: '#dbeafe', 500: '#3b82f6', 700: '#1d4ed8',
        },
        level: {
          strategic: '#d97706',
          coordination: '#7c3aed',
          operational: '#2563eb',
          situational: '#dc2626',
        },
      },
    },
  },
  plugins: [],
};
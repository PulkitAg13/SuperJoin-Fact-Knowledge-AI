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
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          500: '#0284c7',
          600: '#0369a1',
          700: '#075985',
          900: '#0c4a6e',
        },
        corroboration: {
          light: '#ecfdf5',
          border: '#a7f3d0',
          text: '#065f46',
          badge: '#10b981',
        },
        contradiction: {
          light: '#fef2f2',
          border: '#fecaca',
          text: '#991b1b',
          badge: '#ef4444',
        },
        reconciled: {
          light: '#f0f9ff',
          border: '#bae6fd',
          text: '#075985',
          badge: '#0284c7',
        },
        uncertain: {
          light: '#fffbeb',
          border: '#fde68a',
          text: '#92400e',
          badge: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

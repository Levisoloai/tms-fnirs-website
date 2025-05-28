const colors = require('tailwindcss/colors')

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx,html}',
  ],
  darkMode: 'class', // or 'media' if you prefer
  theme: {
    extend: {
      colors: {
        // Dark mode palette
        'dark-background': colors.gray[900],
        'dark-highlight': colors.cyan[400],
        'dark-alert': colors.amber[400],
      },
      fontSize: {
        'xs': '0.75rem',    // 12px
        'sm': '0.875rem',   // 14px
        'base': '1rem',     // 16px
        'lg': '1.125rem',   // 18px
        'xl': '1.25rem',    // 20px
        '2xl': '1.5rem',    // 24px
        '3xl': '1.875rem',  // 30px
        '4xl': '2.25rem',   // 36px
        '5xl': '3rem',      // 48px
      },
    },
  },
  plugins: [],
}

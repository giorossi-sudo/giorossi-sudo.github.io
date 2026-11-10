/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./404.html", "./chi-sono.html", "./articoli/*.html"],
  theme: {
    fontFamily: {
      heading: ['"Bricolage Grotesque"', 'sans-serif'],
      body: ['"Instrument Sans"', 'sans-serif'],
      mono: ['"DM Mono"', 'monospace'],
    },
    extend: {
      colors: {
        bg: '#FAFAF7',
        surface: '#FFFFFF',
        ink: '#111111',
        muted: '#5F5F5A',
        line: '#E6E6E0',
        accent: '#C2370F',
        placeholderBg: '#F2F2EC',
        placeholderBorder: '#D8D8D0',
      },
      maxWidth: {
        container: '1100px',
      }
    }
  },
  plugins: [],
};

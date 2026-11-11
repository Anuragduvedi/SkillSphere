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
        dark: {
          900: '#060911',
          850: '#090D18',
          800: '#0D1322',
          700: '#151D32',
          600: '#1E2945'
        },
        neon: {
          cyan: '#00f5ff',
          emerald: '#10b981',
          purple: '#a855f7',
          pink: '#ec4899',
          amber: '#f59e0b'
        }
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-hover': '0 12px 40px 0 rgba(0, 245, 255, 0.15)',
        'neon-cyan': '0 0 25px rgba(0, 245, 255, 0.35)',
        'neon-emerald': '0 0 25px rgba(16, 185, 129, 0.35)',
        'neon-purple': '0 0 25px rgba(168, 85, 247, 0.35)',
      },
      backdropBlur: {
        'xs': '2px',
      },
      animation: {
        'float-slow': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: 0.4 },
          '50%': { opacity: 0.8 },
        }
      }
    },
  },
  plugins: [],
}

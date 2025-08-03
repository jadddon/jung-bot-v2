import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // ChatGPT-inspired color palette
        chat: {
          bg: '#f7f7f8',
          sidebar: '#171717',
          message: '#ffffff',
          user: '#19c37d',
          assistant: '#ab68ff',
          border: '#e5e5e5',
          hover: '#f5f5f5',
          text: '#353740',
          muted: '#8e8ea0',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      maxWidth: {
        'chat': '48rem',
      },
      animation: {
        'typing': 'typing 1.5s infinite',
        'fade-in': 'fade-in 0.3s ease-in-out',
      },
      keyframes: {
        typing: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config; 
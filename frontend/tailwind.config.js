/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Netflix color system
        netflix: {
          red: '#E50914',      // Netflix 主红色
          'red-dark': '#B20710', // 深红色（hover）
          black: '#141414',     // 主背景色
          'gray-dark': '#2F2F2F', // 卡片背景
          'gray-medium': '#808080', // 次要文字
          'gray-light': '#B3B3B3',  // 普通文字
        },
      },
      backgroundColor: {
        'netflix-bg': '#141414',
        'netflix-card': '#2F2F2F',
        'netflix-hover': '#3F3F3F',
      },
      borderColor: {
        'netflix-border': '#404040',
      },
    },
  },
  plugins: [],
}

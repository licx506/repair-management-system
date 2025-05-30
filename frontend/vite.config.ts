import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8458,
    host: '0.0.0.0',  // 允许从任何IP访问
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'xin.work.gd'  // 添加您的域名
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
})

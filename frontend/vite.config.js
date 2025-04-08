import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ["readable-stream"],
  },
  server: {
    allowedHosts: true,
    proxy: {
      '/api': {
        target: "https://www.puhti.csc.fi/rnode/r07c51.bullx/49496/proxy/8000/",
        changeOrigin: true,
      }
    }
  }
})

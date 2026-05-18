import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Backend runs on 6969; Vite dev server uses a different port.
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": "http://127.0.0.1:6969",
      "/logs": {
        target: "http://127.0.0.1:6969",
        changeOrigin: false,
        ws: false,
      },
    },
  },
})

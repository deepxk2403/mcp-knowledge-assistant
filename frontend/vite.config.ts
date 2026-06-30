import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API calls to the FastAPI backend so the browser can use same-origin
// relative URLs (and SSE streams pass through unbuffered).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/notes': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/sessions': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    open: true,
    // Accept any Host header so the app is reachable via LAN hostnames
    // (e.g. http://mybox.lan:3000), not only localhost/IPs
    // Source - https://stackoverflow.com/a/79377387
    // Posted by ansmonjol, modified by community. See post 'Timeline' for change history
    // Retrieved 2026-06-11, License - CC BY-SA 4.0
    allowedHosts: true,
    proxy: {
      '/api': {
        // The proxy runs server-side, next to the backend — localhost is
        // correct here. Override only if the backend runs elsewhere.
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})

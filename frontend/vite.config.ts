import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react()
  ],
  css: {
    postcss: './postcss.config.js', // Explicitly point to your PostCSS config
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Allow external connections
    port: 3000,     // Using port 3000 as requested
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
    watch: {
      usePolling: true, // Needed for Docker to detect file changes
    },
  },
  base: '/', // Use root-relative paths instead of relative
  build: {
    sourcemap: true, // Enable source maps for debugging
  },
})
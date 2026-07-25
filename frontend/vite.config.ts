import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  // Must equal Django's STATIC_URL — django-vite's dev-server URL builder
  // prepends STATIC_URL even in dev mode, so Vite must expect requests
  // arriving under the same prefix.
  base: '/static/',
  server: {
    host: 'localhost',
    port: 5173,        // must match DJANGO_VITE.default.dev_server_port
    strictPort: true,
    cors: true,
    origin: 'http://localhost:5173',
  },
  build: {
    outDir: resolve(__dirname, 'dist'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        'survey-form': resolve(__dirname, 'src/islands/survey-form/main.tsx'),
        'contact-form': resolve(__dirname, 'src/islands/contact-form/main.tsx'),
        'consultation-form': resolve(__dirname, 'src/islands/consultation-form/main.tsx'),
        'admin-hub-login': resolve(__dirname, 'src/islands/admin-hub-login/main.tsx'),
        'admin-mission-vision': resolve(__dirname, 'src/islands/admin-mission-vision/main.tsx'),
        'admin-client-logos': resolve(__dirname, 'src/islands/admin-client-logos/main.tsx'),
        'admin-brands': resolve(__dirname, 'src/islands/admin-brands/main.tsx'),
        'admin-services': resolve(__dirname, 'src/islands/admin-services/main.tsx'),
        'admin-fire-risk-items': resolve(__dirname, 'src/islands/admin-fire-risk-items/main.tsx'),
        'admin-products': resolve(__dirname, 'src/islands/admin-products/main.tsx'),
        'admin-certifications': resolve(__dirname, 'src/islands/admin-certifications/main.tsx'),
        'admin-site-settings': resolve(__dirname, 'src/islands/admin-site-settings/main.tsx'),
      },
    },
  },
})

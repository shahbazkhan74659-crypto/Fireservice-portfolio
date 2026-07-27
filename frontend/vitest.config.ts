import { defineConfig } from 'vitest/config'

// Deliberately separate from vite.config.ts, not merged into it — that
// file's build.rollupOptions.input is a load-bearing multi-entry map (one
// entry per island, read by django-vite) and has nothing to do with running
// tests; keeping this standalone avoids any risk of vitest picking up the
// island entry points or dev-server settings by accident.
export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
  },
})

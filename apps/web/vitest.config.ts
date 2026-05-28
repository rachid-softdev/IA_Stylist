import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
      '@vfs/shared-types': path.resolve(__dirname, '../../packages/shared-types/src'),
      '@vfs/utils': path.resolve(__dirname, '../../packages/utils/src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['**/__tests__/**/*.test.ts', '**/__tests__/**/*.test.tsx'],
  },
})

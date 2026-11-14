import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

const integration = process.argv.includes('integration');
export default defineConfig({
  plugins: [react()],
  test: {
    projects: [
      { extends: true, test: { name: 'unit', include: ['tests/unit/**/*.test.{js,jsx}'], environment: 'jsdom', setupFiles: ['tests/setup.js'] } },
      { extends: true, test: { name: 'integration', include: ['tests/integration/**/*.test.js'], environment: 'node' } },
    ],
    reporters: ['default', ['junit', { outputFile: `reports/${integration ? 'integration' : 'unit'}.xml` }]],
    coverage: {
      provider: 'v8',
      include: integration ? ['back/app.js'] : ['back/*.js', 'front/src/**/*.{js,jsx}'],
      exclude: integration ? [] : ['back/app.js', 'back/server.js', 'front/src/main.jsx'],
      reportsDirectory: `coverage/${integration ? 'integration' : 'unit'}`,
      reporter: ['text', 'html', 'json-summary', 'lcov'],
      thresholds: { perFile: true, lines: 80, branches: 80, functions: 80, statements: 80 },
    },
  },
});

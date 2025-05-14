// vitest.config.ts
import { defineConfig } from 'vitest/config';
import viteConfig from './vite.config';
export default defineConfig({
    ...viteConfig,
    test: {
        globals: true,
        environment: 'jsdom', // Use jsdom for browser-like tests
        coverage: {
            reporter: ['text', 'json', 'html'], // Optional: Add coverage reports
        },
        setupFiles: 'src/setupTests.ts',
        clearMocks: true,
        restoreMocks: true,
    },
});

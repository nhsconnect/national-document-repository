// vitest.config.ts
import { defineConfig } from 'vitest/config';
import viteConfig from './vite.config';
import { loadEnv } from 'vite';

export default defineConfig({
    ...viteConfig,
    test: {
        globals: true,
        environment: 'jsdom', // Use jsdom for browser-like tests
        coverage: {
            reporter: ['text', 'json', 'html'], // Optional: Add coverage reports
        },
        setupFiles: ['src/setupTests.ts', 'dotenv/config'],
        clearMocks: true,
        restoreMocks: true,
        env: loadEnv('', process.cwd(), ''),
    },
});

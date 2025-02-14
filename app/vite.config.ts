/* eslint-disable */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
    plugins: [react(), svgr()],
    // @ts-ignore
    test: {
        globals: true,
        environment: 'node',
        setupFiles: './src/setupTests.ts',
    },
    server: {
        port: 3000,
    },
});

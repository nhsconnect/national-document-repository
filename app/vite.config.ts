import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import svgr from 'vite-plugin-svgr';
import commonjs from 'vite-plugin-commonjs';
import eslint from 'vite-plugin-eslint';

// https://vitejs.dev/config/
export default defineConfig({
    base: '/',
    plugins: [
        react(),
        svgr({
            svgrOptions: { exportType: 'named', ref: true, svgo: false, titleProp: true },
            include: '**/*.svg',
        }),
        commonjs({
            dynamic: {
                onFiles: (files) => files.filter((f) => f !== 'viewer.html'),
            },
        }),
        eslint(),
    ],
    build: {
        commonjsOptions: { transformMixedEsModules: true },
        chunkSizeWarningLimit: 1024,
    },
});

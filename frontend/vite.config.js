import { defineConfig } from 'vite';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import {watchConfigPlugin} from "./vite-plugins/watch-config.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');
const OUT_DIR = join(__dirname, 'src', 'generated');

export default defineConfig({
    root: '.',
    plugins: [
        watchConfigPlugin({repoRoot: REPO_ROOT, outDir: OUT_DIR})
    ],
    build: {
        outDir: 'dist',
        emptyOutDir: true,
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:5050',
                changeOrigin: true
            }
        }
    }
});
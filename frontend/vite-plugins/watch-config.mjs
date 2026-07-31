import {readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { load } from "js-yaml";


export function  watchConfigPlugin({ repoRoot, outDir }) {
    const configDir = join(repoRoot, 'config');
    const colorsPath = join(configDir, 'colors.yaml');
    const gameConfigPath = join(configDir, 'game_config.yaml');

    function ensureOutDir() {
        mkdirSync(outDir, { recursive: true });
    }

    function generateColors() {

        const colorsParsed = load(readFileSync(colorsPath, 'utf8'));
        writeFileSync(
            join(outDir, 'colors.json'),
            JSON.stringify(colorsParsed.color_schemes, null, 2)
        );
    }

    function generateGameConfig() {
        const gameConfigParsed = load(readFileSync(gameConfigPath, 'utf8'));
        writeFileSync(
            join(outDir, 'game-config.json'),
            JSON.stringify(gameConfigParsed.board, null, 2)
        );
    }

    return {
        name: 'watch-config',
        buildStart() {
            ensureOutDir();
            generateColors();
            generateGameConfig();
        },

        configureServer(server) {
            server.watcher.add([colorsPath, gameConfigPath]);

            server.watcher.on('change', (changedPath) => {
                if (changedPath === colorsPath) {
                    console.log(`[watch-config] colors.yaml changed, regenerating colors.json`);
                    generateColors();
                } else if (changedPath === gameConfigPath) {
                    console.log('[watch-config] game_config.yaml changed, regenerating game-config.json...');
                    generateGameConfig();
                }
            });
        }
    };
}
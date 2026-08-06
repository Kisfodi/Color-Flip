import './style.css';
import colorSchemes from './generated/colors.json';
import gameConfig from './generated/game-config.json';

import {getCurrentState, setColorSchemeCache, setDefaultConfig} from "./app/gameState.js";
import {
    applyDefaultConfig,
    attachModeChangeListener,
    goBackToStartScreen,
    goToLoadGameScreen,
    goToNewGameScreen
} from "./app/screens.js";
import {populateColorSchemeSelect, updateColorPreview} from "./app/colorScheme.js";
import {renderGameBoard, setSolveButtonState, solveGame, updateStatus} from "./app/board.js";

setColorSchemeCache(colorSchemes);
setDefaultConfig(gameConfig);

document.addEventListener('DOMContentLoaded', () => {

    const boardSizeSelect = document.getElementById("start-board-size");
    for (let size = 2; size <= 20; size += 2) {
        const option = document.createElement("option");
        option.value = size;
        option.textContent = `${size}x${size}`;
        boardSizeSelect.appendChild(option);
    }

    applyDefaultConfig(gameConfig);
    populateColorSchemeSelect();
    updateColorPreview();

    // Start screen buttons
    document.getElementById("start-new-game-btn").addEventListener("click", goToNewGameScreen);
    document.getElementById("start-load-game-btn").addEventListener("click", goToLoadGameScreen);

    // Game screen buttons
    document.getElementById("back-btn").addEventListener("click", goBackToStartScreen);
    document.getElementById("solve-game-btn").addEventListener("click", solveGame);
    setSolveButtonState(false);

    // Mode selector change handler
    attachModeChangeListener();

    // Color scheme change handler
    document.getElementById("color-scheme").addEventListener("change", () => {
        updateColorPreview();
        if (getCurrentState()) {
            renderGameBoard();
            updateStatus();
        }
    });

});

// HMR handling
if (import.meta.hot) {
    import.meta.hot.accept(
        ['./generated/colors.json', './generated/game-config.json'],
        ([newColors, newGameConfig]) => {
            if (newColors) {
                setColorSchemeCache(newColors);
            }

            if (newGameConfig) {
                setDefaultConfig(newGameConfig);
                applyDefaultConfig(newGameConfig);
            }

            if (newColors || newGameConfig) {
                populateColorSchemeSelect();
                updateColorPreview();
                if (getCurrentState()) {
                    renderGameBoard();
                }
            }

        }
    );
}
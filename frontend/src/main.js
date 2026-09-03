import './style.css';
import colorSchemes from './generated/colors.json';
import gameConfig from './generated/game-config.json';

import {getCurrentState, setColorSchemeCache, setDefaultConfig} from "./app/gameState.js";
import {
    applyDefaultConfig,
    attachModeChangeListener,
    goBackToStartScreen,
    goToLoadGameScreen,
    goToNewGameScreen,
    openNewGameModal,
    closeNewGameModal,
    resumeLastGame,
    tryAgainCurrentGame,
    startNewPuzzleSameSettings,
    updateResumeButtonState
} from "./app/screens.js";
import {populateColorSchemeSelect, updateColorPreview} from "./app/colorScheme.js";
import {renderGameBoard, setSolveButtonState, solveGame, updateStatus, handleUndo} from "./app/board.js";

setColorSchemeCache(colorSchemes);
setDefaultConfig(gameConfig);

document.addEventListener('DOMContentLoaded', () => {

    const boardSizeSelect = document.getElementById("start-board-size");
    if (boardSizeSelect) {
        boardSizeSelect.innerHTML = '';
        for (let size = 2; size <= 20; size += 2) {
            const option = document.createElement("option");
            option.value = size;
            option.textContent = `${size}x${size}`;
            boardSizeSelect.appendChild(option);
        }
    }

    applyDefaultConfig(gameConfig);
    populateColorSchemeSelect();
    updateColorPreview();
    updateResumeButtonState();

    // Start screen buttons
    document.getElementById("start-resume-game-btn")?.addEventListener("click", resumeLastGame);
    document.getElementById("start-new-game-btn")?.addEventListener("click", openNewGameModal);
    document.getElementById("start-load-game-btn")?.addEventListener("click", goToLoadGameScreen);

    // Modal controls
    document.getElementById("close-modal-btn")?.addEventListener("click", closeNewGameModal);
    document.getElementById("cancel-new-game-btn")?.addEventListener("click", closeNewGameModal);
    document.getElementById("confirm-start-game-btn")?.addEventListener("click", goToNewGameScreen);

    // Close modal on backdrop click
    document.getElementById("new-game-modal")?.addEventListener("click", (e) => {
        if (e.target.id === "new-game-modal") {
            closeNewGameModal();
        }
    });

    // Close modal on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeNewGameModal();
        }
    });

    // Game screen buttons
    document.getElementById("back-btn")?.addEventListener("click", goBackToStartScreen);
    document.getElementById("undo-btn")?.addEventListener("click", handleUndo);
    document.getElementById("solve-game-btn")?.addEventListener("click", solveGame);
    setSolveButtonState(false);

    // Victory actions
    document.getElementById("try-again-btn")?.addEventListener("click", tryAgainCurrentGame);
    document.getElementById("new-puzzle-btn")?.addEventListener("click", startNewPuzzleSameSettings);
    document.getElementById("menu-btn")?.addEventListener("click", goBackToStartScreen);

    // Mode selector change handler
    attachModeChangeListener();

    // Color scheme change handler
    document.getElementById("color-scheme")?.addEventListener("change", () => {
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
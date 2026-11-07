import './style.css';
import colorSchemes from './generated/colors.json';
import gameConfig from './generated/game-config.json';

import {getCurrentState, getCurrentGameId, setColorSchemeCache, setDefaultConfig} from "./app/gameState.js";
import {
    applyDefaultConfig,
    attachModeChangeListener,
    goBackToStartScreen,
    goToLoadGameScreen,
    goToNewGameScreen,
    openNewGameModal,
    closeNewGameModal,
    openSettingsModal,
    closeSettingsModal,
    resumeLastGame,
    tryAgainCurrentGame,
    startNewPuzzleSameSettings,
    updateResumeButtonState
} from "./app/screens.js";
import {populateColorSchemeSelect, updateColorPreview} from "./app/colorScheme.js";
import {renderGameBoard, setSolveButtonState, solveGame, updateStatus, handleUndo, refreshSolveHints} from "./app/board.js";
import {onSettingChange} from "./app/settings.js";
import {getElapsed} from "./app/timer.js";

/**
 * Save the current elapsed time to localStorage whenever the page is hidden
 * (tab switch, tab close, navigate away, mobile background).
 * Uses a key scoped to the active game ID so stale values never bleed across games.
 */
function saveElapsedOnInterrupt() {
    const gameId = getCurrentGameId();
    if (!gameId) return;
    const gameScreen = document.getElementById("game-screen");
    if (!gameScreen || gameScreen.style.display === "none") return;
    localStorage.setItem(`color_flip_paused_elapsed_${gameId}`, getElapsed().toString());
}

// visibilitychange covers tab-switch, minimise, and close on most browsers
document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
        saveElapsedOnInterrupt();
    }
});

// pagehide catches close/navigate-away in browsers where visibilitychange may not fire
window.addEventListener("pagehide", saveElapsedOnInterrupt);

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

    // Settings controls
    document.getElementById("settings-btn")?.addEventListener("click", openSettingsModal);
    document.getElementById("close-settings-modal-btn")?.addEventListener("click", closeSettingsModal);

    // Close modal on backdrop click
    document.getElementById("new-game-modal")?.addEventListener("click", (e) => {
        if (e.target.id === "new-game-modal") {
            closeNewGameModal();
        }
    });
    document.getElementById("settings-modal")?.addEventListener("click", (e) => {
        if (e.target.id === "settings-modal") {
            closeSettingsModal();
        }
    });

    // Close modals on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeNewGameModal();
            closeSettingsModal();
        }
    });

    // React to settings changes in real time
    onSettingChange((key, value) => {
        if (key === 'showOneHint') {
            const state = getCurrentState();
            if (state && state.solve_mode) {
                refreshSolveHints(value);
            }
        } else if (key === 'colorScheme') {
            updateColorPreview(value);
            if (getCurrentState()) {
                renderGameBoard();
                updateStatus();
            }
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
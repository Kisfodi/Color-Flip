import { startNewGameRequest, fetchGameStateRequest } from './api.js';
import {
    setCurrentState,
    setPersistentSolutionCells,
    setCurrentGameId,
    getActiveGameIdFromStorage,
    getCurrentState
} from './gameState.js';
import { renderGameBoard, updateStatus, setSolveButtonState } from './board.js';
import { startTimer, stopTimer } from './timer.js';


function updateModeDescription() {
    const modeSelect = document.getElementById("start-game-mode");
    if (!modeSelect) return;
    const descriptionDiv = document.getElementById("mode-description");
    const mode = modeSelect.value;

    const descriptions = {
        "all_on": "Goal: Light up all cells to the ON state",
        "all_off": "Goal: Darken all cells to the OFF state",
        "mixed": "Goal: Make the board uniform (all same state)"
    };

    if (descriptionDiv) {
        descriptionDiv.textContent = descriptions[mode] || "Select a game mode";
    }
}

function updateGameGoal(mode) {
    const goalDiv = document.getElementById("game-goal");
    if (!goalDiv) return;

    const descriptions = {
        "all_on": "Goal: Light up all cells to the ON state!",
        "all_off": "Goal: Darken all cells to the OFF state!",
        "mixed": "Goal: Make the board uniform!"
    };

    goalDiv.textContent = descriptions[mode] || "Select a game mode";
}

export function updateResumeButtonState() {
    const resumeBtn = document.getElementById("start-resume-game-btn");
    if (!resumeBtn) return;

    const activeGameId = getActiveGameIdFromStorage();
    if (activeGameId) {
        resumeBtn.style.display = "block";
        resumeBtn.disabled = false;
    } else {
        resumeBtn.style.display = "none";
        resumeBtn.disabled = true;
    }
}

export function openNewGameModal() {
    const modal = document.getElementById("new-game-modal");
    if (modal) {
        modal.style.display = "flex";
    }
}

export function closeNewGameModal() {
    const modal = document.getElementById("new-game-modal");
    if (modal) {
        modal.style.display = "none";
    }
}

export function goToNewGameScreen() {

    const boardSizeSelect = document.getElementById("start-board-size");
    const boardSize = parseInt(boardSizeSelect ? boardSizeSelect.value : "4");

    if (isNaN(boardSize)) {
        alert("Please select a valid board size");
        return;
    }

    const gameModeSelect = document.getElementById("start-game-mode");
    const gameMode = gameModeSelect ? gameModeSelect.value : "mixed";

    closeNewGameModal();

    // Hide start screen and show game screen
    document.getElementById("start-screen").style.display = "none";
    document.getElementById("game-screen").style.display = "block";

    startNewGameWithSize(boardSize, gameMode);
}

export function resumeLastGame() {
    const activeGameId = getActiveGameIdFromStorage();
    if (!activeGameId) {
        alert("No active game to resume.");
        return;
    }

    fetchGameStateRequest(activeGameId)
        .then(data => {
            if (!data || data.detail) {
                alert("Could not load saved game session.");
                updateResumeButtonState();
                return;
            }

            setCurrentGameId(activeGameId);
            setCurrentState(data);
            setPersistentSolutionCells(data.solution_cells || []);
            setSolveButtonState(Boolean(data.solve_mode));

            document.getElementById("start-screen").style.display = "none";
            document.getElementById("game-screen").style.display = "block";

            document.getElementById("completion-message").style.display = "none";
            document.getElementById("game-goal").style.display = "block";
            updateGameGoal(data.mode);

            const solveBtn = document.getElementById("solve-game-btn");
            if (solveBtn) solveBtn.disabled = data.game_over;

            renderGameBoard();
            updateStatus();
            stopTimer();
            startTimer();
        })
        .catch(err => {
            console.error("Failed to resume game:", err);
            alert("Failed to resume game session.");
        });
}

export function goToLoadGameScreen() {
    alert("Load game feature coming soon!");
    // TODO: Implement load game functionality
}

export function goBackToStartScreen() {
    stopTimer();

    // Reset timer display
    const timerElem = document.getElementById("timer");
    if (timerElem) timerElem.textContent = "Time: 0:00";

    // Hide game screen and show start screen
    document.getElementById("game-screen").style.display = "none";
    document.getElementById("start-screen").style.display = "flex";

    updateResumeButtonState();
}

export function tryAgainCurrentGame() {
    const state = getCurrentState();
    if (!state) return;

    const size = state.board_size ? state.board_size[0] : parseInt(document.getElementById("start-board-size").value);
    const mode = state.mode || document.getElementById("start-game-mode").value;
    const seed = state.seed !== undefined ? state.seed : null;

    startNewGameWithSize(size, mode, seed);
}

export function startNewPuzzleSameSettings() {
    const state = getCurrentState();
    if (!state) return;

    const size = state.board_size ? state.board_size[0] : parseInt(document.getElementById("start-board-size").value);
    const mode = state.mode || document.getElementById("start-game-mode").value;

    startNewGameWithSize(size, mode, null);
}

export function startNewGameWithSize(size, mode, seed = null) {
    const colorSchemeSelect = document.getElementById("color-scheme");
    const config = {
        size: size,
        mode: mode,
        seed: seed,
        colorScheme: colorSchemeSelect ? colorSchemeSelect.value : "default"
    };

    setPersistentSolutionCells([]);

    const completionMsg = document.getElementById("completion-message");
    const gameGoal = document.getElementById("game-goal");
    const solveBtn = document.getElementById("solve-game-btn");

    if (completionMsg) completionMsg.style.display = "none";
    if (gameGoal) gameGoal.style.display = "block";

    updateGameGoal(mode);

    if (solveBtn) {
        solveBtn.disabled = false;
        setSolveButtonState(false);
    }

    startNewGameRequest(config)
        .then(data => {
            if (data.game_id) {
                setCurrentGameId(data.game_id);
            }
            setCurrentState(data);
            setPersistentSolutionCells(data.solution_cells || []);
            setSolveButtonState(Boolean(data.solve_mode));
            renderGameBoard();
            updateStatus();
            stopTimer();
            startTimer();
        })
        .catch(error => console.error('Error starting game:', error));
}

export function applyDefaultConfig(defaultConfig) {
    const boardSizeSelect = document.getElementById("start-board-size");

    if (boardSizeSelect && defaultConfig.size) {
        boardSizeSelect.value = defaultConfig.size;
    }

    const gameModeSelect = document.getElementById("start-game-mode");
    if (gameModeSelect && defaultConfig.mode) {
        gameModeSelect.value = defaultConfig.mode;
        updateModeDescription();
    }

    updateResumeButtonState();
}

export function attachModeChangeListener() {
    const gameModeSelect = document.getElementById("start-game-mode");
    if (gameModeSelect) {
        gameModeSelect.addEventListener("change", () => {
            updateModeDescription();
        });
    }
}

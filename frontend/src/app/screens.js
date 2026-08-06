import { startNewGameRequest } from './api.js';
import { setCurrentState, setPersistentSolutionCells } from './gameState.js';
import { renderGameBoard, updateStatus, setSolveButtonState } from './board.js';
import { startTimer, stopTimer } from './timer.js';


function updateModeDescription() {
    const modeSelect = document.getElementById("start-game-mode");
    const descriptionDiv = document.getElementById("mode-description");
    const mode = modeSelect.value;

    const descriptions = {
        "all_on": "Goal: Light up all cells to the ON state",
        "all_off": "Goal: Darken all cells to the OFF state",
        "mixed": "Goal: Make the board uniform (all same state)"
    };

    descriptionDiv.textContent = descriptions[mode] || "Select a game mode";
}

function updateGameGoal(mode) {
    const goalDiv = document.getElementById("game-goal");

    const descriptions = {
        "all_on": "Goal: Light up all cells to the ON state!",
        "all_off": "Goal: Darken all cells to the OFF state!",
        "mixed": "Goal: Make the board uniform!"
    };

    goalDiv.textContent = descriptions[mode] || "Select a game mode";
}

export function goToNewGameScreen() {

    const boardSize = parseInt(document.getElementById("start-board-size").value);

    if (isNaN(boardSize)) {
        alert("Please select a valid board size");
        return;
    }

    const gameMode = document.getElementById("start-game-mode").value;

    // Hide start screen and show game screen
    document.getElementById("start-screen").style.display = "none";
    document.getElementById("game-screen").style.display = "block";

    startNewGameWithSize(boardSize, gameMode);
}

export function goToLoadGameScreen() {
    alert("Load game feature coming soon!");
    // TODO: Implement load game functionality
}

export function goBackToStartScreen() {
    stopTimer();

    // Reset timer display
    document.getElementById("timer").textContent = "Time: 0:00";

    // Hide game screen and show start screen
    document.getElementById("game-screen").style.display = "none";
    document.getElementById("start-screen").style.display = "flex";
}

function startNewGameWithSize(size, mode) {
    const config = {
        size: size,
        mode: mode,
        colorScheme: document.getElementById("color-scheme").value
    };


    setPersistentSolutionCells([]);

    document.getElementById("completion-message").style.display = "none";
    document.getElementById("game-goal").style.display = "block";

    updateGameGoal(mode);

    document.getElementById("solve-game-btn").disabled = false;
    setSolveButtonState(false);

    startNewGameRequest(config)
        .then(data => {
            setCurrentState(data);
            setPersistentSolutionCells(data.solution_cells || []);
            setSolveButtonState(Boolean(data.solve_mode));
            // console.log(data);
            renderGameBoard();
            updateStatus();
            stopTimer();
            startTimer();
        })
        .catch(error => console.error('Error starting game:', error));
}

export function applyDefaultConfig(defaultConfig) {
    // console.log("Default config loaded: ", defaultConfig);
    // console.log("Default size: ", defaultConfig.size);

    const boardSizeSelect = document.getElementById("start-board-size");

    if (defaultConfig.size) {
        boardSizeSelect.value = defaultConfig.size;
    }

    const gameModeSelect = document.getElementById("start-game-mode");
    if (defaultConfig.mode) {
        gameModeSelect.value = defaultConfig.mode;
        updateModeDescription();
    }
}

export function attachModeChangeListener() {
    document.getElementById("start-game-mode").addEventListener("change", () => {
        updateModeDescription();
    });
}

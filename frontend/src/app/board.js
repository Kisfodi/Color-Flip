import {solveGameRequest, stepRequest, undoRequest} from "./api.js";
import {
    getCurrentState, getPersistentSolutionCells, handleGameOver,
    removePersistentSolutionCell,
    setCurrentState,
    setPersistentSolutionCells
} from "./gameState.js";
import {getColorScheme} from "./colorScheme.js";

export function setSolveButtonState(enabled) {
    const button = document.getElementById("solve-game-btn");
    if (!button) return;

    const isEnabled = Boolean(enabled);
    button.classList.toggle("active", isEnabled);
    button.dataset.solveState = isEnabled ? "on" : "off";
    button.setAttribute("aria-pressed", isEnabled ? "true" : "false");
    button.innerText = `Solve: ${isEnabled ? "ON" : "OFF"}`;
    button.textContent = `Solve: ${isEnabled ? "ON" : "OFF"}`;
}

export function renderGameBoard(highlightSolutionCells = false, solutionCells = []) {

    const currentState = getCurrentState();
    const boardDiv = document.getElementById("board-container");
    boardDiv.innerHTML = ''; // Clear previous board

    if (!currentState || !currentState.board) {
        return;
    }

    const board = currentState.board;

    const schemeName = document.getElementById("color-scheme").value;
    const colors = getColorScheme(schemeName);

    const cellsToHighlight = currentState?.solve_mode
        ? (highlightSolutionCells ? solutionCells : getPersistentSolutionCells())
        : [];

    const solutionSet = new Set(cellsToHighlight.map(cell => `${cell[0]},${cell[1]}`));

    for (let row = 0; row < board.length; row++) {
        const rowDiv = document.createElement("div");
        rowDiv.className = "row";
        for (let col = 0; col < board[row].length; col++) {
            const cellValue = board[row][col];
            const cellBtn = document.createElement("button");
            cellBtn.className = "cell";
            cellBtn.dataset.row = row.toString();
            cellBtn.dataset.col = col.toString();

            // Apply color scheme to cells
            if (cellValue === true) {
                cellBtn.style.backgroundColor = colors.board.on_cell;
                cellBtn.style.setProperty('--cell-bg-color', colors.board.on_cell);
            } else {
                cellBtn.style.backgroundColor = colors.board.off_cell;
                cellBtn.style.setProperty('--cell-bg-color', colors.board.off_cell);
            }

            cellBtn.style.borderColor = colors.board.border;

            // Highlight solution cells if they exist in the set
            if (solutionSet.has(`${row},${col}`)) {
                cellBtn.classList.add("solution-cell");
                cellBtn.style.setProperty('--highlight-glow-inner', colors.board.solution_glow_inner);
                cellBtn.style.setProperty('--highlight-glow-outer', colors.board.solution_glow_outer);
                cellBtn.style.setProperty('--highlight-border', colors.board.solution_border);
            }

            cellBtn.addEventListener("click", handleStep);
            rowDiv.appendChild(cellBtn);
        }
        boardDiv.appendChild(rowDiv);
    }
}

function handleStep(event) {
    const row = parseInt(event.target.dataset.row);
    const col = parseInt(event.target.dataset.col);
    const wasSolveMode = Boolean(getCurrentState()?.solve_mode);

    removePersistentSolutionCell(row, col);

    stepRequest(row, col)
        .then(data => {
            setCurrentState(data);

            if (wasSolveMode) {
                return refreshSolveHints();
            }

            renderGameBoard();
            updateStatus();
        })
        .catch(error => console.error('Error making step:', error));
}

export function handleUndo() {
    const currentState = getCurrentState();
    if (!currentState || currentState.game_over || (currentState.moves_made || 0) <= 0) {
        return;
    }

    const wasSolveMode = Boolean(currentState?.solve_mode);

    undoRequest()
        .then(data => {
            setCurrentState(data);

            if (wasSolveMode) {
                return refreshSolveHints();
            }

            renderGameBoard();
            updateStatus();
        })
        .catch(error => console.error('Error undoing move:', error));
}

export function updateStatus() {

    const currentState = getCurrentState();
    if (!currentState) return;

    const completionMsg = document.getElementById("completion-message");
    const movesCount = document.getElementById("moves-count");
    const elapsedTime = document.getElementById("elapsed-time");
    const gameGoal = document.getElementById("game-goal");
    const solveBtn = document.getElementById("solve-game-btn");
    const undoBtn = document.getElementById("undo-btn");

    if (solveBtn) {
        solveBtn.disabled = currentState.game_over;
    }

    if (undoBtn) {
        undoBtn.disabled = currentState.game_over || (currentState.moves_made || 0) <= 0;
    }

    if (currentState.game_over) {

        handleGameOver(currentState);

        const minutes = Math.floor(currentState.elapsed_time / 60);
        const seconds = Math.floor(currentState.elapsed_time % 60);
        const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        // Update template values
        if (movesCount) movesCount.textContent = `Moves made: ${currentState.moves_made}`;
        if (elapsedTime) elapsedTime.textContent = `Time: ${timeStr}`;
        if (completionMsg) completionMsg.style.display = "block";
        if (gameGoal) gameGoal.style.display = "none";

        // Disable all board buttons when game is over
        const boardButtons = document.querySelectorAll(".cell");
        boardButtons.forEach(button => {
            button.disabled = true;
            button.style.cursor = "not-allowed";
        });
    } else {
        // Hide the completion message and show the goal when game is not over
        if (completionMsg) completionMsg.style.display = "none";
        if (gameGoal) gameGoal.style.display = "block";
    }
}

function refreshSolveHints() {
    return solveGameRequest(true)
        .then(data => {
            setCurrentState(data);
            const solutionCells = data.solution_cells || [];
            setPersistentSolutionCells(solutionCells);
            setSolveButtonState(Boolean(data.solve_mode));
            renderGameBoard(true, solutionCells);
            updateStatus();
        });
}

export function solveGame() {

    const currentState = getCurrentState();
    const enabled = !currentState?.solve_mode;
    setSolveButtonState(enabled);

    solveGameRequest(enabled)
        .then(data => {
            setCurrentState(data);
            const solutionCells = data.solution_cells || [];
            setPersistentSolutionCells(solutionCells);
            setSolveButtonState(Boolean(data.solve_mode));
            renderGameBoard(true, solutionCells);
            updateStatus();
    });
}
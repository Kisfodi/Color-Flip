let currentState = null;
let currentColorScheme = null;
let timerInterval = null;
let persistentSolutionCells = [];  // Track highlighted cells across renders
let colorSchemeCache = {};  // Cache color schemes after first fetch
let defaultConfig = {};  // Store default config from server

document.addEventListener('DOMContentLoaded', () => {
    // Load default config from server
    loadDefaultConfig();

    // Populate board size dropdown with even numbers only
    const boardSizeSelect = document.getElementById("start-board-size");
    for (let size = 2; size <= 20; size += 2) {
        const option = document.createElement("option");
        option.value = size;
        option.textContent = `${size}x${size}`;
        boardSizeSelect.appendChild(option);
    }

    // Start screen buttons
    document.getElementById("start-new-game-btn").addEventListener("click", goToNewGameScreen);
    document.getElementById("start-load-game-btn").addEventListener("click", goToLoadGameScreen);

    // Game screen buttons
    document.getElementById("back-btn").addEventListener("click", goBackToStartScreen);
    document.getElementById("solve-game-btn").addEventListener("click", solveGame);
    setSolveButtonState(false);

    // Mode selector change handler
    document.getElementById("start-game-mode").addEventListener("change", () => {
        updateModeDescription();
    });

    // Color scheme change handler
    document.getElementById("color-scheme").addEventListener("change", () => {
        updateColorPreview();
        if (currentState) {
            renderGameBoard();
            // Re-apply game-over state if game is finished
            updateStatus();
        }
    });

    // Load colors on startup
    loadAllColorSchemes();
});

function loadDefaultConfig() {
    // Fetch default configuration from server
    fetch('/api/config')
    .then(response => response.json())
    .then(data => {
        defaultConfig = data;
        console.log("Default config loaded:", defaultConfig);

        // Set board size dropdown to default
        const boardSizeSelect = document.getElementById("start-board-size");
        if (defaultConfig.size) {
            boardSizeSelect.value = defaultConfig.size;
        }

        // Set color scheme dropdown to default
        const colorSchemeSelect = document.getElementById("color-scheme");
        if (defaultConfig.color_scheme) {
            colorSchemeSelect.value = defaultConfig.color_scheme;
        }

        // Set game mode dropdown to default
        const gameModeSelect = document.getElementById("start-game-mode");
        if (defaultConfig.mode) {
            gameModeSelect.value = defaultConfig.mode;
            updateModeDescription();
        }

        // Update color preview with the default scheme
        updateColorPreview();
    })
    .catch(error => console.error('Error loading default config:', error));
}

function loadAllColorSchemes() {
    // Fetch all color schemes from backend and cache them.
    fetch('/api/colors')
    .then(response => response.json())
    .then(data => {
        colorSchemeCache = data;
        console.log("Color schemes loaded:", Object.keys(colorSchemeCache));
        // Update color preview after schemes are loaded
        updateColorPreview();
    })
    .catch(error => console.error('Error loading color schemes:', error));
}

function updateColorPreview() {
    // Get the currently selected color scheme
    const schemeName = document.getElementById("color-scheme").value;
    const colors = getColorScheme(schemeName);

    // Update the preview boxes
    const onCellPreview = document.querySelector(".on-cell-preview");
    const offCellPreview = document.querySelector(".off-cell-preview");

    if (onCellPreview && colors.board.on_cell) {
        onCellPreview.style.backgroundColor = colors.board.on_cell;
    }

    if (offCellPreview && colors.board.off_cell) {
        offCellPreview.style.backgroundColor = colors.board.off_cell;
    }
}

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

function getColorScheme(schemeName) {
    // Get color scheme from cache. Returns default scheme if not found.
    return colorSchemeCache[schemeName] || colorSchemeCache['default'] || {
        board: {
            on_cell: "#16c116",
            off_cell: "#c11d1d",
            solution_highlight: "#ffff00",
            solution_glow_inner: "rgba(255, 255, 0, 0.7)",
            solution_glow_outer: "rgba(255, 255, 0, 0.5)",
            solution_border: "#ffff00"
        }
    };
}

function goToNewGameScreen() {
    // Get board size from start screen
    const boardSize = parseInt(document.getElementById("start-board-size").value);

    // Validate board size (select dropdown guarantees even values and valid range)
    if (isNaN(boardSize)) {
        alert("Please select a valid board size");
        return;
    }

    // Get selected game mode
    const gameMode = document.getElementById("start-game-mode").value;

    // Hide start screen and show game screen
    document.getElementById("start-screen").style.display = "none";
    document.getElementById("game-screen").style.display = "block";

    // Start the game with selected size and mode
    startNewGameWithSize(boardSize, gameMode);
}

function goToLoadGameScreen() {
    alert("Load game feature coming soon!");
    // TODO: Implement load game functionality
}

function goBackToStartScreen() {
    // Stop the timer
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

    // Clear persistent highlights when starting a new game
    persistentSolutionCells = [];

    // Clear the completion message when starting a new game
    document.getElementById("completion-message").style.display = "none";
    document.getElementById("game-goal").style.display = "block";

    // Update the game goal display
    updateGameGoal(mode);

    // Re-enable the solve game button for the new game
    document.getElementById("solve-game-btn").disabled = false;
    setSolveButtonState(false);

    fetch('/api/new_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        currentState = data;
        persistentSolutionCells = data.solution_cells || [];
        setSolveButtonState(Boolean(data.solve_mode));
        console.log(data);
        renderGameBoard();
        updateStatus();
        stopTimer(); // Stop any running timer
        startTimer(); // Start fresh timer for new game
    })
    .catch(error => console.error('Error starting game:', error));
}


function setSolveButtonState(enabled) {
    const button = document.getElementById("solve-game-btn");
    if (!button) {
        return;
    }

    const isEnabled = Boolean(enabled);
    button.classList.toggle("active", isEnabled);
    button.dataset.solveState = isEnabled ? "on" : "off";
    button.setAttribute("aria-pressed", isEnabled ? "true" : "false");
    button.innerText = `Solve: ${isEnabled ? "ON" : "OFF"}`;
    button.textContent = `Solve: ${isEnabled ? "ON" : "OFF"}`;
}

function renderGameBoard(highlightSolutionCells = false, solutionCells = []) {
    const boardDiv = document.getElementById("board-container");
    boardDiv.innerHTML = ''; // Clear previous board

    const board = currentState.board;
    console.log("Board:\n");
    console.log(board);

    // Get the current color scheme
    const schemeName = document.getElementById("color-scheme").value;
    const colors = getColorScheme(schemeName);

    const cellsToHighlight = currentState?.solve_mode ? (highlightSolutionCells ? solutionCells : persistentSolutionCells) : [];

    // Create a Set for O(1) lookup of solution cells
    const solutionSet = new Set(cellsToHighlight.map(cell => `${cell[0]},${cell[1]}`));

    for (let row = 0; row < board.length; row++) {
        const rowDiv = document.createElement("div");
        rowDiv.className = "row";
        for (let col = 0; col < board[row].length; col++) {
            const cellValue = board[row][col];
            const cellBtn = document.createElement("button");
            cellBtn.className = "cell";
            cellBtn.dataset.row = row;
            cellBtn.dataset.col = col;

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
                // Apply color scheme to highlights
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

    console.log(row, col);

    // Remove the pressed cell from persistent highlights if it was there
    persistentSolutionCells = persistentSolutionCells.filter(cell => !(cell[0] === row && cell[1] === col));

    fetch('/api/step', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({row: row, col: col})
    })
    .then(response => response.json())
    .then(data => {
        currentState = data;
        setSolveButtonState(Boolean(data.solve_mode));

        if (data.solve_mode) {
            return refreshSolveHints();
        }

        persistentSolutionCells = data.solution_cells || [];
        renderGameBoard();
        updateStatus();
    });
}

function updateStatus() {
    const completionMsg = document.getElementById("completion-message");
    const movesCount = document.getElementById("moves-count");
    const elapsedTime = document.getElementById("elapsed-time");
    const gameGoal = document.getElementById("game-goal");

    document.getElementById("solve-game-btn").disabled = currentState.game_over;

    if (currentState.game_over) {
        stopTimer();
        const minutes = Math.floor(currentState.elapsed_time / 60);
        const seconds = Math.floor(currentState.elapsed_time % 60);
        const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        // Update template values
        movesCount.textContent = `Moves made: ${currentState.moves_made}`;
        elapsedTime.textContent = `Time: ${timeStr}`;
        completionMsg.style.display = "block";
        gameGoal.style.display = "none";

        // Disable all board buttons when game is over
        const boardButtons = document.querySelectorAll(".cell");
        boardButtons.forEach(button => {
            button.disabled = true;
            button.style.cursor = "not-allowed";
        });
    } else {
        // Hide the completion message and show the goal when game is not over
        completionMsg.style.display = "none";
        gameGoal.style.display = "block";
    }

}

function refreshSolveHints() {
    return fetch('/api/solve_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({enabled: true})
    })
    .then(response => response.json())
    .then(data => {
        currentState = data;
        const solutionCells = data.solution_cells || [];
        persistentSolutionCells = solutionCells;
        setSolveButtonState(Boolean(data.solve_mode));
        renderGameBoard(true, solutionCells);
        updateStatus();
    });
}

function solveGame() {
    const enabled = !currentState?.solve_mode;
    setSolveButtonState(enabled);

    fetch('/api/solve_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({enabled: enabled})
    })
    .then(response => response.json())
    .then(data => {
        currentState = data;
        const solutionCells = data.solution_cells || [];
        // Set persistent highlights to the new solution cells
        persistentSolutionCells = solutionCells;
        setSolveButtonState(Boolean(data.solve_mode));
        renderGameBoard(true, solutionCells);
        updateStatus();
    });
}

function updateTimer(elapsed) {
    const minutes = Math.floor(elapsed / 60);
    const seconds = Math.floor(elapsed % 60);
    document.getElementById("timer").textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
    const startTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        updateTimer(elapsed);
    }, 100);
}

function stopTimer() {
    clearInterval(timerInterval);
}
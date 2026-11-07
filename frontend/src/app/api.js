import { getCurrentGameId } from "./gameState.js";
import { getElapsed } from "./timer.js";

function getGameHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    const gameId = getCurrentGameId();
    if (gameId) {
        headers['X-Game-ID'] = gameId;
    }
    return headers;
}

export async function fetchConfig() {
    const response = await fetch('/api/config');
    return response.json();
}

export async function fetchColorSchemes() {
    const response = await fetch('/api/colors');
    return response.json();
}

export async function startNewGameRequest(config) {
    const response = await fetch('/api/new_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    });
    return response.json();
}

export async function stepRequest(row, col) {
    const response = await fetch('/api/step', {
        method: 'POST',
        headers: getGameHeaders(),
        body: JSON.stringify({ row, col, elapsed_time: getElapsed() })
    });

    console.log("Doing step: ", row, col);

    return response.json();
}

export async function undoRequest() {
    const response = await fetch('/api/undo', {
        method: 'POST',
        headers: getGameHeaders(),
        body: JSON.stringify({ elapsed_time: getElapsed() })
    });
    return response.json();
}

export async function solveGameRequest(enabled, showOneStep = null) {
    const payload = { enabled };
    if (showOneStep !== null) {
        payload.show_one_step = Boolean(showOneStep);
    }
    const response = await fetch('/api/solve_game', {
        method: 'POST',
        headers: getGameHeaders(),
        body: JSON.stringify(payload)
    });
    return response.json();
}

export async function fetchGameStateRequest(gameId) {
    const headers = {
        'Content-Type': 'application/json'
    };
    if (gameId) {
        headers['X-Game-ID'] = gameId;
    }
    const response = await fetch('/api/game_state', {
        method: 'GET',
        headers: headers
    });
    return response.json();
}
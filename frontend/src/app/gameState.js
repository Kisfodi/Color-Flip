import {stopTimer} from "./timer.js";

const ACTIVE_GAME_KEY = 'color_flip_active_game_id';

let currentState = null;
let currentGameId = null;
let persistentSolutionCells = [];   // Track highlighted cells across renders
let colorSchemeCache = {};  // Cache color schemes after first fetch
let defaultConfig = {}; // Store default config from server

export function getCurrentState() {
    return currentState;
}

export function setCurrentState(state) {
    currentState = state;
}

export function getCurrentGameId() {
    return currentGameId;
}

export function setCurrentGameId(id) {
    currentGameId = id;
    if (id) {
        localStorage.setItem(ACTIVE_GAME_KEY, id);
    } else {
        localStorage.removeItem(ACTIVE_GAME_KEY);
    }
}

export function getActiveGameIdFromStorage() {
    return localStorage.getItem(ACTIVE_GAME_KEY);
}

export function clearActiveGameId() {
    currentGameId = null;
    localStorage.removeItem(ACTIVE_GAME_KEY);
}

export function getPersistentSolutionCells() {
    return persistentSolutionCells;
}

export function setPersistentSolutionCells(cells) {
    persistentSolutionCells = cells;
}

export function removePersistentSolutionCell(row, col) {
    persistentSolutionCells = persistentSolutionCells.filter(
        cell => !(cell[0] === row && cell[1] === col)
    );
}

export function getColorSchemeCache() {
    return colorSchemeCache;
}

export function setColorSchemeCache(cache) {
    colorSchemeCache = cache;
}

export function getDefaultConfig() {
    return defaultConfig;
}

export function setDefaultConfig(config) {
    defaultConfig = config;
}

export function handleGameOver(currentState) {
    stopTimer();
    // Invalidate active game from resume tracking since it is now finished
    clearActiveGameId();
}
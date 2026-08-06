import {stopTimer} from "./timer.js";

let currentState = null;
let persistentSolutionCells = [];   // Track highlighted cells across renders
let colorSchemeCache = {};  // Cache color schemes after first fetch
let defaultConfig = {}; // Store default config from server

export function getCurrentState() {
    return currentState;
}

export function setCurrentState(state) {
    currentState = state;
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
    //TODO Handle other things in the future, e.g. save the game state, etc.
}
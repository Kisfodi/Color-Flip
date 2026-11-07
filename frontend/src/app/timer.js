let timerInterval = null;
let timerStartTime = null;   // wall-clock ms when the interval was last started
let timerOffset = 0;         // seconds already accumulated before the current interval

function updateTimer(elapsed) {
    const minutes = Math.floor(elapsed / 60);
    const seconds = Math.floor(elapsed % 60);
    document.getElementById("timer").textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * Start (or resume) the timer.
 * @param {number} initialElapsed - Seconds already elapsed before this session (default 0).
 */
export function startTimer(initialElapsed = 0) {
    // Clear any existing interval before starting a new one
    clearInterval(timerInterval);
    timerOffset = initialElapsed;
    timerStartTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = timerOffset + (Date.now() - timerStartTime) / 1000;
        updateTimer(elapsed);
    }, 100);
}

/**
 * Pause the timer and return how many seconds have elapsed in total.
 * @returns {number} Total elapsed seconds at the moment of stopping.
 */
export function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    if (timerStartTime === null) return timerOffset;
    return timerOffset + (Date.now() - timerStartTime) / 1000;
}

/**
 * Return the total elapsed seconds without stopping the timer.
 * @returns {number}
 */
export function getElapsed() {
    if (timerStartTime === null) return timerOffset;
    return timerOffset + (Date.now() - timerStartTime) / 1000;
}

/**
 * Reset the timer display and internal state without starting it.
 */
export function resetTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    timerStartTime = null;
    timerOffset = 0;
    const timerElem = document.getElementById("timer");
    if (timerElem) timerElem.textContent = "Time: 0:00";
}
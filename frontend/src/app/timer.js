let timerInterval = null;

function updateTimer(elapsed) {
    const minutes = Math.floor(elapsed / 60);
    const seconds = Math.floor(elapsed % 60);
    document.getElementById("timer").textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export function startTimer() {
    const startTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        updateTimer(elapsed);
    }, 100);
}

export function stopTimer() {
    clearInterval(timerInterval);
}
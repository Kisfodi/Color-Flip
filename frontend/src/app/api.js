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

export async function stepRequest(row, col){
    const response = await fetch('/api/step', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json'
       },
       body: JSON.stringify({ row, col })
    });
    return response.json();
}

export async function solveGameRequest(enabled) {
    const response = await fetch('/api/solve_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ enabled })
    });
    return response.json();
}
import {getColorSchemeCache, getDefaultConfig} from "./gameState.js";

export function getColorScheme(schemeName) {
    // Get color scheme from cache. Returns default scheme if not found.
    const cache = getColorSchemeCache();

    return cache[schemeName] || cache['default'] || {
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

export function populateColorSchemeSelect() {
    const select = document.getElementById("color-scheme");
    const cache = getColorSchemeCache();
    const defaultConfig = getDefaultConfig();

    select.innerHTML = '';
    for (const [name, scheme] of Object.entries(cache)) {
        const option = document.createElement("option");
        option.value = name;
        option.textContent = scheme.label || name;
        select.appendChild(option);
    }

    if (defaultConfig.color_scheme) {
        select.value = defaultConfig.color_scheme;
    }
}

export function updateColorPreview() {

    const schemeName = document.getElementById("color-scheme").value;
    const colors = getColorScheme(schemeName);

    const onCellPreview = document.querySelector(".on-cell-preview");
    const offCellPreview = document.querySelector(".off-cell-preview");

    if (onCellPreview && colors.board.on_cell) {
        onCellPreview.style.backgroundColor = colors.board.on_cell;
    }

    if (offCellPreview && colors.board.off_cell) {
        offCellPreview.style.backgroundColor = colors.board.off_cell;
    }
}

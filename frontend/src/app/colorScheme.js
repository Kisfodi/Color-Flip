import { getColorSchemeCache, getDefaultConfig } from "./gameState.js";
import { getSetting } from "./settings.js";

export function getColorScheme(schemeName = null) {
    if (!schemeName) {
        schemeName = getSetting('colorScheme') || getDefaultConfig()?.color_scheme || 'default';
    }
    const cache = getColorSchemeCache();

    return cache[schemeName] || cache['default'] || {
        board: {
            on_cell: "#084508",
            off_cell: "#7C1313",
            solution_highlight: "#D0D0D0",
            solution_glow_inner: "rgba(255, 255, 255, 0.9)",
            solution_glow_outer: "rgba(255, 255, 255, 0.7)",
            solution_border: "#D0D0D0"
        }
    };
}

export function populateColorSchemeSelect() {
    const select = document.getElementById("color-scheme");
    if (!select) return;

    const cache = getColorSchemeCache();
    const currentScheme = getSetting('colorScheme') || getDefaultConfig()?.color_scheme || 'default';

    select.innerHTML = '';
    for (const [name, scheme] of Object.entries(cache)) {
        const option = document.createElement("option");
        option.value = name;
        option.textContent = scheme.label || name;
        if (name === currentScheme) {
            option.selected = true;
        }
        select.appendChild(option);
    }
}

export function updateColorPreview(schemeName = null) {
    if (!schemeName) {
        const select = document.getElementById("color-scheme");
        schemeName = select ? select.value : (getSetting('colorScheme') || getDefaultConfig()?.color_scheme || 'default');
    }
    const colors = getColorScheme(schemeName);

    const onCellPreviews = document.querySelectorAll(".on-cell-preview");
    const offCellPreviews = document.querySelectorAll(".off-cell-preview");

    if (colors && colors.board) {
        onCellPreviews.forEach(el => {
            if (colors.board.on_cell) el.style.backgroundColor = colors.board.on_cell;
        });
        offCellPreviews.forEach(el => {
            if (colors.board.off_cell) el.style.backgroundColor = colors.board.off_cell;
        });
    }
}

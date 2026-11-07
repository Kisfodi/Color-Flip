// settings.js - Modular game settings manager
import { getColorSchemeCache, getDefaultConfig } from "./gameState.js";
import { getColorScheme } from "./colorScheme.js";

export const SETTINGS_CONFIG = [
    {
        id: 'showOneHint',
        label: 'Single Step Hint',
        description: 'Show only the next recommended move instead of the full solution.',
        type: 'toggle',
        default: true,
    },
    {
        id: 'colorScheme',
        label: 'Color Scheme',
        description: 'Select board theme for ON and OFF cells.',
        type: 'color-scheme',
        default: 'black_gold_elegance',
    }
];

const SETTINGS_STORAGE_KEY = 'color_flip_settings';
const listeners = new Set();

let currentSettings = null;

export function loadSettings() {
    if (currentSettings) {
        return currentSettings;
    }

    const defaultConfig = getDefaultConfig() || {};
    const defaults = {};
    SETTINGS_CONFIG.forEach(item => {
        if (item.id === 'colorScheme' && defaultConfig.color_scheme) {
            defaults[item.id] = defaultConfig.color_scheme;
        } else {
            defaults[item.id] = item.default;
        }
    });

    try {
        const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
        if (stored) {
            currentSettings = { ...defaults, ...JSON.parse(stored) };
        } else {
            currentSettings = { ...defaults };
        }
    } catch (e) {
        console.warn('Failed to read settings from localStorage:', e);
        currentSettings = { ...defaults };
    }

    return currentSettings;
}

export function saveSettings(settings) {
    currentSettings = { ...settings };
    try {
        localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(currentSettings));
    } catch (e) {
        console.warn('Failed to save settings to localStorage:', e);
    }
}

export function getSetting(id) {
    const settings = loadSettings();
    return settings[id];
}

export function setSetting(id, value) {
    const settings = loadSettings();
    settings[id] = value;
    saveSettings(settings);

    // Notify listeners
    listeners.forEach(cb => {
        try {
            cb(id, value, settings);
        } catch (e) {
            console.error('Error in settings listener:', e);
        }
    });
}

export function onSettingChange(callback) {
    listeners.add(callback);
    return () => listeners.delete(callback);
}

export function renderSettingsModalBody(containerId = 'settings-modal-body') {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    const settings = loadSettings();

    SETTINGS_CONFIG.forEach(item => {
        const itemRow = document.createElement('div');
        itemRow.className = 'setting-item';

        const infoDiv = document.createElement('div');
        infoDiv.className = 'setting-info';

        const label = document.createElement('label');
        label.className = 'setting-label';
        label.htmlFor = `setting-${item.id}`;
        label.textContent = item.label;

        const description = document.createElement('div');
        description.className = 'setting-description';
        description.textContent = item.description;

        infoDiv.appendChild(label);
        infoDiv.appendChild(description);
        itemRow.appendChild(infoDiv);

        if (item.type === 'toggle') {
            const toggleWrapper = document.createElement('label');
            toggleWrapper.className = 'toggle-switch';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `setting-${item.id}`;
            checkbox.checked = Boolean(settings[item.id]);

            checkbox.addEventListener('change', (e) => {
                setSetting(item.id, e.target.checked);
            });

            const slider = document.createElement('span');
            slider.className = 'toggle-slider';

            toggleWrapper.appendChild(checkbox);
            toggleWrapper.appendChild(slider);
            itemRow.appendChild(toggleWrapper);
        } else if (item.type === 'color-scheme') {
            itemRow.classList.add('setting-item-column');

            const controlWrapper = document.createElement('div');
            controlWrapper.className = 'color-scheme-control-wrapper';

            const select = document.createElement('select');
            select.id = 'color-scheme';
            select.className = 'settings-select';

            const cache = getColorSchemeCache();
            const currentScheme = settings[item.id] || 'default';

            for (const [name, scheme] of Object.entries(cache)) {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = scheme.label || name;
                if (name === currentScheme) {
                    option.selected = true;
                }
                select.appendChild(option);
            }

            // Preview container
            const previewContainer = document.createElement('div');
            previewContainer.className = 'settings-color-preview';

            const previewLabel = document.createElement('span');
            previewLabel.className = 'settings-preview-label';
            previewLabel.textContent = 'Preview:';

            const swatches = document.createElement('div');
            swatches.className = 'color-preview';

            const onItem = document.createElement('div');
            onItem.className = 'color-preview-item';
            const onBox = document.createElement('div');
            onBox.className = 'color-box on-cell-preview';
            onBox.title = 'ON cell color';
            const onLabel = document.createElement('div');
            onLabel.className = 'color-label';
            onLabel.textContent = 'ON';
            onItem.appendChild(onBox);
            onItem.appendChild(onLabel);

            const offItem = document.createElement('div');
            offItem.className = 'color-preview-item';
            const offBox = document.createElement('div');
            offBox.className = 'color-box off-cell-preview';
            offBox.title = 'OFF cell color';
            const offLabel = document.createElement('div');
            offLabel.className = 'color-label';
            offLabel.textContent = 'OFF';
            offItem.appendChild(offBox);
            offItem.appendChild(offLabel);

            swatches.appendChild(onItem);
            swatches.appendChild(offItem);

            previewContainer.appendChild(previewLabel);
            previewContainer.appendChild(swatches);

            function updateSwatches(schemeName) {
                const colors = getColorScheme(schemeName);
                if (colors && colors.board) {
                    onBox.style.backgroundColor = colors.board.on_cell;
                    offBox.style.backgroundColor = colors.board.off_cell;
                }
            }

            updateSwatches(select.value || currentScheme);

            select.addEventListener('change', (e) => {
                const val = e.target.value;
                setSetting(item.id, val);
                updateSwatches(val);
            });

            controlWrapper.appendChild(select);
            controlWrapper.appendChild(previewContainer);
            itemRow.appendChild(controlWrapper);
        }

        container.appendChild(itemRow);
    });
}

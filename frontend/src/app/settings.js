// settings.js - Modular game settings manager

export const SETTINGS_CONFIG = [
    {
        id: 'showOneHint',
        label: 'Single Step Hint',
        description: 'Show only the next recommended move instead of the full solution.',
        type: 'toggle',
        default: true,
    }
];

const SETTINGS_STORAGE_KEY = 'color_flip_settings';
const listeners = new Set();

let currentSettings = null;

export function loadSettings() {
    if (currentSettings) {
        return currentSettings;
    }

    const defaults = {};
    SETTINGS_CONFIG.forEach(item => {
        defaults[item.id] = item.default;
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
        }

        container.appendChild(itemRow);
    });
}


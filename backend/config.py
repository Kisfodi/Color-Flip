import os
from functools import lru_cache

import yaml


@lru_cache(maxsize=1)
def load_game_config():
    """Load game configuration from game_config.yaml file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'game_config.yaml')

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('board', {})
    except FileNotFoundError:
        raise FileNotFoundError(f"Game configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing game configuration: {e}")


def _validate_board_size(size):
    """Validate board size is even and within valid range."""
    if not isinstance(size, int):
        return False
    if size < 2 or size > 20:
        return False
    if size % 2 != 0:  # Must be even
        return False
    return True


def _validate_seed(seed):
    """Validate seed is either None or a positive integer."""
    if seed is None:
        return True
    if not isinstance(seed, int):
        return False
    return seed >= 0


def _validate_color_scheme(scheme_name):
    """Validate color scheme exists."""
    if not isinstance(scheme_name, str):
        return False
    # Import here to avoid circular imports
    try:
        from backend.colors import validate_color_scheme
        return validate_color_scheme(scheme_name)
    except Exception:
        return False


def _validate_game_mode(mode):
    """Validate game mode is one of the allowed modes."""
    if not isinstance(mode, str):
        return False
    return mode in ["all_on", "all_off", "mixed"]


def get_default_board_size():
    config = load_game_config()
    size = config.get('size')

    # Validate size
    if _validate_board_size(size):
        return size

    # Log warning about invalid size
    print(f"Warning: Invalid board size in config: {size}. Using fallback: 4")

    # Fallback to 4x4
    return 4


def get_default_seed():
    """Get the default seed from config with validation and fallback."""
    config = load_game_config()
    seed = config.get('seed')

    # Validate seed
    if _validate_seed(seed):
        return seed

    # Log warning about invalid seed
    print(f"Warning: Invalid seed in config: {seed}. Using fallback: None")

    # Fallback to None (random)
    return None


def get_default_color_scheme():
    """Get the default color scheme from config with validation and fallback."""
    config = load_game_config()
    scheme = config.get('color_scheme')

    # Validate scheme
    if _validate_color_scheme(scheme):
        return scheme

    # Log warning about invalid scheme
    print(f"Warning: Invalid color scheme in config: {scheme}. Using fallback: default")

    # Fallback to 'default'
    return 'default'


def get_default_game_mode():
    """Get the default game mode from config with validation and fallback."""
    config = load_game_config()
    mode = config.get('mode')

    # Validate mode
    if _validate_game_mode(mode):
        return mode

    # Log warning about invalid mode
    print(f"Warning: Invalid game mode in config: {mode}. Using fallback: mixed")

    # Fallback to 'mixed'
    return 'mixed'


def get_all_config():
    """Get all board configuration values with validation and fallbacks."""
    return {
        'size': get_default_board_size(),
        'seed': get_default_seed(),
        'color_scheme': get_default_color_scheme(),
        'mode': get_default_game_mode()
    }



import os
from functools import lru_cache

import yaml


@lru_cache(maxsize=1)
def load_color_schemes():
    """Load color schemes from colors.yaml configuration file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'colors.yaml')

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('color_schemes', {})
    except FileNotFoundError:
        raise FileNotFoundError(f"Color configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing color configuration: {e}")


def get_color_scheme(scheme_name: str) -> dict:
    """
    Get a specific color scheme by name.

    Args:
        scheme_name: Name of the color scheme (e.g., 'default', 'pastel', 'neon')

    Returns:
        Dictionary containing color values for the scheme

    Raises:
        ValueError: If the scheme name doesn't exist
    """
    color_schemes = load_color_schemes()

    if scheme_name not in color_schemes:
        available = ', '.join(color_schemes.keys())
        raise ValueError(f"Color scheme '{scheme_name}' not found. Available schemes: {available}")

    return color_schemes[scheme_name]


def get_all_color_schemes() -> dict:
    """Get all available color schemes."""
    return load_color_schemes()


def validate_color_scheme(scheme_name: str) -> bool:
    """Check if a color scheme exists."""
    try:
        color_schemes = load_color_schemes()
        return scheme_name in color_schemes
    except Exception:
        return False


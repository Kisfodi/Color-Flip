from flask import Blueprint, request, jsonify, current_app

from backend.colors import get_color_scheme, get_all_color_schemes, validate_color_scheme
from backend.config import get_default_board_size, get_default_seed, get_default_game_mode
from backend.game import Game

api_blueprint = Blueprint('api', __name__)

def _get_active_game():
    return current_app.config.get('game')


def _set_active_game(game: Game):
    current_app.config['game'] = game

@api_blueprint.route('/config', methods=['GET'])
def get_config():
    """Get default game configuration from game_config.yaml."""
    try:
        from backend.config import get_all_config
        config = get_all_config()
        return jsonify({
            "size": config.get('size', 4),
            "seed": config.get('seed'),
            "color_scheme": config.get('color_scheme', 'default'),
            "mode": config.get('mode', 'mixed')
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_blueprint.route('/colors', methods=['GET'])
def get_colors():
    """Get all available color schemes."""
    try:
        color_schemes = get_all_color_schemes()
        return jsonify(color_schemes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_blueprint.route('/colors/<scheme_name>', methods=['GET'])
def get_color_scheme_endpoint(scheme_name):
    """Get a specific color scheme by name."""
    try:
        if not validate_color_scheme(scheme_name):
            return jsonify({"error": f"Color scheme '{scheme_name}' not found"}), 404

        colors = get_color_scheme(scheme_name)
        return jsonify(colors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_blueprint.route('/new_game', methods=['POST'])
def new_game():
    data = request.json or {}

    # Get values from request, fallback to config file defaults
    size = data.get("size", get_default_board_size())
    seed = data.get("seed", get_default_seed())
    mode = data.get("mode", get_default_game_mode())

    try:
        _set_active_game(Game(size=size, seed=seed, mode=mode))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(_get_active_game().get_game_state())

@api_blueprint.route('/step', methods=['POST'])
def step():
    game = _get_active_game()
    if game is None:
        return jsonify({"error": "No active game. Start a new game first."}), 400

    data = request.json or {}
    row = data.get('row')
    col = data.get('col')

    print(data)

    result = game.step(row, col)
    return jsonify(result)

@api_blueprint.route('/game_state', methods=['GET'])
def get_game_state():
    game = _get_active_game()
    if game is None:
        return jsonify({"error": "No active game. Start a new game first."}), 400

    return jsonify(game.get_game_state())

@api_blueprint.route('/solve_game', methods=['POST'])
def solve_game():
    game = _get_active_game()
    if game is None:
        return jsonify({"error": "No active game. Start a new game first."}), 400

    data = request.json
    result = game.solve_game()
    return jsonify(result)
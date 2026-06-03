import os

from flask import Flask, render_template

from frontend.api import api_blueprint
from backend.db import init_app as init_db_app
from backend.colors import get_all_color_schemes

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static', template_folder='templates', instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if config:
        app.config.update(config)

    # Initialize database
    init_db_app(app)

    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register routes
    @app.route('/')
    def index():
        color_schemes = get_all_color_schemes()
        # Create a list of tuples with (scheme_name, scheme_label) for template
        schemes_with_labels = [(name, scheme.get('label', name)) for name, scheme in color_schemes.items()]
        return render_template('index.html', schemes_with_labels=schemes_with_labels)

    return app

app = create_app()

def main():

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5050, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP")
    parser.add_argument("--debug", action='store_true', help="Debug mode")

    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
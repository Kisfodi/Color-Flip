import os
import argparse
from pathlib import Path

from fastapi import FastAPI

from backend.api import router
from backend.db import init_db

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"


def create_app() -> FastAPI:
    app = FastAPI()
    init_db()
    app.state.game = None

    app.include_router(router, prefix="/api")
    if DIST_DIR.exists():
        app.frontend("/", directory=str(DIST_DIR))

    return app

app = create_app()


def main():

    default_port = int(os.environ.get("PORT", 5050))
    default_host = os.environ.get("HOST", "0.0.0.0")

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=default_port, help="Port to listen on")
    parser.add_argument("--host", type=str, default=default_host, help="Host IP")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run("frontend.app:app", host=args.host, port=args.port, reload=args.debug)


if __name__ == "__main__":
    main()

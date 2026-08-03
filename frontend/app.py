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
    app.frontend("/", directory=str(DIST_DIR))

    return app

app = create_app()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5050, help="Port to listen on")
    parser.add_argument("--host", type=str, default="localhost", help="Host IP")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run("frontend.app:app", host=args.host, port=args.port, reload=args.debug)


if __name__ == "__main__":
    main()

import argparse
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.colors import get_all_color_schemes
from backend.db import init_db
from backend.api import router


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


def create_app() -> FastAPI:
    app = FastAPI()
    init_db()
    app.state.game = None

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(router, prefix="/api")

    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        color_schemes = get_all_color_schemes()
        schemes_with_labels = [
            (name, scheme.get("label", name))
            for name, scheme in color_schemes.items()
        ]

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"schemes_with_labels": schemes_with_labels},
        )

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

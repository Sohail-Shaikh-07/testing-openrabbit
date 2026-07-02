from fastapi import FastAPI

from app.api.routes import auth, tasks
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="TaskFlow API", version="0.1.0")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    return app


app = create_app()

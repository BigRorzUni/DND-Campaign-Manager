from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.session import engine
from app.db.base import Base
from app.api.v1.router import router as api_v1_router
from app.ui.routes import router as ui_router

import app.models

def create_app() -> FastAPI:
    application = FastAPI(title="DnD Campaign Manager API")

    Base.metadata.create_all(bind=engine)

    application.include_router(api_v1_router, prefix="/api/v1")
    application.include_router(ui_router)

    application.mount("/static", StaticFiles(directory="app/static"), name="static")

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()
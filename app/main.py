from fastapi import FastAPI

from app.db.session import engine
from app.db.base import Base
import app.models

from app.api.v1.router import router as api_v1_router


def create_app() -> FastAPI:
    application = FastAPI(title="DnD Campaign Manager API")

    # auto creates tables
    Base.metadata.create_all(bind=engine)

    # mounting api routes
    application.include_router(api_v1_router, prefix="/api/v1")

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()
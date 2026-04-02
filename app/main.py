from fastapi import FastAPI, status
from pydantic import BaseModel

from app.core.config import get_settings

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str

def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for the Internship Copilot.",
    )

    @app.get(
        "/heath",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
        summary="Health check",
    )
    def health_check() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app_name=settings.app_name,
            version=settings.app_version,
            environment=settings.environment,
        )
    return app

app = create_application()
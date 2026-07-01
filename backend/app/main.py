from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.demo import router as demo_router
from app.api.routes.health import router as health_router
from app.api.routes.questionnaire import router as questionnaire_router
from app.api.routes.reports import router as reports_router
from app.api.routes.version import router as version_router
from app.api.routes.windows_checks import router as windows_checks_router
from app.version import APP_NAME, APP_VERSION


def create_app() -> FastAPI:
    application = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="Local-first defensive home cyber hygiene baseline API.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(version_router)
    application.include_router(demo_router)
    application.include_router(questionnaire_router)
    application.include_router(reports_router)
    application.include_router(windows_checks_router)
    return application


app = create_app()

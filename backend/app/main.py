from fastapi import FastAPI
from app.api.v1 import auth as auth_router
from app.api.v1 import db_inspect as db_inspect_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aivendance API",
        version="0.1.0",
        description="Backend API for the AiVendance attendance system (Phase 1: database layer).",
    )

    # System endpoints
    @app.get("/health", tags=["system"])
    def health_check():
        return {"status": "ok"}

    # Routers (v1)
    app.include_router(auth_router.router)
    app.include_router(db_inspect_router.router)

    return app


app = create_app()
# ============== End of App Definition ==============
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.config import get_settings
from app.errors import AppError
from app.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API for the AI Automation Platform — workflows, runs, credentials, and execution.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)  # health also at /health for compose probes


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.get("/")
def root():
    return {"name": settings.app_name, "docs": "/docs"}

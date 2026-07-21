from fastapi import APIRouter
from app.api.endpoints import analyze, auth, history, trends, compare, assistant, reports, privacy

api_router = APIRouter()
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(trends.router, prefix="/history/trends", tags=["trends"])
api_router.include_router(compare.router, prefix="/compare", tags=["compare"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(reports.router, prefix="/history/reports", tags=["reports"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])

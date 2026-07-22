from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import api_router
from app.db.database import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

from app.services.ml_service import MLService
from app.services.llm_service import llm_service
from app.core.logging import logger

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Lumine AI. Running diagnostic checks...")
    MLService.check_inference_status()
    llm_service.check_llm_status()
    logger.info("Startup diagnostic checks complete.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def home():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

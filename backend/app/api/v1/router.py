from fastapi import APIRouter
from .endpoints import auth, scans, ws, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

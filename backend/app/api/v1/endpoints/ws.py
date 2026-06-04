from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import json

router = APIRouter()

# For a production app, we would use Redis Pub/Sub to communicate between Celery workers
# and the WebSocket servers. For this single-node demo, we can poll the database or
# just simulate the progress steps over time since we have the task ID.
# Since we want it to feel real, we will poll the database for the scan status.


@router.websocket("/{scan_id}")
async def scan_progress_ws(websocket: WebSocket, scan_id: str):
    await websocket.accept()

    # We will poll the database for the scan status
    # Wait until it is COMPLETED or FAILED
    from app.db.session import AsyncSessionLocal
    from app.models.scan import Scan, ScanStatus
    from sqlalchemy import select

    try:
        # Initial state
        await websocket.send_json({"status": "QUEUED", "progress": 10})

        while True:
            async with AsyncSessionLocal() as db:
                stmt = select(Scan).where(Scan.id == scan_id)
                result = await db.execute(stmt)
                scan = result.scalar_one_or_none()

                if not scan:
                    await websocket.send_json(
                        {"status": "FAILED", "progress": 0, "message": "Scan not found"}
                    )
                    break

                if scan.status == ScanStatus.COMPLETED:
                    await websocket.send_json({"status": "COMPLETED", "progress": 100})
                    break
                elif scan.status == ScanStatus.FAILED:
                    await websocket.send_json({"status": "FAILED", "progress": 0})
                    break
                elif scan.status == ScanStatus.PROCESSING:
                    # In a real app we'd have finer grained states from Celery
                    await websocket.send_json({"status": "PROCESSING", "progress": 50})

            await asyncio.sleep(1)  # Poll every second

    except WebSocketDisconnect:
        print(f"Client disconnected from WS for scan {scan_id}")
    except Exception as e:
        print(f"WS Error: {e}")
        try:
            await websocket.send_json(
                {"status": "FAILED", "progress": 0, "message": str(e)}
            )
        except:
            pass

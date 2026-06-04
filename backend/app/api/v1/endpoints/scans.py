from typing import Any
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid

from app.api import deps
from app.models.user import User
from app.models.scan import Scan, ScanStatus
from app.services.storage import storage_service
from app.tasks import process_scan_task

router = APIRouter()


@router.post("/analyze")
async def analyze_scan(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """Upload an image and run real AI inference via Celery task."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    # 1. Save uploaded file
    file_path = storage_service.save_upload(file)

    # 2. Create Scan record
    scan = Scan(
        user_id=current_user.id,
        image_url=f"/api/v1/scans/image/{os.path.basename(file_path)}",
        status=ScanStatus.PENDING,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # 3. Trigger Celery Task
    # For full functionality in this local dev environment (where a separate celery worker
    # process might not be actively running), we can gracefully fallback.
    try:
        process_scan_task.delay(
            str(scan.id), file_path, {"name": current_user.full_name}
        )
    except Exception as e:
        print(f"Celery failed (is Redis running?): {e}")
        # Fallback to sync processing if broker is down (useful for testing)
        process_scan_task(str(scan.id), file_path, {"name": current_user.full_name})

    return {"id": str(scan.id), "status": scan.status, "message": "Analysis queued"}


@router.get("/{scan_id}")
async def get_scan_result(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve a specific scan and its prediction."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = (
        select(Scan).options(selectinload(Scan.predictions)).where(Scan.id == scan_id)
    )
    result = await db.execute(stmt)
    scan = result.scalar_one_or_none()

    if not scan or scan.user_id != current_user.id:
        raise HTTPException(404, "Scan not found")

    prediction = scan.predictions[0] if scan.predictions else None

    return {
        "id": str(scan.id),
        "image_url": scan.image_url,
        "status": scan.status,
        "created_at": scan.created_at,
        "prediction": {
            "condition": prediction.condition,
            "confidence": prediction.confidence,
            "severity": prediction.severity,
            "ai_recommendation": prediction.ai_recommendation,
        }
        if prediction
        else None,
    }


@router.get("/image/{filename}")
async def get_image(filename: str) -> Any:
    """Serve uploaded images and heatmaps."""
    file_path = os.path.join(storage_service.upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(404, "Image not found")
    return FileResponse(file_path)

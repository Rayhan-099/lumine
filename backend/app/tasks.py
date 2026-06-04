from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.prediction import Prediction
from app.services.inference import inference_service
from app.services.llm import get_llm_provider
import asyncio
import os
import uuid


# Helper to run async code in Celery synchronous tasks
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3)
def process_scan_task(self, scan_id: str, image_path: str, user_profile: dict = None):
    """
    Celery task that runs the AI inference pipeline, generates Grad-CAM,
    and fetches an LLM report.
    """

    async def _process():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select

            # Fetch the scan
            stmt = select(Scan).where(Scan.id == scan_id)
            result = await db.execute(stmt)
            scan = result.scalar_one_or_none()

            if not scan:
                return

            try:
                # 1. Inference Prediction
                prediction_result = inference_service.predict(image_path)

                # 2. Grad-CAM Visualization
                upload_dir = os.path.dirname(image_path)
                heatmap_path = inference_service.generate_explainability(
                    image_path,
                    class_idx=prediction_result["class_idx"],
                    output_dir=upload_dir,
                )

                # 3. LLM Report Generation
                llm = get_llm_provider()
                report = await llm.generate_report(
                    condition=prediction_result["condition"],
                    confidence=prediction_result["confidence"],
                    severity=prediction_result["severity"],
                    user_profile=user_profile,
                )

                # 4. Save Prediction
                prediction = Prediction(
                    scan_id=scan.id,
                    condition=prediction_result["condition"],
                    confidence=prediction_result["confidence"],
                    severity=prediction_result["severity"],
                    ai_recommendation=report,
                )
                db.add(prediction)

                # Update Scan status and heatmap URL
                scan.status = ScanStatus.COMPLETED
                scan.image_url = f"/api/v1/scans/image/{os.path.basename(heatmap_path)}"

                await db.commit()

            except Exception as exc:
                print(f"Error in process_scan_task: {exc}")
                scan.status = ScanStatus.FAILED
                await db.commit()
                # Retry on failure (e.g., LLM network error)
                raise self.retry(exc=exc, countdown=5)

    run_async(_process())

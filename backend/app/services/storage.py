import os
import shutil
import uuid
from fastapi import UploadFile
from app.core.config import settings


class StorageService:
    def __init__(self):
        # Local fallback for S3/R2
        self.upload_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../uploads")
        )
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_upload(self, file: UploadFile) -> str:
        """Saves file locally and returns absolute path. (Mocking S3 upload)"""
        filename = f"{uuid.uuid4()}-{file.filename}"
        file_path = os.path.join(self.upload_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path


storage_service = StorageService()

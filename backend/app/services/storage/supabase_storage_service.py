"""Supabase Cloud Object Storage service with local file fallback."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import httpx
from structlog import get_logger

from app.core.settings import ApplicationSettings

logger = get_logger(__name__)


class SupabaseStorageService:
    """Manages cloud artifact storage via Supabase Storage REST API."""

    def __init__(self, settings: ApplicationSettings) -> None:
        self._settings = settings
        self._supabase_url = (settings.supabase_url or "").rstrip("/")
        self._service_key = settings.supabase_service_role_key or settings.supabase_anon_key or ""
        self._bucket = settings.supabase_storage_bucket or "workflow-artifacts"
        self._local_storage_dir = Path("./storage/artifacts")
        self._local_storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_cloud_enabled(self) -> bool:
        """Return True if Supabase Cloud storage is configured."""
        return bool(self._supabase_url and self._service_key)

    async def upload_artifact(
        self,
        workflow_id: str,
        filename: str,
        content: bytes,
        content_type: str = "text/markdown",
    ) -> str:
        """Upload a workflow artifact file to Supabase or local storage.

        Args:
            workflow_id: The UUID of the workflow.
            filename: Target file name (e.g. 'deliverable.md').
            content: Raw byte payload.
            content_type: MIME type of the payload.

        Returns:
            str: Public or relative access URL of the stored artifact.
        """
        file_path = f"{workflow_id}/{filename}"

        if not self.is_cloud_enabled:
            # Local disk storage fallback
            target_file = self._local_storage_dir / workflow_id / filename
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_bytes(content)
            logger.info("Saved artifact to local disk", path=str(target_file))
            return f"/storage/artifacts/{file_path}"

        # Cloud Supabase Storage REST API upload
        upload_url = f"{self._supabase_url}/storage/v1/object/{self._bucket}/{file_path}"
        headers = {
            "Authorization": f"Bearer {self._service_key}",
            "apikey": self._service_key,
            "Content-Type": content_type,
            "x-upsert": "true",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(upload_url, content=content, headers=headers)
            if response.status_code not in (200, 201):
                logger.error(
                    "Supabase storage upload failed, falling back to local",
                    status_code=response.status_code,
                    body=response.text,
                )
                target_file = self._local_storage_dir / workflow_id / filename
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_bytes(content)
                return f"/storage/artifacts/{file_path}"

        logger.info("Uploaded artifact to Supabase Storage", bucket=self._bucket, path=file_path)
        return f"{self._supabase_url}/storage/v1/object/public/{self._bucket}/{file_path}"

    async def get_download_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Generate a secure presigned download URL for an artifact.

        Args:
            file_path: Path in bucket (e.g. 'wf_123/report.md').
            expires_in: Time-to-live in seconds.

        Returns:
            str: Presigned download URL.
        """
        if not self.is_cloud_enabled:
            return f"/storage/artifacts/{file_path}"

        sign_url = f"{self._supabase_url}/storage/v1/object/sign/{self._bucket}/{file_path}"
        headers = {
            "Authorization": f"Bearer {self._service_key}",
            "apikey": self._service_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(sign_url, json={"expiresIn": expires_in}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                signed_path = data.get("signedURL", "")
                return f"{self._supabase_url}/storage/v1{signed_path}"

        return f"{self._supabase_url}/storage/v1/object/public/{self._bucket}/{file_path}"

    async def delete_artifact(self, file_path: str) -> bool:
        """Delete an artifact from Supabase or local storage."""
        if not self.is_cloud_enabled:
            target_file = self._local_storage_dir / file_path
            if target_file.exists():
                target_file.unlink()
                return True
            return False

        delete_url = f"{self._supabase_url}/storage/v1/object/{self._bucket}"
        headers = {
            "Authorization": f"Bearer {self._service_key}",
            "apikey": self._service_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                "DELETE",
                delete_url,
                json={"prefixes": [file_path]},
                headers=headers,
            )
            return response.status_code in (200, 204)

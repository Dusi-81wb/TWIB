import pytest
from app.core.settings import ApplicationSettings
from app.services.storage.supabase_storage_service import SupabaseStorageService

@pytest.mark.asyncio
async def test_storage_fallback_when_unconfigured():
    settings = ApplicationSettings(supabase_url="")
    storage = SupabaseStorageService(settings)
    assert not storage.is_cloud_enabled

    url = await storage.upload_artifact(
        workflow_id="wf_test_123",
        filename="report.md",
        content=b"# Market Analysis\nContent here",
        content_type="text/markdown",
    )
    assert url.startswith("/storage/artifacts/")

    # Test download url fallback
    download_url = await storage.get_download_url("wf_test_123/report.md")
    assert download_url == "/storage/artifacts/wf_test_123/report.md"

    # Test delete fallback
    deleted = await storage.delete_artifact("wf_test_123/report.md")
    assert deleted is True

def test_storage_cloud_enabled():
    settings = ApplicationSettings(
        supabase_url="https://xyzproject.supabase.co",
        supabase_service_role_key="service-role-key-test",
    )
    storage = SupabaseStorageService(settings)
    assert storage.is_cloud_enabled

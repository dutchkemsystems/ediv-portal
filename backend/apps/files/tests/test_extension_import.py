"""Extension Plan Feature A tests: import formats endpoint, size limits, async import flag."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.files.models import File
from apps.files.services.import_export_service import ImportExportService

User = get_user_model()


class FileImportFormatsTest(APITestCase):
    """GET /api/files/import/formats/ lists supported formats and size limits."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="fmt@ediv.gov.ng",
            password="TestPass123!@#",
            first_name="Fmt",
            last_name="User",
            role="SYSADMIN",
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    def test_formats_endpoint_lists_extension_formats(self):
        response = self.client.get("/api/files/import/formats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {item["format"] for item in response.data["formats"]}
        for fmt in (
            "doc",
            "docx",
            "xls",
            "xlsx",
            "pdf",
            "jpeg",
            "png",
            "csv",
            "txt",
            "access",
            "mp3",
            "mp4",
        ):
            self.assertIn(fmt, codes)
        mp4 = next(item for item in response.data["formats"] if item["format"] == "mp4")
        self.assertEqual(mp4["max_size_mb"], 200)


class FileImportSizeLimitTest(APITestCase):
    """Oversized uploads are rejected with 413 before import."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="sizelimit@ediv.gov.ng",
            password="TestPass123!@#",
            first_name="Size",
            last_name="Limit",
            role="SYSADMIN",
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    def test_import_rejects_above_limit(self):
        with patch.dict(ImportExportService.MAX_UPLOAD_SIZE_MB, {"txt": 0}):
            upload = SimpleUploadedFile("note.txt", b"hello", content_type="text/plain")
            response = self.client.post(
                "/api/files/import/", {"file": upload, "format": "txt"}
            )
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertEqual(File.objects.count(), 0)

    def test_import_auto_detect_respects_limit(self):
        with patch.dict(ImportExportService.MAX_UPLOAD_SIZE_MB, {"mp4": 0}):
            upload = SimpleUploadedFile("clip.mp4", b"123", content_type="video/mp4")
            response = self.client.post("/api/files/import/", {"file": upload})
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertEqual(File.objects.count(), 0)

    def test_within_limit_imports_sync(self):
        upload = SimpleUploadedFile("note.txt", b"hello", content_type="text/plain")
        response = self.client.post("/api/files/import/", {"file": upload})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(File.objects.count(), 1)


class FileImportAsyncFlagTest(APITestCase):
    """FILES_ASYNC_IMPORT gates the queued (202) path."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="async@ediv.gov.ng",
            password="TestPass123!@#",
            first_name="Async",
            last_name="User",
            role="SYSADMIN",
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    @override_settings(FILES_ASYNC_IMPORT=True)
    def test_async_flag_returns_202_and_imports(self):
        upload = SimpleUploadedFile(
            "note2.txt", b"hello async", content_type="text/plain"
        )
        response = self.client.post("/api/files/import/", {"file": upload})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # CELERY_TASK_ALWAYS_EAGER in tests -> task ran synchronously
        self.assertEqual(File.objects.count(), 1)

    def test_flag_off_imports_sync(self):
        upload = SimpleUploadedFile(
            "note3.txt", b"hello sync", content_type="text/plain"
        )
        response = self.client.post("/api/files/import/", {"file": upload})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(File.objects.count(), 1)

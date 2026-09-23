import mimetypes
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import connection
from django.http import FileResponse, JsonResponse
from django.urls import include, path, re_path
from django.utils.http import http_date

# Cache hashed frontend assets (JS/CSS with content hashes) for 1 year
_ASSET_CACHE_SECONDS = 365 * 24 * 3600
_CONTENT_TYPES = {
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".webp": "image/webp",
    ".map": "application/json",
    ".html": "text/html",
    ".txt": "text/plain",
}


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)


def wake_up(request):
    """Lightweight endpoint for external cron services to keep Render free tier alive."""
    return JsonResponse({"status": "ok", "message": "Service is awake"})


def api_health(request):
    """Fast API health check - no DB query, used by frontend to detect cold start."""
    return JsonResponse({"status": "ok"})


def debug_files(request):
    """Debug endpoint - only available when DEBUG=True. Returns existence checks only."""
    if not settings.DEBUG:
        return JsonResponse({"error": "Not Found"}, status=404)
    base = settings.BASE_DIR
    results = {}
    for name, dir_path in [
        ("BASE_DIR", str(base)),
        ("frontend_dist_1", os.path.join(base, "..", "frontend", "dist")),
        ("frontend_dist_2", os.path.join(base, "frontend", "dist")),
        ("staticfiles", os.path.join(base, "staticfiles")),
        ("static", os.path.join(base, "static")),
    ]:
        results[name] = {"exists": os.path.isdir(dir_path)}
    return JsonResponse(results)


def _get_frontend_dirs():
    """Return possible locations for the frontend build output."""
    return [
        os.path.join(settings.BASE_DIR, "..", "frontend", "dist"),
        os.path.join(settings.BASE_DIR, "frontend", "dist"),
        os.path.join(settings.STATIC_ROOT, "frontend"),
    ]


def serve_frontend(request, path=""):
    """Serve the React frontend for all non-API routes.

    - Static assets (JS/CSS/images) are served directly with long cache headers.
    - All other routes serve index.html for client-side routing (SPA fallback).
    """
    full_path = request.path or ""
    if full_path.startswith("/api/"):
        return JsonResponse({"error": "Not Found", "path": full_path}, status=404)

    for frontend_dir in _get_frontend_dirs():
        if path:
            file_path = os.path.join(frontend_dir, path)
            if os.path.isfile(file_path):
                ext = os.path.splitext(path)[1].lower()
                content_type = (
                    _CONTENT_TYPES.get(ext)
                    or mimetypes.guess_type(path)[0]
                    or "application/octet-stream"
                )
                response = FileResponse(
                    open(file_path, "rb"), content_type=content_type
                )
                # Long-cache hashed assets (Vite adds content hash to filenames)
                if ext in (
                    ".js",
                    ".css",
                    ".woff",
                    ".woff2",
                    ".ttf",
                    ".png",
                    ".jpg",
                    ".svg",
                    ".webp",
                ):
                    response["Cache-Control"] = (
                        f"public, max-age={_ASSET_CACHE_SECONDS}, immutable"
                    )
                    response["Expires"] = http_date(_ASSET_CACHE_SECONDS)
                return response

        # SPA fallback — serve index.html for all non-asset routes
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(open(index_path, "rb"), content_type="text/html")

    return JsonResponse(
        {"error": "Frontend not built. Run: cd frontend && npm run build"}, status=404
    )


urlpatterns = [
    path("health/", health_check),
    path("api/health/", api_health),
    path("wake/", wake_up),
    path("debug/files/", debug_files),
    path("admin/", admin.site.urls),
    # API v1 (versioned)
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/schools/", include("apps.schools.urls")),
    path("api/v1/staff/", include("apps.staff.urls")),
    path("api/v1/students/", include("apps.students.urls")),
    path("api/v1/academics/", include("apps.academics.urls")),
    path("api/v1/attendance/", include("apps.attendance.urls")),
    path("api/v1/finance/", include("apps.finance.urls")),
    path("api/v1/communication/", include("apps.communication.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/hr/", include("apps.hr.urls")),
    path("api/v1/registry/", include("apps.registry.urls")),
    path("api/v1/departments/", include("apps.departments.urls")),
    path("api/v1/files/", include("apps.files.urls")),
    path("api/v1/workflows/", include("apps.workflows.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/inspection/", include("apps.inspection.urls")),
    path("api/v1/co-curricular/", include("apps.co_curricular.urls")),
    path("api/v1/french/", include("apps.french.urls")),
    path("api/v1/infrastructure/", include("apps.infrastructure.urls")),
    path("api/v1/library/", include("apps.library.urls")),
    path("api/v1/e-learning/", include("apps.e_learning.urls")),
    path("api/v1/wellness/", include("apps.wellness.urls")),
    path("api/v1/alumni/", include("apps.alumni.urls")),
    path("api/v1/assets/", include("apps.assets.urls")),
    path("api/v1/discipline/", include("apps.discipline.urls")),
    path("api/v1/timetable/", include("apps.timetable.urls")),
    path("api/v1/transport/", include("apps.transport.urls")),
    path("api/v1/cpd/", include("apps.cpd.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/data-import-export/", include("apps.data_import_export.urls")),
    path("api/v1/access-databases/", include("apps.data_import_export.urls_access")),
    path("api/v1/mail-workflow/", include("apps.mail_workflow.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/v1/parent-teacher/", include("apps.parent_teacher.urls")),
    path("api/v1/predictive/", include("apps.predictive_analytics.urls")),
    path("api/v1/chatbot/", include("apps.chatbot.urls")),
    path("api/v1/blockchain-certs/", include("apps.blockchain_cert.urls")),
    path("api/v1/multilingual/", include("apps.multilingual.urls")),
    path("api/v1/gamification/", include("apps.gamification.urls")),
    path("api/v1/push-notifications/", include("apps.push_notifications.urls")),
    path("api/v1/iot/", include("apps.iot_dashboard.urls")),
    path("api/v1/benchmarking/", include("apps.benchmarking.urls")),
    path("api/v1/report-card-gen/", include("apps.report_card_gen.urls")),
    # Unversioned (backward compatible — DEPRECATED, will be removed in v2)
    # All existing /api/ routes still work but /api/v1/ is preferred.
    path("api/users/", include("apps.users.urls")),
    path("api/schools/", include("apps.schools.urls")),
    path("api/staff/", include("apps.staff.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/academics/", include("apps.academics.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/finance/", include("apps.finance.urls")),
    path("api/communication/", include("apps.communication.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/hr/", include("apps.hr.urls")),
    path("api/registry/", include("apps.registry.urls")),
    path("api/departments/", include("apps.departments.urls")),
    path("api/files/", include("apps.files.urls")),
    path("api/workflows/", include("apps.workflows.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/inspection/", include("apps.inspection.urls")),
    path("api/co-curricular/", include("apps.co_curricular.urls")),
    path("api/french/", include("apps.french.urls")),
    path("api/infrastructure/", include("apps.infrastructure.urls")),
    path("api/library/", include("apps.library.urls")),
    path("api/e-learning/", include("apps.e_learning.urls")),
    path("api/wellness/", include("apps.wellness.urls")),
    path("api/alumni/", include("apps.alumni.urls")),
    path("api/assets/", include("apps.assets.urls")),
    path("api/discipline/", include("apps.discipline.urls")),
    path("api/timetable/", include("apps.timetable.urls")),
    path("api/transport/", include("apps.transport.urls")),
    path("api/cpd/", include("apps.cpd.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/data-import-export/", include("apps.data_import_export.urls")),
    path("api/access-databases/", include("apps.data_import_export.urls_access")),
    path("api/mail-workflow/", include("apps.mail_workflow.urls")),
    path("api/audit/", include("apps.audit.urls")),
    path("api/parent-teacher/", include("apps.parent_teacher.urls")),
    path("api/predictive/", include("apps.predictive_analytics.urls")),
    path("api/chatbot/", include("apps.chatbot.urls")),
    path("api/blockchain-certs/", include("apps.blockchain_cert.urls")),
    path("api/multilingual/", include("apps.multilingual.urls")),
    path("api/gamification/", include("apps.gamification.urls")),
    path("api/push-notifications/", include("apps.push_notifications.urls")),
    path("api/iot/", include("apps.iot_dashboard.urls")),
    path("api/benchmarking/", include("apps.benchmarking.urls")),
    path("api/report-card-gen/", include("apps.report_card_gen.urls")),
    # Catch-all for SPA routing - must be last.
    # `.*` already captures empty path for /; do NOT pass a {"path": ""} default
    # kwarg - Django's default_kwargs.update() would clobber the captured group
    # and make every route (incl. /assets/*.js) fall through to the SPA fallback.
    re_path(r"^(?P<path>.*)$", serve_frontend),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, FileResponse
from django.db import connection
import os


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)


def serve_frontend(request, path=''):
    """Serve the React frontend for all non-API routes"""
    frontend_dir = os.path.join(settings.BASE_DIR, 'static', 'frontend')

    # Try to serve the specific file first
    if path:
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(open(file_path, 'rb'))

    # For all other routes, serve index.html (SPA fallback)
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.isfile(index_path):
        return FileResponse(open(index_path, 'rb'))

    return JsonResponse({'error': 'Frontend not built'}, status=404)


urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/staff/', include('apps.staff.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/academics/', include('apps.academics.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/communication/', include('apps.communication.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/hr/', include('apps.hr.urls')),
    path('api/registry/', include('apps.registry.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/files/', include('apps.files.urls')),
    path('api/workflows/', include('apps.workflows.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/inspection/', include('apps.inspection.urls')),
    path('api/co-curricular/', include('apps.co_curricular.urls')),
    path('api/french/', include('apps.french.urls')),
    path('api/infrastructure/', include('apps.infrastructure.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/e-learning/', include('apps.e_learning.urls')),
    path('api/wellness/', include('apps.wellness.urls')),
    path('api/alumni/', include('apps.alumni.urls')),
    path('api/assets/', include('apps.assets.urls')),
    path('api/discipline/', include('apps.discipline.urls')),
    path('api/timetable/', include('apps.timetable.urls')),
    path('api/transport/', include('apps.transport.urls')),
    path('api/cpd/', include('apps.cpd.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/audit/', include('apps.audit.urls')),
    path('api/parent-teacher/', include('apps.parent_teacher.urls')),
    # Serve static frontend files
    re_path(r'^(?P<path>.*)$', serve_frontend, {'path': ''}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

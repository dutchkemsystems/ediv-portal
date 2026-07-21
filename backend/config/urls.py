from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)


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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

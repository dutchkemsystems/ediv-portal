from django.contrib import admin
from .models import DisciplinaryIncident, BehaviorPlan


@admin.register(DisciplinaryIncident)
class DisciplinaryIncidentAdmin(admin.ModelAdmin):
    list_display = ['student', 'incident_type', 'severity', 'status', 'incident_date']
    list_filter = ['incident_type', 'severity', 'status']
    search_fields = ['title', 'student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'reported_by']


@admin.register(BehaviorPlan)
class BehaviorPlanAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'created_by']

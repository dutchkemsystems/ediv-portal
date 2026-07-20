from django.contrib import admin
from .models import Activity, ActivityParticipant, Competition, CompetitionEntry


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'activity_type', 'coordinator', 'is_active']
    list_filter = ['school', 'activity_type', 'is_active']
    search_fields = ['name', 'description']
    raw_id_fields = ['school', 'coordinator']


@admin.register(ActivityParticipant)
class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = ['activity', 'student', 'role', 'joined_date', 'is_active']
    list_filter = ['is_active']
    raw_id_fields = ['activity', 'student']


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'competition_type', 'organizer', 'start_date', 'end_date', 'is_active']
    list_filter = ['competition_type', 'is_active']
    search_fields = ['name', 'organizer']


@admin.register(CompetitionEntry)
class CompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ['competition', 'student', 'school', 'position', 'score']
    list_filter = ['competition', 'school']
    raw_id_fields = ['competition', 'student', 'school']

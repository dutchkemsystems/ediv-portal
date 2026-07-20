from django.contrib import admin
from .models import FrenchProgram, FrenchClub, FrenchClubMember, FrenchCompetition


@admin.register(FrenchProgram)
class FrenchProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'duration_weeks', 'is_active']
    list_filter = ['level', 'is_active']
    search_fields = ['name', 'description']


@admin.register(FrenchClub)
class FrenchClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'coordinator', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name']
    raw_id_fields = ['school', 'coordinator']


@admin.register(FrenchClubMember)
class FrenchClubMemberAdmin(admin.ModelAdmin):
    list_display = ['club', 'student', 'role', 'joined_date', 'is_active']
    list_filter = ['is_active']
    raw_id_fields = ['club', 'student']


@admin.register(FrenchCompetition)
class FrenchCompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'date', 'organizer', 'is_active']
    list_filter = ['level', 'is_active']
    search_fields = ['name', 'organizer']

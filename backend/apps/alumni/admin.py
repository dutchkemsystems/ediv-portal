from django.contrib import admin
from .models import AlumniMember, AlumniEvent, AlumniDonation


@admin.register(AlumniMember)
class AlumniMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'graduation_year', 'current_occupation', 'is_active_alumni']
    list_filter = ['school', 'graduation_year', 'is_active_alumni', 'is_donor']
    search_fields = ['user__first_name', 'user__last_name']
    raw_id_fields = ['user', 'school']


@admin.register(AlumniEvent)
class AlumniEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_date', 'venue', 'organizer', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    raw_id_fields = ['organizer']


@admin.register(AlumniDonation)
class AlumniDonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'amount', 'purpose', 'donation_date', 'receipt_number']
    search_fields = ['receipt_number', 'purpose']
    raw_id_fields = ['donor']

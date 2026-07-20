from rest_framework import serializers
from .models import AlumniMember, AlumniEvent, AlumniDonation


class AlumniMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AlumniMember
        fields = ['id', 'user', 'user_name', 'school', 'school_name', 'graduation_year',
                  'class_name', 'current_occupation', 'company', 'location', 'achievements',
                  'is_active_alumni', 'is_donor', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    
    def get_school_name(self, obj):
        return obj.school.name


class AlumniEventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AlumniEvent
        fields = ['id', 'name', 'description', 'event_date', 'venue', 'organizer',
                  'organizer_name', 'max_attendees', 'registration_deadline', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_organizer_name(self, obj):
        return obj.organizer.get_full_name()


class AlumniDonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AlumniDonation
        fields = ['id', 'donor', 'donor_name', 'amount', 'purpose', 'donation_date',
                  'receipt_number', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_donor_name(self, obj):
        return obj.donor.user.get_full_name()


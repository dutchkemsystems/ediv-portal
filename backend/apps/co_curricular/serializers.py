from rest_framework import serializers
from .models import Activity, ActivityParticipant, Competition, CompetitionEntry


class ActivityParticipantSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityParticipant
        fields = ['id', 'activity', 'student', 'student_name', 'role', 'joined_date', 'is_active']
        read_only_fields = ['id']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class ActivitySerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()
    participants = ActivityParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = ['id', 'school', 'school_name', 'name', 'activity_type', 'description',
                  'coordinator', 'coordinator_name', 'meeting_schedule', 'meeting_venue',
                  'max_participants', 'is_active', 'participants', 'participant_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_coordinator_name(self, obj):
        if obj.coordinator:
            return obj.coordinator.get_full_name()
        return None
    
    def get_participant_count(self, obj):
        return obj.participants.filter(is_active=True).count()


class ActivityListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = ['id', 'school_name', 'name', 'activity_type', 'is_active']
    
    def get_school_name(self, obj):
        return obj.school.name


class CompetitionEntrySerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CompetitionEntry
        fields = ['id', 'competition', 'student', 'student_name', 'school', 'school_name',
                  'registration_date', 'category', 'position', 'score', 'certificate']
        read_only_fields = ['id']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_school_name(self, obj):
        return obj.school.name


class CompetitionSerializer(serializers.ModelSerializer):
    entries = CompetitionEntrySerializer(many=True, read_only=True)
    entry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Competition
        fields = ['id', 'name', 'competition_type', 'description', 'organizer', 'venue',
                  'start_date', 'end_date', 'registration_deadline', 'max_participants',
                  'is_active', 'entries', 'entry_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_entry_count(self, obj):
        return obj.entries.count()


class CompetitionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'name', 'competition_type', 'start_date', 'end_date', 'is_active']


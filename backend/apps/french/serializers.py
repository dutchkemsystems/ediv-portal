from rest_framework import serializers
from .models import FrenchProgram, FrenchClub, FrenchClubMember, FrenchCompetition


class FrenchProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrenchProgram
        fields = ['id', 'name', 'description', 'level', 'duration_weeks', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FrenchClubMemberSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FrenchClubMember
        fields = ['id', 'club', 'student', 'student_name', 'role', 'joined_date', 'is_active']
        read_only_fields = ['id']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class FrenchClubSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    coordinator_name = serializers.SerializerMethodField()
    members = FrenchClubMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = FrenchClub
        fields = ['id', 'school', 'school_name', 'name', 'coordinator', 'coordinator_name',
                  'meeting_schedule', 'meeting_venue', 'is_active', 'members', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_coordinator_name(self, obj):
        if obj.coordinator:
            return obj.coordinator.get_full_name()
        return None


class FrenchCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrenchCompetition
        fields = ['id', 'name', 'description', 'level', 'venue', 'date', 'organizer',
                  'max_participants', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


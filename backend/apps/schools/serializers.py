from rest_framework import serializers
from .models import School, SchoolAcademicYear


class SchoolAcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolAcademicYear
        fields = ['id', 'year', 'start_date', 'end_date', 'is_current', 'created_at']
        read_only_fields = ['id', 'created_at']


class SchoolSerializer(serializers.ModelSerializer):
    principal_name = serializers.SerializerMethodField()
    vice_principal_name = serializers.SerializerMethodField()
    academic_years = SchoolAcademicYearSerializer(many=True, read_only=True)
    occupancy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'school_type', 'lga', 'address', 'phone', 'email',
                  'website', 'principal', 'principal_name', 'vice_principal', 'vice_principal_name',
                  'established_date', 'student_capacity', 'current_enrollment', 'number_of_classrooms',
                  'number_of_staff', 'has_science_lab', 'has_computer_lab', 'has_library',
                  'has_sports_field', 'latitude', 'longitude', 'is_active', 'occupancy_rate',
                  'academic_years', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_principal_name(self, obj):
        if obj.principal:
            return obj.principal.get_full_name()
        return None
    
    def get_vice_principal_name(self, obj):
        if obj.vice_principal:
            return obj.vice_principal.get_full_name()
        return None


class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'school_type', 'lga', 'current_enrollment', 'is_active']


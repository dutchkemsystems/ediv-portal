from rest_framework import serializers
from .models import StudentAttendance, StaffAttendance, AttendanceSummary


class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAttendance
        fields = ['id', 'student', 'student_name', 'date', 'status', 'time_in', 'time_out',
                  'remark', 'recorded_by', 'recorded_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.get_full_name()
        return None


class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffAttendance
        fields = ['id', 'staff', 'staff_name', 'date', 'status', 'time_in', 'time_out',
                  'overtime_hours', 'remark', 'recorded_by', 'recorded_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_staff_name(self, obj):
        return obj.staff.user.get_full_name()
    
    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.get_full_name()
        return None


class AttendanceSummarySerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSummary
        fields = ['id', 'school', 'school_name', 'academic_year', 'term',
                  'total_school_days', 'total_present', 'total_absent', 'total_late',
                  'attendance_rate', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name


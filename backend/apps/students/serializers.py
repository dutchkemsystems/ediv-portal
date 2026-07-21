from rest_framework import serializers
from .models import Student, StudentParent, StudentMedicalRecord
from apps.users.models import User
from apps.users.serializers import UserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    full_name = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    school_name = serializers.SerializerMethodField()
    class_name_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'user_id', 'full_name', 'admission_number', 'school',
                  'school_name', 'class_name', 'class_name_display', 'date_of_birth',
                  'gender', 'blood_group', 'nationality', 'state_of_origin', 'lga_of_origin',
                  'residential_address', 'parent_name', 'parent_phone', 'parent_email',
                  'parent_occupation', 'parent_address', 'guardian_name', 'guardian_phone',
                  'medical_conditions', 'allergies', 'emergency_contact_name',
                  'emergency_contact_phone', 'previous_school', 'admission_date',
                  'status', 'profile_photo', 'is_boarding', 'bus_route', 'age',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_class_name_display(self, obj):
        if obj.class_name:
            return obj.class_name.name
        return None


class StudentListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    class_name_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'full_name', 'admission_number', 'school_name', 'class_name_display',
                  'gender', 'status']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_class_name_display(self, obj):
        if obj.class_name:
            return obj.class_name.name
        return None


class StudentParentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentParent
        fields = ['id', 'student', 'student_name', 'user', 'parent_name', 'relation', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_parent_name(self, obj):
        return obj.user.get_full_name()


class StudentMedicalRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentMedicalRecord
        fields = ['id', 'student', 'student_name', 'record_date', 'condition', 'description',
                  'treatment', 'medication', 'doctor_name', 'hospital', 'follow_up_date',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

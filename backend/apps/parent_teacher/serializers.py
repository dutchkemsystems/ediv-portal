from rest_framework import serializers
from .models import PTAMeeting, ParentTeacherMessage, StudentReportShare


class PTAMeetingSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    organized_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PTAMeeting
        fields = ['id', 'title', 'meeting_type', 'description', 'school', 'school_name',
                  'scheduled_date', 'scheduled_time', 'duration_minutes', 'venue',
                  'status', 'organized_by', 'organized_by_name', 'minutes',
                  'decisions', 'follow_up_actions', 'is_mandatory',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None

    def get_organized_by_name(self, obj):
        if obj.organized_by:
            return obj.organized_by.get_full_name()
        return None


class PTAMeetingListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = PTAMeeting
        fields = ['id', 'title', 'meeting_type', 'school_name', 'scheduled_date',
                  'scheduled_time', 'venue', 'status', 'is_mandatory']

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None


class ParentTeacherMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = ParentTeacherMessage
        fields = ['id', 'sender', 'sender_name', 'recipient', 'recipient_name',
                  'student', 'student_name', 'category', 'subject', 'body',
                  'is_read', 'read_at', 'parent_reply', 'parent_replied_at',
                  'is_urgent', 'created_at']
        read_only_fields = ['id', 'created_at', 'read_at', 'parent_replied_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_recipient_name(self, obj):
        return obj.recipient.get_full_name()

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class ParentTeacherMessageListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = ParentTeacherMessage
        fields = ['id', 'sender_name', 'student_name', 'category', 'subject',
                  'is_read', 'is_urgent', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class StudentReportShareSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    shared_by_name = serializers.SerializerMethodField()
    shared_with_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentReportShare
        fields = ['id', 'student', 'student_name', 'shared_by', 'shared_by_name',
                  'shared_with', 'shared_with_name', 'report_type', 'academic_year',
                  'term', 'comments', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_shared_by_name(self, obj):
        return obj.shared_by.get_full_name()

    def get_shared_with_name(self, obj):
        return obj.shared_with.get_full_name()


class StudentReportShareListSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentReportShare
        fields = ['id', 'student_name', 'report_type', 'academic_year', 'is_read', 'created_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

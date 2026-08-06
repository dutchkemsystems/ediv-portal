from rest_framework import serializers
from .models import ReportCardTemplate, GeneratedReportCard, ReportCardShareLog


class ReportCardTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCardTemplate
        fields = ['id', 'name', 'school_type', 'header_text', 'footer_text',
                  'include_photo', 'include_signature', 'include_remarks',
                  'include_class_average', 'include_position', 'custom_fields',
                  'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class GeneratedReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedReportCard
        fields = ['id', 'student', 'student_name', 'school', 'school_name',
                  'template', 'academic_session', 'term', 'total_score',
                  'average_score', 'class_average', 'position', 'total_students',
                  'remark', 'teacher_remark', 'principal_remark', 'status',
                  'pdf_file', 'pdf_url', 'error_message', 'generated_by',
                  'generated_at', 'created_at']
        read_only_fields = ['id', 'total_score', 'average_score', 'position',
                           'total_students', 'remark', 'status', 'error_message',
                           'generated_at', 'created_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student else None

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None


class ReportCardShareLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCardShareLog
        fields = ['id', 'report_card', 'channel', 'recipient', 'shared_by',
                  'shared_at', 'status']
        read_only_fields = ['id', 'shared_at']


class GenerateReportCardSerializer(serializers.Serializer):
    student_ids = serializers.ListField(child=serializers.IntegerField())
    academic_session = serializers.CharField(max_length=20)
    term = serializers.CharField(max_length=20)
    template_id = serializers.IntegerField(required=False, allow_null=True)


class ShareReportCardSerializer(serializers.Serializer):
    report_card_id = serializers.IntegerField()
    channel = serializers.ChoiceField(choices=['EMAIL', 'WHATSAPP', 'SMS', 'DOWNLOAD'])
    recipient = serializers.CharField(max_length=200)

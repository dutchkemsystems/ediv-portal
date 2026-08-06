from rest_framework import serializers
from .models import Certificate, CertificateVerification


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    issued_by_name = serializers.SerializerMethodField()
    can_verify = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'student', 'student_name', 'school', 'school_name',
                  'certificate_type', 'title', 'description', 'issued_date',
                  'expiry_date', 'cert_hash', 'previous_hash', 'nonce',
                  'block_data', 'issued_by', 'issued_by_name', 'principal_signature',
                  'is_revoked', 'revocation_reason', 'verified_count',
                  'can_verify', 'created_at', 'updated_at']
        read_only_fields = ['id', 'cert_hash', 'previous_hash', 'nonce', 'block_data',
                           'verified_count', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student else None

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None

    def get_issued_by_name(self, obj):
        return obj.issued_by.get_full_name() if obj.issued_by else None

    def get_can_verify(self, obj):
        if obj.expiry_date:
            from django.utils import timezone
            return obj.expiry_date >= timezone.now().date() and not obj.is_revoked
        return not obj.is_revoked


class CertificateVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateVerification
        fields = ['id', 'certificate', 'verified_by', 'verification_method',
                  'ip_address', 'is_valid', 'verified_at']
        read_only_fields = ['id', 'verified_at']


class VerifyCertificateRequestSerializer(serializers.Serializer):
    cert_hash = serializers.CharField(max_length=64)
    verified_by = serializers.CharField(max_length=200, required=False, default='Public User')

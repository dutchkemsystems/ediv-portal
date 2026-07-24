from rest_framework import serializers
from .models import (
    Document, Correspondence, Filing, DocumentVersion,
    MemoWorkflow, MemoApproval, MemoCirculation
)


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentVersion
        fields = ['id', 'document', 'version_number', 'content', 'file', 'changes',
                  'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class CorrespondenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correspondence
        fields = ['id', 'document', 'direction', 'sender', 'recipient', 'date_received',
                  'date_sent', 'subject', 'is_urgent', 'requires_response',
                  'response_deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


class FilingSerializer(serializers.ModelSerializer):
    document_reference = serializers.SerializerMethodField()
    filed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Filing
        fields = ['id', 'document', 'document_reference', 'file_code', 'box_number',
                  'shelf_number', 'room', 'filed_by', 'filed_by_name', 'filed_date', 'notes']
        read_only_fields = ['id', 'filed_by']
    
    def get_document_reference(self, obj):
        return obj.document.reference_number
    
    def get_filed_by_name(self, obj):
        return obj.filed_by.get_full_name()


class DocumentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    versions = DocumentVersionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'reference_number', 'title', 'document_type', 'content',
                  'created_by', 'created_by_name', 'department', 'department_name',
                  'status', 'classification', 'version', 'effective_date', 'expiry_date',
                  'versions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at', 'created_by']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None


class DocumentListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'reference_number', 'title', 'document_type', 'created_by_name',
                  'status', 'classification', 'version', 'created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class MemoWorkflowSerializer(serializers.ModelSerializer):
    document_reference = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MemoWorkflow
        fields = ['id', 'document', 'document_reference', 'workflow_type', 'status',
                  'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_document_reference(self, obj):
        return obj.document.reference_number

    def get_created_by_name(self, obj):
        return obj.document.created_by.get_full_name()


class MemoApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.SerializerMethodField()

    class Meta:
        model = MemoApproval
        fields = ['id', 'memo_workflow', 'approver', 'approver_name', 'approval_order',
                  'status', 'comments', 'approved_date']
        read_only_fields = ['id', 'approved_date']

    def get_approver_name(self, obj):
        return obj.approver.get_full_name()


class MemoCirculationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = MemoCirculation
        fields = ['id', 'memo_workflow', 'recipient', 'recipient_name', 'date_sent',
                  'date_acknowledged', 'acknowledgement_notes', 'status']
        read_only_fields = ['id', 'date_sent']

    def get_recipient_name(self, obj):
        return obj.recipient.get_full_name()


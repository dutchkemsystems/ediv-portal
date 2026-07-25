import datetime
from django.db import models as db_models
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from config.security import AuditLogger
from .models import (
    IncomingMail, MailScanRecord, MailAssignment, MailMovement,
    OutgoingMail, OutgoingMailApproval, OutgoingMailMovement,
    SchoolHQCorrespondence, SchoolHQCorrespondenceMovement,
    MailCorrespondence, MailCorrespondenceMovement
)
from .serializers import (
    IncomingMailSerializer, IncomingMailListSerializer,
    MailScanRecordSerializer, MailAssignmentSerializer, MailMovementSerializer,
    OutgoingMailSerializer, OutgoingMailListSerializer, OutgoingMailApprovalSerializer, OutgoingMailMovementSerializer,
    SchoolHQCorrespondenceSerializer, SchoolHQCorrespondenceListSerializer, SchoolHQCorrespondenceMovementSerializer,
    MailCorrespondenceSerializer, MailCorrespondenceListSerializer, MailCorrespondenceMovementSerializer
)

User = get_user_model()


class IncomingMailViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return IncomingMailListSerializer
        return IncomingMailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG', 'PS'):
            return IncomingMail.objects.select_related('received_by', 'department').all()
        return IncomingMail.objects.select_related('received_by', 'department').filter(
            db_models.Q(received_by=user) |
            db_models.Q(assignments__assigned_to=user) |
            db_models.Q(movements__to_person=user)
        ).distinct()

    def perform_create(self, serializer):
        year = datetime.date.today().year
        seq = IncomingMail.objects.filter(mail_number__startswith=f'EDIV/MAIL/{year}').count() + 1
        mail_number = f'EDIV/MAIL/{year}/{seq:04d}'
        mail_obj = serializer.save(mail_number=mail_number, received_by=self.request.user)

        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            resource_type='IncomingMail',
            resource_id=mail_obj.id,
            description=f"Received mail {mail_number}: {mail_obj.subject}",
        )

    @action(detail=True, methods=['post'], url_path='scan')
    def scan_mail(self, request, pk=None):
        mail_obj = self.get_object()
        scan_notes = request.data.get('scan_notes', '')
        attachment_count = int(request.data.get('attachment_count', 0))

        MailScanRecord.objects.create(
            mail=mail_obj, scanned_by=request.user,
            scan_notes=scan_notes, attachment_count=attachment_count,
        )
        mail_obj.status = 'SCANNED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id, description=f"Mail {mail_obj.mail_number} scanned",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} marked as scanned."})

    @action(detail=True, methods=['post'], url_path='classify')
    def classify_mail(self, request, pk=None):
        mail_obj = self.get_object()
        classification = request.data.get('classification', mail_obj.classification)
        subject_category = request.data.get('subject_category', mail_obj.subject_category)
        priority = request.data.get('priority', mail_obj.priority)

        valid_classifications = [c[0] for c in IncomingMail.Classification.choices]
        if classification not in valid_classifications:
            return Response({'error': f'Invalid classification. Choose from: {valid_classifications}'},
                            status=status.HTTP_400_BAD_REQUEST)

        mail_obj.classification = classification
        mail_obj.subject_category = subject_category
        mail_obj.priority = priority
        mail_obj.status = 'CLASSIFIED'
        mail_obj.save(update_fields=['classification', 'subject_category', 'priority', 'status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id, description=f"Mail {mail_obj.mail_number} classified as {classification}",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} classified."})

    @action(detail=True, methods=['post'], url_path='assign')
    def assign_mail(self, request, pk=None):
        mail_obj = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        action_required = request.data.get('action_required', '')
        deadline = request.data.get('deadline')

        if not assigned_to_id:
            return Response({'error': 'assigned_to_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignee = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        assignment = MailAssignment.objects.create(
            mail=mail_obj, assigned_by=request.user, assigned_to=assignee,
            action_required=action_required,
            deadline=deadline if deadline else None,
        )

        mail_obj.status = 'ASSIGNED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id,
            description=f"Mail {mail_obj.mail_number} assigned to {assignee.get_full_name()}",
        )
        return Response(MailAssignmentSerializer(assignment).data)

    @action(detail=True, methods=['post'], url_path='forward')
    def forward_mail(self, request, pk=None):
        mail_obj = self.get_object()
        to_person_id = request.data.get('to_person_id')
        action_label = request.data.get('action', 'Forwarded')
        remarks = request.data.get('remarks', '')

        if not to_person_id:
            return Response({'error': 'to_person_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_person = User.objects.get(id=to_person_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        movement = MailMovement.objects.create(
            mail=mail_obj, from_person=request.user, to_person=to_person,
            action=action_label, remarks=remarks,
        )

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id,
            description=f"Mail {mail_obj.mail_number} forwarded to {to_person.get_full_name()}",
        )
        return Response(MailMovementSerializer(movement).data)

    @action(detail=True, methods=['post'], url_path='respond')
    def respond_to_mail(self, request, pk=None):
        mail_obj = self.get_object()
        response_notes = request.data.get('response_notes', '')

        assignment = MailAssignment.objects.filter(
            mail=mail_obj, assigned_to=request.user
        ).order_by('-assignment_date').first()

        if assignment:
            assignment.status = 'COMPLETED'
            assignment.response_notes = response_notes
            assignment.completed_date = datetime.datetime.now()
            assignment.save(update_fields=['status', 'response_notes', 'completed_date'])

        mail_obj.status = 'RESPONDED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id, description=f"Mail {mail_obj.mail_number} response submitted",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} response recorded."})

    @action(detail=True, methods=['post'], url_path='dispatch')
    def dispatch_mail(self, request, pk=None):
        mail_obj = self.get_object()
        if mail_obj.status not in ('RESPONDED', 'IN_ACTION', 'UNDER_REVIEW'):
            return Response(
                {'error': f'Cannot dispatch mail in {mail_obj.status} status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        mail_obj.status = 'DISPATCHED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id, description=f"Mail {mail_obj.mail_number} dispatched",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} dispatched."})

    @action(detail=True, methods=['post'], url_path='archive')
    def archive_mail(self, request, pk=None):
        mail_obj = self.get_object()
        mail_obj.status = 'ARCHIVED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='IncomingMail',
            resource_id=mail_obj.id, description=f"Mail {mail_obj.mail_number} archived",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} archived."})


class MailAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = MailAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['mail', 'assigned_to', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG', 'PS'):
            return MailAssignment.objects.select_related('mail', 'assigned_by', 'assigned_to').all()
        return MailAssignment.objects.select_related('mail', 'assigned_by', 'assigned_to').filter(
            db_models.Q(assigned_by=user) | db_models.Q(assigned_to=user)
        )


class OutgoingMailViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return OutgoingMailListSerializer
        return OutgoingMailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG', 'PS'):
            return OutgoingMail.objects.select_related('created_by', 'department').all()
        return OutgoingMail.objects.select_related('created_by', 'department').filter(
            db_models.Q(created_by=user) | db_models.Q(approvals__approver=user)
        ).distinct()

    def perform_create(self, serializer):
        year = datetime.date.today().year
        seq = OutgoingMail.objects.filter(mail_number__startswith=f'EDIV/OUT/{year}').count() + 1
        mail_number = f'EDIV/OUT/{year}/{seq:04d}'
        mail_obj = serializer.save(mail_number=mail_number, created_by=self.request.user)

        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            resource_type='OutgoingMail',
            resource_id=mail_obj.id,
            description=f"Created outgoing mail {mail_number}: {mail_obj.subject}",
        )

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_for_approval(self, request, pk=None):
        mail_obj = self.get_object()
        if mail_obj.status != 'DRAFT':
            return Response({'error': 'Only DRAFT mails can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        mail_obj.status = 'PENDING_APPROVAL'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='OutgoingMail',
            resource_id=mail_obj.id, description=f"Outgoing mail {mail_obj.mail_number} submitted for approval",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} submitted for approval."})

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_mail(self, request, pk=None):
        mail_obj = self.get_object()
        if request.user.role not in ('SYSADMIN', 'TG', 'PS'):
            return Response({'error': 'Only Admin/TG/PS can approve.'}, status=status.HTTP_403_FORBIDDEN)

        comments = request.data.get('comments', '')
        OutgoingMailApproval.objects.create(
            outgoing_mail=mail_obj, approver=request.user,
            status='APPROVED', comments=comments,
            approved_date=datetime.datetime.now(),
        )
        mail_obj.status = 'APPROVED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='APPROVE', resource_type='OutgoingMail',
            resource_id=mail_obj.id, description=f"Outgoing mail {mail_obj.mail_number} approved",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} approved."})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_mail(self, request, pk=None):
        mail_obj = self.get_object()
        if request.user.role not in ('SYSADMIN', 'TG', 'PS'):
            return Response({'error': 'Only Admin/TG/PS can reject.'}, status=status.HTTP_403_FORBIDDEN)

        comments = request.data.get('comments', '')
        OutgoingMailApproval.objects.create(
            outgoing_mail=mail_obj, approver=request.user,
            status='REJECTED', comments=comments,
            approved_date=datetime.datetime.now(),
        )
        mail_obj.status = 'REJECTED'
        mail_obj.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='REJECT', resource_type='OutgoingMail',
            resource_id=mail_obj.id, description=f"Outgoing mail {mail_obj.mail_number} rejected",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} rejected."})

    @action(detail=True, methods=['post'], url_path='dispatch')
    def dispatch_mail(self, request, pk=None):
        mail_obj = self.get_object()
        if mail_obj.status != 'APPROVED':
            return Response({'error': 'Only APPROVED mails can be dispatched.'}, status=status.HTTP_400_BAD_REQUEST)

        mail_obj.status = 'DISPATCHED'
        mail_obj.date_dispatched = datetime.date.today()
        mail_obj.save(update_fields=['status', 'date_dispatched', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='OutgoingMail',
            resource_id=mail_obj.id, description=f"Outgoing mail {mail_obj.mail_number} dispatched",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} dispatched."})

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver_mail(self, request, pk=None):
        mail_obj = self.get_object()
        if mail_obj.status != 'DISPATCHED':
            return Response({'error': 'Only DISPATCHED mails can be marked as delivered.'}, status=status.HTTP_400_BAD_REQUEST)

        mail_obj.status = 'DELIVERED'
        mail_obj.date_delivered = datetime.date.today()
        mail_obj.save(update_fields=['status', 'date_delivered', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='OutgoingMail',
            resource_id=mail_obj.id, description=f"Outgoing mail {mail_obj.mail_number} delivered",
        )
        return Response({'message': f"Mail {mail_obj.mail_number} marked as delivered."})


class SchoolHQCorrespondenceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return SchoolHQCorrespondenceListSerializer
        return SchoolHQCorrespondenceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG', 'PS'):
            return SchoolHQCorrespondence.objects.select_related('sender', 'recipient', 'school', 'department').all()
        return SchoolHQCorrespondence.objects.select_related('sender', 'recipient', 'school', 'department').filter(
            db_models.Q(sender=user) | db_models.Q(recipient=user)
        ).distinct()

    def perform_create(self, serializer):
        year = datetime.date.today().year
        direction = serializer.validated_data.get('direction', 'SCHOOL_TO_HQ')
        prefix = 'S2H' if direction == 'SCHOOL_TO_HQ' else 'H2S'
        seq = SchoolHQCorrespondence.objects.filter(reference_number__startswith=f'EDIV/{prefix}/{year}').count() + 1
        reference_number = f'EDIV/{prefix}/{year}/{seq:04d}'
        correspondence = serializer.save(reference_number=reference_number, sender=self.request.user)

        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            resource_type='SchoolHQCorrespondence',
            resource_id=correspondence.id,
            description=f"Created {direction} correspondence {reference_number}: {correspondence.subject}",
        )

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_correspondence(self, request, pk=None):
        correspondence = self.get_object()
        if correspondence.status != 'DRAFT':
            return Response({'error': 'Only DRAFT correspondences can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        correspondence.status = 'SUBMITTED'
        correspondence.date_submitted = datetime.date.today()
        correspondence.save(update_fields=['status', 'date_submitted', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='SchoolHQCorrespondence',
            resource_id=correspondence.id, description=f"Correspondence {correspondence.reference_number} submitted",
        )
        return Response({'message': f"Correspondence {correspondence.reference_number} submitted."})

    @action(detail=True, methods=['post'], url_path='receive')
    def receive_correspondence(self, request, pk=None):
        correspondence = self.get_object()
        correspondence.status = 'RECEIVED_AT_HQ'
        correspondence.date_received = datetime.date.today()
        correspondence.save(update_fields=['status', 'date_received', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='SchoolHQCorrespondence',
            resource_id=correspondence.id, description=f"Correspondence {correspondence.reference_number} received",
        )
        return Response({'message': f"Correspondence {correspondence.reference_number} marked as received."})

    @action(detail=True, methods=['post'], url_path='respond')
    def respond_to_correspondence(self, request, pk=None):
        correspondence = self.get_object()
        response_text = request.data.get('response', '')
        correspondence.response = response_text
        correspondence.status = 'COMPLETED'
        correspondence.date_resolved = datetime.date.today()
        correspondence.save(update_fields=['response', 'status', 'date_resolved', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='SchoolHQCorrespondence',
            resource_id=correspondence.id, description=f"Correspondence {correspondence.reference_number} responded to",
        )
        return Response({'message': f"Correspondence {correspondence.reference_number} responded to."})


class MailCorrespondenceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MailCorrespondenceListSerializer
        return MailCorrespondenceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG', 'PS'):
            return MailCorrespondence.objects.select_related('sender', 'recipient', 'department', 'school').all()
        return MailCorrespondence.objects.select_related('sender', 'recipient', 'department', 'school').filter(
            db_models.Q(sender=user) | db_models.Q(recipient=user)
        ).distinct()

    def perform_create(self, serializer):
        year = datetime.date.today().year
        corr_type = serializer.validated_data.get('correspondence_type', 'INTERNAL')
        type_prefix = {
            'INCOMING': 'INC', 'OUTGOING': 'OUT', 'INTERNAL': 'INT',
            'SCHOOL_HQ': 'S2H', 'HQ_SCHOOL': 'H2S', 'DEPARTMENT': 'DEPT'
        }.get(corr_type, 'INT')
        seq = MailCorrespondence.objects.filter(reference_number__startswith=f'EDIV/CORR/{type_prefix}/{year}').count() + 1
        reference_number = f'EDIV/CORR/{type_prefix}/{year}/{seq:04d}'
        correspondence = serializer.save(reference_number=reference_number, sender=self.request.user)

        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            resource_type='MailCorrespondence',
            resource_id=correspondence.id,
            description=f"Created correspondence {reference_number}: {correspondence.subject}",
        )

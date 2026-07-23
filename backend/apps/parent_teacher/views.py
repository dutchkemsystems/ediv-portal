from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import PTAMeeting, ParentTeacherMessage, StudentReportShare
from .serializers import (
    PTAMeetingSerializer, PTAMeetingListSerializer,
    ParentTeacherMessageSerializer, ParentTeacherMessageListSerializer,
    StudentReportShareSerializer, StudentReportShareListSerializer
)


class PTAMeetingViewSet(viewsets.ModelViewSet):
    queryset = PTAMeeting.objects.select_related('school', 'organized_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'meeting_type', 'status', 'scheduled_date']
    search_fields = ['title', 'description', 'venue']
    ordering_fields = ['scheduled_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PTAMeetingListSerializer
        return PTAMeetingSerializer


class ParentTeacherMessageViewSet(viewsets.ModelViewSet):
    queryset = ParentTeacherMessage.objects.select_related('sender', 'recipient', 'student__user').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['sender', 'recipient', 'student', 'category', 'is_read', 'is_urgent']
    search_fields = ['subject', 'body', 'student__user__first_name', 'student__user__last_name']
    ordering_fields = ['created_at', 'category']

    def get_serializer_class(self):
        if self.action == 'list':
            return ParentTeacherMessageListSerializer
        return ParentTeacherMessageSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['SYSADMIN', 'TG', 'PS']:
            return ParentTeacherMessage.objects.select_related('sender', 'recipient', 'student__user').all()
        return ParentTeacherMessage.objects.select_related('sender', 'recipient', 'student__user').filter(
            sender=user
        ) | ParentTeacherMessage.objects.select_related('sender', 'recipient', 'student__user').filter(
            recipient=user
        )


class StudentReportShareViewSet(viewsets.ModelViewSet):
    queryset = StudentReportShare.objects.select_related('student__user', 'shared_by', 'shared_with').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'report_type', 'academic_year', 'is_read']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['created_at', 'report_type']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentReportShareListSerializer
        return StudentReportShareSerializer

    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)

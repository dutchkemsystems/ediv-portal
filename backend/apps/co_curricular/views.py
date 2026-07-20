from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Activity, ActivityParticipant, Competition, CompetitionEntry
from .serializers import (
    ActivitySerializer, ActivityListSerializer,
    ActivityParticipantSerializer, CompetitionSerializer,
    CompetitionListSerializer, CompetitionEntrySerializer
)


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related('school', 'coordinator').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'activity_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ActivityListSerializer
        return ActivitySerializer


class ActivityParticipantViewSet(viewsets.ModelViewSet):
    queryset = ActivityParticipant.objects.select_related('activity', 'student__user').all()
    serializer_class = ActivityParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activity', 'student', 'is_active']


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['competition_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CompetitionListSerializer
        return CompetitionSerializer


class CompetitionEntryViewSet(viewsets.ModelViewSet):
    queryset = CompetitionEntry.objects.select_related('competition', 'student__user', 'school').all()
    serializer_class = CompetitionEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['competition', 'school', 'position']
    search_fields = ['student__user__first_name', 'student__user__last_name']
